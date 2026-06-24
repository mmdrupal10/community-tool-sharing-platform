"""Review and rating endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import ReservationStatus, Review, User
from ..schemas import ReviewCreate, ReviewRead
from ..services.notifications import add_notification
from ..services.reservations import get_reservation_or_404, require_participant

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/{reservation_id}", response_model=ReviewRead, status_code=201)
def create_review(
    reservation_id: int,
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Review:
    reservation = get_reservation_or_404(db, reservation_id)
    require_participant(current_user, reservation)
    if reservation.status != ReservationStatus.RETURNED.value:
        raise HTTPException(status_code=400, detail="Reviews are only allowed after a reservation is RETURNED")

    existing = (
        db.query(Review)
        .filter(Review.reservation_id == reservation_id, Review.reviewer_id == current_user.id)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=400, detail="You already reviewed this reservation")

    reviewee_id = reservation.tool.owner_id if current_user.id == reservation.borrower_id else reservation.borrower_id
    review = Review(
        reservation_id=reservation_id,
        reviewer_id=current_user.id,
        reviewee_id=reviewee_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    add_notification(
        db,
        user_id=reviewee_id,
        reservation_id=reservation.id,
        title="New review received",
        body=f"{current_user.full_name} left a review for reservation #{reservation.id}.",
    )
    db.commit()
    db.refresh(review)
    return review


@router.get("/users/{user_id}", response_model=list[ReviewRead])
def get_user_reviews(user_id: int, db: Session = Depends(get_db)) -> list[Review]:
    return db.query(Review).filter(Review.reviewee_id == user_id).order_by(Review.created_at.desc()).all()
