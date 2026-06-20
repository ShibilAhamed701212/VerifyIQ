"""VerifyIQ V1 — Deterministic claim verification pipeline.

This module wraps the original competition V1 pipeline (code/).
No V1 files are modified — all imports reference the canonical location.
"""

import sys as _sys
from pathlib import Path as _Path

_CODE_DIR = str(_Path(__file__).resolve().parent.parent.parent / "code")
if _CODE_DIR not in _sys.path:
    _sys.path.insert(0, _CODE_DIR)

from code.config import Config
from code.rule_engine import RuleEngine
from code.severity_engine import SeverityEngine
from code.evidence_checker import EvidenceChecker
from code.claim_parser import ClaimParser
from code.risk_analyzer import RiskAnalyzer
from code.output_validator import OutputValidator
from code.decision_agent import DecisionAgent
from code.image_validator import validate_images, any_valid_images, all_images_valid
from code.claim_processor import ClaimProcessor

__all__ = [
    "Config",
    "RuleEngine",
    "SeverityEngine",
    "EvidenceChecker",
    "ClaimParser",
    "RiskAnalyzer",
    "OutputValidator",
    "DecisionAgent",
    "validate_images",
    "any_valid_images",
    "all_images_valid",
    "ClaimProcessor",
]
