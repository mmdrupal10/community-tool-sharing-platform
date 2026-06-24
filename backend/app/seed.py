"""Seed demo data for local demos.

Run from the backend folder:
    python -m app.seed
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .database import Base, SessionLocal, engine
from .models import Invitation, Message, Reservation, ReservationStatus, Review, Tool, User, UserRole
from .security import get_password_hash

DEMO_PASSWORD = "password123"


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "admin@example.com").first():
            print("Seed data already exists.")
            return

        admin = User(
            email="admin@example.com",
            full_name="Ava Admin",
            password_hash=get_password_hash(DEMO_PASSWORD),
            role=UserRole.ADMIN.value,
        )
        owner = User(
            email="owner@example.com",
            full_name="Olivia Owner",
            password_hash=get_password_hash(DEMO_PASSWORD),
            role=UserRole.MEMBER.value,
        )
        borrower = User(
            email="borrower@example.com",
            full_name="Ben Borrower",
            password_hash=get_password_hash(DEMO_PASSWORD),
            role=UserRole.MEMBER.value,
        )
        member = User(
            email="member@example.com",
            full_name="Mia Member",
            password_hash=get_password_hash(DEMO_PASSWORD),
            role=UserRole.MEMBER.value,
        )
        db.add_all([admin, owner, borrower, member])
        db.flush()

        invitation = Invitation(
            email="newneighbor@example.com",
            token="DEMO-INVITE-NEW",
            created_by_id=admin.id,
            expires_at=datetime.utcnow() + timedelta(days=30),
        )
        db.add(invitation)

        drill = Tool(
            owner_id=owner.id,
            name="Cordless Drill",
            description="18V cordless drill with spare battery and bit set.",
            category="Power Tools",
            condition="Good",
            photo_url="https://images.unsplash.com/photo-1504148455328-c376907d081c",
            lending_rules="Maximum 3-day loan. Return with battery charged.",
        )
        ladder = Tool(
            owner_id=owner.id,
            name="8 ft Step Ladder",
            description="Aluminum step ladder for indoor projects.",
            category="Ladders",
            condition="Very Good",
            lending_rules="Pickup after 5 PM. Keep dry.",
        )
        rake = Tool(
            owner_id=member.id,
            name="Garden Rake",
            description="Wide garden rake for leaves and yard cleanup.",
            category="Garden",
            condition="Fair",
            lending_rules="Please rinse after use.",
        )
        db.add_all([drill, ladder, rake])
        db.flush()

        requested = Reservation(
            tool_id=drill.id,
            borrower_id=borrower.id,
            status=ReservationStatus.REQUESTED.value,
            start_date=date(2026, 7, 8),
            end_date=date(2026, 7, 10),
        )
        approved = Reservation(
            tool_id=ladder.id,
            borrower_id=borrower.id,
            status=ReservationStatus.APPROVED.value,
            start_date=date(2026, 7, 15),
            end_date=date(2026, 7, 16),
        )
        returned = Reservation(
            tool_id=rake.id,
            borrower_id=borrower.id,
            status=ReservationStatus.RETURNED.value,
            start_date=date(2026, 6, 10),
            end_date=date(2026, 6, 11),
        )
        db.add_all([requested, approved, returned])
        db.flush()

        db.add(
            Message(
                reservation_id=requested.id,
                sender_id=borrower.id,
                body="Could I pick up the drill after work?",
            )
        )
        db.add(
            Review(
                reservation_id=returned.id,
                reviewer_id=borrower.id,
                reviewee_id=member.id,
                rating=5,
                comment="Easy pickup and the rake worked well.",
            )
        )
        db.commit()
        print("Seed data created.")
        print("Demo password for all users:", DEMO_PASSWORD)
        print("Unused invite token: DEMO-INVITE-NEW")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
