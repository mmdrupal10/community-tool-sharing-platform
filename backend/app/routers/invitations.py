"""Invitation endpoints.

Any active member can invite a neighbor. Admins can view pending invitations.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import Invitation, User
from ..schemas import InvitationCreate, InvitationRead

router = APIRouter(prefix="/invitations", tags=["Invitations"])


@router.post("", response_model=InvitationRead, status_code=201)
def create_invitation(
    payload: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Invitation:
    """Create an invite token for a new community member."""

    invitation = Invitation(
        email=payload.email.lower(),
        token=secrets.token_urlsafe(24),
        created_by_id=current_user.id,
        expires_at=payload.expires_at or (datetime.utcnow() + timedelta(days=30)),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


@router.get("/pending", response_model=list[InvitationRead])
def list_pending_invitations(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[Invitation]:
    """Admin view of invitations that have not been used."""

    return (
        db.query(Invitation)
        .filter(Invitation.used_at.is_(None))
        .order_by(Invitation.created_at.desc())
        .all()
    )
