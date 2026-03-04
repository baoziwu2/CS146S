# TDD tests for Task 2: extended extraction patterns
# Written before any implementation.

from backend.app.services.extract import extract_action_items


# ---------------------------------------------------------------------------
# Existing behaviour must still pass
# ---------------------------------------------------------------------------

def test_existing_todo_and_action_prefixes():
    text = "TODO: write tests\nACTION: review PR\nShip it!"
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items


# ---------------------------------------------------------------------------
# Checkbox syntax  - [ ] and * [ ]
# ---------------------------------------------------------------------------

def test_checkbox_dash():
    items = extract_action_items("- [ ] Buy milk")
    assert "Buy milk" in items


def test_checkbox_asterisk():
    items = extract_action_items("* [ ] Fix the bug")
    assert "Fix the bug" in items


def test_checked_box_not_extracted():
    # Completed items should not be treated as action items
    items = extract_action_items("- [x] Already done")
    assert "Already done" not in items


# ---------------------------------------------------------------------------
# New prefixes: FIXME, NOTE, FOLLOW UP
# ---------------------------------------------------------------------------

def test_fixme_prefix():
    items = extract_action_items("FIXME: handle edge case")
    assert "FIXME: handle edge case" in items


def test_note_prefix():
    items = extract_action_items("NOTE: update the README")
    assert "NOTE: update the README" in items


def test_follow_up_prefix():
    items = extract_action_items("FOLLOW UP: confirm with team")
    assert "FOLLOW UP: confirm with team" in items


def test_new_prefixes_case_insensitive():
    items = extract_action_items("fixme: lowercase\nnote: also lowercase\nfollow up: yep")
    assert "fixme: lowercase" in items
    assert "note: also lowercase" in items
    assert "follow up: yep" in items


# ---------------------------------------------------------------------------
# Imperative verb phrases
# ---------------------------------------------------------------------------

def test_need_to():
    items = extract_action_items("Need to update the docs")
    assert "Need to update the docs" in items


def test_should():
    items = extract_action_items("Should refactor this module")
    assert "Should refactor this module" in items


def test_must():
    items = extract_action_items("Must fix before release")
    assert "Must fix before release" in items


def test_please():
    items = extract_action_items("Please review this PR")
    assert "Please review this PR" in items


def test_imperative_verbs_case_insensitive():
    items = extract_action_items("need to check logs\nshould add tests")
    assert "need to check logs" in items
    assert "should add tests" in items


# ---------------------------------------------------------------------------
# Deduplication: line matching multiple patterns appears only once
# ---------------------------------------------------------------------------

def test_no_duplicates_todo_and_exclamation():
    items = extract_action_items("TODO: ship it!")
    assert items.count("TODO: ship it!") == 1


def test_no_duplicates_checkbox_and_must():
    items = extract_action_items("- [ ] Must deploy now!")
    count = sum(1 for i in items if "Must deploy now!" in i)
    assert count == 1


# ---------------------------------------------------------------------------
# Non-matching lines are not extracted
# ---------------------------------------------------------------------------

def test_plain_lines_not_extracted():
    items = extract_action_items("This is just a note\nNothing special here")
    assert items == []
