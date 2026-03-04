# TDD tests for Task 1: new endpoints + input validation
# Written before any implementation.


# ---------------------------------------------------------------------------
# DELETE /notes/{id}
# ---------------------------------------------------------------------------

def test_delete_note(client):
    r = client.post("/notes/", json={"title": "To delete", "content": "bye"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /action-items/{id}
# ---------------------------------------------------------------------------

def test_delete_action_item(client):
    r = client.post("/action-items/", json={"description": "To delete"})
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404


def test_delete_action_item_not_found(client):
    r = client.delete("/action-items/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# GET /action-items/{id}
# ---------------------------------------------------------------------------

def test_get_action_item_by_id(client):
    r = client.post("/action-items/", json={"description": "Find me"})
    assert r.status_code == 201
    created = r.json()

    r = client.get(f"/action-items/{created['id']}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == created["id"]
    assert data["description"] == "Find me"
    assert data["completed"] is False


def test_get_action_item_by_id_not_found(client):
    r = client.get("/action-items/99999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Input validation – Notes
# ---------------------------------------------------------------------------

def test_create_note_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "some content"})
    assert r.status_code == 422


def test_create_note_title_too_long(client):
    r = client.post("/notes/", json={"title": "x" * 201, "content": "some content"})
    assert r.status_code == 422


def test_create_note_empty_content(client):
    r = client.post("/notes/", json={"title": "Valid title", "content": ""})
    assert r.status_code == 422


def test_patch_note_empty_title(client):
    r = client.post("/notes/", json={"title": "Original", "content": "content"})
    note_id = r.json()["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": ""})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Input validation – Action Items
# ---------------------------------------------------------------------------

def test_create_action_item_empty_description(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422


def test_patch_action_item_empty_description(client):
    r = client.post("/action-items/", json={"description": "Original"})
    item_id = r.json()["id"]
    r = client.patch(f"/action-items/{item_id}", json={"description": ""})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Input validation – Pagination params
# ---------------------------------------------------------------------------

def test_list_notes_invalid_limit(client):
    r = client.get("/notes/", params={"limit": 0})
    assert r.status_code == 422


def test_list_notes_negative_skip(client):
    r = client.get("/notes/", params={"skip": -1})
    assert r.status_code == 422


def test_list_action_items_invalid_limit(client):
    r = client.get("/action-items/", params={"limit": 0})
    assert r.status_code == 422


def test_list_action_items_negative_skip(client):
    r = client.get("/action-items/", params={"skip": -1})
    assert r.status_code == 422
