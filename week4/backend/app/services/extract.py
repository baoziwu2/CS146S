import re


def extract_action_items(text: str) -> list[dict]:
    result = []
    for line in text.splitlines():
        stripped = line.strip("- ").strip()
        if not stripped:
            continue
        tags = re.findall(r"#(\w+)", stripped)
        clean_text = re.sub(r"\s+", " ", re.sub(r"#\w+", "", stripped)).strip()
        if tags or clean_text.endswith("!") or clean_text.lower().startswith("todo:"):
            result.append({"text": clean_text, "tags": tags})
    return result


def extract_tags(text: str) -> list[str]:
    return re.findall(r"#(\w+)", text)
