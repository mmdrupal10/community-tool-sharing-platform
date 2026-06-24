"""Pydantic request and response models.

Schemas keep API input/output separate from SQLAlchemy models. This makes the
API easier to validate and document through FastAPI's generated OpenAPI docs.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .models import ReservationStatus, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_suspended: bool
    created_at: datetime


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    invite_token: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class InvitationCreate(BaseModel):
    email: EmailStr
    expires_at: datetime | None = None


class InvitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    token: str
    created_by_id: int | None
    used_by_id: int | None
    used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime


class ToolBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=5)
    category: str = Field(min_length=2, max_length=80)
    condition: str = Field(min_length=2, max_length=80)
    photo_url: str | None = Field(default=None, max_length=500)
    lending_rules: str | None = None


class ToolCreate(ToolBase):
    pass


class ToolUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = Field(default=None, min_length=5)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    condition: str | None = Field(default=None, min_length=2, max_length=80)
    photo_url: str | None = Field(default=None, max_length=500)
    lending_rules: str | None = None
    is_active: bool | None = None


class ToolRead(ToolBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None
    owner: UserPublic | None = None


class ReservationCreate(BaseModel):
    tool_id: int
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def end_date_must_not_be_before_start(cls, value: date, info: Any) -> date:
        start_date = info.data.get("start_date")
        if start_date and value < start_date:
            raise ValueError("end_date must be on or after start_date")
        return value


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tool_id: int
    borrower_id: int
    status: ReservationStatus
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime | None
    tool: ToolRead | None = None
    borrower: UserPublic | None = None


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    sender_id: int
    body: str
    created_at: datetime
    sender: UserPublic | None = None


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    reservation_id: int | None
    title: str
    body: str
    is_read: bool
    created_at: datetime


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)


class ReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    reviewer_id: int
    reviewee_id: int
    rating: int
    comment: str | None
    created_at: datetime
    reviewer: UserPublic | None = None
    reviewee: UserPublic | None = None


class DamageReportCreate(BaseModel):
    description: str = Field(min_length=5, max_length=2000)
    photo_url: str | None = Field(default=None, max_length=500)


class DamageReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int
    reporter_id: int
    description: str
    photo_url: str | None
    created_at: datetime


class SuspendUserRequest(BaseModel):
    is_suspended: bool


class ToolActivationRequest(BaseModel):
    is_active: bool
