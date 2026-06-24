"""Reservation business rules and state machine.

Centralizing these rules keeps the API routers thin and makes the critical
workflow easy to unit test.
"""

from __future__ import annotations

from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import ACTIVE_BOOKING_STATUSES, Reservation, ReservationStatus, Tool, User
from .notifications import add_notification


def validate_date_range(start_date: date, end_date: date) -> None:
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="End date must be on or after start date")


def ensure_no_active_overlap(
    db: Session,
    *,
    tool_id: int,
    start_date: date,
    end_date: date,
    exclude_reservation_id: int | None = None,
) -> None:
    """Reject reservations that overlap an approved or picked-up reservation.

    Date ranges are inclusive: May 1-May 3 overlaps May 3-May 5 because the tool
    cannot be returned and borrowed by another member on the same day.
    """

    query = db.query(Reservation).filter(
        Reservation.tool_id == tool_id,
        Reservation.status.in_(ACTIVE_BOOKING_STATUSES),
        Reservation.start_date <= end_date,
        Reservation.end_date >= start_date,
    )
    if exclude_reservation_id is not None:
        query = query.filter(Reservation.id != exclude_reservation_id)

    if query.first() is not None:
        raise HTTPException(status_code=400, detail="Tool is already booked for those dates")


def get_reservation_or_404(db: Session, reservation_id: int) -> Reservation:
    reservation = db.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation


def require_owner(user: User, reservation: Reservation) -> None:
    if reservation.tool.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only the tool owner can perform this action")


def require_borrower(user: User, reservation: Reservation) -> None:
    if reservation.borrower_id != user.id:
        raise HTTPException(status_code=403, detail="Only the borrower can perform this action")


def require_participant(user: User, reservation: Reservation) -> None:
    if user.id not in {reservation.borrower_id, reservation.tool.owner_id}:
        raise HTTPException(status_code=403, detail="Only reservation participants can access this")


def create_reservation(
    db: Session,
    *,
    borrower: User,
    tool: Tool,
    start_date: date,
    end_date: date,
) -> Reservation:
    validate_date_range(start_date, end_date)
    if tool.is_deleted or not tool.is_active:
        raise HTTPException(status_code=400, detail="Tool is not available for reservations")
    if tool.owner_id == borrower.id:
        raise HTTPException(status_code=400, detail="Owners cannot borrow their own tools")

    ensure_no_active_overlap(db, tool_id=tool.id, start_date=start_date, end_date=end_date)

    reservation = Reservation(
        tool_id=tool.id,
        borrower_id=borrower.id,
        start_date=start_date,
        end_date=end_date,
        status=ReservationStatus.REQUESTED.value,
    )
    db.add(reservation)
    db.flush()
    add_notification(
        db,
        user_id=tool.owner_id,
        reservation_id=reservation.id,
        title="New reservation request",
        body=f"{borrower.full_name} requested {tool.name} from {start_date} to {end_date}.",
    )
    db.commit()
    db.refresh(reservation)
    return reservation


def approve_reservation(db: Session, *, reservation: Reservation, owner: User) -> Reservation:
    require_owner(owner, reservation)
    if reservation.status != ReservationStatus.REQUESTED.value:
        raise HTTPException(status_code=400, detail="Only REQUESTED reservations can be approved")

    ensure_no_active_overlap(
        db,
        tool_id=reservation.tool_id,
        start_date=reservation.start_date,
        end_date=reservation.end_date,
        exclude_reservation_id=reservation.id,
    )
    reservation.status = ReservationStatus.APPROVED.value
    add_notification(
        db,
        user_id=reservation.borrower_id,
        reservation_id=reservation.id,
        title="Reservation approved",
        body=f"Your request for {reservation.tool.name} was approved.",
    )
    db.commit()
    db.refresh(reservation)
    return reservation


def deny_reservation(db: Session, *, reservation: Reservation, owner: User) -> Reservation:
    require_owner(owner, reservation)
    if reservation.status != ReservationStatus.REQUESTED.value:
        raise HTTPException(status_code=400, detail="Only REQUESTED reservations can be denied")

    reservation.status = ReservationStatus.DENIED.value
    add_notification(
        db,
        user_id=reservation.borrower_id,
        reservation_id=reservation.id,
        title="Reservation denied",
        body=f"Your request for {reservation.tool.name} was denied.",
    )
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, *, reservation: Reservation, user: User) -> Reservation:
    require_participant(user, reservation)
    if reservation.status not in {ReservationStatus.REQUESTED.value, ReservationStatus.APPROVED.value}:
        raise HTTPException(status_code=400, detail="Cancellation is only allowed before pickup")

    reservation.status = ReservationStatus.CANCELLED.value
    other_user_id = reservation.tool.owner_id if user.id == reservation.borrower_id else reservation.borrower_id
    add_notification(
        db,
        user_id=other_user_id,
        reservation_id=reservation.id,
        title="Reservation cancelled",
        body=f"Reservation #{reservation.id} for {reservation.tool.name} was cancelled.",
    )
    db.commit()
    db.refresh(reservation)
    return reservation


def mark_picked_up(db: Session, *, reservation: Reservation, borrower: User) -> Reservation:
    require_borrower(borrower, reservation)
    if reservation.status != ReservationStatus.APPROVED.value:
        raise HTTPException(status_code=400, detail="Only APPROVED reservations can be picked up")

    reservation.status = ReservationStatus.PICKED_UP.value
    add_notification(
        db,
        user_id=reservation.tool.owner_id,
        reservation_id=reservation.id,
        title="Tool picked up",
        body=f"{borrower.full_name} marked {reservation.tool.name} as picked up.",
    )
    db.commit()
    db.refresh(reservation)
    return reservation


def mark_returned(db: Session, *, reservation: Reservation, owner: User) -> Reservation:
    require_owner(owner, reservation)
    if reservation.status != ReservationStatus.PICKED_UP.value:
        raise HTTPException(status_code=400, detail="Only PICKED_UP reservations can be returned")

    reservation.status = ReservationStatus.RETURNED.value
    add_notification(
        db,
        user_id=reservation.borrower_id,
        reservation_id=reservation.id,
        title="Tool returned",
        body=f"{reservation.tool.name} was marked as returned.",
    )
    db.commit()
    db.refresh(reservation)
    return reservation
