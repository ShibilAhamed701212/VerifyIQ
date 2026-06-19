"""
Evidence requirements checking based on the evidence_requirements.csv.
"""

from pathlib import Path
from typing import Dict, List, Tuple

from utils import safe_csv_read


class EvidenceRequirements:

    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.requirements: List[Dict] = []
        self._loaded = False
        self._index: Dict[str, List[Dict]] = {}

    def load(self) -> None:
        if self._loaded:
            return

        rows = safe_csv_read(self.csv_path)
        self.requirements = []

        for row in rows:
            req = {
                "requirement_id": row.get("requirement_id", "").strip(),
                "claim_object": row.get("claim_object", "").strip().lower(),
                "applies_to": row.get("applies_to", "").strip().lower(),
                "minimum_image_evidence": self._parse_int(row.get("minimum_image_evidence", "0")),
            }
            self.requirements.append(req)

        self._index = {}
        for req in self.requirements:
            key = (req["claim_object"], req["applies_to"])
            if key not in self._index:
                self._index[key] = []
            self._index[key].append(req)

        self._loaded = True

    def _parse_int(self, value: str) -> int:
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def get_minimum_evidence(self, claim_object: str, issue_type: str) -> int:
        self.load()

        claim_object = claim_object.lower()
        issue_type = issue_type.lower()

        key = (claim_object, issue_type)
        if key in self._index:
            return max(req["minimum_image_evidence"] for req in self._index[key])

        key_all = ("all", issue_type)
        if key_all in self._index:
            return max(req["minimum_image_evidence"] for req in self._index[key_all])

        key_unknown = (claim_object, "unknown")
        if key_unknown in self._index:
            return max(req["minimum_image_evidence"] for req in self._index[key_unknown])

        return 1

    def meets_standard(
        self,
        claim_object: str,
        issue_type: str,
        supporting_image_ids: List[str],
        total_images: int,
    ) -> Tuple[bool, str]:
        min_required = self.get_minimum_evidence(claim_object, issue_type)

        if min_required == 0:
            return True, "No minimum evidence required for this issue type."

        if total_images == 0:
            return False, "No images submitted."

        supporting_count = len(supporting_image_ids)

        if supporting_count >= min_required:
            return True, f"Found {supporting_count} supporting image(s), meeting the minimum of {min_required}."
        else:
            return False, f"Only {supporting_count} supporting image(s) found, but {min_required} are required."
