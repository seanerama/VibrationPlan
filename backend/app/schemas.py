"""Pydantic request/response schemas for the VME Compatibility Analyzer API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict  # noqa: F401 (ConfigDict used in model_config)

# ---------------------------------------------------------------------------
# VME Matrix schemas
# ---------------------------------------------------------------------------


class VmeMatrixCreate(BaseModel):
    """Fields required to create a new VME matrix entry."""

    os_vendor: str
    os_family: str
    os_versions: str
    classification_tier: str
    notes: Optional[str] = None


class VmeMatrixUpdate(BaseModel):
    """Fields that can be updated on a VME matrix entry (all optional)."""

    os_vendor: Optional[str] = None
    os_family: Optional[str] = None
    os_versions: Optional[str] = None
    classification_tier: Optional[str] = None
    notes: Optional[str] = None


class VmeMatrixResponse(VmeMatrixCreate):
    """Full VME matrix entry including server-assigned fields."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime


# ---------------------------------------------------------------------------
# Migration path schemas
# ---------------------------------------------------------------------------


class MigrationPathUpdate(BaseModel):
    """Only guidance_text may be updated on a migration path entry."""

    guidance_text: str


class MigrationPathResponse(BaseModel):
    """Full migration path entry."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    classification_tier: str
    os_family: Optional[str] = None
    guidance_text: str
    updated_at: datetime


# ---------------------------------------------------------------------------
# Error response schema
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Structured JSON error body returned on 4xx/5xx responses."""

    error: bool = True
    code: str
    message: str


# ---------------------------------------------------------------------------
# Analysis summary schema (serialized into X-Analysis-Summary header)
# ---------------------------------------------------------------------------


class AnalysisSummary(BaseModel):
    """Summary counts by classification tier, included as a response header."""

    total: int
    officially_supported: int
    unofficially_supported: int
    supported_vdi: int
    needs_review: int
    needs_info: int
    not_supported: int
