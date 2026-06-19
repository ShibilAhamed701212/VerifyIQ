"""
Deterministic claim parser.

Extracts the claimed damage type and object part from the user conversation
using normalization, keyword matching, and simple regex-friendly phrase checks.
"""

from typing import Dict

from config import Config
from utils import normalize_text, extract_claim_text


class ClaimParser:
    """Parses user claim text into normalized challenge enum values."""

    def __init__(self, config: Config):
        self.config = config

    def parse(self, user_claim: str, claim_object: str) -> Dict[str, str]:
        claim_text = extract_claim_text(user_claim) or user_claim or ""
        text = normalize_text(claim_text)
        claim_object = (claim_object or "").lower()

        return {
            "claimed_damage_type": self._damage_type(text),
            "claimed_object_part": self._object_part(text, claim_object),
            "claim_text": claim_text,
        }

    def _damage_type(self, text: str) -> str:
        patterns = [
            ("glass_shatter", ["shatter", "shattered", "smashed glass", "broken glass"]),
            ("water_damage", ["water damage", "water", "wet", "moisture", "liquid", "spill"]),
            ("torn_packaging", ["torn", "ripped", "tear"]),
            ("crushed_packaging", ["crushed", "crush", "dented box"]),
            ("broken_part", ["broken", "broke", "snapped", "not working"]),
            ("missing_part", ["missing", "lost", "gone"]),
            ("scratch", ["scratch", "scrape", "scraped", "scuff", "mark"]),
            ("crack", ["crack", "cracked", "fracture"]),
            ("dent", ["dent", "dented", "deformation"]),
            ("stain", ["stain", "stained", "discoloration"]),
        ]
        for damage_type, keywords in patterns:
            if any(keyword in text for keyword in keywords):
                return damage_type
        return "unknown"

    def _object_part(self, text: str, claim_object: str) -> str:
        part_keywords = {
            "car": [
                ("front_bumper", ["front bumper", "bumper front", "front side"]),
                ("rear_bumper", ["rear bumper", "back bumper", "rear side", "back of the car"]),
                ("side_mirror", ["side mirror", "mirror"]),
                ("windshield", ["windshield", "windscreen", "front glass"]),
                ("headlight", ["headlight", "head light"]),
                ("taillight", ["taillight", "tail light"]),
                ("quarter_panel", ["quarter panel"]),
                ("fender", ["fender"]),
                ("door", ["door", "door panel"]),
                ("hood", ["hood", "bonnet"]),
                ("body", ["body", "panel"]),
            ],
            "laptop": [
                ("screen", ["screen", "display"]),
                ("keyboard", ["keyboard", "keycap", "keys"]),
                ("trackpad", ["trackpad", "touchpad"]),
                ("hinge", ["hinge"]),
                ("lid", ["lid", "top cover"]),
                ("corner", ["corner", "edge"]),
                ("port", ["port", "charging slot", "usb"]),
                ("base", ["base", "bottom"]),
                ("body", ["body", "casing", "chassis"]),
            ],
            "package": [
                ("package_corner", ["corner"]),
                ("package_side", ["side"]),
                ("seal", ["seal", "tape", "flap"]),
                ("label", ["label", "sticker", "barcode"]),
                ("contents", ["contents", "inside", "interior"]),
                ("item", ["item", "product"]),
                ("box", ["box", "package", "carton"]),
            ],
        }

        for part, keywords in part_keywords.get(claim_object, []):
            if any(keyword in text for keyword in keywords):
                return part
        return "unknown"
