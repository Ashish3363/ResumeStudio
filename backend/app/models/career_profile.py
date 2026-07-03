# career_profiles table ORM model (1:1 with user; profile_json master pool).

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User


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