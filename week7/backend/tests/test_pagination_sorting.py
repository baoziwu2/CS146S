# TDD tests for Task 4: pagination and sorting coverage
# These verify behavioral correctness of skip/limit/sort/filter params.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_notes(client, n: int) -> list[dict]:
    return [
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Content {i}"}).json()
        for i in range(n)
    ]


def _make_items(client, n: int) -> list[dict]:
    return [
        client.post("/action-items/", json={"description": f"Item {i}"}).json()
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Notes – pagination
# ---------------------------------------------------------------------------

def test_notes_limit_truncates(client):
    _make_notes(client, 5)
    r = client.get("/notes/", params={"limit": 3, "sort": "id"})
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_notes_skip_offsets(client):
    notes = _make_notes(client, 5)
    all_ids = sorted(n["id"] for n in notes)

    r = client.get("/notes/", params={"skip": 2, "limit": 10, "sort": "id"})
    assert r.status_code == 200
    returned_ids = [n["id"] for n in r.json()]
    assert returned_ids == all_ids[2:]


def test_notes_skip_beyond_total_returns_empty(client):
    _make_notes(client, 3)
    r = client.get("/notes/", params={"skip": 100, "limit": 10})
    assert r.status_code == 200
    assert r.json() == []


def test_notes_limit_one(client):
    _make_notes(client, 3)
    r = client.get("/notes/", params={"limit": 1})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_notes_skip_and_limit_combined(client):
    _make_notes(client, 5)
    r_all = client.get("/notes/", params={"limit": 200, "sort": "id"})
    all_ids = [n["id"] for n in r_all.json()]

    r = client.get("/notes/", params={"skip": 1, "limit": 2, "sort": "id"})
    assert [n["id"] for n in r.json()] == all_ids[1:3]


# ---------------------------------------------------------------------------
# Notes – sorting
# ---------------------------------------------------------------------------

def test_notes_sort_by_id_ascending(client):
    _make_notes(client, 4)
    r = client.get("/notes/", params={"sort": "id"})
    ids = [n["id"] for n in r.json()]
    assert ids == sorted(ids)


def test_notes_sort_by_id_descending(client):
    _make_notes(client, 4)
    r = client.get("/notes/", params={"sort": "-id"})
    ids = [n["id"] for n in r.json()]
    assert ids == sorted(ids, reverse=True)


def test_notes_default_sort_is_created_at_desc(client):
    _make_notes(client, 4)
    r_default = client.get("/notes/")
    r_explicit = client.get("/notes/", params={"sort": "-created_at"})
    assert [n["id"] for n in r_default.json()] == [n["id"] for n in r_explicit.json()]


def test_notes_invalid_sort_field_falls_back(client):
    _make_notes(client, 3)
    # Should not error — falls back to -created_at
    r = client.get("/notes/", params={"sort": "nonexistent_field"})
    assert r.status_code == 200
    assert len(r.json()) == 3


# ---------------------------------------------------------------------------
# Notes – search filter + pagination
# ---------------------------------------------------------------------------

def test_notes_search_filter(client):
    client.post("/notes/", json={"title": "Alpha note", "content": "hello"})
    client.post("/notes/", json={"title": "Beta note", "content": "world"})
    client.post("/notes/", json={"title": "Gamma note", "content": "hello world"})

    r = client.get("/notes/", params={"q": "hello"})
    assert r.status_code == 200
    titles = [n["title"] for n in r.json()]
    assert "Alpha note" in titles
    assert "Gamma note" in titles
    assert "Beta note" not in titles


def test_notes_search_with_pagination(client):
    for i in range(5):
        client.post("/notes/", json={"title": f"Match {i}", "content": "searchable"})
    client.post("/notes/", json={"title": "No match", "content": "irrelevant"})

    r = client.get("/notes/", params={"q": "searchable", "limit": 3, "sort": "id"})
    assert r.status_code == 200
    assert len(r.json()) == 3
    for n in r.json():
        assert "Match" in n["title"]


# ---------------------------------------------------------------------------
# Action Items – pagination
# ---------------------------------------------------------------------------

def test_action_items_limit_truncates(client):
    _make_items(client, 5)
    r = client.get("/action-items/", params={"limit": 2, "sort": "id"})
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_action_items_skip_offsets(client):
    items = _make_items(client, 5)
    all_ids = sorted(i["id"] for i in items)

    r = client.get("/action-items/", params={"skip": 3, "limit": 10, "sort": "id"})
    assert [i["id"] for i in r.json()] == all_ids[3:]


def test_action_items_skip_beyond_total_returns_empty(client):
    _make_items(client, 2)
    r = client.get("/action-items/", params={"skip": 50})
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# Action Items – sorting
# ---------------------------------------------------------------------------

def test_action_items_sort_ascending(client):
    _make_items(client, 4)
    r = client.get("/action-items/", params={"sort": "id"})
    ids = [i["id"] for i in r.json()]
    assert ids == sorted(ids)


def test_action_items_sort_descending(client):
    _make_items(client, 4)
    r = client.get("/action-items/", params={"sort": "-id"})
    ids = [i["id"] for i in r.json()]
    assert ids == sorted(ids, reverse=True)


def test_action_items_invalid_sort_falls_back(client):
    _make_items(client, 3)
    r = client.get("/action-items/", params={"sort": "bogus"})
    assert r.status_code == 200
    assert len(r.json()) == 3


# ---------------------------------------------------------------------------
# Action Items – completed filter + pagination
# ---------------------------------------------------------------------------

def test_action_items_filter_completed(client):
    items = _make_items(client, 4)
    client.put(f"/action-items/{items[0]['id']}/complete")
    client.put(f"/action-items/{items[1]['id']}/complete")

    r = client.get("/action-items/", params={"completed": "true"})
    assert r.status_code == 200
    assert all(i["completed"] for i in r.json())
    assert len(r.json()) == 2


def test_action_items_filter_incomplete(client):
    items = _make_items(client, 4)
    client.put(f"/action-items/{items[0]['id']}/complete")

    r = client.get("/action-items/", params={"completed": "false"})
    assert r.status_code == 200
    assert all(not i["completed"] for i in r.json())
    assert len(r.json()) == 3


def test_action_items_filter_with_pagination(client):
    items = _make_items(client, 6)
    for item in items[:4]:
        client.put(f"/action-items/{item['id']}/complete")

    r = client.get("/action-items/", params={"completed": "true", "limit": 2, "sort": "id"})
    assert r.status_code == 200
    assert len(r.json()) == 2
    assert all(i["completed"] for i in r.json())
