"""Reality test v3: Verify the fix — no more misleading messages."""
import os, json
from pathlib import Path

os.environ["GEMINI_API_KEY"] = "test_key"
os.environ["VERIFYIQ_MODE"] = "demo"

from code.v2.pipeline import V2Pipeline
from code.v2.observability.metrics import get_collector

BASE = Path(__file__).parent / "dataset" / "images" / "sample"

test_cases = [
    ("dent on bumper", "/case_001/img_1.jpg", "car"),
    ("cracked windshield", "/case_003/img_1.jpg", "car"),
    ("laptop screen cracked", "/case_019/img_1.jpg", "laptop"),
    ("crushed package", "/case_017/img_1.jpg", "package"),
    ("vague damage", "/case_007/img_1.jpg", "car"),
    ("User: Something is broken", "/case_003/img_1.jpg", "laptop"),
    ("contradictory", "/case_004/img_1.jpg", "package"),
]

pipeline = V2Pipeline(config={"providers": {}})
print(f"Vision state: {pipeline.vision_manager.state.value}")
print(f"Vision mode: {pipeline.vision_manager.mode.value}")
print()

for text, rel_path, obj in test_cases:
    img_path = str(BASE / rel_path.lstrip("/"))
    if not os.path.isfile(img_path):
        print(f"MISSING: {img_path}")
        continue
    get_collector().reset()
    decision = pipeline.process(claim_text=text, image_paths=[img_path], claim_object=obj)
    has_misleading = "no images were submitted" in decision.justification.lower()
    has_honest = "image analysis temporarily unavailable" in decision.justification.lower()
    has_vision_flag = "vision_unavailable" in decision.risk_flags

    print(f"Claim: {text[:40]:40s}")
    print(f"  Status:     {decision.claim_status}")
    print(f"  Confidence: {decision.confidence:.2f}")
    print(f"  Flags:      {decision.risk_flags}")
    print(f"  Justification: {decision.justification[:120]}")
    print(f"  MISLEADING: {has_misleading}  |  HONEST: {has_honest}  |  VISION_FLAG: {has_vision_flag}")
    print()

# Verify production mode rejects
os.environ["VERIFYIQ_MODE"] = "production"
try:
    from code.v2.vision_manager import VisionUnavailableError
    p2 = V2Pipeline(config={"providers": {}})
    p2.vision_manager.ensure_vision(1)
    print("PRODUCTION MODE: DID NOT REJECT (BUG!)")
except VisionUnavailableError as e:
    print(f"PRODUCTION MODE: Correctly rejected with: {str(e)[:80]}...")

# Verify startup validator detects it
os.environ["VERIFYIQ_MODE"] = "demo"
from code.v2.startup_validator import StartupValidator
v = StartupValidator()
result = v.validate_vision_availability()
print(f"\nStartupValidator vision check: {result['status']} — {result['detail'][:100]}")
