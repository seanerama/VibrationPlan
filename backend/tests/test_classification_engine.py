"""Tests for ClassificationEngine — tier assignment, reasons, migration paths, errors."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.constants import (
    ALL_TIERS,
    TIER_COLORS,
    TIER_NEEDS_INFO,
    TIER_NEEDS_REVIEW,
    TIER_NOT_SUPPORTED,
    TIER_OFFICIALLY_SUPPORTED,
    TIER_SUPPORTED_VDI,
    TIER_UNOFFICIALLY_SUPPORTED,
)
from app.models.database import Base
from app.models.seed import seed_database
from app.services.classification_engine import ClassificationEngine, ClassifiedVM
from app.services.file_parser import VMRow


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_session():
    """In-memory SQLite session pre-loaded with seed data."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    seed_database(session)
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def engine(db_session) -> ClassificationEngine:
    return ClassificationEngine(db_session)


def _row(
    vm_name: str = "test-vm",
    os_primary: str = "",
    os_fallback: str = "",
    source: str = "rvtools",
    host_cluster: str = "Cluster-A",
) -> VMRow:
    return VMRow(
        vm_name=vm_name,
        host_cluster=host_cluster,
        os_raw_primary=os_primary,
        os_raw_fallback=os_fallback if os_fallback else None,
        source_format=source,
        row_index=2,
    )


# ---------------------------------------------------------------------------
# Tier assignment — one test per tier
# ---------------------------------------------------------------------------


def test_classify_windows_server_2022_returns_officially_supported(
    engine: ClassificationEngine,
) -> None:
    result = engine.classify_all([_row(os_primary="Microsoft Windows Server 2022 (64-bit)")])
    assert len(result) == 1
    assert result[0].classification_tier == TIER_OFFICIALLY_SUPPORTED


def test_classify_ubuntu_1804_returns_unofficially_supported(
    engine: ClassificationEngine,
) -> None:
    result = engine.classify_all([_row(os_primary="Ubuntu 18.04")])
    assert result[0].classification_tier == TIER_UNOFFICIALLY_SUPPORTED


def test_classify_citrix_returns_supported_vdi(engine: ClassificationEngine) -> None:
    result = engine.classify_all([_row(os_primary="Citrix Virtual Apps")])
    assert result[0].classification_tier == TIER_SUPPORTED_VDI


def test_classify_windows_server_2012_returns_needs_review(
    engine: ClassificationEngine,
) -> None:
    result = engine.classify_all([_row(os_primary="Microsoft Windows Server 2012 (64-bit)")])
    assert result[0].classification_tier == TIER_NEEDS_REVIEW


def test_classify_other_linux_returns_needs_info(engine: ClassificationEngine) -> None:
    result = engine.classify_all([_row(os_primary="Other Linux (64-bit)")])
    assert result[0].classification_tier == TIER_NEEDS_INFO


def test_classify_windows_xp_returns_not_supported(engine: ClassificationEngine) -> None:
    result = engine.classify_all(
        [_row(os_primary="Microsoft Windows XP Professional (32-bit)")]
    )
    assert result[0].classification_tier == TIER_NOT_SUPPORTED


def test_classify_empty_os_returns_needs_info(engine: ClassificationEngine) -> None:
    result = engine.classify_all([_row(os_primary="", os_fallback="")])
    assert result[0].classification_tier == TIER_NEEDS_INFO


def test_classify_low_confidence_os_returns_needs_info(
    engine: ClassificationEngine,
) -> None:
    result = engine.classify_all([_row(os_primary="????")])
    assert result[0].classification_tier == TIER_NEEDS_INFO


# ---------------------------------------------------------------------------
# Reason strings
# ---------------------------------------------------------------------------


def test_reason_contains_os_name_for_officially_supported(
    engine: ClassificationEngine,
) -> None:
    result = engine.classify_all([_row(os_primary="Microsoft Windows Server 2022 (64-bit)")])
    reason = result[0].classification_reason
    assert "Windows Server" in reason
    assert "2022" in reason


def test_reason_explains_kvm_incompatibility_for_not_supported(
    engine: ClassificationEngine,
) -> None:
    result = engine.classify_all(
        [_row(os_primary="Microsoft Windows XP Professional (32-bit)")]
    )
    reason = result[0].classification_reason
    assert "KVM" in reason or "not compatible" in reason


def test_reason_mentions_low_confidence_score(engine: ClassificationEngine) -> None:
    result = engine.classify_all([_row(os_primary="????")])
    reason = result[0].classification_reason
    assert "confidence" in reason.lower()


def test_reason_mentions_os_for_unofficially_supported(
    engine: ClassificationEngine,
) -> None:
    result = engine.classify_all([_row(os_primary="Ubuntu 18.04")])
    reason = result[0].classification_reason
    assert "Ubuntu" in reason


def test_reason_for_empty_os(engine: ClassificationEngine) -> None:
    result = engine.classify_all([_row(os_primary="")])
    assert "empty" in result[0].classification_reason.lower()


# ---------------------------------------------------------------------------
# Migration path
# ---------------------------------------------------------------------------


def test_migration_path_returned_for_all_tiers(db_session) -> None:
    """Every tier must have a non-empty migration path from the seeded data."""
    os_strings = {
        TIER_OFFICIALLY_SUPPORTED: "Microsoft Windows Server 2022 (64-bit)",
        TIER_UNOFFICIALLY_SUPPORTED: "Ubuntu 18.04",
        TIER_SUPPORTED_VDI: "Citrix Virtual Apps",
        TIER_NEEDS_REVIEW: "Microsoft Windows Server 2012 (64-bit)",
        TIER_NEEDS_INFO: "Other Linux (64-bit)",
        TIER_NOT_SUPPORTED: "Microsoft Windows XP Professional (32-bit)",
    }
    eng = ClassificationEngine(db_session)
    for tier, os_str in os_strings.items():
        result = eng.classify_all([_row(os_primary=os_str)])
        assert result[0].migration_path, f"Empty migration_path for tier {tier}"
        assert result[0].migration_path != "No migration guidance available for this classification."


def test_migration_path_fallback_when_no_os_family_match(db_session) -> None:
    """When no os_family-specific path exists, fall back to tier-level default."""
    eng = ClassificationEngine(db_session)
    result = eng.classify_all([_row(os_primary="Microsoft Windows Server 2022 (64-bit)")])
    # Seed data only has tier-level defaults (os_family=NULL); this verifies fallback works
    assert result[0].migration_path
    assert len(result[0].migration_path) > 20


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_batch_continues_when_single_row_errors(db_session) -> None:
    """A row that triggers an internal error must not abort the rest of the batch."""
    from unittest.mock import patch

    eng = ClassificationEngine(db_session)
    rows = [
        _row(vm_name="good-vm", os_primary="Microsoft Windows Server 2022 (64-bit)"),
        _row(vm_name="bad-vm", os_primary="Ubuntu 20.04"),
        _row(vm_name="also-good", os_primary="Red Hat Enterprise Linux 9 (64-bit)"),
    ]

    call_count = 0

    original_classify = eng._classify_one

    def boom_on_second(row):
        nonlocal call_count
        call_count += 1
        if row.vm_name == "bad-vm":
            raise RuntimeError("Simulated parse error")
        return original_classify(row)

    with patch.object(eng, "_classify_one", side_effect=boom_on_second):
        results = eng.classify_all(rows)

    assert len(results) == 3
    bad = next(r for r in results if r.vm_name == "bad-vm")
    assert bad.classification_tier == TIER_NEEDS_INFO


def test_error_row_gets_needs_info_tier(db_session) -> None:
    from unittest.mock import patch

    eng = ClassificationEngine(db_session)
    rows = [_row(vm_name="crash-vm", os_primary="Windows Server 2022")]

    with patch.object(
        eng, "_classify_one", side_effect=ValueError("forced crash")
    ):
        results = eng.classify_all(rows)

    assert results[0].classification_tier == TIER_NEEDS_INFO
    assert "Parse error" in results[0].classification_reason


def test_returns_correct_count_of_classified_vms(engine: ClassificationEngine) -> None:
    rows = [_row(vm_name=f"vm-{i}", os_primary="Windows Server 2022") for i in range(5)]
    results = engine.classify_all(rows)
    assert len(results) == 5


# ---------------------------------------------------------------------------
# Notes field
# ---------------------------------------------------------------------------


def test_notes_includes_low_confidence_warning(engine: ClassificationEngine) -> None:
    result = engine.classify_all([_row(os_primary="Other Linux (64-bit)")])
    assert result[0].notes is not None
    assert "confidence" in result[0].notes.lower()


def test_notes_includes_fallback_column_used_warning(engine: ClassificationEngine) -> None:
    result = engine.classify_all(
        [_row(os_primary="", os_fallback="Microsoft Windows Server 2019 (64-bit)")]
    )
    assert result[0].notes is not None
    assert "fallback" in result[0].notes.lower()


def test_notes_is_none_when_no_warnings(engine: ClassificationEngine) -> None:
    result = engine.classify_all(
        [_row(os_primary="Microsoft Windows Server 2022 (64-bit)")]
    )
    assert result[0].notes is None


# ---------------------------------------------------------------------------
# Color assignment
# ---------------------------------------------------------------------------


def test_classification_color_matches_tier_color_map(engine: ClassificationEngine) -> None:
    os_strings = [
        "Microsoft Windows Server 2022 (64-bit)",
        "Ubuntu 18.04",
        "Citrix Virtual Apps",
        "Other Linux (64-bit)",
        "Microsoft Windows XP Professional (32-bit)",
        "Microsoft Windows Server 2012 (64-bit)",
    ]
    rows = [_row(os_primary=s) for s in os_strings]
    results = engine.classify_all(rows)
    for r in results:
        assert r.classification_color == TIER_COLORS[r.classification_tier]


# ---------------------------------------------------------------------------
# Pipeline integration test (Stage 5 requirement)
# ---------------------------------------------------------------------------


def test_pipeline_rvtools_fixture(db_session) -> None:
    """Full pipeline: parse sample_rvtools.xlsx → classify → validate results."""
    from pathlib import Path

    from app.services.file_parser import FileParser

    fixture = Path(__file__).parent / "fixtures" / "sample_rvtools.xlsx"
    parser = FileParser()
    vm_rows = parser.parse(fixture.read_bytes(), "sample_rvtools.xlsx")

    eng = ClassificationEngine(db_session)
    results = eng.classify_all(vm_rows)

    # Count should match parsed rows (no silent drops)
    assert len(results) == len(vm_rows)

    # Every result must have a tier, color, reason, and migration path
    for r in results:
        assert r.classification_tier in ALL_TIERS
        assert r.classification_color.startswith("#")
        assert r.classification_reason
        assert r.migration_path

    # The fixture includes officially_supported and not_supported VMs
    tiers_seen = {r.classification_tier for r in results}
    assert TIER_OFFICIALLY_SUPPORTED in tiers_seen
    assert TIER_NOT_SUPPORTED in tiers_seen


def test_pipeline_cloudphysics_fixture(db_session) -> None:
    """Full pipeline: parse sample_cloudphysics.xlsx → classify → validate results."""
    from pathlib import Path

    from app.services.file_parser import FileParser

    fixture = Path(__file__).parent / "fixtures" / "sample_cloudphysics.xlsx"
    parser = FileParser()
    vm_rows = parser.parse(fixture.read_bytes(), "sample_cloudphysics.xlsx")

    eng = ClassificationEngine(db_session)
    results = eng.classify_all(vm_rows)

    assert len(results) == len(vm_rows)
    for r in results:
        assert r.classification_tier in ALL_TIERS
        # CloudPhysics has no fallback — os_raw_fallback is None
        assert r.os_raw is not None

    # cp-legacy-01 has Windows XP → not_supported
    legacy = next((r for r in results if "legacy" in r.vm_name), None)
    assert legacy is not None
    assert legacy.classification_tier == TIER_NOT_SUPPORTED


def test_pipeline_fallback_os_used_when_primary_empty(db_session) -> None:
    """app-dev-02 in the RVTools fixture has empty primary OS → uses fallback."""
    from pathlib import Path

    from app.services.file_parser import FileParser

    fixture = Path(__file__).parent / "fixtures" / "sample_rvtools.xlsx"
    parser = FileParser()
    vm_rows = parser.parse(fixture.read_bytes(), "sample_rvtools.xlsx")

    eng = ClassificationEngine(db_session)
    results = eng.classify_all(vm_rows)

    app_dev = next(r for r in results if r.vm_name == "app-dev-02")
    # Primary was empty; fallback "Microsoft Windows 10 (64-bit)" was used
    assert app_dev.notes is not None
    assert "fallback" in app_dev.notes.lower()
    # Windows 10 is officially_supported
    assert app_dev.classification_tier == TIER_OFFICIALLY_SUPPORTED


def test_pipeline_empty_os_vm_gets_needs_info(db_session) -> None:
    """unknown-vm-01 has both OS columns empty → needs_info."""
    from pathlib import Path

    from app.services.file_parser import FileParser

    fixture = Path(__file__).parent / "fixtures" / "sample_rvtools.xlsx"
    parser = FileParser()
    vm_rows = parser.parse(fixture.read_bytes(), "sample_rvtools.xlsx")

    eng = ClassificationEngine(db_session)
    results = eng.classify_all(vm_rows)

    unknown = next(r for r in results if r.vm_name == "unknown-vm-01")
    assert unknown.classification_tier == TIER_NEEDS_INFO
