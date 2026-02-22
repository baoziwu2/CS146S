import json
from typing import Any, Callable

from ..app.services import extract
from ..app.services.extract import extract_action_items


def fake_chat_factory(return_items: list[str]) -> Callable:
    def fake_chat(
        model: str,
        messages: list[dict[str, Any]],
        stream: bool = False,
        format: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        # 返回符合 ActionItemsList schema 的 JSON 格式
        return {
            "message": {
                "content": json.dumps({"items": return_items}),
            },
        }

    return fake_chat


def test_extract_action_items_llm_basic(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "dummy-model")
    fake_chat = fake_chat_factory(["Do A", "Do B"])
    monkeypatch.setattr(extract, "chat", fake_chat)

    text = "Some meeting notes about tasks."
    items = extract.extract_action_items_llm(text)

    assert items == ["Do A", "Do B"]


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_action_items_llm_empty_input(monkeypatch):
    # 空输入直接返回 []
    monkeypatch.setenv("OLLAMA_MODEL", "dummy-model")
    # 即使不打补丁 chat，也不会被调用，因为函数直接返回
    items = extract.extract_action_items_llm("")
    assert items == []


def test_extract_action_items_llm_with_bullets(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "dummy-model")

    text = """
    - [ ] Set up database
    todo: write documentation
    """.strip()

    fake_chat = fake_chat_factory(["Set up database", "write documentation"])
    monkeypatch.setattr(extract, "chat", fake_chat)

    items = extract.extract_action_items_llm(text)
    assert "Set up database" in items
    assert "write documentation" in items
