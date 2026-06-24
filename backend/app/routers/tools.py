"""Tool listing endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Reservation, Tool, User
from ..schemas import ToolCreate, ToolRead, ToolUpdate

router = APIRouter(prefix="/tools", tags=["Tools"])


def get_tool_or_404(db: Session, tool_id: int) -> Tool:
    tool = db.get(Tool, tool_id)
    if tool is None or tool.is_deleted:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


def require_tool_owner(tool: Tool, user: User) -> None:
    if tool.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the tool owner can modify this listing")


@router.get("", response_model=list[ToolRead])
def search_tools(
    q: str | None = Query(default=None, description="Keyword search for name or description"),
    category: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Tool]:
    """Browse active tool listings by keyword and category."""

    query = db.query(Tool).filter(Tool.is_deleted.is_(False), Tool.is_active.is_(True))
    if category:
        query = query.filter(Tool.category.ilike(f"%{category}%"))
    if q:
        query = query.filter(or_(Tool.name.ilike(f"%{q}%"), Tool.description.ilike(f"%{q}%")))
    return query.order_by(Tool.created_at.desc()).all()


@router.get("/mine", response_model=list[ToolRead])
def list_my_tools(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Tool]:
    return (
        db.query(Tool)
        .filter(Tool.owner_id == current_user.id, Tool.is_deleted.is_(False))
        .order_by(Tool.created_at.desc())
        .all()
    )


@router.post("", response_model=ToolRead, status_code=201)
def create_tool(
    payload: ToolCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tool:
    """Create a new tool listing for the current user."""

    tool = Tool(owner_id=current_user.id, **payload.model_dump())
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool


@router.get("/{tool_id}", response_model=ToolRead)
def get_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tool:
    return get_tool_or_404(db, tool_id)


@router.put("/{tool_id}", response_model=ToolRead)
def update_tool(
    tool_id: int,
    payload: ToolUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tool:
    tool = get_tool_or_404(db, tool_id)
    require_tool_owner(tool, current_user)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(tool, key, value)
    db.commit()
    db.refresh(tool)
    return tool


@router.patch("/{tool_id}/hide", response_model=ToolRead)
def hide_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tool:
    tool = get_tool_or_404(db, tool_id)
    require_tool_owner(tool, current_user)
    tool.is_active = False
    db.commit()
    db.refresh(tool)
    return tool


@router.patch("/{tool_id}/show", response_model=ToolRead)
def show_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tool:
    tool = get_tool_or_404(db, tool_id)
    require_tool_owner(tool, current_user)
    tool.is_active = True
    db.commit()
    db.refresh(tool)
    return tool


@router.delete("/{tool_id}", status_code=204, response_class=Response)
def delete_tool(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    """Soft-delete a tool so reservation audit history remains intact."""

    tool = get_tool_or_404(db, tool_id)
    require_tool_owner(tool, current_user)
    tool.is_deleted = True
    tool.is_active = False
    db.commit()
    return Response(status_code=204)


@router.get("/{tool_id}/availability")
def get_tool_availability(
    tool_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return active reservation windows for a simple availability calendar."""

    get_tool_or_404(db, tool_id)
    reservations = (
        db.query(Reservation)
        .filter(
            Reservation.tool_id == tool_id,
            Reservation.status.in_(["APPROVED", "PICKED_UP"]),
        )
        .order_by(Reservation.start_date)
        .all()
    )
    return [
        {"reservation_id": item.id, "start_date": item.start_date, "end_date": item.end_date, "status": item.status}
        for item in reservations
    ]
