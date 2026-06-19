"""
OCR text detector using pytesseract.
"""

import pytesseract
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class TextDetector:
    """Detects text in images using Tesseract OCR."""

    def __init__(self, min_text_length: int = 3, confidence_threshold: int = 30):
        self.min_text_length = min_text_length
        self.confidence_threshold = confidence_threshold

    def contains_text(self, image_path: Path) -> bool:
        if not image_path.exists():
            return False
        data = pytesseract.image_to_data(str(image_path), output_type=pytesseract.Output.DICT)
        for i, conf in enumerate(data["conf"]):
            try:
                conf_val = int(conf)
            except (ValueError, TypeError):
                continue
            text = (data["text"][i] or "").strip()
            if conf_val > self.confidence_threshold and len(text) >= self.min_text_length:
                return True
        return False

    def has_text_images(self, image_paths: list) -> list:
        results = []
        for p in image_paths:
            results.append({
                "image_id": p.stem,
                "contains_text": self.contains_text(p),
            })
        return results
