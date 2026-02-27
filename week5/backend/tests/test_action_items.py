def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()["data"]
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()["data"]
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) == 1


# ── Filter by completion status (Task 4) ──────────────────────────────────────


def test_filter_completed_action_items(client):
    """GET /action-items?completed=true returns only completed items."""
    client.post("/action-items/", json={"description": "Pending task"})
    r2 = client.post("/action-items/", json={"description": "Done task"})
    client.put(f"/action-items/{r2.json()['data']['id']}/complete")

    r = client.get("/action-items/", params={"completed": "true"})
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["completed"] is True


def test_filter_incomplete_action_items(client):
    """GET /action-items?completed=false returns only incomplete items."""
    client.post("/action-items/", json={"description": "Pending task"})
    r2 = client.post("/action-items/", json={"description": "Done task"})
    client.put(f"/action-items/{r2.json()['data']['id']}/complete")

    r = client.get("/action-items/", params={"completed": "false"})
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["completed"] is False


def test_list_all_action_items_no_filter(client):
    """GET /action-items with no filter returns all items regardless of status."""
    client.post("/action-items/", json={"description": "Pending"})
    r2 = client.post("/action-items/", json={"description": "Done"})
    client.put(f"/action-items/{r2.json()['data']['id']}/complete")

    r = client.get("/action-items/")
    assert r.status_code == 200
    assert len(r.json()["data"]["items"]) == 2


# ── Bulk complete (Task 4) ─────────────────────────────────────────────────────


def test_bulk_complete_marks_all_specified_items(client):
    """POST /action-items/bulk-complete marks all given IDs as completed."""
    r1 = client.post("/action-items/", json={"description": "First"})
    r2 = client.post("/action-items/", json={"description": "Second"})
    ids = [r1.json()["data"]["id"], r2.json()["data"]["id"]]

    r = client.post("/action-items/bulk-complete", json={"ids": ids})
    assert r.status_code == 200
    results = r.json()["data"]
    assert len(results) == 2
    assert all(item["completed"] is True for item in results)


def test_bulk_complete_nonexistent_id_returns_404(client):
    """POST /action-items/bulk-complete with an unknown ID returns 404."""
    r = client.post("/action-items/bulk-complete", json={"ids": [9999]})
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "NOT_FOUND"


def test_bulk_complete_rolls_back_on_invalid_id(client):
    """All changes are rolled back if any ID in the bulk request is not found."""
    r1 = client.post("/action-items/", json={"description": "Valid item"})
    valid_id = r1.json()["data"]["id"]

    # valid_id first so it gets marked before the error is hit on 9999
    r = client.post("/action-items/bulk-complete", json={"ids": [valid_id, 9999]})
    assert r.status_code == 404

    # valid_id must still be incomplete — the whole transaction rolled back
    r = client.get("/action-items/")
    all_items = {i["id"]: i for i in r.json()["data"]["items"]}
    assert all_items[valid_id]["completed"] is False


# ── List endpoint pagination (Task 8) ─────────────────────────────────────────


def test_list_action_items_returns_paginated_envelope(client):
    """GET /action-items/ returns {items, total, page, page_size} inside data."""
    client.post("/action-items/", json={"description": "Task"})
    r = client.get("/action-items/")
    assert r.status_code == 200
    assert r.json()["ok"] is True
    data = r.json()["data"]
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_list_action_items_pagination_limits_results(client):
    """page_size=2 with 3 items returns only 2 items with correct total."""
    for i in range(3):
        client.post("/action-items/", json={"description": f"Item {i}"})
    r = client.get("/action-items/", params={"page": 1, "page_size": 2})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_list_action_items_page_2_returns_remaining(client):
    """Page 2 returns the remaining items."""
    for i in range(3):
        client.post("/action-items/", json={"description": f"Item {i}"})
    r = client.get("/action-items/", params={"page": 2, "page_size": 2})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 1
    assert data["total"] == 3


def test_list_action_items_empty_page_beyond_total(client):
    """Requesting a page beyond the last returns empty items and correct total."""
    client.post("/action-items/", json={"description": "Only item"})
    r = client.get("/action-items/", params={"page": 99, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["items"] == []
    assert data["total"] == 1


def test_list_action_items_filter_with_pagination(client):
    """completed filter combined with pagination returns correct subset and total."""
    client.post("/action-items/", json={"description": "Pending 1"})
    client.post("/action-items/", json={"description": "Pending 2"})
    r2 = client.post("/action-items/", json={"description": "Done"})
    client.put(f"/action-items/{r2.json()['data']['id']}/complete")

    r = client.get("/action-items/", params={"completed": "false", "page": 1, "page_size": 1})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 1


# ── Additional 404 / edge-case coverage (Task 10) ─────────────────────────────


def test_complete_nonexistent_action_item_returns_404(client):
    """PUT /action-items/9999/complete returns 404 with NOT_FOUND error code."""
    r = client.put("/action-items/9999/complete")
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "NOT_FOUND"


def test_create_action_item_with_empty_description_returns_422(client):
    """POST /action-items/ with an empty description string is rejected with 422."""
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_bulk_complete_empty_list_returns_empty_array(client):
    """POST /action-items/bulk-complete with an empty ids list returns an empty list."""
    r = client.post("/action-items/bulk-complete", json={"ids": []})
    assert r.status_code == 200
    assert r.json()["data"] == []


def test_bulk_complete_already_completed_item_is_idempotent(client):
    """Completing an already-completed item via bulk-complete succeeds and stays completed."""
    r = client.post("/action-items/", json={"description": "Will be done twice"})
    item_id = r.json()["data"]["id"]
    client.put(f"/action-items/{item_id}/complete")

    r = client.post("/action-items/bulk-complete", json={"ids": [item_id]})
    assert r.status_code == 200
    result = r.json()["data"]
    assert len(result) == 1
    assert result[0]["completed"] is True
