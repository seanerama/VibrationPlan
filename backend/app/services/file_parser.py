"""File parser service — detects RVTools/CloudPhysics format and extracts VM rows."""

import logging
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class FileParserError(Exception):
    """Base exception for file parsing errors."""


class UnsupportedFormatError(FileParserError):
    """File format not recognized or unsupported."""


class MissingColumnsError(FileParserError):
    """Required columns are absent from the file."""

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(f"Missing required columns: {missing}")


class FileTooLargeError(FileParserError):
    """File exceeds the configured size limit."""


# ---------------------------------------------------------------------------
# Data contract
# ---------------------------------------------------------------------------


@dataclass
class VMRow:
    """Structured representation of a single VM record from an uploaded inventory file."""

    vm_name: str
    host_cluster: Optional[str]
    os_raw_primary: str  # Never None — empty string when missing
    os_raw_fallback: Optional[str]  # RVTools only; None for CloudPhysics
    source_format: str  # "rvtools" | "cloudphysics"
    row_index: int  # 1-based Excel row number


# ---------------------------------------------------------------------------
# Column signatures used for format detection
# ---------------------------------------------------------------------------

_RVTOOLS_SIGNATURE = {"VM", "Powerstate", "OS according to VMware Tools"}
_CLOUDPHYSICS_SIGNATURE = {"VM Name", "Guest OS"}

_RVTOOLS_REQUIRED = {
    "VM",
    "OS according to VMware Tools",
    "OS according to configuration file",
}
_CLOUDPHYSICS_REQUIRED = {"VM Name", "Guest OS"}

_RVTOOLS_TARGET_SHEET = "vInfo"


# ---------------------------------------------------------------------------
# FileParser
# ---------------------------------------------------------------------------


class FileParser:
    """Parses RVTools and CloudPhysics .xlsx exports into structured VMRow lists."""

    def parse(self, file_bytes: bytes, filename: str) -> list[VMRow]:
        """Parse an uploaded xlsx file and return a list of VMRow objects.

        Args:
            file_bytes: Raw bytes of the uploaded file.
            filename: Original filename (used for extension validation).

        Returns:
            List of VMRow objects, one per non-blank VM in the file.

        Raises:
            FileTooLargeError: If file exceeds MAX_UPLOAD_SIZE_MB.
            UnsupportedFormatError: If file is not .xlsx or not RVTools/CloudPhysics.
            MissingColumnsError: If required columns are absent.
        """
        self._validate_extension(filename)
        self._validate_size(file_bytes, filename)

        excel = pd.ExcelFile(BytesIO(file_bytes), engine="openpyxl")
        detected_format = self._detect_format(excel, filename)

        if detected_format == "rvtools":
            rows = self._extract_rvtools(excel, filename)
        else:
            rows = self._extract_cloudphysics(excel, filename)

        logger.info(
            "File upload received: format=%s, rows=%d, filename=%s",
            detected_format,
            len(rows),
            filename,
        )
        return rows

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_extension(self, filename: str) -> None:
        """Raise UnsupportedFormatError if filename does not end with .xlsx."""
        if not filename.lower().endswith(".xlsx"):
            raise UnsupportedFormatError(
                f"Unsupported file type: '{filename}'. Only .xlsx files are accepted."
            )

    def _validate_size(self, file_bytes: bytes, filename: str) -> None:
        """Raise FileTooLargeError if file exceeds the configured max size."""
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise FileTooLargeError(
                f"File '{filename}' exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB size limit."
            )

    # ------------------------------------------------------------------
    # Format detection
    # ------------------------------------------------------------------

    def _detect_format(self, excel: pd.ExcelFile, filename: str) -> str:
        """Return 'rvtools' or 'cloudphysics'; raise UnsupportedFormatError otherwise."""
        # Check for RVTools: prefer vInfo sheet, fall back to scanning all sheets
        candidate_sheet = self._find_rvtools_sheet(excel)
        if candidate_sheet is not None:
            cols = set(pd.read_excel(excel, sheet_name=candidate_sheet, nrows=0).columns)
            if _RVTOOLS_SIGNATURE.issubset(cols):
                return "rvtools"

        # Check for CloudPhysics: first sheet
        first_sheet = excel.sheet_names[0]
        cols = set(pd.read_excel(excel, sheet_name=first_sheet, nrows=0).columns)
        if _CLOUDPHYSICS_SIGNATURE.issubset(cols) and not _RVTOOLS_SIGNATURE.issubset(cols):
            return "cloudphysics"

        raise UnsupportedFormatError(
            f"'{filename}' does not match RVTools or CloudPhysics format. "
            "Ensure you are uploading a valid RVTools vInfo export or a CloudPhysics VM export."
        )

    def _find_rvtools_sheet(self, excel: pd.ExcelFile) -> Optional[str]:
        """Return the name of the best candidate sheet for RVTools data."""
        if _RVTOOLS_TARGET_SHEET in excel.sheet_names:
            return _RVTOOLS_TARGET_SHEET
        # Fall back: scan all sheets for the signature columns
        for sheet in excel.sheet_names:
            cols = set(pd.read_excel(excel, sheet_name=sheet, nrows=0).columns)
            if _RVTOOLS_SIGNATURE.issubset(cols):
                return sheet
        return None

    # ------------------------------------------------------------------
    # RVTools extraction
    # ------------------------------------------------------------------

    def _extract_rvtools(self, excel: pd.ExcelFile, filename: str) -> list[VMRow]:
        """Extract VMRow list from an RVTools export."""
        sheet = self._find_rvtools_sheet(excel)
        df = pd.read_excel(excel, sheet_name=sheet, dtype=str)

        # Validate required columns
        missing = [c for c in _RVTOOLS_REQUIRED if c not in df.columns]
        if missing:
            raise MissingColumnsError(missing)

        rows: list[VMRow] = []
        for excel_row_idx, (_, row) in enumerate(df.iterrows(), start=2):
            vm_name = self._clean(row.get("VM"))
            if not vm_name:
                continue

            os_primary = self._clean(row.get("OS according to VMware Tools"))
            os_fallback = self._clean(row.get("OS according to configuration file"))

            host_cluster = self._clean(row.get("Cluster") or row.get("Host"))

            if not os_primary and not os_fallback:
                logger.warning(
                    "VM row %d: both OS columns empty — will be classified as Needs Info",
                    excel_row_idx,
                )

            rows.append(
                VMRow(
                    vm_name=vm_name,
                    host_cluster=host_cluster if host_cluster else None,
                    os_raw_primary=os_primary,
                    os_raw_fallback=os_fallback,
                    source_format="rvtools",
                    row_index=excel_row_idx,
                )
            )

        return rows

    # ------------------------------------------------------------------
    # CloudPhysics extraction
    # ------------------------------------------------------------------

    def _extract_cloudphysics(self, excel: pd.ExcelFile, filename: str) -> list[VMRow]:
        """Extract VMRow list from a CloudPhysics export."""
        first_sheet = excel.sheet_names[0]
        df = pd.read_excel(excel, sheet_name=first_sheet, dtype=str)

        missing = [c for c in _CLOUDPHYSICS_REQUIRED if c not in df.columns]
        if missing:
            raise MissingColumnsError(missing)

        rows: list[VMRow] = []
        for excel_row_idx, (_, row) in enumerate(df.iterrows(), start=2):
            vm_name = self._clean(row.get("VM Name"))
            if not vm_name:
                continue

            os_primary = self._clean(row.get("Guest OS"))
            host_cluster = self._clean(row.get("Cluster"))

            rows.append(
                VMRow(
                    vm_name=vm_name,
                    host_cluster=host_cluster if host_cluster else None,
                    os_raw_primary=os_primary,
                    os_raw_fallback=None,
                    source_format="cloudphysics",
                    row_index=excel_row_idx,
                )
            )

        return rows

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @staticmethod
    def _clean(value: object) -> str:
        """Coerce a cell value to a stripped string; return '' for null/NaN."""
        if value is None:
            return ""
        s = str(value).strip()
        return "" if s.lower() == "nan" else s
