import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

# ── Resolve the DB URL ────────────────────────────────────────────────────────
# Priority: DATABASE_URL env var (Neon/Postgres) → local SQLite fallback
_raw_url = os.getenv("DATABASE_URL", "")

# Heroku / some Neon configs emit postgres:// which SQLAlchemy needs as postgresql://
if _raw_url.startswith("postgres://"):
    _raw_url = _raw_url.replace("postgres://", "postgresql://", 1)

# psycopg2 doesn't understand channel_binding — strip it to avoid connection errors
if _raw_url.startswith("postgresql://") and "channel_binding" in _raw_url:
    parsed = urlparse(_raw_url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("channel_binding", None)
    _raw_url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))

DATABASE_URL: str = _raw_url or f"sqlite:///{os.getenv('DATABASE_PATH', './data/app.db')}"
_is_sqlite: bool = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()


def apply_seed_if_needed() -> None:
    """Seed the database on first run (idempotent — skips if rows already exist)."""
    # Ensure the SQLite data directory exists
    if _is_sqlite:
        db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)

    # Check whether data is already present
    try:
        with engine.connect() as conn:
            if conn.execute(text("SELECT COUNT(*) FROM notes")).scalar() > 0:
                return  # already seeded
    except Exception:  # noqa: BLE001
        return  # table may not exist yet; create_all runs before this

    seed_file = Path("./data/seed.sql")
    if not seed_file.exists():
        return

    sql = seed_file.read_text()
    statements = [s.strip() for s in sql.split(";") if s.strip() and not s.strip().startswith("--")]

    if _is_sqlite:
        # SQLite: run everything (CREATE TABLE + INSERT) from the seed file
        with engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))
    else:
        # Postgres: schema is handled by SQLAlchemy create_all; only run INSERTs
        insert_stmts = [s for s in statements if s.upper().lstrip().startswith("INSERT")]
        with engine.begin() as conn:
            for stmt in insert_stmts:
                conn.execute(text(stmt))
