_NEW_PREFIXES = ("fixme:", "note:", "follow up:")
_IMPERATIVE_VERBS = ("need to ", "should ", "must ", "please ")


def extract_action_items(text: str) -> list[str]:
    results: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        normalized = line.lower()

        # Checkbox syntax: - [ ] or * [ ]  (must check before stripping bullet)
        if normalized.startswith("- [ ] ") or normalized.startswith("* [ ] "):
            results.append(line[6:])
            continue

        # Strip leading bullet marker for prefix/verb checks
        content = line[2:] if (line.startswith("- ") or line.startswith("* ")) else line
        norm_content = content.lower()

        # Existing prefixes: todo: / action:
        if norm_content.startswith("todo:") or norm_content.startswith("action:"):
            results.append(content)
            continue

        # New prefixes: fixme: / note: / follow up:
        if any(norm_content.startswith(p) for p in _NEW_PREFIXES):
            results.append(content)
            continue

        # Imperative verb phrases
        if any(norm_content.startswith(v) for v in _IMPERATIVE_VERBS):
            results.append(content)
            continue

        # Exclamation suffix
        if content.endswith("!"):
            results.append(content)

    return results
