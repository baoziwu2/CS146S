def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_complete_nonexistent_item_returns_404(client):
    r = client.put("/action-items/99999/complete")
    assert r.status_code == 404


def test_complete_is_idempotent(client):
    r = client.post("/action-items/", json={"description": "Do twice"})
    item_id = r.json()["id"]

    client.put(f"/action-items/{item_id}/complete")
    r = client.put(f"/action-items/{item_id}/complete")
    assert r.status_code == 200
    assert r.json()["completed"] is True


def test_completed_item_reflected_in_list(client):
    r = client.post("/action-items/", json={"description": "List check"})
    item_id = r.json()["id"]

    client.put(f"/action-items/{item_id}/complete")

    items = client.get("/action-items/").json()
    match = next(i for i in items if i["id"] == item_id)
    assert match["completed"] is True


def test_create_action_item_empty_description_rejected(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422


def test_create_action_item_missing_description_rejected(client):
    r = client.post("/action-items/", json={})
    assert r.status_code == 422


def test_validation_error_has_detail(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422
    body = r.json()
    assert "detail" in body
