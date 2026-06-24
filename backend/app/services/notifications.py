"""Notification service.

Notifications are created by business actions. The service does not commit; the
caller commits so notification and status change are saved atomically.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..models import Notification


def add_notification(
    db: Session,
    *,
    user_id: int,
    title: str,
    body: str,
    reservation_id: int | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id,
        reservation_id=reservation_id,
        title=title,
        body=body,
    )
    db.add(notification)
    return notification
