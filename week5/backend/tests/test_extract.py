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


# ── extract_tags ───────────────────────────────────────────────────────────────


def test_extract_tags_finds_hashtags():
    """Hashtag names (without #) are returned."""
    assert extract_tags("Hello #python and #world") == ["python", "world"]


def test_extract_tags_deduplicates():
    """Duplicate hashtags appear only once in the result."""
    result = extract_tags("#python is great #python")
    assert result == ["python"]


def test_extract_tags_empty_when_none_present():
    """Text without any hashtags returns an empty list."""
    assert extract_tags("No hashtags here") == []


def test_extract_tags_handles_mixed_content():
    """Hashtags are extracted even when mixed with other content."""
    result = extract_tags("Use #fastapi with #sqlalchemy for the backend")
    assert "fastapi" in result
    assert "sqlalchemy" in result


# ── extract_tasks ──────────────────────────────────────────────────────────────


def test_extract_tasks_finds_checkbox_items():
    """Unchecked markdown checkboxes are returned as task strings."""
    text = "- [ ] write tests\n- [ ] ship it"
    items = extract_tasks(text)
    assert "write tests" in items
    assert "ship it" in items


def test_extract_tasks_ignores_checked_boxes():
    """Already-checked items (- [x]) are not returned."""
    text = "- [x] already done\n- [ ] still to do"
    items = extract_tasks(text)
    assert "already done" not in items
    assert "still to do" in items


def test_extract_tasks_empty_when_none_present():
    """Text without any checkboxes returns an empty list."""
    assert extract_tasks("No tasks here") == []
