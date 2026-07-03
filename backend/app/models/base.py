# Declarative Base + shared mixins (UUIDv7 pk, created_at/updated_at).
import uuid 
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import uuid7 

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