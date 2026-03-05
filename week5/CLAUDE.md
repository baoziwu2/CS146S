# CLAUDE.md — Week 5 Project Guide

## Project Overview

Full-stack note-taking app (autonomous coding agent starter).

- **Backend**: FastAPI + SQLite (SQLAlchemy ORM)
- **Frontend**: Static HTML/JS served by FastAPI
- **Tests**: pytest + FastAPI TestClient (in-memory SQLite per test)

### Data Models

| Model | Table | Fields |
|---|---|---|
| `Note` | `notes` | `id`, `title` (str, ≤200), `content` (text) |
| `ActionItem` | `action_items` | `id`, `description` (text), `completed` (bool) |

### Existing API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/notes/` | List all notes |
| POST | `/notes/` | Create note `{title, content}` |
| GET | `/notes/{id}` | Get note by ID (404 if missing) |
| GET | `/notes/search/?q=...` | Search notes by title/content |
| GET | `/action-items/` | List all action items |
| POST | `/action-items/` | Create action item `{description}` |
| PUT | `/action-items/{id}/complete` | Mark item as completed (404 if missing) |

### Key Source Files

```
backend/app/
  main.py          # FastAPI app, mounts static frontend, startup hook
  models.py        # SQLAlchemy models (Note, ActionItem)
  schemas.py       # Pydantic schemas (NoteCreate/Read, ActionItemCreate/Read)
  db.py            # Engine, session factory, get_db dependency, seed
  routers/
    notes.py       # Note CRUD routes
    action_items.py # ActionItem routes
  services/
    extract.py     # extract_action_items(text) -> list[str]
backend/tests/
  conftest.py      # `client` fixture: in-memory SQLite + TestClient per test
  test_notes.py    # Note endpoint tests
  test_action_items.py
  test_extract.py
```

---

## Environment Setup (Windows)

This project uses a **week5-local virtual environment** created with the native Windows Python 3.13.

```bash
# 1. Create venv (only once)
py -3.13 -m venv venv

# 2. Activate (Git Bash)
source venv/Scripts/activate

# 3. Install all dependencies
pip install "fastapi>=0.111.0" "uvicorn[standard]>=0.23.0" \
  "sqlalchemy>=2.0.0" "pydantic>=2.0.0" "python-dotenv>=1.0.0" \
  "openai>=1.0.0" "ollama>=0.5.3" \
  "pytest>=7.0.0" "httpx>=0.24.0" "black>=24.1.0" \
  "ruff>=0.4.0" "pre-commit>=3.6.0"
```

> **Important — shell requirement**: All `make` commands use bash syntax.
> Run them from **Git Bash** (not PowerShell/cmd). If you must use PowerShell,
> the Makefile `SHELL` is already set to `C:/Program Files/Git/usr/bin/bash.exe`.

### Make Targets

```bash
make run     # Start dev server at http://localhost:8000 (hot-reload)
make test    # Run pytest
make format  # black + ruff --fix
make lint    # ruff check
make seed    # Apply DB seed data
```

Tests use a **fresh in-memory SQLite DB per test case** via the `client` fixture in `conftest.py`. No external services needed.

---

## Available Tasks (`docs/TASKS.md`)

Short list of open work items (see full file for details):

1. **Migrate frontend to Vite + React** (complex)
2. **Notes search with pagination and sorting** (medium)
3. **Full Notes CRUD** — add `PUT /notes/{id}`, `DELETE /notes/{id}` (medium)
4. **Action items: filters and bulk complete** (medium)
5. **Tags — many-to-many with notes** (complex)
6. **Improve extraction logic** — parse `#hashtags`, `- [ ] tasks` (medium)
7. **Robust error handling and response envelopes** (easy-medium)
8. **List endpoint pagination** (easy)
9. **Query performance and indexes** (easy-medium)
10. **Test coverage improvements** (easy)
11. **Deploy to Vercel** (medium-complex)

---

## Development Workflow — Strict TDD

All feature development **must** follow this six-step TDD cycle. Each step is a
hard gate — do not move to the next until the current step is complete.

---

### Step 1 — Write tests only (no implementation)

**You are doing TDD. Write only tests — do not write any implementation code.**

Write tests in the appropriate file under `backend/tests/`. Base every test on
concrete expected inputs and outputs, not on internal implementation details.
One test per behaviour. Cover the happy path and at least one failure/edge case.

```python
# Example: test an endpoint that doesn't exist yet
def test_delete_note_returns_204(client):
    r = client.post("/notes/", json={"title": "x", "content": "y"})
    note_id = r.json()["id"]
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

def test_delete_nonexistent_note_returns_404(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404
```

Use the existing `client` fixture from `conftest.py` — do not create new fixtures
unless the new feature genuinely requires a different DB state.

---

### Step 2 — Run tests and confirm they fail

```bash
make test
```

**All new tests must fail at this point.**
If a test passes without implementation, it is not testing anything useful — go
back and strengthen it. Do not write any implementation code yet.

---

### Step 3 — Commit the tests

```bash
git add backend/tests/<changed file>
git commit -m "test: <what behaviour these tests cover>"
```

Only stage test files. No implementation files.

---

### Step 4 — Write implementation code to make tests pass

**Do not modify any test files.** Only edit files under `backend/app/`.

Iterate until `make test` passes with no failures. Allowed changes:
- Add/modify routes in `routers/`
- Add/modify models in `models.py`
- Add/modify schemas in `schemas.py`
- Add/modify service logic in `services/`

Run `make test` after every meaningful change.
Run `make lint` before committing.

---

### Step 5 — Verify with a subagent (no overfitting)

Before committing implementation, launch a subagent with the following prompt:

> "Review the tests in `backend/tests/` and the implementation in
> `backend/app/`. Check whether the implementation is overfit to the tests —
> i.e., it handles only the exact inputs used in the tests rather than the
> general case. Report any hardcoded values, special-cased IDs, or logic that
> would fail on inputs not present in the tests. Do not suggest fixes — only
> report findings."

Fix any overfitting found before proceeding.

---

### Step 5.5 — E2E smoke test with Playwright MCP (frontend features only)

When a task involves **frontend-visible behaviour** (UI rendering, form
submission, navigation, etc.), run a quick browser smoke test after all unit
tests pass and before committing.

**Prerequisites**: the dev server must be running (`make run` in a separate
terminal, default `http://localhost:8000`).

Use the Playwright MCP tools in this order:

1. **Navigate** to the relevant page:
   ```
   browser_navigate  url="http://localhost:8000"
   ```
2. **Snapshot** the page to verify the DOM structure is correct:
   ```
   browser_snapshot
   ```
3. **Interact** (click buttons, fill forms) to exercise the new feature:
   ```
   browser_click / browser_type / browser_fill_form
   ```
4. **Assert** the expected outcome is visible in a follow-up snapshot or
   screenshot. If the page shows an error or the expected element is absent,
   treat this as a failing gate — fix the issue before proceeding.

> **Scope**: Only run Playwright smoke tests for tasks that have a UI
> component. Pure backend / API-only tasks skip this step.

---

### Step 6 — Commit the implementation

```bash
git add backend/app/<changed files>
git commit -m "feat: <what was implemented>"
```

Only stage implementation files. Do not re-stage test files unless a test
genuinely needed a bug fix (document why in the commit message).

---

## Code Style

- Line length: **100** characters (`black`, `ruff` both configured for this)
- Python target: **3.10+**
- Ruff rules: `E, F, I, UP, B` (ignoring `E501`, `B008`)
- All new schemas use `model_config = ConfigDict(from_attributes=True)` (Pydantic v2 style)
- Keep routers thin — business logic belongs in `services/`
