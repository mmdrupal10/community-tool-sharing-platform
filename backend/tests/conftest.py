"""Shared test fixtures.

Tests use SQLite for speed. The app itself uses PostgreSQL by default, matching
course requirements.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

# Configure the test database before importing the application modules.
TEST_DB = Path(__file__).with_name("test_toolshare.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Reservation, ReservationStatus, Tool, User, UserRole
from app.security import get_password_hash


@pytest.fixture(autouse=True)
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    with TestClient(app) as test_client:
        yield test_client


def create_user(db, email: str, *, role: str = UserRole.MEMBER.value, password: str = "password123") -> User:
    user = User(
        email=email,
        full_name=email.split("@")[0].title(),
        password_hash=get_password_hash(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_tool(db, owner: User, *, name: str = "Cordless Drill") -> Tool:
    tool = Tool(
        owner_id=owner.id,
        name=name,
        description="A useful community tool.",
        category="Power Tools",
        condition="Good",
        lending_rules="Return clean.",
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool


def create_reservation(
    db,
    tool: Tool,
    borrower: User,
    *,
    status: str = ReservationStatus.REQUESTED.value,
    start_date: date = date(2026, 7, 1),
    end_date: date = date(2026, 7, 3),
) -> Reservation:
    reservation = Reservation(
        tool_id=tool.id,
        borrower_id=borrower.id,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def auth_headers(client: TestClient, email: str, password: str = "password123") -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
