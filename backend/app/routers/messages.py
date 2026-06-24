"""Private message thread endpoints for reservations."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Message, User
from ..schemas import MessageCreate, MessageRead
from ..services.notifications import add_notification
from ..services.reservations import get_reservation_or_404, require_participant

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("/{reservation_id}", response_model=list[MessageRead])
def list_messages(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Message]:
    reservation = get_reservation_or_404(db, reservation_id)
    require_participant(current_user, reservation)
    return (
        db.query(Message)
        .filter(Message.reservation_id == reservation_id)
        .order_by(Message.created_at.asc())
        .all()
    )


@router.post("/{reservation_id}", response_model=MessageRead, status_code=201)
def send_message(
    reservation_id: int,
    payload: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    reservation = get_reservation_or_404(db, reservation_id)
    require_participant(current_user, reservation)
    message = Message(reservation_id=reservation_id, sender_id=current_user.id, body=payload.body)
    db.add(message)

    recipient_id = reservation.tool.owner_id if current_user.id == reservation.borrower_id else reservation.borrower_id
    add_notification(
        db,
        user_id=recipient_id,
        reservation_id=reservation.id,
        title="New reservation message",
        body=f"{current_user.full_name} sent a message about {reservation.tool.name}.",
    )
    db.commit()
    db.refresh(message)
    return message
