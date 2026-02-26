import re


def extract_tags(text: str) -> list[str]:
    """Return unique lowercase tag names found as #hashtags in text."""
    seen: dict[str, None] = {}
    for m in re.finditer(r"#(\w+)", text):
        seen[m.group(1).lower()] = None
    return list(seen)


def extract_tasks(text: str) -> list[str]:
    """Return task descriptions from Markdown unchecked checkboxes (- [ ] ...)."""
    return [m.group(1).strip() for m in re.finditer(r"-\s*\[\s*\]\s*(.+)", text)]


def extract_action_items(text: str) -> list[str]:
    """Legacy: extract lines ending with ! or starting with todo:."""
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]
