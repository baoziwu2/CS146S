import re


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> list[str]:
    """Return unique hashtag names found in text (e.g. '#python' → 'python')."""
    found = re.findall(r"#(\w+)", text)
    seen: set[str] = set()
    result: list[str] = []
    for name in found:
        if name not in seen:
            seen.add(name)
            result.append(name)
    return result


def extract_tasks(text: str) -> list[str]:
    """Return the text of unchecked markdown checkbox items ('- [ ] task')."""
    return re.findall(r"^- \[ \] (.+)$", text, re.MULTILINE)
