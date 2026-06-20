"""RiskMerger — classifies risk flags into competition vs enhancement categories.

Three modes:
  competition: V1-compatible flags only (for exact-match scoring)
  enhanced:    all flags (production, current V2+V1RiskAdapter behavior)
  hybrid:      both groups separated + combined (research/analysis)
"""

# V1-compatible flag types — the 13 categories V1's RiskAnalyzer produces.
# These form the exact-match ground truth for competition scoring.
V1_FLAG_TYPES = frozenset({
    "blurry_image",
    "cropped_or_obstructed",
    "low_light_or_glare",
    "wrong_angle",
    "wrong_object",
    "wrong_object_part",
    "damage_not_visible",
    "claim_mismatch",
    "possible_manipulation",
    "non_original_image",
    "text_instruction_present",
    "user_history_risk",
    "manual_review_required",
})

# V2-only enhancement flags — flags V2 produces that V1 does not.
# These are valid production improvements but cause exact-match failures
# in competition scoring. Do NOT remove from enhanced/hybrid modes.
ENHANCEMENT_FLAGS = frozenset({
    # Conversation analysis (4 flags)
    "uncertain_claim",
    "conversation_conflict",
    "possible_sarcasm",
    "claim_retraction",
    # V1 internal passthrough (RuleEngine internal; RiskAnalyzer filters out)
    "evidence_insufficient",
    "low_confidence",
    # Image fraud detection (3 flags)
    "duplicate_image",
    "screenshot_detected",
    "photo_of_photo",
    # Metadata fraud detection (5 flags)
    "edited_image",
    "timestamp_mismatch",
    "camera_mismatch",
    "no_exif",
    "exif_read_error",
    # Behavioral fraud detection (3 flags)
    "frequent_claims",
    "image_reuse",
    "severity_escalation",
})


class RiskMerger:
    """Merges risk flags from multiple sources with mode-aware classification.

    Usage:
        merger = RiskMerger("competition")
        flags = merger.merge(v2_flags, v1_flags, fraud_flags, conversation_flags)
        # Returns sorted list of competition-only flags

        merger = RiskMerger("hybrid")
        result = merger.merge(...)
        # Returns {"competition_flags": [...], "enhancement_flags": [...], "all_flags": [...]}
    """

    def __init__(self, mode: str = "hybrid"):
        if mode not in ("competition", "enhanced", "hybrid"):
            raise ValueError(f"Unknown risk mode: {mode!r}. Use competition/enhanced/hybrid.")
        self.mode = mode

    @staticmethod
    def classify(flags: list[str]) -> dict:
        """Split a flat flag list into competition and enhancement groups.

        Args:
            flags: Any iterable of flag strings (including ["none"])

        Returns:
            dict with keys: competition_flags, enhancement_flags, all_flags
        """
        flag_set = {f for f in flags if f and f != "none"}
        competition = sorted(flag_set & V1_FLAG_TYPES)
        enhancement = sorted((flag_set & ENHANCEMENT_FLAGS) | (flag_set - V1_FLAG_TYPES - ENHANCEMENT_FLAGS))
        all_f = sorted(flag_set)
        return {
            "competition_flags": competition if competition else ["none"],
            "enhancement_flags": enhancement if enhancement else ["none"],
            "all_flags": all_f if all_f else ["none"],
        }

    def merge(self, *flag_lists: list[str]) -> list[str] | dict:
        """Merge flags from multiple sources, filtered by mode.

        Args:
            *flag_lists: One or more lists of flag strings.

        Returns:
            competition mode: sorted list of V1-compatible flags (or ["none"])
            enhanced mode:    sorted list of all flags (or ["none"])
            hybrid mode:      dict with competition/enhancement/all groups
        """
        combined = set()
        for fl in flag_lists:
            combined |= {f for f in fl if f and f != "none"}

        if self.mode == "competition":
            result = sorted(combined & V1_FLAG_TYPES)
            return result if result else ["none"]

        if self.mode == "enhanced":
            result = sorted(combined)
            return result if result else ["none"]

        # hybrid mode
        return self.classify(list(combined))
