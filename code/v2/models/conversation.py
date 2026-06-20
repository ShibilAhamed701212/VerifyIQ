from dataclasses import dataclass, field


@dataclass
class ConversationAnomaly:
    anomaly_type: str
    description: str
    severity: str = "low"
    span: tuple[int, int] = (0, 0)


@dataclass
class ConversationReport:
    has_contradictions: bool = False
    has_negation: bool = False
    has_retraction: bool = False
    has_uncertainty: bool = False
    has_sarcasm: bool = False
    has_changing_claims: bool = False
    anomalies: list[ConversationAnomaly] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
