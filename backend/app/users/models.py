# users + career_profiles table ORM models
#   User          — auth, plan, token_version
#   CareerProfile — 1:1 with user; profile_json master truth pool

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    full_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false"), nullable=False,
    )
    profile_picture: Mapped[str | None] = mapped_column(String)
    token_version: Mapped[int] = mapped_column(
        Integer, default=0, server_default=text("0"), nullable=False,
    )
    plan: Mapped[str] = mapped_column(
        String(20), default="free", server_default=text("'free'"), nullable=False,
    )
    career_profile: Mapped["CareerProfile | None"] = relationship(
        back_populates="user",
        uselist=False,                       # 1:1 → single object, not a list
        cascade="all, delete-orphan",        # ORM-side cascade to match the DB
        passive_deletes=True,                # let the DB's ON DELETE CASCADE do the work
    )


class CareerProfile(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "career_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,          # UNIQUE → enforces 1:1 with users
        index=True,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255))
    profile_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    user: Mapped["User"] = relationship(back_populates="career_profile")
