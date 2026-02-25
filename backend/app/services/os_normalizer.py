"""OS normalization service — fuzzy-matches raw OS strings to known patterns."""

import logging
import re
from dataclasses import dataclass
from typing import Optional

from rapidfuzz import fuzz, process

from app.config import settings
from app.services.os_patterns import OS_PATTERNS, OSPattern

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Preprocessing helpers
# ---------------------------------------------------------------------------

# Removes "(64-bit)", "(32-bit)", "(x86)", "(x86-64)" etc.
_NOISE_RE = re.compile(r"\s*\(\s*(?:32|64)\s*[- ]?\s*bit\s*\)\s*|\s*\(x86(?:-64)?\)\s*", re.IGNORECASE)

# Extracts version strings in order of specificity (most specific patterns first):
#   2022 R2, 2012 R2, 2008 R2   — year with Rx suffix
#   2022, 2019, 2016 …          — plain year
#   22.04 LTS, 20.04            — dot-separated with optional LTS
#   15 SP4, 12 SP5              — single/double number with optional SPx
#   8, 9, 7                     — bare single number (lowest priority)
_VERSION_RE = re.compile(
    r"\b(\d{4}\s+R\d|\d{4}|\d+\.\d+(?:\.\d+)?(?:\s+LTS)?|\d+(?:\s+SP\d)?)\b"
)


def _strip_noise(s: str) -> str:
    """Remove bit-depth qualifiers from an OS string."""
    return _NOISE_RE.sub(" ", s).strip()


def _extract_version(raw: str) -> Optional[str]:
    """Return the first version token found in a raw OS string, or None."""
    cleaned = _strip_noise(raw)
    m = _VERSION_RE.search(cleaned)
    return m.group(1).strip() if m else None


def _preprocess(s: str) -> str:
    """Normalise for fuzzy comparison: strip noise, lowercase, collapse whitespace."""
    s = _strip_noise(s)
    s = s.lower().strip()
    return re.sub(r"\s+", " ", s)


# ---------------------------------------------------------------------------
# Precompute the flat choice list once at import time
# ---------------------------------------------------------------------------

_PROCESSED_CHOICES: list[str] = []
_PATTERN_LOOKUP: list[OSPattern] = []

for _pat in OS_PATTERNS:
    for _ms in _pat.match_strings:
        _PROCESSED_CHOICES.append(_preprocess(_ms))
        _PATTERN_LOOKUP.append(_pat)


# ---------------------------------------------------------------------------
# Data contract
# ---------------------------------------------------------------------------


@dataclass
class NormalizedOS:
    """Structured result of OS normalization."""

    os_interpreted: str  # e.g. "Windows Server 2022", "RHEL 8", "Ubuntu 22.04"
    os_vendor: Optional[str]  # e.g. "Microsoft", "Red Hat", "Canonical"
    os_family: Optional[str]  # e.g. "Windows Server", "RHEL", "Ubuntu"
    os_version: Optional[str]  # e.g. "2022", "8", "22.04"
    confidence: float  # 0.0–1.0
    low_confidence: bool  # True when confidence < configured threshold


# ---------------------------------------------------------------------------
# Normalizer
# ---------------------------------------------------------------------------


class OSNormalizer:
    """Normalises raw OS strings from VM inventory exports using fuzzy matching.

    Design philosophy: prefer over-flagging.  When the normalizer cannot
    confidently identify an OS it sets low_confidence=True, which the
    Classification Engine interprets as needs_info or needs_review rather than
    silently mis-classifying the VM.
    """

    def normalize(self, raw_os: str) -> NormalizedOS:
        """Normalize a raw OS string to a structured NormalizedOS result.

        Never raises exceptions — always returns a NormalizedOS.

        Args:
            raw_os: Raw OS string from the VM inventory file.

        Returns:
            NormalizedOS populated with vendor, family, version, and confidence.
        """
        try:
            return self._normalize_internal(raw_os)
        except Exception:
            logger.exception(
                "Unexpected error normalizing OS string %r; returning Unknown.", raw_os
            )
            return NormalizedOS("Unknown", None, None, None, 0.0, True)

    def _normalize_internal(self, raw_os: str) -> NormalizedOS:
        threshold = settings.FUZZY_MATCH_THRESHOLD / 100.0

        # Special case: empty / whitespace-only input
        if not raw_os or not raw_os.strip():
            return NormalizedOS("Unknown", None, None, None, 0.0, True)

        version = _extract_version(raw_os)
        cleaned = _preprocess(raw_os)

        result = process.extractOne(
            cleaned,
            _PROCESSED_CHOICES,
            scorer=fuzz.token_sort_ratio,
            processor=None,
        )

        if result is None:
            logger.warning(
                "No match found for OS string %r — returning as-is with zero confidence.",
                raw_os,
            )
            return NormalizedOS(raw_os.strip(), None, None, version, 0.0, True)

        _best_match, score, idx = result
        confidence = score / 100.0
        low_confidence = confidence < threshold
        matched = _PATTERN_LOOKUP[idx]

        os_interpreted = (
            f"{matched.canonical_name} {version}" if version else matched.canonical_name
        )

        if low_confidence:
            logger.warning(
                "Low confidence OS match: raw=%r score=%.2f matched=%r",
                raw_os,
                confidence,
                matched.canonical_name,
            )
        else:
            logger.debug(
                "Normalized OS: %r → %r (confidence=%.2f)", raw_os, os_interpreted, confidence
            )

        return NormalizedOS(
            os_interpreted=os_interpreted,
            os_vendor=matched.vendor,
            os_family=matched.family,
            os_version=version,
            confidence=confidence,
            low_confidence=low_confidence,
        )
