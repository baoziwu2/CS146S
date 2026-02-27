"""Task 9 — verify DB indexes exist and that large datasets produce no regressions."""

from sqlalchemy import text


# ---------------------------------------------------------------------------
# Schema inspection helpers
# ---------------------------------------------------------------------------


def _index_names(engine, table: str) -> set[str]:
    """Return the set of index names SQLite reports for *table*."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name=:t"),
            {"t": table},
        ).fetchall()
    return {row[0] for row in rows}


# ---------------------------------------------------------------------------
# Index-existence tests (fail until models.py adds the indexes)
# ---------------------------------------------------------------------------


def test_notes_title_index_exists(db_engine):
    """notes.title must be indexed to speed up ORDER BY title and prefix searches."""
    names = _index_names(db_engine, "notes")
    assert any("title" in n for n in names), f"No title index found on notes; got {names}"


def test_action_items_completed_index_exists(db_engine):
    """action_items.completed must be indexed to speed up completed=true/false filters."""
    names = _index_names(db_engine, "action_items")
    assert any("completed" in n for n in names), (
        f"No completed index found on action_items; got {names}"
    )


def test_note_tags_tag_id_index_exists(db_engine):
    """note_tags.tag_id must have its own index for efficient 'notes by tag' joins."""
    names = _index_names(db_engine, "note_tags")
    assert any("tag_id" in n for n in names), (
        f"No tag_id index found on note_tags; got {names}"
    )


# ---------------------------------------------------------------------------
# Large-dataset no-regression tests
# ---------------------------------------------------------------------------


def test_list_notes_large_dataset_pagination(client):
    """Seeding 50 notes and paginating must return correct totals and item counts."""
    for i in range(50):
        r = client.post("/notes/", json={"title": f"Note {i:02d}", "content": f"Content {i}"})
        assert r.status_code == 201

    r = client.get("/notes/", params={"page": 1, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 50
    assert len(data["items"]) == 10
    assert data["page"] == 1

    r = client.get("/notes/", params={"page": 5, "page_size": 10})
    data = r.json()["data"]
    assert data["total"] == 50
    assert len(data["items"]) == 10

    # Page beyond the last should return 0 items, not an error
    r = client.get("/notes/", params={"page": 6, "page_size": 10})
    data = r.json()["data"]
    assert data["total"] == 50
    assert len(data["items"]) == 0


def test_search_notes_large_dataset(client):
    """Searching across 50 notes must return only matching notes with correct total."""
    for i in range(40):
        client.post("/notes/", json={"title": f"Generic {i}", "content": "Nothing special"})
    for i in range(10):
        client.post("/notes/", json={"title": f"Special {i}", "content": "unique keyword"})

    r = client.get("/notes/search/", params={"q": "unique keyword", "page": 1, "page_size": 20})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 10
    assert len(data["items"]) == 10


def test_filter_action_items_large_dataset(client):
    """Filtering action items by completed across 60 items must return accurate subsets."""
    for i in range(40):
        r = client.post("/action-items/", json={"description": f"Pending task {i}"})
        assert r.status_code == 201

    for i in range(20):
        r = client.post("/action-items/", json={"description": f"Done task {i}"})
        assert r.status_code == 201
        item_id = r.json()["data"]["id"]
        client.put(f"/action-items/{item_id}/complete")

    r = client.get("/action-items/", params={"completed": "false", "page": 1, "page_size": 50})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 40

    r = client.get("/action-items/", params={"completed": "true", "page": 1, "page_size": 50})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 20


def test_notes_tag_filter_large_dataset(client):
    """Tag-filtered list must return only notes carrying that tag, across many notes."""
    r = client.post("/tags/", json={"name": "important"})
    tag_id = r.json()["data"]["id"]

    # Create 30 notes without the tag and 5 with it
    for i in range(30):
        client.post("/notes/", json={"title": f"Plain {i}", "content": "no tag"})

    for i in range(5):
        r = client.post("/notes/", json={"title": f"Tagged {i}", "content": "#important"})
        note_id = r.json()["data"]["id"]
        client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})

    r = client.get("/notes/", params={"tag_id": tag_id, "page": 1, "page_size": 20})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 5
    assert len(data["items"]) == 5
