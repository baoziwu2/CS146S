# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands must be run from the `week7/` directory with `PYTHONPATH=.` set (handled by the Makefile targets).

```bash
make run       # Start the dev server at http://localhost:8000
make test      # Run all tests with pytest
make format    # Auto-format with black + ruff --fix
make lint      # Check with ruff (no auto-fix)
make seed      # Seed the SQLite database manually
```

Run a single test file:
```bash
PYTHONPATH=. pytest -q backend/tests/test_notes.py
```

Run a single test by name:
```bash
PYTHONPATH=. pytest -q -k "test_name"
```

## Architecture

This is a FastAPI + SQLite full-stack app with a static vanilla-JS frontend.

**Request flow:** browser → FastAPI (`/`) → `frontend/index.html`; API calls hit `/notes` or `/action-items` routers → SQLAlchemy ORM → SQLite at `data/app.db`.

**Key layers:**
- `backend/app/main.py` — app bootstrap, mounts `/static` → `frontend/`, includes routers, runs `Base.metadata.create_all` + seed on startup
- `backend/app/models.py` — SQLAlchemy models (`Note`, `ActionItem`) with `TimestampMixin` (`created_at`, `updated_at`)
- `backend/app/schemas.py` — Pydantic schemas: `*Create`, `*Read`, `*Patch` variants for each model
- `backend/app/routers/` — one file per resource; list endpoints support `skip`/`limit` pagination, `sort` (prefix `-` for desc), and optional filters (e.g., `?completed=true`)
- `backend/app/services/extract.py` — pure function `extract_action_items(text)` for parsing action items from free text
- `backend/app/db.py` — `get_db()` FastAPI dependency (yields a session, commits on success, rolls back on exception); `apply_seed_if_needed()` seeds only on first run

**Database:** SQLite at `./data/app.db` (relative to the working directory). Override with the `DATABASE_PATH` env var or a `.env` file.

**Tests:** `backend/tests/conftest.py` creates a throwaway in-memory SQLite DB per test via a `client` fixture that overrides `get_db`. Tests use `TestClient` and hit real HTTP endpoints.

## Development Workflow

**Strictly follow** this TDD process for every task — do not skip or reorder steps.

1. Read `docs/TASKS.md`; ask the user to clarify anything ambiguous before proceeding.
2. Write tests based on expected inputs/outputs. Explicitly state you are doing TDD to prevent generating mock implementations.
3. Run the tests and confirm they **fail**. Do not write any implementation code at this point.
4. Commit the failing tests.
5. Write implementation code to make the tests pass. **Do not modify the tests** — iterate on the implementation only until tests pass.
6. Use a sub-agent to validate that the implementation is not overfit to the tests.
8. Commit the implementation.

## Conventions

- Routers use `db.flush()` + `db.refresh()` after writes (not `db.commit()`) — the session commits in `get_db()`.
- PATCH endpoints accept all-optional Pydantic models; only non-`None` fields are applied.
- Sort parameter convention: bare field name = ascending, `-field` = descending; invalid fields silently fall back to `-created_at`.
- The `extract_action_items` service is intentionally kept as a pure function with no DB access.
