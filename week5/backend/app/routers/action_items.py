from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..response import api_ok
from ..schemas import ActionItemCreate, ActionItemRead, ActionItemsPage, BulkCompleteRequest

_DEFAULT_PAGE_SIZE = 10

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/")
def list_items(
    completed: bool | None = None,
    page: int = 1,
    page_size: int = _DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
) -> JSONResponse:
    stmt = select(ActionItem)
    if completed is not None:
        stmt = stmt.where(ActionItem.completed == completed)
    total: int = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
    stmt = stmt.order_by(ActionItem.id.asc()).offset((page - 1) * page_size).limit(page_size)
    rows = db.execute(stmt).scalars().all()
    return api_ok(
        ActionItemsPage(
            items=[ActionItemRead.model_validate(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/", status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> JSONResponse:
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return api_ok(ActionItemRead.model_validate(item), status_code=201)


@router.post("/bulk-complete")
def bulk_complete(payload: BulkCompleteRequest, db: Session = Depends(get_db)) -> JSONResponse:
    items = []
    for item_id in payload.ids:
        item = db.get(ActionItem, item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Action item {item_id} not found")
        item.completed = True
        items.append(item)
    db.flush()
    for item in items:
        db.refresh(item)
    return api_ok([ActionItemRead.model_validate(item) for item in items])


@router.put("/{item_id}/complete")
def complete_item(item_id: int, db: Session = Depends(get_db)) -> JSONResponse:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return api_ok(ActionItemRead.model_validate(item))
