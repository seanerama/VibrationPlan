"""ORM model for the migration_paths table."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class MigrationPath(Base):
    """Stores migration guidance text keyed by classification tier and optional OS family."""

    __tablename__ = "migration_paths"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    classification_tier: Mapped[str] = mapped_column(String(50), nullable=False)
    # NULL means this row is the tier-level default (applies to all OS families in the tier)
    os_family: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    guidance_text: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<MigrationPath id={self.id} tier={self.classification_tier!r} "
            f"os_family={self.os_family!r}>"
        )
