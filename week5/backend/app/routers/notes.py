from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem, Note, Tag
from ..response import api_ok
from ..schemas import (
    ExtractionResult,
    NoteCreate,
    NoteRead,
    NoteSearchPage,
    NoteUpdate,
    TagAttachRequest,
)
from ..services.extract import extract_tags, extract_tasks

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/")
def list_notes(tag_id: int | None = None, db: Session = Depends(get_db)) -> JSONResponse:
    stmt = select(Note)
    if tag_id is not None:
        stmt = stmt.join(Note.tags).where(Tag.id == tag_id)
    rows = db.execute(stmt).scalars().all()
    return api_ok([NoteRead.model_validate(row) for row in rows])


@router.post("/", status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> JSONResponse:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return api_ok(NoteRead.model_validate(note), status_code=201)


@router.get("/search/")
def search_notes(
    q: str | None = None,
    tag_id: int | None = None,
    page: int = 1,
    page_size: int = 10,
    sort: str = "created_desc",
    db: Session = Depends(get_db),
) -> JSONResponse:
    stmt = select(Note)
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(Note.title.ilike(pattern) | Note.content.ilike(pattern))
    if tag_id is not None:
        stmt = stmt.join(Note.tags).where(Tag.id == tag_id)

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

    return api_ok(
        NoteSearchPage(
            items=[NoteRead.model_validate(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/{note_id}/tags")
def attach_tag(
    note_id: int, payload: TagAttachRequest, db: Session = Depends(get_db)
) -> JSONResponse:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = db.get(Tag, payload.tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag not in note.tags:
        note.tags.append(tag)
        db.flush()
    return api_ok(NoteRead.model_validate(note))


@router.delete("/{note_id}/tags/{tag_id}")
def detach_tag(note_id: int, tag_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = db.get(Tag, tag_id)
    if not tag or tag not in note.tags:
        raise HTTPException(status_code=404, detail="Tag not attached to this note")
    note.tags.remove(tag)
    db.flush()
    return api_ok(NoteRead.model_validate(note))


@router.post("/{note_id}/extract")
def extract_note(
    note_id: int, apply: bool = False, db: Session = Depends(get_db)
) -> JSONResponse:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    tag_names = extract_tags(note.content)
    task_texts = extract_tasks(note.content)

    if apply:
        for name in tag_names:
            tag = db.execute(select(Tag).where(Tag.name == name)).scalar_one_or_none()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
                db.flush()
            if tag not in note.tags:
                note.tags.append(tag)
        for description in task_texts:
            db.add(ActionItem(description=description, completed=False))
        db.flush()

    return api_ok(ExtractionResult(tags=tag_names, action_items=task_texts))


@router.get("/{note_id}")
def get_note(note_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return api_ok(NoteRead.model_validate(note))


@router.put("/{note_id}")
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> JSONResponse:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = payload.title
    note.content = payload.content
    db.flush()
    db.refresh(note)
    return api_ok(NoteRead.model_validate(note))


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.flush()
