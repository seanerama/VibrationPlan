"""Tests for classification tier constants."""

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


def test_all_six_tier_keys_defined():
    assert TIER_OFFICIALLY_SUPPORTED == "officially_supported"
    assert TIER_UNOFFICIALLY_SUPPORTED == "unofficially_supported"
    assert TIER_SUPPORTED_VDI == "supported_vdi"
    assert TIER_NEEDS_REVIEW == "needs_review"
    assert TIER_NEEDS_INFO == "needs_info"
    assert TIER_NOT_SUPPORTED == "not_supported"


def test_all_tiers_list_contains_six_entries():
    assert len(ALL_TIERS) == 6
    assert TIER_OFFICIALLY_SUPPORTED in ALL_TIERS
    assert TIER_UNOFFICIALLY_SUPPORTED in ALL_TIERS
    assert TIER_SUPPORTED_VDI in ALL_TIERS
    assert TIER_NEEDS_REVIEW in ALL_TIERS
    assert TIER_NEEDS_INFO in ALL_TIERS
    assert TIER_NOT_SUPPORTED in ALL_TIERS


def test_tier_colors_has_entry_for_every_tier():
    for tier in ALL_TIERS:
        assert tier in TIER_COLORS, f"Missing color for tier: {tier}"


def test_tier_color_values_match_design_system():
    """Verify colors match design-system.md (source of truth)."""
    assert TIER_COLORS[TIER_OFFICIALLY_SUPPORTED] == "#10B981"
    # Violet — from design-system.md, NOT the old #14B8A6 in project-plan.md
    assert TIER_COLORS[TIER_UNOFFICIALLY_SUPPORTED] == "#8B5CF6"
    assert TIER_COLORS[TIER_SUPPORTED_VDI] == "#14B8A6"
    assert TIER_COLORS[TIER_NEEDS_REVIEW] == "#F59E0B"
    assert TIER_COLORS[TIER_NEEDS_INFO] == "#0028FA"
    assert TIER_COLORS[TIER_NOT_SUPPORTED] == "#F43F5E"


def test_tier_colors_are_valid_hex():
    for tier, color in TIER_COLORS.items():
        assert color.startswith("#"), f"Color for {tier} must start with '#'"
        assert len(color) == 7, f"Color for {tier} must be 7 chars (e.g. #RRGGBB)"
