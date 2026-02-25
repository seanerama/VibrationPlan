"""ORM model for the vme_matrix table."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class VmeMatrix(Base):
    """Maps OS families and versions to a VME compatibility classification tier."""

    __tablename__ = "vme_matrix"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    os_vendor: Mapped[str] = mapped_column(String(100), nullable=False)
    os_family: Mapped[str] = mapped_column(String(100), nullable=False)
    os_versions: Mapped[str] = mapped_column(String(500), nullable=False)  # comma-separated
    classification_tier: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return (
            f"<VmeMatrix id={self.id} os_vendor={self.os_vendor!r} "
            f"os_family={self.os_family!r} tier={self.classification_tier!r}>"
        )
