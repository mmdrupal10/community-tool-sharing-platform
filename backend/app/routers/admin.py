"""Administrator endpoints for reporting and moderation."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import DamageReport, Reservation, Review, Tool, User
from ..schemas import SuspendUserRequest, ToolActivationRequest, ToolRead, UserPublic

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/users", response_model=list[UserPublic])
def list_users(_admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}/suspend", response_model=UserPublic)
def suspend_user(
    user_id: int,
    payload: SuspendUserRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Admins cannot suspend themselves")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_suspended = payload.is_suspended
    db.commit()
    db.refresh(user)
    return user


@router.get("/tools", response_model=list[ToolRead])
def list_all_tools(_admin: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[Tool]:
    return db.query(Tool).filter(Tool.is_deleted.is_(False)).order_by(Tool.created_at.desc()).all()


@router.patch("/tools/{tool_id}/activation", response_model=ToolRead)
def set_tool_activation(
    tool_id: int,
    payload: ToolActivationRequest,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Tool:
    tool = db.get(Tool, tool_id)
    if tool is None or tool.is_deleted:
        raise HTTPException(status_code=404, detail="Tool not found")
    tool.is_active = payload.is_active
    db.commit()
    db.refresh(tool)
    return tool


@router.get("/reports")
def get_basic_reports(_admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    """Generate simple counts for the admin reporting user story."""

    reservation_counts = dict(db.query(Reservation.status, func.count(Reservation.id)).group_by(Reservation.status).all())
    category_counts = dict(db.query(Tool.category, func.count(Tool.id)).group_by(Tool.category).all())
    return {
        "total_users": db.query(func.count(User.id)).scalar(),
        "suspended_users": db.query(func.count(User.id)).filter(User.is_suspended.is_(True)).scalar(),
        "active_tools": db.query(func.count(Tool.id)).filter(Tool.is_active.is_(True), Tool.is_deleted.is_(False)).scalar(),
        "hidden_tools": db.query(func.count(Tool.id)).filter(Tool.is_active.is_(False), Tool.is_deleted.is_(False)).scalar(),
        "reservations_by_status": reservation_counts,
        "tools_by_category": category_counts,
        "reviews": db.query(func.count(Review.id)).scalar(),
        "damage_reports": db.query(func.count(DamageReport.id)).scalar(),
    }
