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


# ── Filter by completion status (Task 4) ──────────────────────────────────────


def test_filter_completed_action_items(client):
    """GET /action-items?completed=true returns only completed items."""
    r1 = client.post("/action-items/", json={"description": "Pending task"})
    r2 = client.post("/action-items/", json={"description": "Done task"})
    client.put(f"/action-items/{r2.json()['id']}/complete")

    r = client.get("/action-items/", params={"completed": "true"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["completed"] is True


def test_filter_incomplete_action_items(client):
    """GET /action-items?completed=false returns only incomplete items."""
    r1 = client.post("/action-items/", json={"description": "Pending task"})
    r2 = client.post("/action-items/", json={"description": "Done task"})
    client.put(f"/action-items/{r2.json()['id']}/complete")

    r = client.get("/action-items/", params={"completed": "false"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["completed"] is False


def test_list_all_action_items_no_filter(client):
    """GET /action-items with no filter returns all items regardless of status."""
    r1 = client.post("/action-items/", json={"description": "Pending"})
    r2 = client.post("/action-items/", json={"description": "Done"})
    client.put(f"/action-items/{r2.json()['id']}/complete")

    r = client.get("/action-items/")
    assert r.status_code == 200
    assert len(r.json()) == 2


# ── Bulk complete (Task 4) ─────────────────────────────────────────────────────


def test_bulk_complete_marks_all_specified_items(client):
    """POST /action-items/bulk-complete marks all given IDs as completed."""
    r1 = client.post("/action-items/", json={"description": "First"})
    r2 = client.post("/action-items/", json={"description": "Second"})
    ids = [r1.json()["id"], r2.json()["id"]]

    r = client.post("/action-items/bulk-complete", json={"ids": ids})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 2
    assert all(item["completed"] is True for item in results)


def test_bulk_complete_nonexistent_id_returns_404(client):
    """POST /action-items/bulk-complete with an unknown ID returns 404."""
    r = client.post("/action-items/bulk-complete", json={"ids": [9999]})
    assert r.status_code == 404


def test_bulk_complete_rolls_back_on_invalid_id(client):
    """All changes are rolled back if any ID in the bulk request is not found."""
    r1 = client.post("/action-items/", json={"description": "Valid item"})
    valid_id = r1.json()["id"]

    # valid_id first so it gets marked before the error is hit on 9999
    r = client.post("/action-items/bulk-complete", json={"ids": [valid_id, 9999]})
    assert r.status_code == 404

    # valid_id must still be incomplete — the whole transaction rolled back
    r = client.get("/action-items/")
    all_items = {i["id"]: i for i in r.json()}
    assert all_items[valid_id]["completed"] is False
