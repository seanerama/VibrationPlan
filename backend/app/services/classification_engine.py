"""Classification Engine — orchestrates the full VM classification pipeline.

Pipeline per VM:
    VMRow → OS string selection → OSNormalizer → matrix query → tier assignment
          → reason generation → migration path lookup → ClassifiedVM
"""

import logging
from collections import Counter
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import null
from sqlalchemy.orm import Session

from app.models.constants import (
    TIER_COLORS,
    TIER_NEEDS_INFO,
    TIER_NEEDS_REVIEW,
    TIER_NOT_SUPPORTED,
    TIER_OFFICIALLY_SUPPORTED,
    TIER_SUPPORTED_VDI,
    TIER_UNOFFICIALLY_SUPPORTED,
)
from app.models.migration_paths import MigrationPath
from app.models.vme_matrix import VmeMatrix
from app.services.file_parser import VMRow
from app.services.os_normalizer import NormalizedOS, OSNormalizer

logger = logging.getLogger(__name__)

# OS families that are KVM-compatible but not HPE-validated → unofficially_supported
_UNOFFICIALLY_SUPPORTED_FAMILIES = {
    "Ubuntu",
    "Debian",
    "Fedora",
    "CentOS",
    "FreeBSD",
}

# OS families that are definitively KVM-incompatible → not_supported
_NOT_SUPPORTED_FAMILIES = {
    "DOS",
    "OS/2",
    "NetWare",
    "Solaris",
}

# OS families that represent VDI workloads → supported_vdi
_VDI_FAMILIES = {
    "Citrix Virtual Apps",
    "Omnissa Horizon",
    "HP Anyware",
}

_NO_GUIDANCE = "No migration guidance available for this classification."


# ---------------------------------------------------------------------------
# Output contract
# ---------------------------------------------------------------------------


@dataclass
class ClassifiedVM:
    """Fully classified VM record — output contract for Stage 6 Output Builder."""

    # Pass-through from VMRow
    vm_name: str
    host_cluster: Optional[str]
    os_raw: str  # The actual OS string used for classification

    # From OSNormalizer
    os_interpreted: str

    # Classification outputs
    classification_tier: str  # One of the 6 TIER_* constants
    classification_color: str  # Hex from TIER_COLORS
    classification_reason: str
    migration_path: str
    notes: Optional[str]  # Low-confidence warning, fallback-column notice, errors


# ---------------------------------------------------------------------------
# Classification Engine
# ---------------------------------------------------------------------------


class ClassificationEngine:
    """Classifies a list of VMRow objects against the HPE VME compatibility matrix.

    Args:
        db: SQLAlchemy session used for matrix and migration path queries.
        normalizer: OSNormalizer instance (injected for testability).
    """

    def __init__(self, db: Session, normalizer: Optional[OSNormalizer] = None) -> None:
        self._db = db
        self._normalizer = normalizer or OSNormalizer()

    def classify_all(self, vm_rows: list[VMRow]) -> list[ClassifiedVM]:
        """Classify every VM in the list.

        Row-level errors never abort the batch — any failing VM receives a
        needs_info tier with an explanatory reason string.

        Args:
            vm_rows: Parsed VM rows from FileParser.

        Returns:
            List of ClassifiedVM, same length as vm_rows.
        """
        results: list[ClassifiedVM] = []

        for row in vm_rows:
            try:
                results.append(self._classify_one(row))
            except Exception as exc:
                logger.warning("Error classifying VM %r: %s", row.vm_name, exc)
                results.append(
                    ClassifiedVM(
                        vm_name=row.vm_name,
                        host_cluster=row.host_cluster,
                        os_raw=row.os_raw_primary or "",
                        os_interpreted="Unknown",
                        classification_tier=TIER_NEEDS_INFO,
                        classification_color=TIER_COLORS[TIER_NEEDS_INFO],
                        classification_reason=f"Parse error: {exc}",
                        migration_path=self._get_migration_path(TIER_NEEDS_INFO, None),
                        notes=None,
                    )
                )

        tier_counts = Counter(r.classification_tier for r in results)
        logger.info(
            "Classification complete: %d VMs — %s", len(results), dict(tier_counts)
        )
        return results

    # ------------------------------------------------------------------
    # Single-VM classification
    # ------------------------------------------------------------------

    def _classify_one(self, row: VMRow) -> ClassifiedVM:
        """Classify a single VMRow and return a ClassifiedVM."""
        os_raw, used_fallback = self._select_os_string(row)
        normalized = self._normalizer.normalize(os_raw)
        tier, reason = self._assign_tier(normalized, os_raw)
        migration_path = self._get_migration_path(tier, normalized.os_family)
        notes = self._build_notes(normalized, used_fallback)

        return ClassifiedVM(
            vm_name=row.vm_name,
            host_cluster=row.host_cluster,
            os_raw=os_raw,
            os_interpreted=normalized.os_interpreted,
            classification_tier=tier,
            classification_color=TIER_COLORS[tier],
            classification_reason=reason,
            migration_path=migration_path,
            notes=notes,
        )

    # ------------------------------------------------------------------
    # OS string selection
    # ------------------------------------------------------------------

    @staticmethod
    def _select_os_string(row: VMRow) -> tuple[str, bool]:
        """Return (os_string_to_use, used_fallback).

        RVTools: prefer primary; fall back to fallback when primary is empty.
        CloudPhysics: always primary (fallback is None).
        """
        if row.os_raw_primary:
            return row.os_raw_primary, False
        if row.os_raw_fallback:
            return row.os_raw_fallback, True
        return "", False

    # ------------------------------------------------------------------
    # Tier assignment
    # ------------------------------------------------------------------

    def _assign_tier(
        self, normalized: NormalizedOS, os_raw: str
    ) -> tuple[str, str]:
        """Apply the 7-step decision tree and return (tier, reason)."""

        # 1. Empty / low-confidence → needs_info
        if not os_raw.strip():
            return TIER_NEEDS_INFO, "OS string is empty — insufficient data to classify"

        if normalized.low_confidence:
            return (
                TIER_NEEDS_INFO,
                f"Low confidence OS match (score: {normalized.confidence:.2f}) — "
                f"insufficient data to classify '{os_raw}'",
            )

        family = normalized.os_family
        version = normalized.os_version
        interpreted = normalized.os_interpreted

        # 2. VDI workload families → supported_vdi (checked before matrix query)
        if family in _VDI_FAMILIES:
            return (
                TIER_SUPPORTED_VDI,
                f"{interpreted} is a validated VDI workload on HPE VME",
            )

        # 3. Query the VME matrix
        matrix_entry = self._query_matrix(normalized, os_raw)

        if matrix_entry is not None:
            entry_tier = matrix_entry.classification_tier

            if entry_tier == TIER_OFFICIALLY_SUPPORTED:
                return (
                    TIER_OFFICIALLY_SUPPORTED,
                    f"Matched {interpreted} — HPE validated in VME matrix",
                )

            if entry_tier == TIER_UNOFFICIALLY_SUPPORTED:
                return (
                    TIER_UNOFFICIALLY_SUPPORTED,
                    f"{interpreted} is KVM-compatible but not HPE-validated",
                )

            if entry_tier == TIER_NEEDS_REVIEW:
                return (
                    TIER_NEEDS_REVIEW,
                    f"OS version ambiguous for {interpreted} — verify exact version with customer",
                )

            if entry_tier == TIER_NOT_SUPPORTED:
                return (
                    TIER_NOT_SUPPORTED,
                    f"{interpreted} is not compatible with the KVM hypervisor underlying HPE VME",
                )

            if entry_tier == TIER_NEEDS_INFO:
                return (
                    TIER_NEEDS_INFO,
                    f"OS string '{os_raw}' lacks sufficient detail for classification",
                )

            if entry_tier == TIER_SUPPORTED_VDI:
                return (
                    TIER_SUPPORTED_VDI,
                    f"{interpreted} is a validated VDI workload on HPE VME",
                )

        # 4. No matrix match — apply fallback rules based on known family sets

        if family in _NOT_SUPPORTED_FAMILIES:
            return (
                TIER_NOT_SUPPORTED,
                f"{interpreted} is not compatible with the KVM hypervisor underlying HPE VME",
            )

        if family in _UNOFFICIALLY_SUPPORTED_FAMILIES:
            return (
                TIER_UNOFFICIALLY_SUPPORTED,
                f"{interpreted} is KVM-compatible but not HPE-validated",
            )

        # 5. OS was recognised but no version info → needs_review
        if family and not version:
            return (
                TIER_NEEDS_REVIEW,
                f"OS family '{family}' identified but version is missing — "
                "review with customer to confirm",
            )

        # 6. OS was recognised with a version but no matrix entry found → needs_review
        if family and version:
            return (
                TIER_NEEDS_REVIEW,
                f"OS version ambiguous for {interpreted} — verify exact version with customer",
            )

        # 7. Catch-all → needs_info
        return (
            TIER_NEEDS_INFO,
            f"OS string '{os_raw}' lacks sufficient detail for classification",
        )

    # ------------------------------------------------------------------
    # Database helpers
    # ------------------------------------------------------------------

    def _query_matrix(
        self, normalized: NormalizedOS, os_raw: str = ""
    ) -> Optional[VmeMatrix]:
        """Return the best matching VmeMatrix entry for the normalised OS, or None.

        Matching priority:
        1. Extracted numeric version found in entry's os_versions list.
        2. Any version token from entry's os_versions list found in the raw OS string
           (handles non-numeric versions like "XP", "Vista").
        3. First entry for the family (family-level fallback).
        """
        if not normalized.os_family:
            return None

        entries = (
            self._db.query(VmeMatrix)
            .filter(VmeMatrix.os_family == normalized.os_family)
            .all()
        )

        if not entries:
            return None

        version = normalized.os_version
        raw_lower = os_raw.lower()

        # Pass 1: match by extracted numeric version
        if version:
            for entry in entries:
                versions = [v.strip() for v in entry.os_versions.split(",")]
                if version in versions or "any" in versions:
                    return entry

        # Pass 2: scan each entry's version tokens against the raw OS string
        # (catches non-numeric tokens like "XP", "Vista", "ME")
        for entry in entries:
            version_tokens = [v.strip().lower() for v in entry.os_versions.split(",")]
            if "any" in version_tokens:
                return entry
            if raw_lower and any(tok and tok in raw_lower for tok in version_tokens):
                return entry

        # Pass 3: family-level fallback — return first entry
        return entries[0]

    def _get_migration_path(self, tier: str, os_family: Optional[str]) -> str:
        """Return guidance text for the given tier, with os_family fallback to tier default."""
        if os_family:
            specific = (
                self._db.query(MigrationPath)
                .filter(
                    MigrationPath.classification_tier == tier,
                    MigrationPath.os_family == os_family,
                )
                .first()
            )
            if specific:
                return specific.guidance_text

        default = (
            self._db.query(MigrationPath)
            .filter(
                MigrationPath.classification_tier == tier,
                MigrationPath.os_family == null(),
            )
            .first()
        )
        return default.guidance_text if default else _NO_GUIDANCE

    # ------------------------------------------------------------------
    # Notes field
    # ------------------------------------------------------------------

    @staticmethod
    def _build_notes(normalized: NormalizedOS, used_fallback: bool) -> Optional[str]:
        """Build the notes string from edge-case flags."""
        parts: list[str] = []
        if normalized.low_confidence:
            parts.append(f"Low confidence match: {normalized.confidence:.2f}")
        if used_fallback:
            parts.append("Primary OS empty — used fallback column")
        return "; ".join(parts) if parts else None
