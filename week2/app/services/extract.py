from __future__ import annotations

import os
import re
from typing import List

from dotenv import load_dotenv
from ollama import chat
from pydantic import BaseModel

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


class ActionItemsList(BaseModel):
    """Pydantic model for structured action items extraction."""

    items: List[str]


def extract_action_items_llm(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []

    model = os.getenv("OLLAMA_MODEL")
    if not model:
        raise ValueError("OLLAMA_MODEL environment variable is not set")

    schema = ActionItemsList.model_json_schema()

    response = chat(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that extracts action items from text. Return as JSON.",
            },
            {
                "role": "user",
                "content": f"Extract action items from the following text and return as JSON:\n\n{text}",
            },
        ],
        stream=False,
        format=schema,
        options={"temperature": 0},  # 设置 temperature 为 0 以获得更确定性的输出
    )

    content = response["message"]["content"]
    action_items = ActionItemsList.model_validate_json(content)
    return action_items.items


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
