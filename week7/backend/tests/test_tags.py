# TDD tests for Task 3: Tags model and note-tag relationships
# Written before any implementation.


# ---------------------------------------------------------------------------
# Tag CRUD
# ---------------------------------------------------------------------------

def test_create_tag(client):
    r = client.post("/tags/", json={"name": "urgent"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "urgent"
    assert "id" in data
    assert "created_at" in data


def test_list_tags(client):
    client.post("/tags/", json={"name": "alpha"})
    client.post("/tags/", json={"name": "beta"})
    r = client.get("/tags/")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "alpha" in names
    assert "beta" in names


def test_create_duplicate_tag_returns_409(client):
    client.post("/tags/", json={"name": "duplicate"})
    r = client.post("/tags/", json={"name": "duplicate"})
    assert r.status_code == 409


def test_create_tag_empty_name_returns_422(client):
    r = client.post("/tags/", json={"name": ""})
    assert r.status_code == 422


def test_create_tag_name_too_long_returns_422(client):
    r = client.post("/tags/", json={"name": "x" * 51})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Attach / detach tag to note
# ---------------------------------------------------------------------------

def test_attach_tag_to_note(client):
    note = client.post("/notes/", json={"title": "My note", "content": "content"}).json()
    tag = client.post("/tags/", json={"name": "important"}).json()

    r = client.post(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 200
    data = r.json()
    tag_names = [t["name"] for t in data["tags"]]
    assert "important" in tag_names


def test_attach_tag_note_not_found(client):
    tag = client.post("/tags/", json={"name": "orphan"}).json()
    r = client.post(f"/notes/99999/tags/{tag['id']}")
    assert r.status_code == 404


def test_attach_tag_not_found(client):
    note = client.post("/notes/", json={"title": "Note", "content": "c"}).json()
    r = client.post(f"/notes/{note['id']}/tags/99999")
    assert r.status_code == 404


def test_attach_tag_idempotent(client):
    note = client.post("/notes/", json={"title": "Note", "content": "c"}).json()
    tag = client.post("/tags/", json={"name": "dup-attach"}).json()
    client.post(f"/notes/{note['id']}/tags/{tag['id']}")
    r = client.post(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 200
    # Tag should appear only once
    assert sum(1 for t in r.json()["tags"] if t["name"] == "dup-attach") == 1


def test_detach_tag_from_note(client):
    note = client.post("/notes/", json={"title": "Note", "content": "c"}).json()
    tag = client.post("/tags/", json={"name": "removable"}).json()
    client.post(f"/notes/{note['id']}/tags/{tag['id']}")

    r = client.delete(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 200
    tag_names = [t["name"] for t in r.json()["tags"]]
    assert "removable" not in tag_names


def test_detach_tag_note_not_found(client):
    tag = client.post("/tags/", json={"name": "x"}).json()
    r = client.delete(f"/notes/99999/tags/{tag['id']}")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Tags included in note responses
# ---------------------------------------------------------------------------

def test_get_note_includes_tags(client):
    note = client.post("/notes/", json={"title": "Tagged note", "content": "c"}).json()
    tag = client.post("/tags/", json={"name": "featured"}).json()
    client.post(f"/notes/{note['id']}/tags/{tag['id']}")

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert "tags" in r.json()
    assert any(t["name"] == "featured" for t in r.json()["tags"])


def test_list_notes_includes_tags(client):
    note = client.post("/notes/", json={"title": "Listed", "content": "c"}).json()
    tag = client.post("/tags/", json={"name": "listed-tag"}).json()
    client.post(f"/notes/{note['id']}/tags/{tag['id']}")

    r = client.get("/notes/")
    assert r.status_code == 200
    matched = next(n for n in r.json() if n["id"] == note["id"])
    assert any(t["name"] == "listed-tag" for t in matched["tags"])


def test_new_note_has_empty_tags(client):
    note = client.post("/notes/", json={"title": "Fresh", "content": "c"}).json()
    assert note["tags"] == []
