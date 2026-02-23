from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem, Note
from ..schemas import ActionItemRead, NoteCreate, NoteRead, NoteUpdate
from ..services.extract import extract_action_items

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search/", response_model=list[NoteRead])
def search_notes(q: str | None = None, db: Session = Depends(get_db)) -> list[NoteRead]:
    if not q:
        rows = db.execute(select(Note)).scalars().all()
    else:
        rows = (
            db.execute(
                select(Note).where(Note.title.ilike(f"%{q}%") | Note.content.ilike(f"%{q}%"))
            )
            .scalars()
            .all()
        )
    return [NoteRead.model_validate(row) for row in rows]


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)


@router.post("/{note_id}/extract", response_model=list[ActionItemRead], status_code=201)
def extract_note(note_id: int, db: Session = Depends(get_db)) -> list[ActionItemRead]:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    extracted = extract_action_items(note.content)
    items = []
    for extracted_item in extracted:
        item = ActionItem(description=extracted_item["text"], completed=False)
        db.add(item)
        db.flush()
        db.refresh(item)
        items.append(ActionItemRead.model_validate(item))
    return items
