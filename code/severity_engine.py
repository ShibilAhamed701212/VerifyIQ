"""
Deterministic severity mapping.
"""

from utils import normalize_text


class SeverityEngine:
    """Maps visible damage type and claim wording to final severity."""

    ORDER = ["none", "low", "medium", "high"]

    BASE = {
        "glass_shatter": "high",
        "water_damage": "medium",
        "crack": "medium",
        "broken_part": "medium",
        "missing_part": "medium",
        "crushed_packaging": "medium",
        "dent": "medium",
        "scratch": "low",
        "stain": "medium",
        "torn_packaging": "medium",
        "none": "none",
    }

    BASE_OVERRIDE = {
        "laptop": {"dent": "low"},
    }

    BOOST_WORDS = {
        "severe", "major", "extensive", "large", "heavy", "deep",
        "significant", "smashed",
    }

    NEGATION_WORDS = {"no", "not", "nothing", "never", "didn't", "doesn't", "don't", "isn't"}

    def determine(self, damage_type: str, user_claim: str, claim_object: str = "",
                  risk_flags: list = None) -> str:
        base = self._base_for(damage_type, claim_object)
        if base == "none":
            return base

        flags = set(risk_flags or [])
        if "non_original_image" in flags:
            return "high"

        text = normalize_text(user_claim or "")
        if self._has_boost(text) and base != "unknown":
            idx = self.ORDER.index(base)
            base = self.ORDER[min(idx + 1, len(self.ORDER) - 1)]

        return base

    def _base_for(self, damage_type: str, claim_object: str) -> str:
        override = self.BASE_OVERRIDE.get(claim_object, {})
        if damage_type in override:
            return override[damage_type]
        return self.BASE.get(damage_type, "unknown")

    def _has_boost(self, text: str) -> bool:
        for word in self.BOOST_WORDS:
            pos = text.find(word)
            if pos == -1:
                continue
            pre = text[max(0, pos - 50):pos].split()
            negated = False
            for neg in self.NEGATION_WORDS:
                if neg in pre[-5:]:
                    negated = True
                    break
            if negated:
                continue
            return True
        return False
