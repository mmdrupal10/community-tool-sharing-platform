"""Database configuration for the data layer.

The course requires PostgreSQL. Tests can override DATABASE_URL with SQLite so
business rules can be tested quickly without a running database server.
"""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://toolshare:toolshare@localhost:5432/toolshare",
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_db():
    """FastAPI dependency that gives each request its own database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
