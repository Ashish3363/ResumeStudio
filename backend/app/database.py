"""
app/database.py
===============

The database foundation shared by every feature.

Two layers live here:

1. ORM base + mixins
   - `Base`          : the SQLAlchemy 2.0 declarative base every model extends.
                       `Base.metadata` is what Alembic diffs to autogenerate
                       migrations.
   - `UUIDMixin`     : a UUIDv7 primary key (`id`).
   - `TimestampMixin`: `created_at` / `updated_at`, maintained by the DB.

2. Runtime connection machinery
   - `engine`       : the connection pool, built from settings.DATABASE_URL.
   - `SessionLocal` : a factory that produces a new Session per request.
   - `get_db`       : a FastAPI dependency that yields a Session and always
                      closes it afterwards.
   - `SessionDep`   : a typing alias so routes can write `db: SessionDep`
                      instead of repeating `Depends(get_db)`.

A "session" is a single unit of work / transaction. The rule of thumb: one
session per HTTP request. `get_db` enforces that lifecycle.
"""

import uuid
from datetime import datetime
from typing import Annotated, Iterator

from fastapi import Depends
from sqlalchemy import DateTime, create_engine, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)
from uuid6 import uuid7

from app.config import settings


# ---------------------------------------------------------------------------
# ORM base + shared mixins
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """All ORM models inherit from this. `Base.metadata` is what Alembic reads."""

    pass


class UUIDMixin:
    """Adds a UUIDv7 primary key. v7 is time-ordered, so rows sort roughly by
    creation time — nicer for indexes than random UUIDv4."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid7)


class TimestampMixin:
    """Adds DB-managed `created_at` / `updated_at` timestamps.

    `server_default=func.now()` and `onupdate=func.now()` mean the *database*
    stamps these, so they're correct even if a row is written outside the app.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )


# ---------------------------------------------------------------------------
# Engine / Session / dependency
# ---------------------------------------------------------------------------
# The engine owns the connection pool. It's created once, at import time, and
# shared for the whole process.
engine = create_engine(
    settings.DATABASE_URL,
    # Neon (and any cloud Postgres) will silently drop idle connections.
    # pool_pre_ping issues a lightweight check before handing out a connection
    # and transparently reconnects, so we don't hit "server closed the
    # connection" errors after the app has been idle.
    pool_pre_ping=True,
    future=True,
)

# Factory for per-request sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,      # we flush explicitly in repositories; no surprise writes
    autocommit=False,     # transactions are committed explicitly in the service layer
    expire_on_commit=False,  # keep object attributes readable after commit(), so a
                             # route can still return the freshly-saved User
)


def get_db() -> Iterator[Session]:
    """FastAPI dependency that provides a database session for one request.

    Yields a session, then guarantees it's closed once the request finishes —
    even if the handler raises. Use it in routes/deps via `Depends(get_db)` or
    the `SessionDep` alias below.

    Yields:
        Session: an open SQLAlchemy session bound to the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Reusable typing alias: write `db: SessionDep` in a route signature and
# FastAPI injects a session. Cleaner than repeating `Depends(get_db)`.
SessionDep = Annotated[Session, Depends(get_db)]
