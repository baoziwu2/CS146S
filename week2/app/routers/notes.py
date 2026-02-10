from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import db


class NoteBase(BaseModel):
    content: str


class NoteResponse(NoteBase):
    id: int
    created_at: str


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def create_note(payload: NoteBase) -> NoteResponse:
    """Create a new note with the given content."""
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")

    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    return NoteResponse(
        id=note_id,
        content=note["content"],
        created_at=note["created_at"],
    )


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """Fetch a single note by its ID."""
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteResponse(
        id=note_id,
        content=row["content"],
        created_at=row["created_at"],
    )


@router.get("", response_model=List[NoteResponse])
def list_notes() -> List[NoteResponse]:
    """List all notes ordered by newest first."""
    rows = db.list_notes()
    return [
        NoteResponse(id=r["id"], content=r["content"], created_at=r["created_at"])
        for r in rows
    ]


