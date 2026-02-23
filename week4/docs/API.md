# API Reference

> Generated from `/openapi.json` (OpenAPI 3.1.0).
> Base URL: `http://localhost:8000`
> Interactive docs: `http://localhost:8000/docs`

---

## Schemas

### NoteCreate
| Field | Type | Rules |
|---|---|---|
| `title` | string | required, 1–200 chars |
| `content` | string | required, min 1 char |

### NoteRead
| Field | Type |
|---|---|
| `id` | integer |
| `title` | string |
| `content` | string |

### NoteUpdate *(all fields optional)*
| Field | Type | Rules |
|---|---|---|
| `title` | string \| null | if provided: 1–200 chars |
| `content` | string \| null | if provided: min 1 char |

### ActionItemCreate
| Field | Type | Rules |
|---|---|---|
| `description` | string | required, min 1 char |

### ActionItemRead
| Field | Type |
|---|---|
| `id` | integer |
| `description` | string |
| `completed` | boolean |

---

## Notes

### `GET /notes/`
List all notes.

**Response `200`** — `NoteRead[]`

---

### `POST /notes/`
Create a new note.

**Request body** — `NoteCreate`
```json
{ "title": "Sprint goals", "content": "- TODO: deploy #infra\n- 记得回复邮件 #work" }
```

**Response `201`** — `NoteRead`
**Response `422`** — validation error (empty/missing fields, title > 200 chars)

---

### `GET /notes/search/`
Search notes by keyword (case-insensitive, matches title or content).

**Query params**
| Param | Type | Required | Description |
|---|---|---|---|
| `q` | string | no | Search term; omit to return all notes |

**Response `200`** — `NoteRead[]`

---

### `GET /notes/{note_id}`
Fetch a single note by ID.

**Response `200`** — `NoteRead`
**Response `404`** — `{ "detail": "Note not found" }`

---

### `PUT /notes/{note_id}`
Partially update a note's title and/or content.

**Request body** — `NoteUpdate` *(send only the fields you want to change)*
```json
{ "title": "New title" }
```

**Response `200`** — `NoteRead` (updated)
**Response `404`** — `{ "detail": "Note not found" }`
**Response `422`** — validation error (empty string provided)

---

### `DELETE /notes/{note_id}`
Delete a note permanently.

**Response `204`** — no content
**Response `404`** — `{ "detail": "Note not found" }`

---

### `POST /notes/{note_id}/extract`
Parse the note's content and create action items from it.

A line is extracted when it:
- starts with `TODO:`, **or**
- ends with `!`, **or**
- contains at least one `#tag`

`#tag` tokens are stripped from the stored description.

**Response `201`** — `ActionItemRead[]`
```json
[
  { "id": 1, "description": "TODO: 买牛奶", "completed": false },
  { "id": 2, "description": "记得回复邮件", "completed": false }
]
```
**Response `404`** — `{ "detail": "Note not found" }`

---

## Action Items

### `GET /action-items/`
List all action items.

**Response `200`** — `ActionItemRead[]`

---

### `POST /action-items/`
Create a new action item.

**Request body** — `ActionItemCreate`
```json
{ "description": "Buy milk" }
```

**Response `201`** — `ActionItemRead`
**Response `422`** — validation error (empty/missing description)

---

### `PUT /action-items/{item_id}/complete`
Mark an action item as completed (idempotent).

**Response `200`** — `ActionItemRead` with `completed: true`
**Response `404`** — `{ "detail": "Action item not found" }`

---

## Validation Error Format (`422`)

All validation errors share this shape:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "type": "string_too_short"
    }
  ]
}
```
