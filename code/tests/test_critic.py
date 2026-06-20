"""Tests for submission_critic post-processing."""

import submission_critic
from submission_critic import validate_output_rows


def _row(**overrides):
    base = {
        "user_id": "test", "image_paths": "img.jpg", "user_claim": "dent on door",
        "claim_object": "car", "evidence_standard_met": "true",
        "evidence_standard_met_reason": "ok", "risk_flags": "none", "issue_type": "dent",
        "object_part": "door", "claim_status": "supported",
        "claim_status_justification": "good match", "supporting_image_ids": "none",
        "valid_image": "true", "severity": "low",
    }
    base.update(overrides)
    return base


class TestSubmissionCritic:
    def test_clean_row_unchanged(self):
        rows = [_row()]
        result = validate_output_rows(rows)
        assert result[0]["claim_status"] == "supported"
        assert result[0]["risk_flags"] == "none"

    def test_supported_with_none_damage_contradicted(self):
        rows = [_row(claim_status="supported", issue_type="none")]
        result = validate_output_rows(rows)
        assert result[0]["claim_status"] == "contradicted"

    def test_supported_with_unknown_damage_not_enough(self):
        rows = [_row(claim_status="supported", issue_type="unknown")]
        result = validate_output_rows(rows)
        assert result[0]["claim_status"] == "not_enough_information"

    def test_supported_with_claim_mismatch_flag_contradicted(self):
        rows = [_row(claim_status="supported", risk_flags="claim_mismatch")]
        result = validate_output_rows(rows)
        assert result[0]["claim_status"] == "contradicted"

    def test_critical_flag_adds_manual_review(self):
        rows = [_row(claim_status="supported", issue_type="dent",
                     risk_flags="possible_manipulation")]
        result = validate_output_rows(rows)
        assert "manual_review_required" in result[0]["risk_flags"]

    def test_unknown_issue_without_flag_adds_review(self):
        rows = [_row(claim_status="supported", issue_type="unknown", risk_flags="none")]
        result = validate_output_rows(rows)
        assert "manual_review_required" in result[0]["risk_flags"]

    def test_empty_fields_filled(self):
        rows = [{"user_id": "test", "image_paths": "", "user_claim": "",
                 "claim_object": "", "evidence_standard_met": "",
                 "evidence_standard_met_reason": "", "risk_flags": "",
                 "issue_type": "", "object_part": "", "claim_status": "",
                 "claim_status_justification": "", "supporting_image_ids": "",
                 "valid_image": "", "severity": ""}]
        result = validate_output_rows(rows)
        for field in submission_critic.REQUIRED_FIELDS:
            assert field in result[0]
