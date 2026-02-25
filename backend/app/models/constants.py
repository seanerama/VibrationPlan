"""Classification tier constants shared across all modules."""

# Tier key strings — use these everywhere; never hard-code raw strings
TIER_OFFICIALLY_SUPPORTED = "officially_supported"
TIER_UNOFFICIALLY_SUPPORTED = "unofficially_supported"
TIER_SUPPORTED_VDI = "supported_vdi"
TIER_NEEDS_REVIEW = "needs_review"
TIER_NEEDS_INFO = "needs_info"
TIER_NOT_SUPPORTED = "not_supported"

ALL_TIERS = [
    TIER_OFFICIALLY_SUPPORTED,
    TIER_UNOFFICIALLY_SUPPORTED,
    TIER_SUPPORTED_VDI,
    TIER_NEEDS_REVIEW,
    TIER_NEEDS_INFO,
    TIER_NOT_SUPPORTED,
]

# Hex colors for Excel cell fills and frontend badges.
# Source of truth: design-system.md — takes precedence over project-plan.md.
TIER_COLORS: dict[str, str] = {
    TIER_OFFICIALLY_SUPPORTED: "#10B981",
    TIER_UNOFFICIALLY_SUPPORTED: "#8B5CF6",
    TIER_SUPPORTED_VDI: "#14B8A6",
    TIER_NEEDS_REVIEW: "#F59E0B",
    TIER_NEEDS_INFO: "#0028FA",
    TIER_NOT_SUPPORTED: "#F43F5E",
}

# Human-readable display names for the output spreadsheet.
TIER_DISPLAY_NAMES: dict[str, str] = {
    TIER_OFFICIALLY_SUPPORTED: "Officially Supported",
    TIER_UNOFFICIALLY_SUPPORTED: "Unofficially Supported",
    TIER_SUPPORTED_VDI: "Supported VDI VM",
    TIER_NEEDS_REVIEW: "Needs Review with Customer",
    TIER_NEEDS_INFO: "Needs Additional Info",
    TIER_NOT_SUPPORTED: "Not Supported",
}

# Row background tint colors for xlsx fills (ARGB format: FF = full opacity).
TIER_ROW_BG: dict[str, str] = {
    TIER_OFFICIALLY_SUPPORTED: "FF052E1A",
    TIER_UNOFFICIALLY_SUPPORTED: "FF1A0A2E",
    TIER_SUPPORTED_VDI: "FF042322",
    TIER_NEEDS_REVIEW: "FF2D1A00",
    TIER_NEEDS_INFO: "FF00082F",
    TIER_NOT_SUPPORTED: "FF2D0A14",
}
