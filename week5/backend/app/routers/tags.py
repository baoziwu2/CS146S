from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tag
from ..response import api_ok
from ..schemas import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/")
def list_tags(db: Session = Depends(get_db)) -> JSONResponse:
    rows = db.execute(select(Tag)).scalars().all()
    return api_ok([TagRead.model_validate(row) for row in rows])


@router.post("/", status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> JSONResponse:
    existing = db.execute(select(Tag).where(Tag.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Tag already exists")
    tag = Tag(name=payload.name)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return api_ok(TagRead.model_validate(tag), status_code=201)


@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.flush()
