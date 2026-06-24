"""Reservation workflow endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Reservation, ReservationStatus, Tool, User
from ..schemas import ReservationCreate, ReservationRead
from ..services.reservations import (
    approve_reservation,
    cancel_reservation,
    create_reservation,
    deny_reservation,
    get_reservation_or_404,
    mark_picked_up,
    mark_returned,
    require_participant,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.post("", response_model=ReservationRead, status_code=201)
def request_reservation(
    payload: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Reservation:
    tool = db.get(Tool, payload.tool_id)
    if tool is None:
        raise HTTPException(status_code=404, detail="Tool not found")
    return create_reservation(
        db,
        borrower=current_user,
        tool=tool,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )


@router.get("/incoming", response_model=list[ReservationRead])
def list_incoming_requests(
    status: ReservationStatus | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Reservation]:
    query = db.query(Reservation).join(Tool, Reservation.tool_id == Tool.id).filter(Tool.owner_id == current_user.id)
    if status:
        query = query.filter(Reservation.status == status.value)
    return query.order_by(Reservation.created_at.desc()).all()


@router.get("/outgoing", response_model=list[ReservationRead])
def list_outgoing_reservations(
    status: ReservationStatus | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Reservation]:
    query = db.query(Reservation).filter(Reservation.borrower_id == current_user.id)
    if status:
        query = query.filter(Reservation.status == status.value)
    return query.order_by(Reservation.created_at.desc()).all()


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Reservation:
    reservation = get_reservation_or_404(db, reservation_id)
    require_participant(current_user, reservation)
    return reservation


@router.post("/{reservation_id}/approve", response_model=ReservationRead)
def approve(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Reservation:
    return approve_reservation(db, reservation=get_reservation_or_404(db, reservation_id), owner=current_user)


@router.post("/{reservation_id}/deny", response_model=ReservationRead)
def deny(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Reservation:
    return deny_reservation(db, reservation=get_reservation_or_404(db, reservation_id), owner=current_user)


@router.post("/{reservation_id}/cancel", response_model=ReservationRead)
def cancel(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Reservation:
    return cancel_reservation(db, reservation=get_reservation_or_404(db, reservation_id), user=current_user)


@router.post("/{reservation_id}/pickup", response_model=ReservationRead)
def pickup(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Reservation:
    return mark_picked_up(db, reservation=get_reservation_or_404(db, reservation_id), borrower=current_user)


@router.post("/{reservation_id}/return", response_model=ReservationRead)
def returned(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Reservation:
    return mark_returned(db, reservation=get_reservation_or_404(db, reservation_id), owner=current_user)
