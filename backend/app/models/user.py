# users table ORM model (auth, plan, token_version).

from __future__ import annotations
from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.career_profile import CareerProfile
    
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
    career_profile: Mapped["CareerProfile | None"]= relationship(
        back_populates="user",
        uselist=False,                       # 1:1 → single object, not a list
        cascade="all, delete-orphan",        # ORM-side cascade to match the DB
        passive_deletes=True,                # let the DB's ON DELETE CASCADE do the work
    )