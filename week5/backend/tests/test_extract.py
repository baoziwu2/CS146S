from backend.app.services.extract import extract_action_items, extract_tags, extract_tasks


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


# ── New parsing functions (Task 6) ────────────────────────────────────────────


def test_extract_tags_from_text():
    tags = extract_tags("Working on #python and #fastapi project")
    assert "python" in tags
    assert "fastapi" in tags


def test_extract_tags_returns_empty_for_no_hashtags():
    assert extract_tags("plain text no hashtags") == []


def test_extract_tags_deduplicates():
    tags = extract_tags("#python is great, use #python always")
    assert tags.count("python") == 1


def test_extract_tasks_from_text():
    text = "- [ ] write unit tests\n- [ ] deploy to prod\n- [x] already done"
    tasks = extract_tasks(text)
    assert "write unit tests" in tasks
    assert "deploy to prod" in tasks
    assert "already done" not in tasks  # [x] is not a pending checkbox


def test_extract_tasks_returns_empty_for_no_checkboxes():
    assert extract_tasks("plain text no tasks") == []


# ── POST /notes/{id}/extract endpoint (Task 6) ────────────────────────────────


def test_extract_endpoint_returns_structured_result(client):
    note_id = client.post(
        "/notes/", json={"title": "T", "content": "#python - [ ] write tests"}
    ).json()["id"]
    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    data = r.json()
    assert "tags" in data
    assert "action_items" in data
    assert "python" in data["tags"]
    assert "write tests" in data["action_items"]


def test_extract_endpoint_apply_false_does_not_persist(client):
    note_id = client.post(
        "/notes/", json={"title": "T", "content": "#newtag - [ ] new task"}
    ).json()["id"]
    r = client.post(f"/notes/{note_id}/extract", params={"apply": "false"})
    assert r.status_code == 200
    assert not any(t["name"] == "newtag" for t in client.get("/tags/").json())
    assert not any(i["description"] == "new task" for i in client.get("/action-items/").json())


def test_extract_endpoint_apply_true_persists_tags_and_actions(client):
    note_id = client.post(
        "/notes/", json={"title": "T", "content": "#mytag - [ ] my task"}
    ).json()["id"]
    r = client.post(f"/notes/{note_id}/extract", params={"apply": "true"})
    assert r.status_code == 200
    note = client.get(f"/notes/{note_id}").json()
    assert any(t["name"] == "mytag" for t in note["tags"])
    assert any(i["description"] == "my task" for i in client.get("/action-items/").json())


def test_extract_endpoint_apply_true_idempotent_tag(client):
    """Applying extraction twice does not duplicate the tag on the note."""
    note_id = client.post(
        "/notes/", json={"title": "T", "content": "#idempotent"}
    ).json()["id"]
    client.post(f"/notes/{note_id}/extract", params={"apply": "true"})
    client.post(f"/notes/{note_id}/extract", params={"apply": "true"})
    note = client.get(f"/notes/{note_id}").json()
    assert sum(1 for t in note["tags"] if t["name"] == "idempotent") == 1


def test_extract_nonexistent_note_returns_404(client):
    r = client.post("/notes/9999/extract")
    assert r.status_code == 404
