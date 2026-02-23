"""
Drift check: verify that the endpoints documented in docs/API.md all exist
in the live OpenAPI schema.  Run `make test` after any route change to catch
docs drift early.
"""

from pathlib import Path

from backend.app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

DOCUMENTED_ROUTES = [
    ("get", "/notes/"),
    ("post", "/notes/"),
    ("get", "/notes/search/"),
    ("get", "/notes/{note_id}"),
    ("put", "/notes/{note_id}"),
    ("delete", "/notes/{note_id}"),
    ("post", "/notes/{note_id}/extract"),
    ("get", "/action-items/"),
    ("post", "/action-items/"),
    ("put", "/action-items/{item_id}/complete"),
]


def test_openapi_schema_reachable():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    assert "paths" in r.json()


def test_documented_routes_exist_in_openapi():
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    missing = []
    for method, path in DOCUMENTED_ROUTES:
        if path not in paths or method not in paths[path]:
            missing.append(f"{method.upper()} {path}")
    assert not missing, f"Routes in API.md missing from OpenAPI: {missing}"


def test_api_md_exists():
    api_md = Path(__file__).parents[2] / "docs" / "API.md"
    assert api_md.exists(), "docs/API.md not found"
    assert api_md.stat().st_size > 0, "docs/API.md is empty"
