"""Admin endpoints — VME matrix CRUD and migration path management."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.migration_paths import MigrationPath
from app.models.vme_matrix import VmeMatrix
from app.schemas import (
    MigrationPathResponse,
    MigrationPathUpdate,
    VmeMatrixCreate,
    VmeMatrixResponse,
    VmeMatrixUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _not_found(resource: str, id: int) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={
            "error": True,
            "code": "NOT_FOUND",
            "message": f"{resource} with id {id} not found.",
        },
    )


# ---------------------------------------------------------------------------
# VME Matrix endpoints
# ---------------------------------------------------------------------------


@router.get("/matrix", response_model=list[VmeMatrixResponse])
def get_matrix(db: Session = Depends(get_db)) -> list[VmeMatrix]:
    """Return all VME matrix entries."""
    return db.query(VmeMatrix).order_by(VmeMatrix.id).all()


@router.post("/matrix", response_model=VmeMatrixResponse, status_code=201)
def create_matrix_entry(
    payload: VmeMatrixCreate, db: Session = Depends(get_db)
) -> VmeMatrix:
    """Create a new VME matrix entry."""
    entry = VmeMatrix(**payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    logger.info("Created matrix entry id=%d os_family=%s", entry.id, entry.os_family)
    return entry


@router.put("/matrix/{entry_id}", response_model=VmeMatrixResponse)
def update_matrix_entry(
    entry_id: int, payload: VmeMatrixUpdate, db: Session = Depends(get_db)
) -> VmeMatrix | JSONResponse:
    """Update an existing VME matrix entry."""
    entry = db.get(VmeMatrix, entry_id)
    if entry is None:
        return _not_found("Matrix entry", entry_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)
    db.commit()
    db.refresh(entry)
    logger.info("Updated matrix entry id=%d", entry_id)
    return entry


@router.delete("/matrix/{entry_id}", status_code=204)
def delete_matrix_entry(
    entry_id: int, db: Session = Depends(get_db)
) -> Response:
    """Delete a VME matrix entry."""
    entry = db.get(VmeMatrix, entry_id)
    if entry is None:
        return _not_found("Matrix entry", entry_id)

    db.delete(entry)
    db.commit()
    logger.info("Deleted matrix entry id=%d", entry_id)
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Migration path endpoints
# ---------------------------------------------------------------------------


@router.get("/migration-paths", response_model=list[MigrationPathResponse])
def get_migration_paths(db: Session = Depends(get_db)) -> list[MigrationPath]:
    """Return all migration path entries."""
    return db.query(MigrationPath).order_by(MigrationPath.id).all()


@router.put("/migration-paths/{path_id}", response_model=MigrationPathResponse)
def update_migration_path(
    path_id: int, payload: MigrationPathUpdate, db: Session = Depends(get_db)
) -> MigrationPath | JSONResponse:
    """Update the guidance_text of a migration path entry."""
    path = db.get(MigrationPath, path_id)
    if path is None:
        return _not_found("Migration path", path_id)

    path.guidance_text = payload.guidance_text
    db.commit()
    db.refresh(path)
    logger.info("Updated migration path id=%d tier=%s", path_id, path.classification_tier)
    return path
