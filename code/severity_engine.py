"""
Deterministic severity mapping.
"""

from utils import normalize_text


class SeverityEngine:
    """Maps visible damage type and claim wording to final severity."""

    ORDER = ["none", "low", "medium", "high"]

    BASE = {
        "glass_shatter": "high",
        "water_damage": "high",
        "crack": "medium",
        "broken_part": "medium",
        "missing_part": "medium",
        "crushed_packaging": "medium",
        "dent": "low",
        "scratch": "low",
        "stain": "low",
        "torn_packaging": "low",
        "none": "none",
    }

    BOOST_WORDS = {
        "severe", "major", "extensive", "large", "heavy", "deep",
        "significant", "smashed",
    }

    def determine(self, damage_type: str, user_claim: str) -> str:
        base = self.BASE.get(damage_type, "unknown")
        if base in ("unknown", "none", "high"):
            return base

        text = normalize_text(user_claim or "")
        if not any(word in text for word in self.BOOST_WORDS):
            return base

        idx = self.ORDER.index(base)
        return self.ORDER[min(idx + 1, len(self.ORDER) - 1)]
