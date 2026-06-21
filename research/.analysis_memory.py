import sys, os
sys.path.insert(0, "code")
sys.path.insert(0, "code/v2")

import inspect

def count_module(mod):
    classes = 0
    funcs = 0
    for name in dir(mod):
        obj = getattr(mod, name)
        if inspect.isclass(obj): classes += 1
        elif inspect.isfunction(obj): funcs += 1
    return classes, funcs

# V1 Modules
import config, claim_parser, rule_engine, risk_analyzer, evidence_checker
import severity_engine, decision_agent, output_validator, utils, image_validator
v1 = [
    ("config", config), ("claim_parser", claim_parser), ("rule_engine", rule_engine),
    ("risk_analyzer", risk_analyzer), ("evidence_checker", evidence_checker),
    ("severity_engine", severity_engine), ("decision_agent", decision_agent),
    ("output_validator", output_validator), ("utils", utils), ("image_validator", image_validator),
]

print("=== V1 Module Complexity ===")
print(f"  {'Module':20s} {'Classes':8s} {'Functions':10s}")
for name, mod in v1:
    c, f = count_module(mod)
    print(f"  {name:20s} {c:<8d} {f:<10d}")

# V2 Modules
import sys
sys.path.insert(0, "code/v2")
from code.v2.conversation.analyzer import ConversationAnalyzer
from code.v2.confidence.calibrator import ConfidenceCalibrator
from code.v2.consensus.engine import ConsensusEngine
from code.v2.critic.v2_critic import V2Critic
from code.v2.evidence.recommender import EvidenceRecommender
from code.v2.explainability.tracer import DecisionTracer
from code.v2.security.sanitizer import InputSanitizer
from code.v2.observability.metrics import MetricsCollector
from code.v2.observability.tracing import TraceLogger
from code.v2.risk_merger import RiskMerger
from code.v2.v1_adapter import V1RuleAdapter, V1RiskAdapter
from code.v2.pipeline import V2Pipeline

v2 = [
    ("conversation.analyzer", ConversationAnalyzer),
    ("confidence.calibrator", ConfidenceCalibrator),
    ("consensus.engine", ConsensusEngine),
    ("critic.v2_critic", V2Critic),
    ("evidence.recommender", EvidenceRecommender),
    ("explainability.tracer", DecisionTracer),
    ("security.sanitizer", InputSanitizer),
    ("observability.metrics", MetricsCollector),
    ("risk_merger", RiskMerger),
    ("v1_adapter (V1RuleAdapter)", V1RuleAdapter),
    ("pipeline", V2Pipeline),
]

print()
print("=== V2 Module Complexity ===")
print(f"  {'Module':35s} {'Classes':8s} {'Functions':10s}")
for name, mod in v2:
    c, f = count_module(mod)
    print(f"  {name:35s} {c:<8d} {f:<10d}")

# File sizes
print()
print("=== File Size Distribution ===")
sizes = []
for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".py") and "__pycache__" not in root:
            path = os.path.join(root, f)
            sizes.append(os.path.getsize(path))

sizes.sort()
print(f"  Total Python files: {len(sizes)}")
print(f"  Total bytes: {sum(sizes):,}")
print(f"  Avg bytes/file: {sum(sizes)//len(sizes):,}")
print(f"  Median bytes: {sizes[len(sizes)//2]:,}")
print(f"  Largest: {sizes[-1]:,}")
print(f"  Smallest (non-empty): {sizes[0]:,}")
print(f"  Empty files: {sum(1 for s in sizes if s == 0)}")

# Count .md files
md_count = 0
md_bytes = 0
for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".md") and "__pycache__" not in root:
            path = os.path.join(root, f)
            s = os.path.getsize(path)
            md_count += 1
            md_bytes += s
print(f"\n  Total .md files: {md_count}")
print(f"  Total .md bytes: {md_bytes:,}")

try:
    import psutil
    proc = psutil.Process(os.getpid())
    print(f"\n=== Process Memory ===")
    print(f"  RSS: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
    print(f"  VMS: {proc.memory_info().vms / 1024 / 1024:.1f} MB")
except ImportError:
    print("\npsutil not available")
    print(f"  Python process PID: {os.getpid()}")
