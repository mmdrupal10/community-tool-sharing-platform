"""Permission and review tests for common negative paths."""

from __future__ import annotations

from app.models import ReservationStatus
from tests.conftest import auth_headers, create_reservation, create_tool, create_user


def test_review_is_blocked_before_returned(client, db_session):
    owner = create_user(db_session, "owner@example.com")
    borrower = create_user(db_session, "borrower@example.com")
    tool = create_tool(db_session, owner)
    reservation = create_reservation(db_session, tool, borrower, status=ReservationStatus.APPROVED.value)

    response = client.post(
        f"/reviews/{reservation.id}",
        headers=auth_headers(client, borrower.email),
        json={"rating": 4, "comment": "Too early."},
    )
    assert response.status_code == 400
    assert "RETURNED" in response.json()["detail"]


def test_non_participant_cannot_send_message(client, db_session):
    owner = create_user(db_session, "owner@example.com")
    borrower = create_user(db_session, "borrower@example.com")
    stranger = create_user(db_session, "stranger@example.com")
    tool = create_tool(db_session, owner)
    reservation = create_reservation(db_session, tool, borrower)

    response = client.post(
        f"/messages/{reservation.id}",
        headers=auth_headers(client, stranger.email),
        json={"body": "Can I join this thread?"},
    )
    assert response.status_code == 403


def test_admin_can_suspend_member(client, db_session):
    admin = create_user(db_session, "admin@example.com", role="admin")
    member = create_user(db_session, "member@example.com")

    response = client.patch(
        f"/admin/users/{member.id}/suspend",
        headers=auth_headers(client, admin.email),
        json={"is_suspended": True},
    )
    assert response.status_code == 200
    assert response.json()["is_suspended"] is True

    response = client.post("/auth/login", json={"email": member.email, "password": "password123"})
    assert response.status_code == 403
