# ── Tag CRUD ──────────────────────────────────────────────────────────────────


def test_create_tag(client):
    """POST /tags creates a tag and returns 201 with id and name."""
    r = client.post("/tags", json={"name": "python"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "python"
    assert "id" in data


def test_list_tags(client):
    """GET /tags returns all created tags."""
    client.post("/tags", json={"name": "python"})
    client.post("/tags", json={"name": "fastapi"})
    r = client.get("/tags")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "python" in names
    assert "fastapi" in names


def test_delete_tag(client):
    """DELETE /tags/{id} removes the tag (204)."""
    r = client.post("/tags", json={"name": "todelete"})
    tag_id = r.json()["id"]
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204
    ids = [t["id"] for t in client.get("/tags").json()]
    assert tag_id not in ids


def test_delete_nonexistent_tag_returns_404(client):
    r = client.delete("/tags/9999")
    assert r.status_code == 404


def test_create_duplicate_tag_returns_409(client):
    """Creating two tags with the same name returns 409 Conflict."""
    client.post("/tags", json={"name": "unique"})
    r = client.post("/tags", json={"name": "unique"})
    assert r.status_code == 409


# ── Note–Tag relations ─────────────────────────────────────────────────────────


def test_attach_tag_to_note(client):
    """POST /notes/{id}/tags attaches a tag; response is the updated note."""
    note = client.post("/notes/", json={"title": "T", "content": "C"}).json()
    tag = client.post("/tags", json={"name": "demo"}).json()
    r = client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    assert r.status_code == 200
    assert any(t["id"] == tag["id"] for t in r.json()["tags"])


def test_attach_tag_to_nonexistent_note_returns_404(client):
    tag = client.post("/tags", json={"name": "orphan"}).json()
    r = client.post("/notes/9999/tags", json={"tag_id": tag["id"]})
    assert r.status_code == 404


def test_attach_nonexistent_tag_returns_404(client):
    note = client.post("/notes/", json={"title": "T", "content": "C"}).json()
    r = client.post(f"/notes/{note['id']}/tags", json={"tag_id": 9999})
    assert r.status_code == 404


def test_detach_tag_from_note(client):
    """DELETE /notes/{id}/tags/{tag_id} removes the association."""
    note = client.post("/notes/", json={"title": "T", "content": "C"}).json()
    tag = client.post("/tags", json={"name": "detachme"}).json()
    client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    r = client.delete(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 200
    assert not any(t["id"] == tag["id"] for t in r.json()["tags"])


def test_detach_tag_not_on_note_returns_404(client):
    """Detaching a tag that isn't on the note returns 404."""
    note = client.post("/notes/", json={"title": "T", "content": "C"}).json()
    tag = client.post("/tags", json={"name": "notattached"}).json()
    r = client.delete(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 404


def test_note_tags_visible_in_note_read(client):
    """GET /notes/{id} returns the note with its attached tags."""
    note = client.post("/notes/", json={"title": "Tagged", "content": "Content"}).json()
    tag = client.post("/tags", json={"name": "visible"}).json()
    client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    data = r.json()
    assert "tags" in data
    assert any(t["name"] == "visible" for t in data["tags"])


def test_delete_tag_cascades_from_note(client):
    """Deleting a tag removes it from any notes it was attached to."""
    note = client.post("/notes/", json={"title": "T", "content": "C"}).json()
    tag = client.post("/tags", json={"name": "cascade"}).json()
    client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    client.delete(f"/tags/{tag['id']}")
    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert not any(t["id"] == tag["id"] for t in r.json()["tags"])


def test_filter_notes_by_tag(client):
    """GET /notes/search/?tag_id=N returns only notes bearing that tag."""
    note1 = client.post("/notes/", json={"title": "Tagged note", "content": "yes"}).json()
    client.post("/notes/", json={"title": "Untagged note", "content": "no"})
    tag = client.post("/tags", json={"name": "filter-tag"}).json()
    client.post(f"/notes/{note1['id']}/tags", json={"tag_id": tag["id"]})
    r = client.get("/notes/search/", params={"tag_id": tag["id"]})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == note1["id"]
