"""
Risk flag and severity analysis.
"""

from typing import List, Dict, Any, Set, Optional
from config import Config
from utils import normalize_text


class RiskAnalyzer:

    def __init__(self, config: Config):
        self.config = config
        self.risk_indicators = config.risk_flag_indicators

    def analyze(
        self,
        image_analysis: Dict[str, Any],
        user_history: Optional[Dict[str, Any]],
        claim_object: str,
        user_claim: str,
    ) -> tuple[List[str], str]:
        risk_flags: Set[str] = set()
        severity = "unknown"

        image_assessments = image_analysis.get("image_assessments", [])
        for assessment in image_assessments:
            if not assessment.get("is_clear", True):
                risk_flags.add("blurry_image")
            if assessment.get("is_cropped", False):
                risk_flags.add("cropped_or_obstructed")
            if not assessment.get("lighting_adequate", True):
                risk_flags.add("low_light_or_glare")
            if not assessment.get("angle_sufficient", True):
                risk_flags.add("wrong_angle")

        if image_analysis.get("claim_supported") is False:
            risk_flags.add("claim_mismatch")

        if image_analysis.get("overall_issue_type") in ("none", "unknown"):
            if self._user_claimed_damage(user_claim):
                risk_flags.add("damage_not_visible")

        notes = image_analysis.get("notes", "").lower()
        if any(word in notes for word in ["photoshopped", "edited", "manipulated", "altered"]):
            risk_flags.add("possible_manipulation")
        if any(word in notes for word in ["screenshot", "stock photo", "stock image", "template", "non-original"]):
            risk_flags.add("non_original_image")

        if user_history:
            history_flags = user_history.get("history_flags", "")
            if history_flags and history_flags.lower() != "none":
                risk_flags.add("user_history_risk")

            last_90_days = int(user_history.get("last_90_days_claim_count", 0))
            if last_90_days > 3:
                risk_flags.add("user_history_risk")

            rejected = int(user_history.get("rejected_claim", 0))
            if rejected > 2:
                risk_flags.add("user_history_risk")

        if image_analysis.get("confidence", 1.0) < 0.5:
            risk_flags.add("manual_review_required")

        if "text" in notes or "label" in notes:
            risk_flags.add("text_instruction_present")

        if len(risk_flags) >= 3:
            risk_flags.add("manual_review_required")
        if "claim_mismatch" in risk_flags and "user_history_risk" in risk_flags:
            risk_flags.add("manual_review_required")

        severity = self._determine_severity(image_analysis, user_claim)

        if not risk_flags:
            return ["none"], severity

        return sorted(risk_flags), severity

    def _user_claimed_damage(self, user_claim: str) -> bool:
        if not user_claim:
            return False
        text = normalize_text(user_claim)
        damage_keywords = [
            "dent", "scratch", "crack", "shatter", "broken", "missing",
            "torn", "crushed", "water damage", "stain", "damage", "issue",
            "defect", "problem", "not working", "faulty"
        ]
        return any(kw in text for kw in damage_keywords)

    def _determine_severity(self, image_analysis: Dict[str, Any], user_claim: str) -> str:
        issue_type = image_analysis.get("overall_issue_type", "unknown")

        severity_map = {
            "dent": "low",
            "scratch": "low",
            "crack": "medium",
            "glass_shatter": "high",
            "broken_part": "medium",
            "missing_part": "medium",
            "torn_packaging": "low",
            "crushed_packaging": "medium",
            "water_damage": "high",
            "stain": "low",
            "none": "none",
        }

        mapped = severity_map.get(issue_type)
        if mapped:
            return mapped

        return image_analysis.get("severity", "unknown")
