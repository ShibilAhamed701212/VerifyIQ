import sys, time, csv
sys.path.insert(0, "code")
sys.path.insert(0, "code/v2")

from code.v2.v1_adapter import V1RuleAdapter, V1RiskAdapter
from code.v2.conversation.analyzer import ConversationAnalyzer
from code.v2.confidence.calibrator import ConfidenceCalibrator
from code.v2.consensus.engine import ConsensusEngine
from code.v2.risk_merger import RiskMerger
from code.v2.models.decision import V2Decision
from code.v2.models.observation import ObservationReport, Observation, PerImageAssessment
from code.v2.models.fraud import FraudReport
from code.v2.models.evidence import EvidenceReport
from code.v2.models.conversation import ConversationReport
from code.v2.models.consensus import ConsensusReport
from config import Config
from claim_parser import ClaimParser

config = Config()
rows = []
with open(config.sample_claims_path, encoding="utf-8") as f:
    for r in csv.DictReader(f): rows.append(r)

user_history_cache = {}
if config.user_history_path.exists():
    with open(config.user_history_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            u = r.get("user_id", "").strip()
            if u: user_history_cache[u] = r

row = rows[3]
uid = row["user_id"]
dt = row["issue_type"]
op = row["object_part"]
exp = row.get("risk_flags", "")
user_claim = row.get("user_claim", "")
claim_object = row.get("claim_object", "").strip().lower()
dv = "damage_not_visible" not in exp and dt not in ("none", "")

t = time.time
times = {}

t0 = t()
parser = ClaimParser(config)
parsed = parser.parse(user_claim, claim_object)
times["parsing"] = t() - t0

t0 = t()
conv = ConversationAnalyzer().analyze(user_claim)
times["conversation"] = t() - t0

t0 = t()
consensus = ConsensusEngine().evaluate(
    ObservationReport(observations=[], all_failed=False, primary_model="ideal"))
times["consensus"] = t() - t0

t0 = t()
fraud = FraudReport(flags=[])
times["fraud_init"] = t() - t0

t0 = t()
evidence = EvidenceReport(evidence_standard_met=False, reason="test")
times["evidence"] = t() - t0

t0 = t()
confidence = ConfidenceCalibrator().calibrate(consensus, fraud, evidence, conv)
times["confidence"] = t() - t0

t0 = t()
rule_ada = V1RuleAdapter()
v1_result = rule_ada.evaluate({
    "damage_type": parsed.get("claimed_damage_type", "unknown"),
    "object_part": parsed.get("claimed_object_part", "unknown"),
    "evidence_standard_met": evidence.evidence_standard_met,
    "damage_visible": dv, "visible_damage_type": dt, "visible_object_part": op,
    "confidence": 0.85,
})
times["rule_engine"] = t() - t0

t0 = t()
risk_ada = V1RiskAdapter()
v1_risk = risk_ada.analyze(
    image_analysis={"damage_type": dt, "object_part": op, "damage_visible": dv, "confidence": 0.85},
    user_history=user_history_cache.get(uid), claim_object=claim_object,
    user_claim=user_claim, image_paths=None,
)
times["risk_analyzer"] = t() - t0

t0 = t()
merger = RiskMerger("hybrid")
merged = merger.merge(v1_result.get("risk_flags", []), v1_risk, fraud.flags, conv.risk_flags)
times["risk_merger"] = t() - t0

t0 = t()
for _ in range(1000):
    _ = RiskMerger("hybrid").merge(v1_result.get("risk_flags", []), v1_risk, fraud.flags, conv.risk_flags)
times["risk_merger_1000x"] = t() - t0

print("=== Per-Phase Latency (1 claim, user_004) ===")
for k, v in sorted(times.items()):
    print(f"  {k:25s}: {v*1000:8.3f}ms")
total = sum(times.values())
print(f"  {'Total':25s}: {total*1000:8.3f}ms")
print(f"  RiskMerger per-call: {times['risk_merger_1000x']*1000:.3f}ms avg over 1000")
