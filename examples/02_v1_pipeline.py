"""VerifyIQ V1 Pipeline — run a claim through the full deterministic pipeline."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))

from config import Config
from claim_parser import ClaimParser
from evidence_checker import EvidenceChecker
from rule_engine import RuleEngine
from severity_engine import SeverityEngine
from output_validator import OutputValidator
from decision_agent import DecisionAgent
from utils import parse_image_paths


def main():
    config = Config()
    parser = ClaimParser(config)
    checker = EvidenceChecker(config.evidence_reqs_path)
    rule = RuleEngine()
    val = OutputValidator(config)
    sev = SeverityEngine()
    agent = DecisionAgent(val, sev)

    sample_path = config.sample_claims_path
    print(f"Loading sample claims from: {sample_path}")
    print(f"Evidence requirements from: {config.evidence_reqs_path}")
    print()

    with open(sample_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("No sample claims found.")
        return

    row = rows[0]
    uid = row["user_id"]
    user_claim = row.get("user_claim", "").strip()
    claim_object = row.get("claim_object", "").strip().lower()
    image_paths_str = row.get("image_paths", "").strip()
    image_paths = parse_image_paths(image_paths_str, config.images_dir)

    print(f"Processing claim: {uid}")
    print(f"  Object: {claim_object}")
    print(f"  Images: {len(image_paths)}")
    print(f"  Claim:  {user_claim[:80]}...")
    print()

    parser_result = parser.parse(user_claim, claim_object)
    print(f"Parsed: damage_type={parser_result['claimed_damage_type']}, "
          f"object_part={parser_result['claimed_object_part']}")
    print()

    expected_damage_type = row.get("issue_type", "unknown")
    expected_object_part = row.get("object_part", "unknown")
    expected_risk = row.get("risk_flags", "")

    dv = "damage_not_visible" not in expected_risk and expected_damage_type not in ("none", "")
    no_angle = "wrong_angle" in expected_risk
    no_obstruct = "cropped_or_obstructed" in expected_risk
    no_original = "non_original_image" in expected_risk
    wrong_obj = "wrong_object" in expected_risk

    assessments_list = [{
        "image_id": p.stem, "damage_visible": dv,
        "damage_type": expected_damage_type, "object_part": expected_object_part,
        "is_clear": True,
        "is_cropped": no_obstruct,
        "lighting_adequate": True,
        "angle_sufficient": not no_angle,
        "confidence": 0.85,
        "image_quality": "good",
        "issues_visible": [expected_damage_type] if dv else [],
        "affected_parts": [expected_object_part]
                         if expected_object_part not in ("unknown", "") else [],
        "damage_description": "",
    } for p in image_paths] if image_paths else []

    vision = {
        "damage_type": expected_damage_type,
        "object_part": expected_object_part,
        "damage_visible": dv,
        "confidence": 0.85,
        "supporting_images": [p.stem for p in image_paths],
        "image_assessments": assessments_list,
        "per_image_assessments": assessments_list,
        "conflicting_images": False,
        "notes": "non-original" if no_original else (
            "wrong object" if wrong_obj else ""),
        "image_quality": "good",
    }

    evidence_result = checker.evaluate(
        claim_object=claim_object,
        parser_result=parser_result,
        vision_result=vision,
        total_images=len(image_paths),
    )
    print(f"Evidence standard met: {evidence_result['evidence_standard_met']}")
    print(f"  {evidence_result['evidence_standard_met_reason']}")
    print()

    rule_result = rule.evaluate(parser_result, vision, evidence_result)
    print(f"Rule decision: {rule_result['claim_status']}")
    print(f"  {rule_result['justification']}")
    print()

    claim_input = {
        "user_id": uid,
        "image_paths": image_paths_str,
        "user_claim": user_claim,
        "claim_object": claim_object,
    }
    output = agent.build_output_row(
        claim_input, parser_result, vision,
        evidence_result, rule_result, ["none"],
    )

    print("Output row:")
    for key in config.ALLOWED_OBJECT_PARTS.get(claim_object, {}) | {
        "claim_status", "issue_type", "object_part", "severity",
        "risk_flags", "evidence_standard_met", "valid_image",
    }:
        if key in output:
            print(f"  {key}: {output[key]}")
    print()
    print("Match with expected:", all(
        output.get(f) == row.get(f)
        for f in ["evidence_standard_met", "issue_type", "object_part",
                   "claim_status", "valid_image", "severity"]
    ))


if __name__ == "__main__":
    main()
