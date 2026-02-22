.PHONY: run test format lint seed
SHELL := powershell.exe
.SHELLFLAGS := -NoProfile -Command

run:
	$$env:PYTHONPATH='.'; uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
test:
	$$env:PYTHONPATH='.'; pytest -q backend/tests

format:
	black .
	ruff check . --fix

lint:
	ruff check .

seed:
	$$env:PYTHONPATH='.'; python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
