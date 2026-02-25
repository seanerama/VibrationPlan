"""POST /api/analyze — file upload, classification pipeline, xlsx response."""

from __future__ import annotations

import io
import json
import logging
from collections import Counter
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.models.constants import ALL_TIERS
from app.models.database import get_db
from app.services.classification_engine import ClassificationEngine
from app.services.file_parser import (
    FileParser,
    FileTooLargeError,
    MissingColumnsError,
    UnsupportedFormatError,
)
from app.services.output_builder import OutputBuilder

logger = logging.getLogger(__name__)

router = APIRouter()

_XLSX_MEDIA_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


def _error(status: int, code: str, message: str, extra: Optional[dict] = None) -> JSONResponse:
    body: dict = {"error": True, "code": code, "message": message}
    if extra:
        body.update(extra)
    return JSONResponse(status_code=status, content=body)


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    customer_name: Optional[str] = Form(None),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    """Accept an RVTools or CloudPhysics .xlsx upload and return a classified report.

    Args:
        file: The uploaded .xlsx file.
        customer_name: Optional customer name to include in the report.
        db: SQLAlchemy session (injected).

    Returns:
        StreamingResponse with the branded xlsx report as the body and an
        ``X-Analysis-Summary`` header containing tier counts as JSON.

    Raises HTTP errors:
        400 UNRECOGNIZED_FORMAT: Not .xlsx or unrecognized column layout.
        400 MISSING_COLUMNS: Required columns absent.
        413 FILE_TOO_LARGE: File exceeds MAX_UPLOAD_SIZE_MB.
        500 PROCESSING_ERROR: Any unexpected exception.
    """
    file_bytes = await file.read()
    filename = file.filename or "upload.xlsx"

    # Size guard (FileParser also checks, but check early for a cleaner 413)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        return _error(
            413,
            "FILE_TOO_LARGE",
            f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB} MB limit.",
        )

    try:
        parser = FileParser()
        vm_rows = parser.parse(file_bytes, filename)
        logger.info(
            "File received: filename=%s, rows=%d", filename, len(vm_rows)
        )

        engine = ClassificationEngine(db)
        classified = engine.classify_all(vm_rows)

        counts: Counter = Counter(vm.classification_tier for vm in classified)
        summary = {
            "total": len(classified),
            **{tier: counts.get(tier, 0) for tier in ALL_TIERS},
        }
        logger.info("Classification complete: %s", summary)

        builder = OutputBuilder()
        output_bytes = builder.build(classified, customer_name)
        output_filename = OutputBuilder.build_filename(customer_name)

        return StreamingResponse(
            io.BytesIO(output_bytes),
            media_type=_XLSX_MEDIA_TYPE,
            headers={
                "Content-Disposition": f'attachment; filename="{output_filename}"',
                "X-Analysis-Summary": json.dumps(summary),
            },
        )

    except FileTooLargeError as exc:
        return _error(413, "FILE_TOO_LARGE", str(exc))
    except UnsupportedFormatError as exc:
        return _error(400, "UNRECOGNIZED_FORMAT", str(exc))
    except MissingColumnsError as exc:
        return _error(
            400,
            "MISSING_COLUMNS",
            str(exc),
            extra={"missing": exc.missing},
        )
    except Exception as exc:
        logger.exception("Unexpected error processing file: %s", filename)
        return _error(500, "PROCESSING_ERROR", f"An unexpected error occurred: {exc}")
