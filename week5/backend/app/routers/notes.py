from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import NoteCreate, NoteRead, NoteSearchPage, NoteTagAttach, NoteUpdate

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


@router.get("/search/", response_model=NoteSearchPage)
def search_notes(
    q: str | None = None,
    tag_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
    sort: str = "created_desc",
    db: Session = Depends(get_db),
) -> NoteSearchPage:
    stmt = select(Note)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(Note.title.ilike(pattern) | Note.content.ilike(pattern))
    if tag_id is not None:
        stmt = stmt.where(Note.tags.any(Tag.id == tag_id))

    # Count total matching results before pagination
    total: int = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    # Apply sorting
    if sort == "title_asc":
        stmt = stmt.order_by(Note.title.asc())
    else:  # default: created_desc — use id as creation-order proxy
        stmt = stmt.order_by(Note.id.desc())

    # Apply pagination
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(stmt).scalars().all()

    return NoteSearchPage(
        items=[NoteRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


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
    note.title = payload.title
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
    db.flush()


@router.post("/{note_id}/tags", response_model=NoteRead)
def attach_tag(note_id: int, payload: NoteTagAttach, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = db.get(Tag, payload.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag not in note.tags:
        note.tags.append(tag)
        db.flush()
    return NoteRead.model_validate(note)


@router.delete("/{note_id}/tags/{tag_id}", response_model=NoteRead)
def detach_tag(note_id: int, tag_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = next((t for t in note.tags if t.id == tag_id), None)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not attached to this note")
    note.tags.remove(tag)
    db.flush()
    return NoteRead.model_validate(note)
