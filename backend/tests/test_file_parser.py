"""Tests for FileParser — format detection, extraction, and error handling."""

from pathlib import Path

import pytest

from app.services.file_parser import (
    FileTooLargeError,
    FileParser,
    MissingColumnsError,
    UnsupportedFormatError,
    VMRow,
)

FIXTURES = Path(__file__).parent / "fixtures"

RVTOOLS_BYTES = (FIXTURES / "sample_rvtools.xlsx").read_bytes()
CLOUDPHYSICS_BYTES = (FIXTURES / "sample_cloudphysics.xlsx").read_bytes()


@pytest.fixture
def parser() -> FileParser:
    return FileParser()


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------


def test_detect_rvtools_format(parser: FileParser) -> None:
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    assert all(r.source_format == "rvtools" for r in rows)


def test_detect_cloudphysics_format(parser: FileParser) -> None:
    rows = parser.parse(CLOUDPHYSICS_BYTES, "export.xlsx")
    assert all(r.source_format == "cloudphysics" for r in rows)


def test_raises_on_unknown_format(parser: FileParser, tmp_path: Path) -> None:
    """A well-formed xlsx with unrecognized columns raises UnsupportedFormatError."""
    import pandas as pd

    xlsx = tmp_path / "random.xlsx"
    pd.DataFrame({"Column A": [1, 2], "Column B": ["x", "y"]}).to_excel(
        str(xlsx), index=False
    )
    with pytest.raises(UnsupportedFormatError):
        parser.parse(xlsx.read_bytes(), "random.xlsx")


def test_raises_on_non_xlsx(parser: FileParser) -> None:
    with pytest.raises(UnsupportedFormatError, match=r"\.xlsx"):
        parser.parse(b"dummy", "inventory.csv")


def test_raises_on_non_xlsx_xls(parser: FileParser) -> None:
    with pytest.raises(UnsupportedFormatError):
        parser.parse(b"dummy", "inventory.xls")


# ---------------------------------------------------------------------------
# Missing columns
# ---------------------------------------------------------------------------


def test_raises_on_missing_rvtools_columns(parser: FileParser, tmp_path: Path) -> None:
    """RVTools file missing required columns raises MissingColumnsError."""
    import pandas as pd

    xlsx = tmp_path / "rvtools_incomplete.xlsx"
    # Has the signature columns for detection but missing 'OS according to configuration file'
    pd.DataFrame(
        {
            "VM": ["vm1"],
            "Powerstate": ["poweredOn"],
            "OS according to VMware Tools": ["Windows Server 2022"],
            # deliberately omitting 'OS according to configuration file'
        }
    ).to_excel(str(xlsx), sheet_name="vInfo", index=False)

    with pytest.raises(MissingColumnsError) as exc_info:
        parser.parse(xlsx.read_bytes(), "rvtools_incomplete.xlsx")
    assert "OS according to configuration file" in exc_info.value.missing


def test_raises_on_cloudphysics_missing_guest_os_column(parser: FileParser, tmp_path: Path) -> None:
    """CloudPhysics detection requires both 'VM Name' and 'Guest OS'.
    A file with only 'VM Name' fails detection → UnsupportedFormatError (not MissingColumnsError),
    because 'Guest OS' is part of the signature used to identify the format.
    """
    import pandas as pd

    xlsx = tmp_path / "cp_incomplete.xlsx"
    pd.DataFrame({"VM Name": ["vm1"]}).to_excel(str(xlsx), index=False)

    with pytest.raises(UnsupportedFormatError):
        parser.parse(xlsx.read_bytes(), "cp_incomplete.xlsx")


# ---------------------------------------------------------------------------
# File size enforcement
# ---------------------------------------------------------------------------


def test_raises_on_oversized_file(parser: FileParser) -> None:
    # 11 MB of zeros — exceeds the 10 MB limit
    big_bytes = b"\x00" * (11 * 1024 * 1024)
    with pytest.raises(FileTooLargeError):
        parser.parse(big_bytes, "huge.xlsx")


# ---------------------------------------------------------------------------
# RVTools extraction
# ---------------------------------------------------------------------------


def test_rvtools_primary_os_extraction(parser: FileParser) -> None:
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    web = next(r for r in rows if r.vm_name == "web-prod-01")
    assert web.os_raw_primary == "Microsoft Windows Server 2022 (64-bit)"


def test_rvtools_fallback_os_used_when_primary_empty(parser: FileParser) -> None:
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    app = next(r for r in rows if r.vm_name == "app-dev-02")
    assert app.os_raw_primary == ""
    assert app.os_raw_fallback == "Microsoft Windows 10 (64-bit)"


def test_rvtools_both_os_empty(parser: FileParser) -> None:
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    unknown = next(r for r in rows if r.vm_name == "unknown-vm-01")
    assert unknown.os_raw_primary == ""
    assert unknown.os_raw_fallback == ""


def test_rvtools_skips_blank_vm_names(parser: FileParser) -> None:
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    names = [r.vm_name for r in rows]
    assert "" not in names


def test_rvtools_returns_correct_vm_count(parser: FileParser) -> None:
    """Fixture has 7 rows; 1 blank name → 6 VMs returned."""
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    assert len(rows) == 6


def test_rvtools_host_cluster_populated(parser: FileParser) -> None:
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    web = next(r for r in rows if r.vm_name == "web-prod-01")
    assert web.host_cluster == "Cluster-A"


# ---------------------------------------------------------------------------
# CloudPhysics extraction
# ---------------------------------------------------------------------------


def test_cloudphysics_extraction(parser: FileParser) -> None:
    rows = parser.parse(CLOUDPHYSICS_BYTES, "cp_export.xlsx")
    assert len(rows) == 4  # 5 rows, 1 blank name skipped
    web = next(r for r in rows if r.vm_name == "cp-web-01")
    assert web.os_raw_primary == "Microsoft Windows Server 2019 Standard"
    assert web.host_cluster == "Prod-Cluster"


def test_cloudphysics_no_fallback(parser: FileParser) -> None:
    rows = parser.parse(CLOUDPHYSICS_BYTES, "cp_export.xlsx")
    assert all(r.os_raw_fallback is None for r in rows)


def test_cloudphysics_skips_blank_vm_names(parser: FileParser) -> None:
    rows = parser.parse(CLOUDPHYSICS_BYTES, "cp_export.xlsx")
    assert all(r.vm_name != "" for r in rows)


def test_cloudphysics_null_cluster_when_empty(parser: FileParser) -> None:
    rows = parser.parse(CLOUDPHYSICS_BYTES, "cp_export.xlsx")
    unknown = next(r for r in rows if r.vm_name == "cp-unknown-01")
    assert unknown.host_cluster is None


# ---------------------------------------------------------------------------
# row_index and source_format
# ---------------------------------------------------------------------------


def test_row_index_is_1based(parser: FileParser) -> None:
    """First data row (Excel row 2, after header) should have row_index=2."""
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    assert rows[0].row_index == 2


def test_row_index_increments(parser: FileParser) -> None:
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    indices = [r.row_index for r in rows]
    assert indices == sorted(indices)
    assert indices[1] == indices[0] + 1


def test_returns_correct_source_format_rvtools(parser: FileParser) -> None:
    rows = parser.parse(RVTOOLS_BYTES, "export.xlsx")
    assert all(r.source_format == "rvtools" for r in rows)


def test_returns_correct_source_format_cloudphysics(parser: FileParser) -> None:
    rows = parser.parse(CLOUDPHYSICS_BYTES, "export.xlsx")
    assert all(r.source_format == "cloudphysics" for r in rows)


# ---------------------------------------------------------------------------
# VMRow dataclass contract
# ---------------------------------------------------------------------------


def test_vmrow_fields_present() -> None:
    row = VMRow(
        vm_name="test-vm",
        host_cluster="Cluster-A",
        os_raw_primary="Windows Server 2022",
        os_raw_fallback="Windows Server 2022",
        source_format="rvtools",
        row_index=2,
    )
    assert row.vm_name == "test-vm"
    assert row.host_cluster == "Cluster-A"
    assert row.os_raw_primary == "Windows Server 2022"
    assert row.os_raw_fallback == "Windows Server 2022"
    assert row.source_format == "rvtools"
    assert row.row_index == 2


def test_vmrow_optional_fields_accept_none() -> None:
    row = VMRow(
        vm_name="test-vm",
        host_cluster=None,
        os_raw_primary="",
        os_raw_fallback=None,
        source_format="cloudphysics",
        row_index=3,
    )
    assert row.host_cluster is None
    assert row.os_raw_fallback is None
