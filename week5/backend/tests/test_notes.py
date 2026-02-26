def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1


def test_update_note_returns_updated_data(client):
    r = client.post("/notes/", json={"title": "Original", "content": "Old content"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "Updated", "content": "New content"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "Updated"
    assert data["content"] == "New content"
    assert data["id"] == note_id


def test_update_nonexistent_note_returns_404(client):
    r = client.put("/notes/9999", json={"title": "X", "content": "Y"})
    assert r.status_code == 404


def test_delete_note_returns_204(client):
    r = client.post("/notes/", json={"title": "To delete", "content": "Bye"})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_nonexistent_note_returns_404(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404


# ── Search: pagination & sorting (Task 2) ─────────────────────────────────────


def test_search_returns_paginated_envelope(client):
    """Search endpoint returns {items, total, page, page_size} envelope."""
    client.post("/notes/", json={"title": "Envelope note", "content": "envelope check"})
    r = client.get("/notes/search/", params={"q": "envelope check"})
    assert r.status_code == 200
    data = r.json()
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
    data = r.json()
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
    data = r.json()
    assert len(data["items"]) == 1
    assert data["total"] == 3


def test_search_case_insensitive(client):
    """Query matching is case-insensitive on both title and content."""
    client.post("/notes/", json={"title": "CaseSensitive Title", "content": "mixed content"})
    r = client.get("/notes/search/", params={"q": "casesensitive"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert any("CaseSensitive" in item["title"] for item in data["items"])

    # Also match against content, case-insensitively
    r2 = client.get("/notes/search/", params={"q": "MIXED CONTENT"})
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["total"] >= 1


def test_search_sort_title_asc(client):
    """sort=title_asc returns notes in ascending alphabetical order by title."""
    client.post("/notes/", json={"title": "Zebra note", "content": "sort test"})
    client.post("/notes/", json={"title": "Apple note", "content": "sort test"})
    client.post("/notes/", json={"title": "Mango note", "content": "sort test"})
    r = client.get("/notes/search/", params={"q": "sort test", "sort": "title_asc"})
    assert r.status_code == 200
    titles = [item["title"] for item in r.json()["items"]]
    assert titles == sorted(titles)


def test_search_sort_created_desc(client):
    """sort=created_desc returns newest notes first (highest id first)."""
    client.post("/notes/", json={"title": "First created", "content": "order test"})
    client.post("/notes/", json={"title": "Second created", "content": "order test"})
    client.post("/notes/", json={"title": "Third created", "content": "order test"})
    r = client.get("/notes/search/", params={"q": "order test", "sort": "created_desc"})
    assert r.status_code == 200
    items = r.json()["items"]
    ids = [item["id"] for item in items]
    assert ids == sorted(ids, reverse=True)


def test_search_total_reflects_filter_not_page(client):
    """total in envelope counts all matching results, not just the current page."""
    for i in range(5):
        client.post("/notes/", json={"title": f"Total test {i}", "content": "totalcheck"})
    r = client.get("/notes/search/", params={"q": "totalcheck", "page": 1, "page_size": 2})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2


def test_search_empty_page_beyond_total(client):
    """Requesting a page number beyond available results returns empty items list."""
    client.post("/notes/", json={"title": "Only one", "content": "lonely note"})
    r = client.get("/notes/search/", params={"q": "lonely note", "page": 99, "page_size": 10})
    assert r.status_code == 200
    data = r.json()
    assert data["items"] == []
    assert data["total"] == 1


# ── Validation: payload min/max lengths (Task 3) ──────────────────────────────


def test_create_note_with_empty_title_returns_422(client):
    """POST /notes/ with an empty title is rejected with 422."""
    r = client.post("/notes/", json={"title": "", "content": "some content"})
    assert r.status_code == 422


def test_create_note_with_title_too_long_returns_422(client):
    """POST /notes/ with a title exceeding 200 characters is rejected with 422."""
    r = client.post("/notes/", json={"title": "x" * 201, "content": "some content"})
    assert r.status_code == 422


def test_create_note_with_empty_content_returns_422(client):
    """POST /notes/ with empty content is rejected with 422."""
    r = client.post("/notes/", json={"title": "Valid title", "content": ""})
    assert r.status_code == 422


def test_update_note_with_empty_title_returns_422(client):
    """PUT /notes/{id} with an empty title is rejected with 422."""
    r = client.post("/notes/", json={"title": "Original", "content": "content"})
    note_id = r.json()["id"]
    r = client.put(f"/notes/{note_id}", json={"title": "", "content": "content"})
    assert r.status_code == 422


def test_update_note_with_title_too_long_returns_422(client):
    """PUT /notes/{id} with a title exceeding 200 characters is rejected with 422."""
    r = client.post("/notes/", json={"title": "Original", "content": "content"})
    note_id = r.json()["id"]
    r = client.put(f"/notes/{note_id}", json={"title": "x" * 201, "content": "content"})
    assert r.status_code == 422


def test_update_note_with_empty_content_returns_422(client):
    """PUT /notes/{id} with empty content is rejected with 422."""
    r = client.post("/notes/", json={"title": "Original", "content": "content"})
    note_id = r.json()["id"]
    r = client.put(f"/notes/{note_id}", json={"title": "Original", "content": ""})
    assert r.status_code == 422


# ── POST /notes/{id}/extract (Task 6) ─────────────────────────────────────────


def test_extract_endpoint_returns_structure(client):
    """POST /notes/{id}/extract returns {tags, action_items} without persisting."""
    note = client.post(
        "/notes/", json={"title": "#python note", "content": "- [ ] write docs"}
    ).json()
    r = client.post(f"/notes/{note['id']}/extract")
    assert r.status_code == 200
    data = r.json()
    assert "tags" in data
    assert "action_items" in data
    assert "python" in data["tags"]
    assert "write docs" in data["action_items"]


def test_extract_endpoint_404_for_missing_note(client):
    """POST /notes/9999/extract returns 404."""
    r = client.post("/notes/9999/extract")
    assert r.status_code == 404


def test_extract_without_apply_does_not_persist(client):
    """Without apply=true, the endpoint returns 200 but creates no action items or tags."""
    note = client.post("/notes/", json={"title": "#temp", "content": "- [ ] do nothing"}).json()
    r = client.post(f"/notes/{note['id']}/extract")
    assert r.status_code == 200
    assert client.get("/action-items/").json() == []
    assert client.get(f"/notes/{note['id']}").json()["tags"] == []


def test_extract_apply_persists_tags(client):
    """apply=true creates missing tags and attaches them to the note."""
    note = client.post("/notes/", json={"title": "#fastapi tips", "content": "content"}).json()
    r = client.post(f"/notes/{note['id']}/extract", params={"apply": "true"})
    assert r.status_code == 200
    tag_names = [t["name"] for t in client.get(f"/notes/{note['id']}").json()["tags"]]
    assert "fastapi" in tag_names


def test_extract_apply_persists_action_items(client):
    """apply=true creates an ActionItem for each unchecked checkbox."""
    note = client.post(
        "/notes/", json={"title": "Tasks", "content": "- [ ] buy milk\n- [ ] code review"}
    ).json()
    r = client.post(f"/notes/{note['id']}/extract", params={"apply": "true"})
    assert r.status_code == 200
    descriptions = [i["description"] for i in client.get("/action-items/").json()]
    assert "buy milk" in descriptions
    assert "code review" in descriptions


def test_extract_apply_reuses_existing_tag(client):
    """apply=true reuses an existing tag rather than creating a duplicate."""
    client.post("/tags", json={"name": "existing"})
    note = client.post("/notes/", json={"title": "#existing note", "content": "c"}).json()
    r = client.post(f"/notes/{note['id']}/extract", params={"apply": "true"})
    assert r.status_code == 200
    # Tag is now attached to the note
    note_tags = [t["name"] for t in client.get(f"/notes/{note['id']}").json()["tags"]]
    assert "existing" in note_tags
    # Still only one tag with that name in the system
    all_tags = client.get("/tags").json()
    assert sum(1 for t in all_tags if t["name"] == "existing") == 1
