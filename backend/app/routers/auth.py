"""Authentication and invite-only registration endpoints."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Invitation, User, UserRole
from ..schemas import Token, UserCreate, UserLogin, UserPublic
from ..security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _is_expired(expires_at: datetime | None) -> bool:
    if expires_at is None:
        return False
    now = datetime.now(expires_at.tzinfo) if expires_at.tzinfo else datetime.utcnow()
    return expires_at < now


def _token_for_user(user: User) -> Token:
    access_token = create_access_token(str(user.id), {"role": user.role})
    return Token(access_token=access_token)


@router.post("/register", response_model=Token, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    """Create a member account using a valid, unused invitation token."""

    existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")

    invitation = db.query(Invitation).filter(Invitation.token == payload.invite_token).first()
    if invitation is None or invitation.used_at is not None or _is_expired(invitation.expires_at):
        raise HTTPException(status_code=400, detail="Invitation token is invalid or expired")
    if invitation.email.lower() != payload.email.lower():
        raise HTTPException(status_code=400, detail="Invitation email does not match registration email")

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
        role=UserRole.MEMBER.value,
    )
    db.add(user)
    db.flush()
    invitation.used_by_id = user.id
    invitation.used_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return _token_for_user(user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Return a JWT access token when email and password are valid."""

    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.is_suspended:
        raise HTTPException(status_code=403, detail="User account is suspended")
    return _token_for_user(user)


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
