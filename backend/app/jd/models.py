# job_descriptions table ORM model (raw + parsed_jd_json).

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.users.models import User


class JobDescription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_descriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False,
    )
    company_name: Mapped[str | None] = mapped_column(String(255))
    job_title: Mapped[str | None] = mapped_column(String(255))
    jd_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_jd_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    user: Mapped["User"] = relationship()
