"""
Output schema and enum validation.
"""

from typing import Any, Dict

from config import Config


class OutputValidator:
    """Ensures no invalid enum values reach output.csv."""

    FIELDNAMES = [
        "user_id",
        "image_paths",
        "user_claim",
        "claim_object",
        "evidence_standard_met",
        "evidence_standard_met_reason",
        "risk_flags",
        "issue_type",
        "object_part",
        "claim_status",
        "claim_status_justification",
        "supporting_image_ids",
        "valid_image",
        "severity",
    ]

    def __init__(self, config: Config):
        self.config = config

    def validate(self, row: Dict[str, Any]) -> Dict[str, str]:
        cleaned = {field: str(row.get(field, "")) for field in self.FIELDNAMES}

        if cleaned["claim_object"] not in self.config.ALLOWED_OBJECT_PARTS:
            cleaned["claim_object"] = "car" if not cleaned["claim_object"] else cleaned["claim_object"]

        if cleaned["issue_type"] not in self.config.ALLOWED_ISSUE_TYPES:
            cleaned["issue_type"] = "unknown"

        allowed_parts = self.config.ALLOWED_OBJECT_PARTS.get(cleaned["claim_object"], {"unknown"})
        if cleaned["object_part"] not in allowed_parts:
            cleaned["object_part"] = "unknown"

        if cleaned["claim_status"] not in self.config.ALLOWED_CLAIM_STATUS:
            cleaned["claim_status"] = "not_enough_information"

        if cleaned["severity"] not in self.config.ALLOWED_SEVERITY:
            cleaned["severity"] = "unknown"

        for bool_field in ("evidence_standard_met", "valid_image"):
            cleaned[bool_field] = "true" if str(cleaned[bool_field]).lower() == "true" else "false"

        flags = [f for f in cleaned["risk_flags"].split(";") if f]
        valid_flags = [f for f in flags if f in self.config.ALLOWED_RISK_FLAGS and f != "none"]
        cleaned["risk_flags"] = ";".join(sorted(set(valid_flags))) if valid_flags else "none"

        if not cleaned["supporting_image_ids"]:
            cleaned["supporting_image_ids"] = "none"

        return cleaned
