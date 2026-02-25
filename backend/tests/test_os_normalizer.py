"""Tests for OSNormalizer — matching accuracy, confidence scoring, and edge cases."""

import pytest

from app.services.os_normalizer import NormalizedOS, OSNormalizer


@pytest.fixture
def norm() -> OSNormalizer:
    return OSNormalizer()


# ---------------------------------------------------------------------------
# High-confidence OS matches
# ---------------------------------------------------------------------------


def test_normalize_windows_server_2022(norm: OSNormalizer) -> None:
    r = norm.normalize("Microsoft Windows Server 2022 (64-bit)")
    assert r.os_vendor == "Microsoft"
    assert r.os_family == "Windows Server"
    assert r.os_version == "2022"
    assert r.os_interpreted == "Windows Server 2022"
    assert r.confidence >= 0.90
    assert not r.low_confidence


def test_normalize_windows_server_2019(norm: OSNormalizer) -> None:
    r = norm.normalize("Microsoft Windows Server 2019 (64-bit)")
    assert r.os_family == "Windows Server"
    assert r.os_version == "2019"
    assert r.confidence >= 0.90


def test_normalize_windows_server_2012r2(norm: OSNormalizer) -> None:
    r = norm.normalize("Microsoft Windows Server 2012 R2 (64-bit)")
    assert r.os_family == "Windows Server"
    assert r.os_version == "2012 R2"
    assert r.os_interpreted == "Windows Server 2012 R2"
    assert r.confidence >= 0.90


def test_normalize_rhel_8(norm: OSNormalizer) -> None:
    r = norm.normalize("Red Hat Enterprise Linux 8 (64-bit)")
    assert r.os_vendor == "Red Hat"
    assert r.os_family == "RHEL"
    assert r.os_version == "8"
    assert r.os_interpreted == "RHEL 8"
    assert r.confidence >= 0.90
    assert not r.low_confidence


def test_normalize_ubuntu_2204(norm: OSNormalizer) -> None:
    r = norm.normalize("Ubuntu 22.04 LTS")
    assert r.os_vendor == "Canonical"
    assert r.os_family == "Ubuntu"
    assert r.os_version == "22.04 LTS"
    assert "22.04" in r.os_interpreted
    assert r.confidence >= 0.90


def test_normalize_centos_7(norm: OSNormalizer) -> None:
    r = norm.normalize("CentOS 7 (64-bit)")
    assert r.os_family == "CentOS"
    assert r.os_version == "7"
    assert r.confidence >= 0.90


def test_normalize_sles_15(norm: OSNormalizer) -> None:
    r = norm.normalize("SUSE Linux Enterprise 15 (64-bit)")
    assert r.os_vendor == "SUSE"
    assert r.os_family == "SLES"
    assert r.os_version == "15"
    assert r.confidence >= 0.90


def test_normalize_windows_xp(norm: OSNormalizer) -> None:
    """XP is not_supported but the normalizer still identifies the family correctly."""
    r = norm.normalize("Microsoft Windows XP Professional (32-bit)")
    assert r.os_vendor == "Microsoft"
    assert r.os_family == "Windows Desktop"
    assert r.confidence >= 0.90


def test_normalize_vdi_citrix(norm: OSNormalizer) -> None:
    r = norm.normalize("Citrix Virtual Apps")
    assert r.os_family == "Citrix Virtual Apps"
    assert r.os_vendor == "ISV"
    assert r.confidence >= 0.90


# ---------------------------------------------------------------------------
# Short forms and noise
# ---------------------------------------------------------------------------


def test_normalize_short_form(norm: OSNormalizer) -> None:
    """'Win Server 2019' should still match Windows Server."""
    r = norm.normalize("Win Server 2019")
    assert r.os_family == "Windows Server"
    assert r.os_version == "2019"
    assert r.os_interpreted == "Windows Server 2019"
    assert r.confidence >= 0.70


def test_normalize_rhel_short_form(norm: OSNormalizer) -> None:
    r = norm.normalize("RHEL 8")
    assert r.os_family == "RHEL"
    assert r.os_version == "8"
    assert r.confidence >= 0.90


def test_normalize_sles_short_form(norm: OSNormalizer) -> None:
    r = norm.normalize("SLES 15")
    assert r.os_family == "SLES"
    assert r.os_version == "15"
    assert r.confidence >= 0.90


def test_normalize_with_bitness_noise(norm: OSNormalizer) -> None:
    """(64-bit) suffix must not break matching."""
    r_with = norm.normalize("CentOS Linux 7 (64-bit)")
    r_without = norm.normalize("CentOS Linux 7")
    assert r_with.os_family == r_without.os_family
    assert r_with.os_version == r_without.os_version


def test_normalize_windows_server_bare(norm: OSNormalizer) -> None:
    r = norm.normalize("Windows Server 2022")
    assert r.os_family == "Windows Server"
    assert r.os_version == "2022"
    assert r.confidence >= 0.90


# ---------------------------------------------------------------------------
# Version extraction
# ---------------------------------------------------------------------------


def test_version_extraction_year_format(norm: OSNormalizer) -> None:
    r = norm.normalize("Microsoft Windows Server 2016 (64-bit)")
    assert r.os_version == "2016"


def test_version_extraction_with_r2(norm: OSNormalizer) -> None:
    r = norm.normalize("Microsoft Windows Server 2008 R2 (64-bit)")
    assert r.os_version == "2008 R2"


def test_version_extraction_dotted(norm: OSNormalizer) -> None:
    r = norm.normalize("Ubuntu 20.04 LTS (64-bit)")
    assert r.os_version is not None
    assert "20.04" in r.os_version


def test_version_extraction_single_digit(norm: OSNormalizer) -> None:
    r = norm.normalize("Oracle Linux 9 (64-bit)")
    assert r.os_version == "9"


def test_no_version_for_vdi(norm: OSNormalizer) -> None:
    """VDI product entries typically have no version number."""
    r = norm.normalize("Citrix Virtual Apps")
    assert r.os_version is None


# ---------------------------------------------------------------------------
# Low confidence / edge cases
# ---------------------------------------------------------------------------


def test_normalize_other_linux_is_low_confidence(norm: OSNormalizer) -> None:
    """'Other Linux' is not in the pattern library — should produce low confidence."""
    r = norm.normalize("Other Linux (64-bit)")
    assert r.confidence < 0.70
    assert r.low_confidence


def test_normalize_empty_string_returns_unknown(norm: OSNormalizer) -> None:
    r = norm.normalize("")
    assert r.os_interpreted == "Unknown"
    assert r.os_vendor is None
    assert r.os_family is None
    assert r.os_version is None
    assert r.confidence == 0.0
    assert r.low_confidence


def test_normalize_whitespace_only_returns_unknown(norm: OSNormalizer) -> None:
    r = norm.normalize("   ")
    assert r.os_interpreted == "Unknown"
    assert r.low_confidence


def test_normalize_garbage_string_returns_low_confidence(norm: OSNormalizer) -> None:
    r = norm.normalize("????")
    assert r.low_confidence
    assert r.confidence < 0.70


def test_normalize_unknown_os_string(norm: OSNormalizer) -> None:
    r = norm.normalize("Unknown")
    assert r.low_confidence


# ---------------------------------------------------------------------------
# Confidence scoring
# ---------------------------------------------------------------------------


def test_exact_match_has_high_confidence(norm: OSNormalizer) -> None:
    """A string from the pattern library should match with confidence >= 0.90."""
    r = norm.normalize("Microsoft Windows Server 2022 (64-bit)")
    assert r.confidence >= 0.90


def test_fuzzy_match_has_lower_confidence(norm: OSNormalizer) -> None:
    """A short-form variant should match above threshold but below 0.90."""
    r = norm.normalize("Win Server 2019")
    assert 0.70 <= r.confidence < 0.95


def test_low_confidence_flag_set_below_threshold(norm: OSNormalizer) -> None:
    r = norm.normalize("Other Linux (32-bit)")
    assert r.low_confidence is True


def test_low_confidence_flag_not_set_above_threshold(norm: OSNormalizer) -> None:
    r = norm.normalize("Red Hat Enterprise Linux 9 (64-bit)")
    assert r.low_confidence is False


# ---------------------------------------------------------------------------
# Never raises exceptions
# ---------------------------------------------------------------------------


def test_never_raises_exception(norm: OSNormalizer) -> None:
    """Any input must return a NormalizedOS and never raise."""
    tricky_inputs = [
        "",
        "   ",
        "????",
        None,  # type: ignore[arg-type]  # defensive — callers might pass None
        "\x00\x01\x02",
        "a" * 1000,
        "Windows" * 50,
        "1234567890",
    ]
    for inp in tricky_inputs:
        result = norm.normalize(inp)
        assert isinstance(result, NormalizedOS)


# ---------------------------------------------------------------------------
# NormalizedOS dataclass contract
# ---------------------------------------------------------------------------


def test_normalized_os_fields_present() -> None:
    r = NormalizedOS(
        os_interpreted="Windows Server 2022",
        os_vendor="Microsoft",
        os_family="Windows Server",
        os_version="2022",
        confidence=1.0,
        low_confidence=False,
    )
    assert r.os_interpreted == "Windows Server 2022"
    assert r.os_vendor == "Microsoft"
    assert r.os_family == "Windows Server"
    assert r.os_version == "2022"
    assert r.confidence == 1.0
    assert not r.low_confidence


def test_normalized_os_optional_fields_accept_none() -> None:
    r = NormalizedOS(
        os_interpreted="Unknown",
        os_vendor=None,
        os_family=None,
        os_version=None,
        confidence=0.0,
        low_confidence=True,
    )
    assert r.os_vendor is None
    assert r.os_family is None
    assert r.os_version is None
