def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["ok"] is True
    data = body["data"]
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()["data"]
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 1


def test_update_note_returns_updated_data(client):
    r = client.post("/notes/", json={"title": "Original", "content": "Old content"})
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "Updated", "content": "New content"})
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["title"] == "Updated"
    assert data["content"] == "New content"
    assert data["id"] == note_id


def test_update_nonexistent_note_returns_404(client):
    r = client.put("/notes/9999", json={"title": "X", "content": "Y"})
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "NOT_FOUND"


def test_delete_note_returns_204(client):
    r = client.post("/notes/", json={"title": "To delete", "content": "Bye"})
    assert r.status_code == 201
    note_id = r.json()["data"]["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_nonexistent_note_returns_404(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "NOT_FOUND"


# ── Search: pagination & sorting (Task 2) ─────────────────────────────────────


def test_search_returns_paginated_envelope(client):
    """Search endpoint returns {items, total, page, page_size} inside data."""
    client.post("/notes/", json={"title": "Envelope note", "content": "envelope check"})
    r = client.get("/notes/search/", params={"q": "envelope check"})
    assert r.status_code == 200
    assert r.json()["ok"] is True
    data = r.json()["data"]
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_search_pagination_limits_results(client):
    """page_size=2 with 3 matching notes returns only 2 items."""
    for i in range(3):
        client.post("/notes/", json={"title": f"Page note {i}", "content": "paginate me"})
    r = client.get("/notes/search/", params={"q": "paginate me", "page": 1, "page_size": 2})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 2
    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2


def test_search_page_2_returns_remaining(client):
    """Page 2 returns the item(s) not returned on page 1."""
    for i in range(3):
        client.post("/notes/", json={"title": f"Page2 note {i}", "content": "paginate2"})
    r = client.get("/notes/search/", params={"q": "paginate2", "page": 2, "page_size": 2})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["items"]) == 1
    assert data["total"] == 3


def test_search_case_insensitive(client):
    """Query matching is case-insensitive on both title and content."""
    client.post("/notes/", json={"title": "CaseSensitive Title", "content": "mixed content"})
    r = client.get("/notes/search/", params={"q": "casesensitive"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 1
    assert any("CaseSensitive" in item["title"] for item in data["items"])

    # Also match against content, case-insensitively
    r2 = client.get("/notes/search/", params={"q": "MIXED CONTENT"})
    assert r2.status_code == 200
    data2 = r2.json()["data"]
    assert data2["total"] >= 1


def test_search_sort_title_asc(client):
    """sort=title_asc returns notes in ascending alphabetical order by title."""
    client.post("/notes/", json={"title": "Zebra note", "content": "sort test"})
    client.post("/notes/", json={"title": "Apple note", "content": "sort test"})
    client.post("/notes/", json={"title": "Mango note", "content": "sort test"})
    r = client.get("/notes/search/", params={"q": "sort test", "sort": "title_asc"})
    assert r.status_code == 200
    titles = [item["title"] for item in r.json()["data"]["items"]]
    assert titles == sorted(titles)


def test_search_sort_created_desc(client):
    """sort=created_desc returns newest notes first (highest id first)."""
    client.post("/notes/", json={"title": "First created", "content": "order test"})
    client.post("/notes/", json={"title": "Second created", "content": "order test"})
    client.post("/notes/", json={"title": "Third created", "content": "order test"})
    r = client.get("/notes/search/", params={"q": "order test", "sort": "created_desc"})
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    ids = [item["id"] for item in items]
    assert ids == sorted(ids, reverse=True)


def test_search_total_reflects_filter_not_page(client):
    """total in envelope counts all matching results, not just the current page."""
    for i in range(5):
        client.post("/notes/", json={"title": f"Total test {i}", "content": "totalcheck"})
    r = client.get("/notes/search/", params={"q": "totalcheck", "page": 1, "page_size": 2})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_search_empty_page_beyond_total(client):
    """Requesting a page number beyond available results returns empty items list."""
    client.post("/notes/", json={"title": "Only one", "content": "lonely note"})
    r = client.get("/notes/search/", params={"q": "lonely note", "page": 99, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["items"] == []
    assert data["total"] == 1


# ── Validation: payload min/max lengths (Task 3) ──────────────────────────────


def test_create_note_with_empty_title_returns_422(client):
    """POST /notes/ with an empty title is rejected with 422 and VALIDATION_ERROR code."""
    r = client.post("/notes/", json={"title": "", "content": "some content"})
    assert r.status_code == 422
    body = r.json()
    assert body["ok"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_create_note_with_title_too_long_returns_422(client):
    """POST /notes/ with a title exceeding 200 characters is rejected with 422."""
    r = client.post("/notes/", json={"title": "x" * 201, "content": "some content"})
    assert r.status_code == 422
    assert r.json()["ok"] is False


def test_create_note_with_empty_content_returns_422(client):
    """POST /notes/ with empty content is rejected with 422."""
    r = client.post("/notes/", json={"title": "Valid title", "content": ""})
    assert r.status_code == 422
    assert r.json()["ok"] is False


def test_update_note_with_empty_title_returns_422(client):
    """PUT /notes/{id} with an empty title is rejected with 422."""
    r = client.post("/notes/", json={"title": "Original", "content": "content"})
    note_id = r.json()["data"]["id"]
    r = client.put(f"/notes/{note_id}", json={"title": "", "content": "content"})
    assert r.status_code == 422
    assert r.json()["ok"] is False


def test_update_note_with_title_too_long_returns_422(client):
    """PUT /notes/{id} with a title exceeding 200 characters is rejected with 422."""
    r = client.post("/notes/", json={"title": "Original", "content": "content"})
    note_id = r.json()["data"]["id"]
    r = client.put(f"/notes/{note_id}", json={"title": "x" * 201, "content": "content"})
    assert r.status_code == 422
    assert r.json()["ok"] is False


def test_update_note_with_empty_content_returns_422(client):
    """PUT /notes/{id} with empty content is rejected with 422."""
    r = client.post("/notes/", json={"title": "Original", "content": "content"})
    note_id = r.json()["data"]["id"]
    r = client.put(f"/notes/{note_id}", json={"title": "Original", "content": ""})
    assert r.status_code == 422
    assert r.json()["ok"] is False
