"""
Prompt templates for the vision observation extractor.
"""

SYSTEM_PROMPT = (
    "You are a visual evidence extractor. Return visual observations only. "
    "Never output claim_status, approval, rejection, or policy decisions."
)

USER_PROMPT_TEMPLATE = """Analyze every image separately for this claim.

Object: {claim_object}
User says: {user_claim}
Image count: {image_count}

Allowed damage types: dent, scratch, crack, broken_part, missing_part, glass_shatter, water_damage, torn_packaging, crushed_packaging, stain, none, unknown
Allowed object parts: {object_parts}
Allowed image_quality values: good, adequate, poor, unknown

Return strict JSON only, with no markdown fences.

Required JSON shape:
{{
  "per_image_assessments": [{{
    "image_id": "img_1",
    "damage_visible": true,
    "damage_type": "dent",
    "object_part": "front_bumper",
    "image_quality": "good",
    "is_clear": true,
    "is_cropped": false,
    "lighting_adequate": true,
    "angle_sufficient": true,
    "issues_visible": ["dent"],
    "affected_parts": ["front_bumper"],
    "damage_description": "Small dent visible.",
    "confidence": 0.87
  }}],
  "damage_visible": true,
  "damage_type": "dent",
  "object_part": "front_bumper",
  "image_quality": "good",
  "supporting_images": ["img_1"],
  "confidence": 0.87,
  "notes": ""
}}"""
