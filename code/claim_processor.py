"""
Core claim processing logic.
Orchestrates image analysis, evidence checking, risk analysis, and final decision.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from config import Config
from utils import (
    parse_image_paths,
    get_image_id_from_path,
    extract_claim_text,
    safe_csv_read,
    normalize_text,
)
from vision_analyzer import analyze_images
from evidence_requirements import EvidenceRequirements
from risk_analyzer import RiskAnalyzer

logger = logging.getLogger("evidence_review.processor")


class ClaimProcessor:

    def __init__(self, config: Config):
        self.config = config
        self.evidence_reqs = EvidenceRequirements(config.evidence_reqs_path)
        self.risk_analyzer = RiskAnalyzer(config)
        self.user_history_cache: Dict[str, Dict] = {}
        self._load_user_history()

    def _load_user_history(self) -> None:
        if not self.config.user_history_path.exists():
            logger.warning(f"User history file not found: {self.config.user_history_path}")
            return

        rows = safe_csv_read(self.config.user_history_path)
        for row in rows:
            user_id = row.get("user_id", "").strip()
            if user_id:
                self.user_history_cache[user_id] = row
        logger.info(f"Loaded history for {len(self.user_history_cache)} users")

    def _get_user_history(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.user_history_cache.get(user_id)

    @staticmethod
    def _extract_claim_details(user_claim: str, claim_object: str) -> Tuple[str, str]:
        if not user_claim:
            return "unknown", "unknown"
        text = normalize_text(user_claim).lower()

        issue_kw = {
            "dent": ["dent"],
            "scratch": ["scratch"],
            "crack": ["crack"],
            "glass_shatter": ["shatter", "smashed"],
            "broken_part": ["broken", "broke"],
            "missing_part": ["missing"],
            "torn_packaging": ["torn", "ripped"],
            "crushed_packaging": ["crush"],
            "water_damage": ["water", "wet", "moisture", "liquid", "spill"],
            "stain": ["stain"],
        }
        claimed_issue = "unknown"
        for itype, kws in issue_kw.items():
            if any(kw in text for kw in kws):
                claimed_issue = itype
                break

        if claim_object == "car":
            part_kw = {
                "front_bumper": ["front bumper"],
                "rear_bumper": ["rear bumper", "back bumper"],
                "door": ["door"],
                "hood": ["hood"],
                "windshield": ["windshield", "windscreen", "front glass", "front screen"],
                "side_mirror": ["side mirror", "mirror"],
                "headlight": ["headlight"],
                "taillight": ["taillight", "tail light"],
                "fender": ["fender"],
                "quarter_panel": ["quarter panel"],
                "body": ["body"],
            }
        elif claim_object == "laptop":
            part_kw = {
                "screen": ["screen", "display"],
                "keyboard": ["keyboard"],
                "trackpad": ["trackpad", "touchpad"],
                "hinge": ["hinge"],
                "lid": ["lid"],
                "corner": ["corner"],
                "port": ["port"],
                "base": ["base"],
                "body": ["body", "casing", "chassis"],
            }
        elif claim_object == "package":
            part_kw = {
                "box": ["box"],
                "package_corner": ["corner"],
                "package_side": ["side"],
                "seal": ["seal"],
                "label": ["label", "sticker"],
                "contents": ["inside", "content", "item"],
                "item": ["item"],
            }
        else:
            part_kw = {}

        claimed_part = "unknown"
        for part, kws in part_kw.items():
            if any(kw in text for kw in kws):
                claimed_part = part
                break

        return claimed_issue, claimed_part

    def process_claim(self, claim_row: Dict[str, str]) -> Dict[str, Any]:
        user_id = claim_row.get("user_id", "").strip()
        image_paths_str = claim_row.get("image_paths", "").strip()
        user_claim = claim_row.get("user_claim", "").strip()
        claim_object = claim_row.get("claim_object", "").strip().lower()

        image_paths = parse_image_paths(image_paths_str, self.config.images_dir)
        logger.debug(f"Parsed {len(image_paths)} images for user {user_id}")

        user_history = self._get_user_history(user_id)
        claim_text = extract_claim_text(user_claim)

        try:
            vision_analysis = analyze_images(
                image_paths=image_paths,
                user_claim=claim_text or user_claim,
                claim_object=claim_object,
                config=self.config,
            )
        except Exception as e:
            logger.error(f"Vision analysis failed for user {user_id}: {e}")
            return self._fallback_output(claim_row, f"Vision analysis error: {str(e)[:100]}")

        # Extract what the user claimed for cross-reference
        claim_text_for_extraction = claim_text or user_claim
        claimed_issue, claimed_part = self._extract_claim_details(claim_text_for_extraction, claim_object)

        supporting_image_ids = vision_analysis.get("supporting_image_ids", [])
        if not supporting_image_ids and vision_analysis.get("claim_supported", False):
            for assessment in vision_analysis.get("image_assessments", []):
                if assessment.get("is_clear", False) and assessment.get("issues_visible", []):
                    img_id = assessment.get("image_id", "")
                    if img_id:
                        supporting_image_ids.append(img_id)

        issue_type = vision_analysis.get("overall_issue_type", "unknown")
        object_part = vision_analysis.get("overall_object_part", "unknown")

        # only force-supported when model contradicted but found real damage
        if not vision_analysis.get("claim_supported", False):
            cr = (vision_analysis.get("contradiction_reason") or "").lower()
            part_mismatch = any(w in cr for w in ["part", "area", "section", "region", "location", "different"])
            has_actual_damage = any(
                a.get("issues_visible") and a["issues_visible"][0] not in ("none", "unknown")
                for a in vision_analysis.get("image_assessments", [])
            )
            if has_actual_damage and not part_mismatch:
                vision_analysis["claim_supported"] = True
                if not supporting_image_ids:
                    for a in vision_analysis["image_assessments"]:
                        if a.get("issues_visible") and a["issues_visible"][0] not in ("none", "unknown"):
                            supporting_image_ids.append(a.get("image_id", ""))
                            break

        meets_standard, standard_reason = self.evidence_reqs.meets_standard(
            claim_object=claim_object,
            issue_type=issue_type,
            supporting_image_ids=supporting_image_ids,
            total_images=len(image_paths),
        )

        claim_status, status_justification = self._determine_claim_status(
            vision_analysis=vision_analysis,
            meets_standard=meets_standard,
            supporting_image_ids=supporting_image_ids,
            user_claim=user_claim,
            claim_object=claim_object,
        )

        risk_flags, severity = self.risk_analyzer.analyze(
            image_analysis=vision_analysis,
            user_history=user_history,
            claim_object=claim_object,
            user_claim=user_claim,
        )

        valid_image = self._is_image_set_valid(
            vision_analysis=vision_analysis,
            image_paths=image_paths,
        )

        # Post-processing corrections
        if issue_type == "none":
            issue_type = "unknown"

        if claim_status == "contradicted" and vision_analysis.get("overall_issue_type", "") in ("none", "unknown"):
            claim_status = "not_enough_information"

        if issue_type == "unknown" and not valid_image:
            claim_status = "not_enough_information"
            severity = "unknown"

        notes = (vision_analysis.get("notes") or "").lower()
        if any(w in notes for w in ["screenshot", "stock", "template", "non-original"]):
            valid_image = False

        severity_map_override = {
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
        base_sev = severity_map_override.get(issue_type)
        if base_sev and issue_type not in ("unknown", "none"):
            text_lc = normalize_text(user_claim).lower() if user_claim else ""
            boost_words = ["severe", "extensive", "large", "deep", "bad", "heavy", "major", "significant", "shatter", "smashed"]
            sev_boost = sum(1 for w in boost_words if w in text_lc)
            sev_order = ["none", "low", "medium", "high", "unknown"]
            base_idx = sev_order.index(base_sev) if base_sev in sev_order else 1
            boost_idx = min(sev_boost // 2, 2)
            final_idx = min(base_idx + boost_idx, 3)
            severity = sev_order[final_idx]

        output_row = {
            "user_id": user_id,
            "image_paths": image_paths_str,
            "user_claim": user_claim,
            "claim_object": claim_object,
            "evidence_standard_met": "true" if meets_standard else "false",
            "evidence_standard_met_reason": standard_reason,
            "risk_flags": ";".join(risk_flags) if risk_flags else "none",
            "issue_type": issue_type,
            "object_part": object_part,
            "claim_status": claim_status,
            "claim_status_justification": status_justification,
            "supporting_image_ids": ";".join(supporting_image_ids) if supporting_image_ids else "none",
            "valid_image": "true" if valid_image else "false",
            "severity": severity,
        }

        output_row = self._validate_output(output_row)

        return output_row

    def _determine_claim_status(
        self,
        vision_analysis: Dict[str, Any],
        meets_standard: bool,
        supporting_image_ids: List[str],
        user_claim: str,
        claim_object: str,
    ) -> Tuple[str, str]:
        claim_supported = vision_analysis.get("claim_supported", False)
        contradiction_reason = vision_analysis.get("contradiction_reason", "")

        if claim_supported is False and contradiction_reason:
            return "contradicted", f"Image evidence contradicts the claim: {contradiction_reason}"

        if claim_supported is True and supporting_image_ids:
            if meets_standard:
                return "supported", f"Image evidence supports the claim. Supporting images: {', '.join(supporting_image_ids)}"
            else:
                return "not_enough_information", "Claim appears supported but insufficient evidence to meet the standard."

        if not supporting_image_ids:
            return "not_enough_information", "No supporting images found; insufficient evidence to verify the claim."

        return "not_enough_information", "Unable to determine claim status from the available evidence."

    def _is_image_set_valid(self, vision_analysis: Dict[str, Any], image_paths: List[Path]) -> bool:
        if not image_paths:
            return False

        assessments = vision_analysis.get("image_assessments", [])
        if not assessments:
            return False

        for assessment in assessments:
            if assessment.get("is_clear", False) and not assessment.get("is_cropped", True):
                return True

        return False

    def _validate_output(self, row: Dict[str, Any]) -> Dict[str, Any]:
        issue_type = row.get("issue_type", "unknown")
        if issue_type not in self.config.ALLOWED_ISSUE_TYPES:
            row["issue_type"] = "unknown"

        claim_object = row.get("claim_object", "")
        object_part = row.get("object_part", "unknown")
        allowed_parts = self.config.ALLOWED_OBJECT_PARTS.get(claim_object, {"unknown"})
        if object_part not in allowed_parts:
            row["object_part"] = "unknown"

        status = row.get("claim_status", "not_enough_information")
        if status not in self.config.ALLOWED_CLAIM_STATUS:
            row["claim_status"] = "not_enough_information"

        severity = row.get("severity", "unknown")
        if severity not in self.config.ALLOWED_SEVERITY:
            row["severity"] = "unknown"

        risk_flags = row.get("risk_flags", "none")
        if risk_flags != "none":
            flags = risk_flags.split(";") if risk_flags else []
            valid_flags = [f for f in flags if f in self.config.ALLOWED_RISK_FLAGS]
            row["risk_flags"] = ";".join(valid_flags) if valid_flags else "none"

        return row

    def _fallback_output(self, claim_row: Dict[str, str], error_message: str) -> Dict[str, Any]:
        return {
            "user_id": claim_row.get("user_id", "unknown"),
            "image_paths": claim_row.get("image_paths", ""),
            "user_claim": claim_row.get("user_claim", ""),
            "claim_object": claim_row.get("claim_object", "unknown"),
            "evidence_standard_met": "false",
            "evidence_standard_met_reason": f"Processing error: {error_message[:100]}",
            "risk_flags": "manual_review_required",
            "issue_type": "unknown",
            "object_part": "unknown",
            "claim_status": "not_enough_information",
            "claim_status_justification": "Automated processing failed; manual review required.",
            "supporting_image_ids": "none",
            "valid_image": "false",
            "severity": "unknown",
        }
