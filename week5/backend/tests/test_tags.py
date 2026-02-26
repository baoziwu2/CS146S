# Task 5: Tags feature with many-to-many relation


# ── Tag CRUD ──────────────────────────────────────────────────────────────────


def test_create_and_list_tags(client):
    """POST /tags/ creates a tag; GET /tags/ returns it."""
    r = client.post("/tags/", json={"name": "python"})
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "python"
    assert "id" in data

    r = client.get("/tags/")
    assert r.status_code == 200
    tags = r.json()
    assert any(t["name"] == "python" for t in tags)


def test_delete_tag(client):
    """DELETE /tags/{id} removes the tag and returns 204."""
    r = client.post("/tags/", json={"name": "todelete"})
    assert r.status_code == 201
    tag_id = r.json()["id"]

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get("/tags/")
    assert not any(t["id"] == tag_id for t in r.json())


def test_delete_nonexistent_tag_returns_404(client):
    """DELETE /tags/9999 returns 404."""
    r = client.delete("/tags/9999")
    assert r.status_code == 404


def test_duplicate_tag_name_returns_409(client):
    """Creating a tag with a duplicate name returns 409 Conflict."""
    client.post("/tags/", json={"name": "unique"})
    r = client.post("/tags/", json={"name": "unique"})
    assert r.status_code == 409


# ── Note-tag relations ────────────────────────────────────────────────────────


def test_attach_tag_to_note(client):
    """POST /notes/{id}/tags attaches a tag; response includes the tag."""
    note_id = client.post("/notes/", json={"title": "Tagged Note", "content": "content"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "mytag"}).json()["id"]

    r = client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "tags" in data
    assert any(t["id"] == tag_id for t in data["tags"])


def test_detach_tag_from_note(client):
    """DELETE /notes/{id}/tags/{tag_id} removes the relation."""
    note_id = client.post("/notes/", json={"title": "Detach note", "content": "content"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "detachtag"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})

    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 200, r.text
    data = r.json()
    assert not any(t["id"] == tag_id for t in data["tags"])


def test_note_read_includes_tags(client):
    """GET /notes/{id} response includes a 'tags' list."""
    note_id = client.post("/notes/", json={"title": "Note with tags", "content": "content"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "visible"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert "tags" in data
    assert any(t["name"] == "visible" for t in data["tags"])


def test_notes_list_includes_tags(client):
    """GET /notes/ returns notes each with a 'tags' field."""
    note_id = client.post("/notes/", json={"title": "Listed tag note", "content": "content"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "listed"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})

    r = client.get("/notes/")
    assert r.status_code == 200
    note = next(n for n in r.json() if n["id"] == note_id)
    assert "tags" in note
    assert any(t["name"] == "listed" for t in note["tags"])


def test_attach_tag_to_nonexistent_note_returns_404(client):
    """POST /notes/9999/tags returns 404."""
    tag_id = client.post("/tags/", json={"name": "orphan"}).json()["id"]
    r = client.post("/notes/9999/tags", json={"tag_id": tag_id})
    assert r.status_code == 404


def test_attach_nonexistent_tag_returns_404(client):
    """POST /notes/{id}/tags with unknown tag_id returns 404."""
    note_id = client.post("/notes/", json={"title": "Note", "content": "content"}).json()["id"]
    r = client.post(f"/notes/{note_id}/tags", json={"tag_id": 9999})
    assert r.status_code == 404


def test_detach_nonexistent_relation_returns_404(client):
    """DELETE /notes/{id}/tags/{tag_id} when not attached returns 404."""
    note_id = client.post("/notes/", json={"title": "Note", "content": "content"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "notattached"}).json()["id"]

    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 404


# ── Filter notes by tag ───────────────────────────────────────────────────────


def test_filter_notes_by_tag(client):
    """GET /notes/?tag_id=... returns only notes with that tag."""
    note1_id = client.post("/notes/", json={"title": "Tagged", "content": "has tag"}).json()["id"]
    client.post("/notes/", json={"title": "Untagged", "content": "no tag"})

    tag_id = client.post("/tags/", json={"name": "filter_tag"}).json()["id"]
    client.post(f"/notes/{note1_id}/tags", json={"tag_id": tag_id})

    r = client.get("/notes/", params={"tag_id": tag_id})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["id"] == note1_id


# ── Cascade delete ────────────────────────────────────────────────────────────


def test_cascade_delete_note_keeps_tag(client):
    """Deleting a note removes the relation but the Tag itself survives."""
    note_id = client.post("/notes/", json={"title": "Cascade", "content": "content"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "survivor"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get("/tags/")
    assert any(t["id"] == tag_id for t in r.json())


def test_cascade_delete_tag_keeps_note(client):
    """Deleting a tag removes the relation but the Note itself survives."""
    note_id = client.post("/notes/", json={"title": "Note survives", "content": "content"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "deletedtag"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    data = r.json()
    assert not any(t["id"] == tag_id for t in data["tags"])
