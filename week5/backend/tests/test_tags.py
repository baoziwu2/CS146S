# ── Tag CRUD (Task 5) ──────────────────────────────────────────────────────────


def test_create_tag_returns_201(client):
    r = client.post("/tags/", json={"name": "python"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "python"
    assert "id" in data


def test_create_duplicate_tag_returns_409(client):
    client.post("/tags/", json={"name": "python"})
    r = client.post("/tags/", json={"name": "python"})
    assert r.status_code == 409


def test_list_tags_returns_all(client):
    client.post("/tags/", json={"name": "python"})
    client.post("/tags/", json={"name": "javascript"})
    r = client.get("/tags/")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "python" in names
    assert "javascript" in names


def test_delete_tag_returns_204(client):
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204
    tags = client.get("/tags/").json()
    assert not any(t["id"] == tag_id for t in tags)


def test_delete_nonexistent_tag_returns_404(client):
    r = client.delete("/tags/9999")
    assert r.status_code == 404


# ── Note-tag attachment / detachment (Task 5) ─────────────────────────────────


def test_attach_tag_to_note(client):
    note_id = client.post("/notes/", json={"title": "Tagged", "content": "note body"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    r = client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    assert r.status_code == 200
    assert any(t["id"] == tag_id for t in r.json()["tags"])


def test_note_read_includes_tags(client):
    note_id = client.post("/notes/", json={"title": "Tagged", "content": "note body"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    note = r.json()
    assert "tags" in note
    assert any(t["id"] == tag_id for t in note["tags"])


def test_attach_nonexistent_tag_returns_404(client):
    note_id = client.post("/notes/", json={"title": "T", "content": "c"}).json()["id"]
    r = client.post(f"/notes/{note_id}/tags", json={"tag_id": 9999})
    assert r.status_code == 404


def test_attach_tag_to_nonexistent_note_returns_404(client):
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    r = client.post("/notes/9999/tags", json={"tag_id": tag_id})
    assert r.status_code == 404


def test_detach_tag_from_note(client):
    note_id = client.post("/notes/", json={"title": "T", "content": "c"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 200
    assert not any(t["id"] == tag_id for t in r.json()["tags"])


def test_detach_unattached_tag_returns_404(client):
    """Tag exists but was never attached to this note — should 404."""
    note_id = client.post("/notes/", json={"title": "T", "content": "c"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 404


# ── Cascade behaviour (Task 5) ────────────────────────────────────────────────


def test_delete_tag_removes_from_note_note_survives(client):
    note_id = client.post("/notes/", json={"title": "T", "content": "c"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    client.delete(f"/tags/{tag_id}")
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert not any(t["id"] == tag_id for t in r.json()["tags"])


def test_delete_note_does_not_delete_tag(client):
    note_id = client.post("/notes/", json={"title": "T", "content": "c"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    client.delete(f"/notes/{note_id}")
    tags = client.get("/tags/").json()
    assert any(t["id"] == tag_id for t in tags)


# ── Search filter by tag (Task 5) ─────────────────────────────────────────────


def test_search_filter_by_tag_returns_tagged_notes_only(client):
    note_id = client.post("/notes/", json={"title": "Python note", "content": "about py"}).json()["id"]
    client.post("/notes/", json={"title": "JS note", "content": "about js"})
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})

    r = client.get("/notes/search/", params={"tag": "python"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == note_id


def test_search_filter_by_tag_no_results(client):
    client.post("/notes/", json={"title": "Untagged", "content": "no tags here"})
    r = client.get("/notes/search/", params={"tag": "nonexistent"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_search_combined_q_and_tag_filter(client):
    """Both q= and tag= filters apply together (AND semantics)."""
    note_id = client.post("/notes/", json={"title": "Python TDD", "content": "tdd content"}).json()["id"]
    other_id = client.post("/notes/", json={"title": "Python OOP", "content": "oop content"}).json()["id"]
    tag_id = client.post("/tags/", json={"name": "python"}).json()["id"]
    client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    client.post(f"/notes/{other_id}/tags", json={"tag_id": tag_id})

    # Both notes have #python tag; only one matches q="TDD"
    r = client.get("/notes/search/", params={"q": "TDD", "tag": "python"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == note_id
