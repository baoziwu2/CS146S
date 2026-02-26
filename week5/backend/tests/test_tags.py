# ── Tag CRUD ──────────────────────────────────────────────────────────────────


def test_list_tags_initially_empty(client):
    """GET /tags returns an empty list when no tags exist."""
    r = client.get("/tags")
    assert r.status_code == 200
    assert r.json() == []


def test_create_tag_returns_201(client):
    """POST /tags creates a tag and returns 201 with id and name."""
    r = client.post("/tags", json={"name": "python"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "python"
    assert "id" in data


def test_create_tag_appears_in_list(client):
    """A newly created tag is returned by GET /tags."""
    client.post("/tags", json={"name": "listed"})
    r = client.get("/tags")
    assert r.status_code == 200
    assert any(t["name"] == "listed" for t in r.json())


def test_create_duplicate_tag_returns_409(client):
    """POST /tags with a name that already exists returns 409."""
    client.post("/tags", json={"name": "dup"})
    r = client.post("/tags", json={"name": "dup"})
    assert r.status_code == 409


def test_create_tag_empty_name_returns_422(client):
    """POST /tags with an empty name is rejected with 422."""
    r = client.post("/tags", json={"name": ""})
    assert r.status_code == 422


def test_delete_tag_returns_204(client):
    """DELETE /tags/{id} removes the tag and returns 204."""
    tag_id = client.post("/tags", json={"name": "removeme"}).json()["id"]
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204
    assert not any(t["id"] == tag_id for t in client.get("/tags").json())


def test_delete_nonexistent_tag_returns_404(client):
    """DELETE /tags/9999 returns 404."""
    r = client.delete("/tags/9999")
    assert r.status_code == 404


# ── Note–tag relations ────────────────────────────────────────────────────────


def test_attach_tag_to_note(client):
    """POST /notes/{id}/tags attaches a tag and returns the updated note."""
    note = client.post("/notes/", json={"title": "Tagged", "content": "hello"}).json()
    tag = client.post("/tags", json={"name": "feature"}).json()
    r = client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    assert r.status_code == 200
    assert any(t["id"] == tag["id"] for t in r.json()["tags"])


def test_attach_tag_to_nonexistent_note_returns_404(client):
    """POST /notes/9999/tags returns 404 when note does not exist."""
    tag = client.post("/tags", json={"name": "orphan"}).json()
    r = client.post("/notes/9999/tags", json={"tag_id": tag["id"]})
    assert r.status_code == 404


def test_attach_nonexistent_tag_to_note_returns_404(client):
    """POST /notes/{id}/tags returns 404 when tag_id does not exist."""
    note = client.post("/notes/", json={"title": "Note", "content": "content"}).json()
    r = client.post(f"/notes/{note['id']}/tags", json={"tag_id": 9999})
    assert r.status_code == 404


def test_attach_same_tag_twice_is_idempotent(client):
    """Attaching the same tag a second time does not create a duplicate entry."""
    note = client.post("/notes/", json={"title": "Note", "content": "content"}).json()
    tag = client.post("/tags", json={"name": "idem"}).json()
    client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    r = client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    assert r.status_code == 200
    assert len([t for t in r.json()["tags"] if t["id"] == tag["id"]]) == 1


def test_detach_tag_from_note(client):
    """DELETE /notes/{id}/tags/{tag_id} removes the tag from the note."""
    note = client.post("/notes/", json={"title": "Tagged", "content": "hello"}).json()
    tag = client.post("/tags", json={"name": "removetag"}).json()
    client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    r = client.delete(f"/notes/{note['id']}/tags/{tag['id']}")
    assert r.status_code == 200
    assert not any(t["id"] == tag["id"] for t in r.json()["tags"])


def test_get_note_includes_tags(client):
    """GET /notes/{id} returns the note with its attached tags."""
    note = client.post("/notes/", json={"title": "Tagged", "content": "hello"}).json()
    tag = client.post("/tags", json={"name": "gettag"}).json()
    client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    data = r.json()
    assert "tags" in data
    assert any(t["name"] == "gettag" for t in data["tags"])


def test_list_notes_includes_tags(client):
    """GET /notes/ includes the tags list for each note."""
    note = client.post("/notes/", json={"title": "Tagged", "content": "hello"}).json()
    tag = client.post("/tags", json={"name": "listtag"}).json()
    client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    r = client.get("/notes/")
    assert r.status_code == 200
    tagged = next(n for n in r.json() if n["id"] == note["id"])
    assert any(t["name"] == "listtag" for t in tagged["tags"])


def test_delete_tag_detaches_it_from_notes(client):
    """Deleting a tag removes it from notes that had it attached."""
    note = client.post("/notes/", json={"title": "Note", "content": "content"}).json()
    tag = client.post("/tags", json={"name": "cascade"}).json()
    client.post(f"/notes/{note['id']}/tags", json={"tag_id": tag["id"]})
    client.delete(f"/tags/{tag['id']}")
    r = client.get(f"/notes/{note['id']}")
    assert not any(t["id"] == tag["id"] for t in r.json()["tags"])


# ── Search filter by tag ──────────────────────────────────────────────────────


def test_search_filter_by_tag_id(client):
    """GET /notes/search/?tag_id returns only notes that have that tag."""
    note1 = client.post("/notes/", json={"title": "Tagged note", "content": "content"}).json()
    note2 = client.post("/notes/", json={"title": "Untagged note", "content": "content"}).json()
    tag = client.post("/tags", json={"name": "searchtag"}).json()
    client.post(f"/notes/{note1['id']}/tags", json={"tag_id": tag["id"]})

    r = client.get("/notes/search/", params={"tag_id": tag["id"]})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    ids = [item["id"] for item in data["items"]]
    assert note1["id"] in ids
    assert note2["id"] not in ids


def test_search_filter_by_tag_and_query(client):
    """tag_id and q filters can be combined."""
    note1 = client.post("/notes/", json={"title": "Alpha", "content": "combo"}).json()
    note2 = client.post("/notes/", json={"title": "Beta", "content": "combo"}).json()
    tag = client.post("/tags", json={"name": "combo"}).json()
    client.post(f"/notes/{note1['id']}/tags", json={"tag_id": tag["id"]})
    client.post(f"/notes/{note2['id']}/tags", json={"tag_id": tag["id"]})

    # Both notes have the tag, but only note1 matches "Alpha"
    r = client.get("/notes/search/", params={"q": "Alpha", "tag_id": tag["id"]})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == note1["id"]
