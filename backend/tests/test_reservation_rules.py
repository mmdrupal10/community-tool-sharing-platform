"""Automated tests for the critical reservation workflow rules."""

from __future__ import annotations

from datetime import date

from app.models import ReservationStatus
from tests.conftest import auth_headers, create_reservation, create_tool, create_user


def test_only_owner_can_approve_request(client, db_session):
    owner = create_user(db_session, "owner@example.com")
    borrower = create_user(db_session, "borrower@example.com")
    stranger = create_user(db_session, "stranger@example.com")
    tool = create_tool(db_session, owner)
    reservation = create_reservation(db_session, tool, borrower)

    stranger_headers = auth_headers(client, stranger.email)
    response = client.post(f"/reservations/{reservation.id}/approve", headers=stranger_headers)
    assert response.status_code == 403

    owner_headers = auth_headers(client, owner.email)
    response = client.post(f"/reservations/{reservation.id}/approve", headers=owner_headers)
    assert response.status_code == 200
    assert response.json()["status"] == ReservationStatus.APPROVED.value


def test_overlapping_approved_reservations_are_rejected(client, db_session):
    owner = create_user(db_session, "owner@example.com")
    borrower = create_user(db_session, "borrower@example.com")
    second_borrower = create_user(db_session, "second@example.com")
    tool = create_tool(db_session, owner)
    create_reservation(
        db_session,
        tool,
        borrower,
        status=ReservationStatus.APPROVED.value,
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 3),
    )

    response = client.post(
        "/reservations",
        headers=auth_headers(client, second_borrower.email),
        json={"tool_id": tool.id, "start_date": "2026-07-02", "end_date": "2026-07-04"},
    )
    assert response.status_code == 400
    assert "already booked" in response.json()["detail"]


def test_cancel_is_not_allowed_after_pickup(client, db_session):
    owner = create_user(db_session, "owner@example.com")
    borrower = create_user(db_session, "borrower@example.com")
    tool = create_tool(db_session, owner)
    reservation = create_reservation(db_session, tool, borrower, status=ReservationStatus.PICKED_UP.value)

    response = client.post(
        f"/reservations/{reservation.id}/cancel",
        headers=auth_headers(client, borrower.email),
    )
    assert response.status_code == 400
    assert "before pickup" in response.json()["detail"]


def test_end_to_end_reservation_flow(client, db_session):
    owner = create_user(db_session, "owner@example.com")
    borrower = create_user(db_session, "borrower@example.com")
    tool = create_tool(db_session, owner)

    borrower_headers = auth_headers(client, borrower.email)
    owner_headers = auth_headers(client, owner.email)

    response = client.post(
        "/reservations",
        headers=borrower_headers,
        json={"tool_id": tool.id, "start_date": "2026-08-01", "end_date": "2026-08-02"},
    )
    assert response.status_code == 201
    reservation_id = response.json()["id"]

    response = client.post(f"/reservations/{reservation_id}/approve", headers=owner_headers)
    assert response.json()["status"] == ReservationStatus.APPROVED.value

    response = client.post(f"/reservations/{reservation_id}/pickup", headers=borrower_headers)
    assert response.json()["status"] == ReservationStatus.PICKED_UP.value

    response = client.post(f"/reservations/{reservation_id}/return", headers=owner_headers)
    assert response.json()["status"] == ReservationStatus.RETURNED.value

    response = client.post(
        f"/reviews/{reservation_id}",
        headers=borrower_headers,
        json={"rating": 5, "comment": "Great owner and easy pickup."},
    )
    assert response.status_code == 201
    assert response.json()["rating"] == 5
