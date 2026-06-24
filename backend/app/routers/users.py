"""User profile and dashboard endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Notification, Reservation, Tool, User
from ..schemas import ReservationRead, ToolRead, UserPublic, UserUpdate
from ..security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


def _dump_list(schema, rows):
    return [schema.model_validate(row).model_dump(mode="json") for row in rows]


@router.put("/me/profile", response_model=UserPublic)
def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Update basic profile details for the logged-in user."""

    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.password is not None:
        current_user.password_hash = get_password_hash(payload.password)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the data needed for the member dashboard."""

    my_tools = (
        db.query(Tool)
        .filter(Tool.owner_id == current_user.id, Tool.is_deleted.is_(False))
        .order_by(Tool.created_at.desc())
        .all()
    )
    incoming_requests = (
        db.query(Reservation)
        .join(Tool, Reservation.tool_id == Tool.id)
        .filter(Tool.owner_id == current_user.id)
        .order_by(Reservation.created_at.desc())
        .all()
    )
    outgoing_reservations = (
        db.query(Reservation)
        .filter(Reservation.borrower_id == current_user.id)
        .order_by(Reservation.created_at.desc())
        .all()
    )
    unread_notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "profile": UserPublic.model_validate(current_user).model_dump(mode="json"),
        "my_tools": _dump_list(ToolRead, my_tools),
        "incoming_requests": _dump_list(ReservationRead, incoming_requests),
        "outgoing_reservations": _dump_list(ReservationRead, outgoing_reservations),
        "unread_notifications": [
            {
                "id": item.id,
                "title": item.title,
                "body": item.body,
                "reservation_id": item.reservation_id,
                "created_at": item.created_at,
            }
            for item in unread_notifications
        ],
    }
