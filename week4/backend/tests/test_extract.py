from backend.app.services.extract import extract_action_items, extract_tags


def test_extract_action_items():
    text = "This is a note\n" "- TODO: write tests\n" "- Ship it!\n" "Not actionable"
    items = extract_action_items(text)
    texts = [i["text"] for i in items]
    assert "TODO: write tests" in texts
    assert "Ship it!" in texts
    assert not any("Not actionable" in t for t in texts)


def test_extract_tags_only_line_is_action_item():
    """有 #tag 的行即使没有 TODO:/! 也应被识别为 action item。"""
    items = extract_action_items("- 记得回复邮件 #work #urgent")
    assert len(items) == 1
    assert items[0]["text"] == "记得回复邮件"
    assert items[0]["tags"] == ["work", "urgent"]


def test_extract_tags_stripped_from_text():
    """text 字段不应包含 #tag，tags 字段单独列出。"""
    items = extract_action_items("- TODO: 买牛奶 #shopping")
    assert len(items) == 1
    assert items[0]["text"] == "TODO: 买牛奶"
    assert items[0]["tags"] == ["shopping"]


def test_extract_no_tags_line_without_marker_excluded():
    """既没有 TODO:/! 也没有 #tag 的行不应被提取。"""
    items = extract_action_items("这一行没有标签。")
    assert items == []


def test_extract_tags_single():
    tags = extract_tags("Hello #world")
    assert tags == ["world"]


def test_extract_tags_multiple():
    tags = extract_tags("Tagged as #alpha and #beta today")
    assert "alpha" in tags
    assert "beta" in tags


def test_extract_tags_none():
    assert extract_tags("no tags here") == []


def test_extract_tags_mixed_with_action_items():
    text = "- TODO: deploy #infra and notify #team"
    items = extract_action_items(text)
    tags = extract_tags(text)
    assert len(items) == 1
    assert items[0]["text"] == "TODO: deploy and notify"
    assert set(items[0]["tags"]) == {"infra", "team"}
    assert "infra" in tags
    assert "team" in tags


def test_multiline_chinese_content_action_items():
    """用户实际场景：TODO 行 和 含 tag 行都应被提取，纯文本行排除。"""
    text = (
        "这里是一些笔记内容。\n"
        "- TODO: 买牛奶 #shopping\n"
        "- 记得回复邮件 #work #urgent\n"
        "这一行没有标签。"
    )
    items = extract_action_items(text)
    texts = [i["text"] for i in items]
    assert len(items) == 2
    assert "TODO: 买牛奶" in texts
    assert "记得回复邮件" in texts
    # 验证 tags 结构
    shopping_item = next(i for i in items if "TODO" in i["text"])
    assert shopping_item["tags"] == ["shopping"]
    email_item = next(i for i in items if "回复" in i["text"])
    assert set(email_item["tags"]) == {"work", "urgent"}


def test_multiline_chinese_content_tags():
    """extract_tags 跨行收集所有 #tag。"""
    text = (
        "这里是一些笔记内容。\n"
        "- TODO: 买牛奶 #shopping\n"
        "- 记得回复邮件 #work #urgent\n"
        "这一行没有标签。"
    )
    tags = extract_tags(text)
    assert "shopping" in tags
    assert "work" in tags
    assert "urgent" in tags
    assert len(tags) == 3
