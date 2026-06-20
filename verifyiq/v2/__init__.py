"""VerifyIQ V2 — Production-grade multimodal claim verification pipeline.

This module wraps the original V2 pipeline (code/v2/).
No V2 files are modified — all imports reference the canonical location.
"""

import sys as _sys
from pathlib import Path as _Path

_CODE_DIR = str(_Path(__file__).resolve().parent.parent.parent / "code")
if _CODE_DIR not in _sys.path:
    _sys.path.insert(0, _CODE_DIR)

from code.v2.pipeline import V2Pipeline
from code.v2.v1_adapter import V1RuleAdapter, V1SeverityAdapter, V1EvidenceAdapter, V1ParserAdapter
from code.v2.models.decision import V2Decision
from code.v2.models.observation import ObservationReport, Observation, PerImageAssessment
from code.v2.models.evidence import EvidenceReport, EvidenceRecommendation
from code.v2.models.fraud import FraudReport, ImageFraudResult, MetadataFraudResult, BehavioralFraudResult
from code.v2.models.conversation import ConversationReport
from code.v2.models.consensus import ConsensusReport
from code.v2.models.confidence import ConfidenceReport, ConfidenceBreakdown
from code.v2.conversation.analyzer import ConversationAnalyzer
from code.v2.confidence.calibrator import ConfidenceCalibrator
from code.v2.evidence.recommender import EvidenceRecommender
from code.v2.critic.v2_critic import V2Critic
from code.v2.explainability.tracer import DecisionTracer
from code.v2.observability.metrics import MetricsCollector
from code.v2.observability.tracing import TraceLogger
from code.v2.security.sanitizer import InputSanitizer
from code.v2.consensus.engine import ConsensusEngine
from code.v2.fraud.image_fraud import ImageFraudDetector
from code.v2.fraud.metadata_fraud import MetadataFraudDetector
from code.v2.fraud.behavioral_fraud import BehavioralFraudDetector

__all__ = [
    "V2Pipeline",
    "V1RuleAdapter",
    "V1SeverityAdapter",
    "V1EvidenceAdapter",
    "V1ParserAdapter",
    "V2Decision",
    "ObservationReport", "Observation", "PerImageAssessment",
    "EvidenceReport", "EvidenceRecommendation",
    "FraudReport", "ImageFraudResult", "MetadataFraudResult", "BehavioralFraudResult",
    "ConversationReport",
    "ConsensusReport",
    "ConfidenceReport", "ConfidenceBreakdown",
    "ConversationAnalyzer",
    "ConfidenceCalibrator",
    "EvidenceRecommender",
    "V2Critic",
    "DecisionTracer",
    "MetricsCollector",
    "TraceLogger",
    "InputSanitizer",
    "ConsensusEngine",
    "ImageFraudDetector",
    "MetadataFraudDetector",
    "BehavioralFraudDetector",
]
