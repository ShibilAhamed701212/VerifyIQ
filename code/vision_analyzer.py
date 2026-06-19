"""
Vision LLM client using Google Gemini (free tier).
Reads images, sends to Gemini with structured JSON output, returns normalized analysis.
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import List, Dict, Any

from google import genai
from google.genai import types

from config import Config
from utils import get_image_id_from_path

logger = logging.getLogger("evidence_review.vision")


class GeminiVisionClient:

    def __init__(self, config: Config):
        self.config = config
        api_key = config.api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment or config.")
        self.client = genai.Client(api_key=api_key)
        self.model = config.vision_model

    def analyze_images(
        self,
        image_paths: List[Path],
        user_claim: str,
        claim_object: str,
        object_parts: List[str],
    ) -> Dict[str, Any]:
        if not image_paths:
            return self._empty_analysis("No images provided.")

        from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

        prompt = USER_PROMPT_TEMPLATE.format(
            claim_object=claim_object,
            user_claim=user_claim[:500],
            image_count=len(image_paths),
            object_parts=", ".join(object_parts),
        )

        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

        parts = [types.Part.from_text(text=full_prompt)]

        for img_path in image_paths[:self.config.max_images_per_claim]:
            if not img_path.exists():
                logger.warning(f"Image not found: {img_path}")
                continue
            try:
                data = img_path.read_bytes()
                mime = self._get_mime(img_path)
                parts.append(types.Part.from_bytes(data=data, mime_type=mime))
            except Exception as e:
                logger.error(f"Failed to read image {img_path}: {e}")

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=types.Content(role="user", parts=parts),
                    config=types.GenerateContentConfig(
                        temperature=self.config.temperature,
                        response_mime_type="application/json",
                    ),
                )
                time.sleep(2)
                break
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    wait = 2 ** attempt * 5
                    logger.warning(f"Rate limited, retrying in {wait}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                else:
                    logger.error(f"Gemini API call failed: {e}")
                    return self._empty_analysis(f"API error: {str(e)[:100]}")
        else:
            logger.error("Max retries exceeded for Gemini API")
            return self._empty_analysis("API rate limit exceeded after retries")

        return self._parse_response(response, image_paths)

    def _parse_response(self, response, image_paths: List[Path]) -> Dict[str, Any]:
        text = response.text if hasattr(response, "text") and response.text else ""

        if not text:
            return self._empty_analysis("Empty response from Gemini")

        try:
            json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_match = re.search(r"\{[\s\S]*\}", text)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    json_str = text

            analysis = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            return self._empty_analysis(f"JSON parsing error: {str(e)[:100]}")

        return self._normalize_analysis(analysis, image_paths)

    def _normalize_analysis(self, analysis: Dict, image_paths: List[Path]) -> Dict[str, Any]:
        image_ids = [get_image_id_from_path(p) for p in image_paths]

        default = {
            "image_assessments": [],
            "overall_issue_type": "unknown",
            "overall_object_part": "unknown",
            "claim_supported": False,
            "supporting_image_ids": [],
            "contradiction_reason": None,
            "severity": "unknown",
            "confidence": 0.0,
            "notes": "",
        }

        result = default.copy()
        for key in default:
            if key in analysis and analysis[key] is not None:
                result[key] = analysis[key]

        if not isinstance(result["image_assessments"], list):
            result["image_assessments"] = []

        if not isinstance(result["supporting_image_ids"], list):
            result["supporting_image_ids"] = []

        result["supporting_image_ids"] = [
            img_id for img_id in result["supporting_image_ids"]
            if img_id in image_ids
        ]

        result["claim_supported"] = self._to_bool(result.get("claim_supported", False))

        for assessment in result["image_assessments"]:
            for field in ("is_clear", "is_cropped", "lighting_adequate", "angle_sufficient"):
                if field in assessment:
                    assessment[field] = self._to_bool(assessment[field])

        if result["claim_supported"] and not result["supporting_image_ids"]:
            for assessment in result["image_assessments"]:
                if assessment.get("is_clear", False) and assessment.get("issues_visible", []):
                    result["supporting_image_ids"].append(assessment.get("image_id", ""))
                    break

        return result

    def _to_bool(self, value) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "y", "clear", "good", "1", "adequate", "sufficient")
        if isinstance(value, (int, float)):
            return value > 0
        return False

    def _empty_analysis(self, reason: str) -> Dict[str, Any]:
        return {
            "image_assessments": [],
            "overall_issue_type": "unknown",
            "overall_object_part": "unknown",
            "claim_supported": False,
            "supporting_image_ids": [],
            "contradiction_reason": reason,
            "severity": "unknown",
            "confidence": 0.0,
            "notes": f"Analysis failed: {reason}",
        }

    def _get_mime(self, path: Path) -> str:
        ext = path.suffix.lower()
        mime_map = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png", ".gif": "image/gif",
            ".webp": "image/webp", ".bmp": "image/bmp",
        }
        return mime_map.get(ext, "image/jpeg")


def analyze_images(
    image_paths: List[Path],
    user_claim: str,
    claim_object: str,
    config: Config,
) -> Dict[str, Any]:
    client = GeminiVisionClient(config)
    object_parts = list(config.ALLOWED_OBJECT_PARTS.get(claim_object, ["unknown"]))
    return client.analyze_images(image_paths, user_claim, claim_object, object_parts)
