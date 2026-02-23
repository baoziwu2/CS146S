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
    items = r.json()
    assert len(items) >= 1


def test_search_case_insensitive_content(client):
    client.post("/notes/", json={"title": "My Note", "content": "Hello World"})

    # lowercase query should match uppercase content
    r = client.get("/notes/search/", params={"q": "hello"})
    assert r.status_code == 200
    assert len(r.json()) >= 1

    # uppercase query should match lowercase content
    r = client.get("/notes/search/", params={"q": "WORLD"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_search_case_insensitive_title(client):
    client.post("/notes/", json={"title": "FastAPI Guide", "content": "some content"})

    r = client.get("/notes/search/", params={"q": "fastapi"})
    assert r.status_code == 200
    items = r.json()
    assert any(n["title"] == "FastAPI Guide" for n in items)


def test_search_no_results(client):
    client.post("/notes/", json={"title": "Alpha", "content": "Beta"})

    r = client.get("/notes/search/", params={"q": "zzznomatch"})
    assert r.status_code == 200
    assert r.json() == []


def test_search_empty_query_returns_all(client):
    client.post("/notes/", json={"title": "A", "content": "1"})
    client.post("/notes/", json={"title": "B", "content": "2"})

    r = client.get("/notes/search/")
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_extract_creates_action_items(client):
    content = "- TODO: write docs\n- Deploy it!\nJust a note"
    r = client.post("/notes/", json={"title": "Sprint", "content": content})
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 201
    created = r.json()
    descriptions = [a["description"] for a in created]
    assert any("TODO: write docs" in d for d in descriptions)
    assert any("Deploy it!" in d for d in descriptions)
    assert all(a["completed"] is False for a in created)


def test_extract_nonexistent_note_returns_404(client):
    r = client.post("/notes/99999/extract")
    assert r.status_code == 404


def test_extract_no_action_items_returns_empty(client):
    r = client.post("/notes/", json={"title": "Plain", "content": "Just a plain note"})
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 201
    assert r.json() == []


def test_edit_note(client):
    r = client.post("/notes/", json={"title": "Old Title", "content": "Old content"})
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "New Title", "content": "New content"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "New Title"
    assert data["content"] == "New content"


def test_edit_note_partial(client):
    r = client.post("/notes/", json={"title": "Keep", "content": "Original"})
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "Changed"})
    assert r.status_code == 200
    assert r.json()["title"] == "Changed"
    assert r.json()["content"] == "Original"


def test_edit_note_not_found(client):
    r = client.put("/notes/99999", json={"title": "x"})
    assert r.status_code == 404


def test_delete_note(client):
    r = client.post("/notes/", json={"title": "Temp", "content": "Gone"})
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404


def test_create_note_empty_title_rejected(client):
    r = client.post("/notes/", json={"title": "", "content": "some content"})
    assert r.status_code == 422


def test_create_note_empty_content_rejected(client):
    r = client.post("/notes/", json={"title": "Title", "content": ""})
    assert r.status_code == 422


def test_create_note_title_too_long_rejected(client):
    r = client.post("/notes/", json={"title": "x" * 201, "content": "ok"})
    assert r.status_code == 422


def test_edit_note_empty_title_rejected(client):
    r = client.post("/notes/", json={"title": "OK", "content": "ok"})
    note_id = r.json()["id"]
    r = client.put(f"/notes/{note_id}", json={"title": ""})
    assert r.status_code == 422


def test_edit_note_empty_content_rejected(client):
    r = client.post("/notes/", json={"title": "OK", "content": "ok"})
    note_id = r.json()["id"]
    r = client.put(f"/notes/{note_id}", json={"content": ""})
    assert r.status_code == 422


def test_extract_multiline_chinese_via_api(client):
    """多行中文笔记：TODO 行和含 tag 行都被提取，tags 从 description 中剥离。"""
    content = (
        "这里是一些笔记内容。\n"
        "- TODO: 买牛奶 #shopping\n"
        "- 记得回复邮件 #work #urgent\n"
        "这一行没有标签。"
    )
    r = client.post("/notes/", json={"title": "中文笔记", "content": content})
    assert r.status_code == 201
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 201
    descriptions = [a["description"] for a in r.json()]
    # TODO 行 + 含 tag 行，共 2 条
    assert len(descriptions) == 2
    # tags 已从 description 中剥离
    assert any("TODO: 买牛奶" in d for d in descriptions)
    assert any("记得回复邮件" in d for d in descriptions)
    assert not any("#" in d for d in descriptions)
