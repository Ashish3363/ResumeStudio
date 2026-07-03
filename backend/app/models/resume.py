# resumes table ORM model (saved tailored resumes; flat, 10/user FIFO).

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.job_description import JobDescription
    from app.models.user import User


class Resume(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False,
    )
    job_description_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="SET NULL"), index=True,
    )
    resume_name: Mapped[str] = mapped_column(String(255), nullable=False)

    resume_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    changes_summary: Mapped[dict | None] = mapped_column(JSONB)
    match_report: Mapped[dict | None] = mapped_column(JSONB)

    pdf_url: Mapped[str | None] = mapped_column(String)
    ats_score: Mapped[int | None] = mapped_column(Integer)
    overall_match_score: Mapped[int | None] = mapped_column(Integer)

    user: Mapped["User"] = relationship()
    job_description: Mapped["JobDescription | None"] = relationship()
