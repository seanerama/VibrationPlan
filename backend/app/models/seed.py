"""Database seed data for the VME compatibility matrix and migration paths.

Call seed_database(db) on app startup. It is idempotent — it skips seeding
when tables already contain rows.
"""

import logging

from sqlalchemy.orm import Session

from app.models.constants import (
    TIER_NEEDS_INFO,
    TIER_NEEDS_REVIEW,
    TIER_NOT_SUPPORTED,
    TIER_OFFICIALLY_SUPPORTED,
    TIER_SUPPORTED_VDI,
    TIER_UNOFFICIALLY_SUPPORTED,
)
from app.models.migration_paths import MigrationPath
from app.models.vme_matrix import VmeMatrix

logger = logging.getLogger(__name__)

_VME_MATRIX_SEED: list[dict] = [
    {
        "os_vendor": "Microsoft",
        "os_family": "Windows Server",
        "os_versions": "2016,2019,2022,2025",
        "classification_tier": TIER_OFFICIALLY_SUPPORTED,
        "notes": "HPE validated",
    },
    {
        "os_vendor": "Microsoft",
        "os_family": "Windows Server",
        "os_versions": "2012,2012 R2",
        "classification_tier": TIER_NEEDS_REVIEW,
        "notes": "End of support — check with customer",
    },
    {
        "os_vendor": "Microsoft",
        "os_family": "Windows Server",
        "os_versions": "2003,2008,2008 R2",
        "classification_tier": TIER_NOT_SUPPORTED,
        "notes": "Pre-KVM era",
    },
    {
        "os_vendor": "Microsoft",
        "os_family": "Windows Desktop",
        "os_versions": "10,11",
        "classification_tier": TIER_OFFICIALLY_SUPPORTED,
        "notes": "HPE validated",
    },
    {
        "os_vendor": "Microsoft",
        "os_family": "Windows Desktop",
        "os_versions": "XP,Vista,7,8,8.1",
        "classification_tier": TIER_NOT_SUPPORTED,
        "notes": "KVM incompatible",
    },
    {
        "os_vendor": "Red Hat",
        "os_family": "RHEL",
        "os_versions": "7,8,9",
        "classification_tier": TIER_OFFICIALLY_SUPPORTED,
        "notes": "HPE validated",
    },
    {
        "os_vendor": "Red Hat",
        "os_family": "RHEL",
        "os_versions": "6",
        "classification_tier": TIER_NEEDS_REVIEW,
        "notes": "End of life — verify kernel",
    },
    {
        "os_vendor": "Canonical",
        "os_family": "Ubuntu",
        "os_versions": "20.04,22.04,24.04",
        "classification_tier": TIER_OFFICIALLY_SUPPORTED,
        "notes": "HPE validated",
    },
    {
        "os_vendor": "Canonical",
        "os_family": "Ubuntu",
        "os_versions": "18.04",
        "classification_tier": TIER_UNOFFICIALLY_SUPPORTED,
        "notes": "KVM compatible, not HPE validated",
    },
    {
        "os_vendor": "SUSE",
        "os_family": "SLES",
        "os_versions": "12,15",
        "classification_tier": TIER_OFFICIALLY_SUPPORTED,
        "notes": "HPE validated",
    },
    {
        "os_vendor": "Debian",
        "os_family": "Debian",
        "os_versions": "10,11,12",
        "classification_tier": TIER_UNOFFICIALLY_SUPPORTED,
        "notes": "KVM compatible, not HPE validated",
    },
    {
        "os_vendor": "Fedora",
        "os_family": "Fedora",
        "os_versions": "37,38,39,40",
        "classification_tier": TIER_UNOFFICIALLY_SUPPORTED,
        "notes": "KVM compatible, not HPE validated",
    },
    {
        "os_vendor": "CentOS",
        "os_family": "CentOS",
        "os_versions": "7,8",
        "classification_tier": TIER_UNOFFICIALLY_SUPPORTED,
        "notes": "KVM compatible, not HPE validated",
    },
    {
        "os_vendor": "Oracle",
        "os_family": "Oracle Linux",
        "os_versions": "7,8,9",
        "classification_tier": TIER_OFFICIALLY_SUPPORTED,
        "notes": "HPE validated",
    },
    {
        "os_vendor": "ISV",
        "os_family": "Citrix Virtual Apps",
        "os_versions": "any",
        "classification_tier": TIER_SUPPORTED_VDI,
        "notes": "VDI workload",
    },
    {
        "os_vendor": "ISV",
        "os_family": "Omnissa Horizon",
        "os_versions": "any",
        "classification_tier": TIER_SUPPORTED_VDI,
        "notes": "VDI workload",
    },
    {
        "os_vendor": "ISV",
        "os_family": "HP Anyware",
        "os_versions": "any",
        "classification_tier": TIER_SUPPORTED_VDI,
        "notes": "VDI workload",
    },
    {
        "os_vendor": "Generic",
        "os_family": "Other Linux",
        "os_versions": "any",
        "classification_tier": TIER_NEEDS_INFO,
        "notes": "Too vague to classify",
    },
    {
        "os_vendor": "Generic",
        "os_family": "Unknown",
        "os_versions": "any",
        "classification_tier": TIER_NEEDS_INFO,
        "notes": "Insufficient OS data",
    },
    {
        "os_vendor": "Novell",
        "os_family": "NetWare",
        "os_versions": "any",
        "classification_tier": TIER_NOT_SUPPORTED,
        "notes": "Not KVM compatible",
    },
    {
        "os_vendor": "IBM",
        "os_family": "OS/2",
        "os_versions": "any",
        "classification_tier": TIER_NOT_SUPPORTED,
        "notes": "Not KVM compatible",
    },
    {
        "os_vendor": "Generic",
        "os_family": "DOS",
        "os_versions": "any",
        "classification_tier": TIER_NOT_SUPPORTED,
        "notes": "Not KVM compatible",
    },
]

_MIGRATION_PATHS_SEED: list[dict] = [
    {
        "classification_tier": TIER_OFFICIALLY_SUPPORTED,
        "os_family": None,
        "guidance_text": (
            "VM is HPE-validated and ready for migration to HPE VME with no OS changes required. "
            "Proceed with standard P2V migration tooling."
        ),
    },
    {
        "classification_tier": TIER_UNOFFICIALLY_SUPPORTED,
        "os_family": None,
        "guidance_text": (
            "OS is KVM-compatible but not HPE-validated. Migration is likely to succeed but HPE "
            "support coverage may be limited. Recommend testing in a non-production environment "
            "before full migration."
        ),
    },
    {
        "classification_tier": TIER_SUPPORTED_VDI,
        "os_family": None,
        "guidance_text": (
            "VM is running a validated VDI workload (Citrix, Omnissa Horizon, or HP Anyware) and "
            "is supported on HPE VME. Proceed with standard VDI migration procedures."
        ),
    },
    {
        "classification_tier": TIER_NEEDS_REVIEW,
        "os_family": None,
        "guidance_text": (
            "OS was identified but version information is ambiguous or incomplete. Review with "
            "customer to confirm exact OS version before making a migration recommendation."
        ),
    },
    {
        "classification_tier": TIER_NEEDS_INFO,
        "os_family": None,
        "guidance_text": (
            "Insufficient OS data to classify this VM. Gather additional information from the "
            "customer (exact OS name and version) and re-run analysis."
        ),
    },
    {
        "classification_tier": TIER_NOT_SUPPORTED,
        "os_family": None,
        "guidance_text": (
            "OS is not compatible with the KVM hypervisor underlying HPE VME. Options: "
            "(1) upgrade OS to a supported version before migration, "
            "(2) re-platform to a supported OS, or "
            "(3) retain on existing VMware infrastructure."
        ),
    },
]


def seed_database(db: Session) -> None:
    """Populate vme_matrix and migration_paths with initial data.

    Idempotent: skips seeding if either table already contains rows.
    """
    if db.query(VmeMatrix).count() == 0:
        db.bulk_insert_mappings(VmeMatrix, _VME_MATRIX_SEED)
        logger.info("Seeded vme_matrix with %d rows.", len(_VME_MATRIX_SEED))
    else:
        logger.debug("vme_matrix already populated — skipping seed.")

    if db.query(MigrationPath).count() == 0:
        db.bulk_insert_mappings(MigrationPath, _MIGRATION_PATHS_SEED)
        logger.info("Seeded migration_paths with %d rows.", len(_MIGRATION_PATHS_SEED))
    else:
        logger.debug("migration_paths already populated — skipping seed.")

    db.commit()
