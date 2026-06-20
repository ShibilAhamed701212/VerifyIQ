from dataclasses import dataclass, field


@dataclass
class ConfidenceBreakdown:
    model_confidence: float = 0.0
    agreement_contribution: float = 0.0
    fraud_penalty: float = 0.0
    evidence_boost: float = 0.0
    conversation_penalty: float = 0.0


@dataclass
class ConfidenceReport:
    final_confidence: float = 0.0
    routing: str = "evidence_request"
    breakdown: ConfidenceBreakdown = field(default_factory=ConfidenceBreakdown)
    calibrator_version: str = "v2.0"
