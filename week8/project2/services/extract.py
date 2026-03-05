"""
Auto-extraction service for tags and action items from note content.
"""
import re
from typing import List, Set


def extract_tags(content: str) -> Set[str]:
    """
    Extract hashtags from content.
    Returns a set of tag names (without the # prefix).

    Examples:
        "#python #fasthtml" -> {"python", "fasthtml"}
    """
    tags = set()
    pattern = r'#(\w+)'
    matches = re.findall(pattern, content)
    for match in matches:
        tags.add(match.lower())
    return tags


def extract_action_items(content: str) -> List[str]:
    """
    Extract action items from content based on various patterns.

    Patterns matched (case-insensitive where applicable):
    1. Checkbox syntax: "- [ ] " or "* [ ] "
    2. Prefixes: "todo:", "action:", "fixme:", "note:", "follow up:"
    3. Imperative verbs: "need to ", "should ", "must ", "please "
    4. Lines ending with "!"

    Returns a list of action item descriptions.
    """
    action_items = []
    lines = content.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        is_action_item = False
        cleaned_line = line

        # Pattern 1: Checkbox syntax
        checkbox_pattern = r'^[-*]\s*\[\s*\]\s*(.+)$'
        checkbox_match = re.match(checkbox_pattern, line)
        if checkbox_match:
            cleaned_line = checkbox_match.group(1).strip()
            is_action_item = True

        # Pattern 2: Prefixes
        prefix_pattern = r'^(todo|action|fixme|note|follow\s+up):\s*(.+)$'
        prefix_match = re.match(prefix_pattern, line, re.IGNORECASE)
        if prefix_match:
            cleaned_line = prefix_match.group(2).strip()
            is_action_item = True

        # Pattern 3: Imperative verbs
        verb_pattern = r'^(need\s+to|should|must|please)\s+(.+)$'
        verb_match = re.match(verb_pattern, line, re.IGNORECASE)
        if verb_match:
            cleaned_line = line.strip()
            is_action_item = True

        # Pattern 4: Lines ending with "!"
        if line.endswith('!'):
            cleaned_line = line.strip()
            is_action_item = True

        if is_action_item:
            action_items.append(cleaned_line)

    return action_items
