"""Damage report endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import DamageReport, ReservationStatus, User
from ..schemas import DamageReportCreate, DamageReportRead
from ..services.notifications import add_notification
from ..services.reservations import get_reservation_or_404, require_borrower

router = APIRouter(prefix="/damage-reports", tags=["Damage Reports"])


@router.post("/{reservation_id}", response_model=DamageReportRead, status_code=201)
def create_damage_report(
    reservation_id: int,
    payload: DamageReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DamageReport:
    reservation = get_reservation_or_404(db, reservation_id)
    require_borrower(current_user, reservation)
    if reservation.status not in {ReservationStatus.PICKED_UP.value, ReservationStatus.RETURNED.value}:
        raise HTTPException(status_code=400, detail="Damage can only be reported during or after pickup")

    report = DamageReport(
        reservation_id=reservation_id,
        reporter_id=current_user.id,
        description=payload.description,
        photo_url=payload.photo_url,
    )
    db.add(report)
    add_notification(
        db,
        user_id=reservation.tool.owner_id,
        reservation_id=reservation.id,
        title="Damage report submitted",
        body=f"A damage report was submitted for {reservation.tool.name}.",
    )
    db.commit()
    db.refresh(report)
    return report


@router.get("", response_model=list[DamageReportRead])
def list_damage_reports(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[DamageReport]:
    return db.query(DamageReport).order_by(DamageReport.created_at.desc()).all()
