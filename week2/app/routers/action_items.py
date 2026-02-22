from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .. import db
from ..services.extract import extract_action_items, extract_action_items_llm


class ExtractRequest(BaseModel):
    text: str
    save_note: bool = False


class ExtractResponseItem(BaseModel):
    id: int
    text: str


class ExtractResponse(BaseModel):
    note_id: int | None
    items: List[ExtractResponseItem]


class MarkDoneRequest(BaseModel):
    done: bool


class MarkDoneResponse(BaseModel):
    id: int
    done: bool


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract")
def extract(payload: ExtractRequest) -> ExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id, items=[ExtractResponseItem(id=i, text=t) for i, t in zip(ids, items)]
    )


@router.post("/extract-llm")
def extract_llm(payload: ExtractRequest) -> ExtractResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id = None
    if payload.save_note:
        note_id = db.insert_note(text)

    try:
        items = extract_action_items_llm(text)
        # 调试日志：打印提取到的 items
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"LLM extracted {len(items)} items: {items}")
    except Exception as exc:  # Fallback to heuristic extractor on failure
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {exc}") from exc

    ids = db.insert_action_items(items, note_id=note_id)
    response = ExtractResponse(
        note_id=note_id, items=[ExtractResponseItem(id=i, text=t) for i, t in zip(ids, items)]
    )
    # 调试日志：打印响应
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Returning response with {len(response.items)} items")
    return response


@router.get("")
def list_all(note_id: Optional[int] = None) -> List[ExtractResponseItem]:
    rows = db.list_action_items(note_id=note_id)
    return [ExtractResponseItem(id=r["id"], text=r["text"]) for r in rows]


@router.post("/{action_item_id}/done")
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    done = payload.done
    db.mark_action_item_done(action_item_id, done)
    return MarkDoneResponse(id=action_item_id, done=done)
