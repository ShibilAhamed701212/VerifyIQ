"""
Prompt templates for the Vision LLM.
"""

SYSTEM_PROMPT = "You are a damage claim verifier. Classify visible damage from images."

USER_PROMPT_TEMPLATE = """Analyse image(s) for this claim.

Object: {claim_object}
User says: {user_claim}

**Allowed issue types:** dent, scratch, crack, glass_shatter, broken_part, missing_part, torn_packaging, crushed_packaging, water_damage, stain, none, unknown
**Allowed object parts:** {object_parts}
**Severity:** none, low, medium, high, unknown

**Rules for claim_supported:**
- true = damage EXISTS in the claimed area, even if exact type differs (e.g. user says scratch, you see dent → true)
- true = the claim is broadly correct about there being damage
- false = ONLY if the relevant area is completely undamaged/pristine
- false = ONLY if damage is on a completely different object part

Return JSON with booleans as true/false, not strings:
{{
  "image_assessments": [{{
    "image_id": "img_1",
    "is_clear": true,
    "is_cropped": false,
    "lighting_adequate": true,
    "angle_sufficient": true,
    "issues_visible": ["dent"],
    "affected_parts": ["front_bumper"],
    "damage_description": "Small dent visible."
  }}],
  "overall_issue_type": "dent",
  "overall_object_part": "front_bumper",
  "claim_supported": true,
  "supporting_image_ids": ["img_1"],
  "contradiction_reason": null,
  "severity": "low",
  "confidence": 0.9,
  "notes": ""
}}"""
