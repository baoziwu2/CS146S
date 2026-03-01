# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Assignment Context

This is the **Week 6 assignment** for CS146S: run Semgrep static analysis against the app, triage findings, and fix at least 3 security vulnerabilities. The codebase intentionally contains multiple security issues for educational purposes.

## Commands

All commands should be run from `week6/` (this directory):

```bash
make run      # Start FastAPI dev server at http://127.0.0.1:8000
make test     # Run pytest suite
make lint     # Check with ruff
make format   # Auto-format with black + ruff --fix
make seed     # Seed the SQLite database
```

Run a single test file:
```bash
PYTHONPATH=. pytest -q backend/tests/test_notes.py
```

Run Semgrep scan (from repo root):
```bash
semgrep ci --subdir week6
```

## Architecture

**Full-stack app** — FastAPI backend serving both REST API and static frontend files.

- `backend/app/main.py` — App entry point: registers routers, mounts `frontend/` as `/static`, seeds DB on startup
- `backend/app/db.py` — SQLite via SQLAlchemy; `DATABASE_PATH` env var sets DB file; `apply_seed_if_needed()` runs `data/seed.sql` on first start
- `backend/app/models.py` — ORM models: `Note`, `ActionItem` (both with timestamp mixin)
- `backend/app/schemas.py` — Pydantic request/response schemas
- `backend/app/routers/notes.py` — Notes CRUD + debug endpoints
- `backend/app/routers/action_items.py` — Action items CRUD
- `backend/app/services/extract.py` — Parses note content to extract action items (lines starting with `TODO:`/`ACTION:` or ending with `!`)
- `frontend/` — Vanilla HTML/JS/CSS; `app.js` fetches from the API and renders results
- `backend/tests/conftest.py` — Pytest fixtures; uses an in-memory SQLite DB for tests

## Development Process (TDD)

Follow test-driven development in this order:

1. **Write tests first** — based on expected inputs/outputs. Explicitly tell Claude you are doing TDD to prevent it from generating mock implementations or jumping straight to business logic.
2. **Confirm tests fail** — run `make test` and verify the new tests are red. Tell Claude *not to write implementation code* at this step; only check that the tests fail correctly.
3. **Commit the tests** — keep test commits separate from implementation commits.
4. **Write the implementation** — tell Claude to make the tests pass **without modifying the tests**. Let it iterate until everything is green.
5. **Validate with a subagent** — have a subagent independently review the implementation to confirm it is not overfitted to the test cases (i.e., it is genuinely general, not hardcoded to match test inputs).
6. **Commit the implementation** — commit separately once all tests pass.

## Intentional Vulnerabilities (Semgrep Targets)

The following issues are deliberately planted for the assignment:

| Location | Issue |
|---|---|
| `routers/notes.py` `unsafe_search()` | SQL injection via raw string interpolation |
| `routers/notes.py` `/debug/eval` | Arbitrary Python `eval()` execution |
| `routers/notes.py` `/debug/run` | Shell command injection via `subprocess` |
| `routers/notes.py` `/debug/fetch` | SSRF — fetches arbitrary URLs |
| `routers/notes.py` `/debug/read` | Path traversal — reads arbitrary files |
| `routers/notes.py` `/debug/hash-md5` | Weak cryptography (MD5) |
| `services/extract.py` | Hardcoded API token/secret |
| `frontend/app.js` | XSS via `innerHTML` with unsanitized data |
| `main.py` | Overly permissive CORS (`allow_origins=["*"]`) |
| `requirements.txt` | Outdated dependencies with known CVEs |

When fixing issues, prefer minimal targeted changes. Re-run `semgrep ci --subdir week6` after each fix to confirm the finding is resolved.
