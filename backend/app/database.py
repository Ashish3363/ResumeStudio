# SQLAlchemy 2.0 declarative Base, shared mixins, engine, SessionLocal, and get_db dependency.
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid6 import uuid7


class Base(DeclarativeBase):
    """ All ORM models inherits from this. `Base.metadata` is what Alembic reads."""
    pass


class UUIDMixin:     #Reusable class
    id: Mapped[uuid.UUID]=mapped_column(primary_key=True, default=uuid7)


class TimestampMixin:
    created_at:Mapped[datetime]=mapped_column(
          DateTime(timezone=True), server_default=func.now(), nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,
    )


# --- Engine / SessionLocal / get_db dependency ---
# TODO (unchanged from scaffold): build the SQLAlchemy 2.0 engine from
# settings.DATABASE_URL, a SessionLocal factory, and a get_db() FastAPI
# dependency here. Left as a stub so this refactor stays reorganization-only.
