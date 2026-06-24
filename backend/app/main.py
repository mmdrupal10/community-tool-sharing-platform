"""FastAPI entry point for the Community Tool Sharing Platform."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401 - imports models so metadata is registered.
from .database import Base, engine
from .routers import (
    admin,
    auth,
    damage_reports,
    invitations,
    messages,
    notifications,
    reservations,
    reviews,
    tools,
    users,
)

app = FastAPI(
    title="Community Tool Sharing Platform API",
    description="ICS 613 Neighborhood Tool Sharing backend built with FastAPI.",
    version="0.1.0",
)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Create tables for a simple class-project deployment.

    A production application would use Alembic migrations instead.
    """

    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Community Tool Sharing Platform API"}


app.include_router(auth.router)
app.include_router(invitations.router)
app.include_router(users.router)
app.include_router(tools.router)
app.include_router(reservations.router)
app.include_router(messages.router)
app.include_router(notifications.router)
app.include_router(reviews.router)
app.include_router(damage_reports.router)
app.include_router(admin.router)
