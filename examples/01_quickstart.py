"""VerifyIQ Quickstart — parse a claim and evaluate it with the V1 rule engine."""

try:
    from verifyiq.v1 import Config, RuleEngine, ClaimParser
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
    from config import Config
    from rule_engine import RuleEngine
    from claim_parser import ClaimParser


def main():
    config = Config()
    parser = ClaimParser(config)
    rule_engine = RuleEngine()

    claim_text = "I noticed a crack on my windshield"
    claim_object = "car"

    parser_result = parser.parse(claim_text, claim_object)
    print(f"Parsed claim: damage_type={parser_result['claimed_damage_type']}, "
          f"object_part={parser_result['claimed_object_part']}")

    vision_result = {
        "damage_type": "crack",
        "object_part": "windshield",
        "damage_visible": True,
        "confidence": 0.92,
        "supporting_images": ["img_1"],
        "image_assessments": [{
            "image_id": "img_1", "damage_visible": True,
            "damage_type": "crack", "object_part": "windshield",
            "is_clear": True, "is_cropped": False,
            "lighting_adequate": True, "angle_sufficient": True,
            "confidence": 0.92, "image_quality": "good",
            "issues_visible": ["crack"], "affected_parts": ["windshield"],
        }],
        "per_image_assessments": [{
            "image_id": "img_1", "damage_visible": True,
            "damage_type": "crack", "object_part": "windshield",
            "is_clear": True, "is_cropped": False,
            "lighting_adequate": True, "angle_sufficient": True,
            "confidence": 0.92, "image_quality": "good",
        }],
        "conflicting_images": False,
        "notes": "",
        "image_quality": "good",
    }

    evidence_result = {
        "evidence_standard_met": True,
        "evidence_standard_met_reason": "Requirement met: sufficient image quality.",
        "reason": "Requirement met: sufficient image quality.",
        "requirement_text": "Images should clearly show the claimed object and relevant part.",
        "valid_image": True,
    }

    rule_result = rule_engine.evaluate(parser_result, vision_result, evidence_result)
    print(f"Rule decision: {rule_result['claim_status']}")
    print(f"Justification: {rule_result['justification']}")
    print(f"Confidence: {rule_result['confidence']:.2f}")


if __name__ == "__main__":
    main()
