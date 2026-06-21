"""Reality test v2: 50 claims with real sample images + fraud detection."""
import json, sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ["GEMINI_API_KEY"] = "test_key"

from code.v2.pipeline import V2Pipeline
from code.v2.observability.metrics import get_collector

BASE = Path(__file__).parent / "dataset" / "images" / "sample"

# Available images per case
IMG_POOL = sorted([str(p) for p in BASE.rglob("*.[jJ][pP][gG]")])
print(f"Found {len(IMG_POOL)} sample images")

# 50 claims — each with an existing sample image path
CLAIMS = [
    # === CARS 1-18 === (use images from car cases: 1-4, 6-10, 14-20)
    ("1", "There is a dent on my front bumper after I hit a pole.", "/case_001/img_1.jpg", "car", "dent", "user001"),
    ("2", "The rear bumper has a large scratch from a parking incident.", "/case_002/img_1.jpg", "car", "scratch", "user002"),
    ("3", "Windshield cracked after a rock hit it on the highway.", "/case_003/img_1.jpg", "car", "crack", "user003"),
    ("4", "My headlight is shattered after someone hit my car in the lot.", "/case_004/img_1.jpg", "car", "glass_shatter", "user004"),
    ("5", "The side mirror is completely broken off.", "/case_005/img_1.jpg", "car", "broken_part", "user005"),
    ("6", "Something is wrong with my car door.", "/case_006/img_1.jpg", "car", "unknown", "user006"),
    ("7", "The car got damaged somehow.", "/case_007/img_1.jpg", "car", "unknown", "user007"),
    ("8", "I need to file a claim for my vehicle.", "/case_008/img_1.jpg", "car", "unknown", "user008"),
    ("9", "There's some issue with the front area of the car.", "/case_009/img_1.jpg", "car", "unknown", "user009"),
    ("10", "My car was hit but I don't know where.", "/case_010/img_1.jpg", "car", "unknown", "user010"),
    ("11", "The hood is dented but there is absolutely no damage.", "/case_011/img_1.jpg", "car", "unknown", "user011"),
    ("12", "My windshield is both cracked and perfectly fine.", "/case_012/img_1.jpg", "car", "unknown", "user012"),
    ("13", "The front bumper needs replacement but nothing happened.", "/case_013/img_1.jpg", "car", "unknown", "user013"),
    ("14", "Taillight is shattered but the car is undamaged.", "/case_014/img_1.jpg", "car", "unknown", "user014"),
    ("15", "I scratched all four doors and the roof — cover everything.", "/case_015/img_1.jpg", "car", "scratch", "user015"),
    ("16", "Third claim this week. The fender is dented again.", "/case_016/img_1.jpg", "car", "dent", "user016"),
    ("17", "Crack just appeared. I hit nothing.", "/case_017/img_1.jpg", "car", "crack", "user017"),
    ("18", "Multiple dents everywhere. Total replacement needed.", "/case_018/img_1.jpg", "car", "dent", "user018"),
    # === LAPTOPS 19-36 ===
    ("19", "My laptop screen is cracked from the corner.", "/case_019/img_1.jpg", "laptop", "crack", "user019"),
    ("20", "The keyboard has a broken key from a spill.", "/case_020/img_1.jpg", "laptop", "broken_part", "user020"),
    # Reuse remaining images with different claims
    ("21", "The hinge snapped when I closed the lid.", "/case_001/img_1.jpg", "laptop", "broken_part", "user021"),
    ("22", "Water damaged the trackpad.", "/case_002/img_1.jpg", "laptop", "water_damage", "user022"),
    ("23", "Something is broken on my laptop.", "/case_003/img_1.jpg", "laptop", "unknown", "user023"),
    ("24", "The laptop screen area has an issue.", "/case_004/img_1.jpg", "laptop", "unknown", "user024"),
    ("25", "My device was damaged in shipping.", "/case_005/img_1.jpg", "laptop", "unknown", "user025"),
    ("26", "There might be a problem with the lid.", "/case_006/img_1.jpg", "laptop", "unknown", "user026"),
    ("27", "Screen is cracked but works fine with no visible damage.", "/case_007/img_1.jpg", "laptop", "unknown", "user027"),
    ("28", "Laptop is destroyed except it looks brand new.", "/case_008/img_1.jpg", "laptop", "unknown", "user028"),
    ("29", "Keyboard is missing keys. All keys are present.", "/case_009/img_1.jpg", "laptop", "unknown", "user029"),
    ("30", "Working before flight, broken after. I did not drop it.", "/case_010/img_1.jpg", "laptop", "unknown", "user030"),
    ("31", "Fifth claim this year. Screen cracked again.", "/case_011/img_1.jpg", "laptop", "crack", "user031"),
    ("32", "Water damage already there when I opened the box.", "/case_012/img_1.jpg", "laptop", "water_damage", "user032"),
    ("33", "Full replacement needed. Dents on every surface.", "/case_013/img_1.jpg", "laptop", "dent", "user033"),
    ("34", "Laptop stolen but I have pictures from before.", "/case_014/img_1.jpg", "laptop", "unknown", "user034"),
    ("35", "Coffee on keyboard last week. Some keys stick.", "/case_015/img_1.jpg", "laptop", "water_damage", "user035"),
    ("36", "Screen flickers. Might be loose connection.", "/case_016/img_1.jpg", "laptop", "unknown", "user036"),
    # === PACKAGES 37-50 ===
    ("37", "The box arrived crushed on the corner.", "/case_017/img_1.jpg", "package", "crushed_packaging", "user037"),
    ("38", "The package has a water stain from rain during delivery.", "/case_018/img_1.jpg", "package", "stain", "user038"),
    ("39", "The seal is torn and the contents fell out.", "/case_019/img_1.jpg", "package", "torn_packaging", "user039"),
    ("40", "The package side is completely crushed.", "/case_020/img_1.jpg", "package", "crushed_packaging", "user040"),
    ("41", "Something is wrong with the packaging.", "/case_001/img_1.jpg", "package", "unknown", "user041"),
    ("42", "The item was not in good condition when I got it.", "/case_002/img_1.jpg", "package", "unknown", "user042"),
    ("43", "I received a damaged delivery today.", "/case_003/img_1.jpg", "package", "unknown", "user043"),
    ("44", "Box is both crushed and in perfect condition.", "/case_004/img_1.jpg", "package", "unknown", "user044"),
    ("45", "Seal was broken but nothing could have fallen out.", "/case_005/img_1.jpg", "package", "unknown", "user045"),
    ("46", "Stains all over but nothing was spilled on it.", "/case_006/img_1.jpg", "package", "unknown", "user046"),
    ("47", "Every week every expensive item arrives damaged.", "/case_007/img_1.jpg", "package", "unknown", "user047"),
    ("48", "Eighth damaged shipment this month.", "/case_008/img_1.jpg", "package", "unknown", "user048"),
    ("49", "Outer box crushed, inner item fine. Still want full refund.", "/case_009/img_1.jpg", "package", "unknown", "user049"),
    ("50", "Multiple items same box different damage types.", "/case_010/img_1.jpg", "package", "unknown", "user050"),
]

def classify_claim(idx):
    i = int(idx)
    if i in [6,7,8,9,10,23,24,25,26,41,42,43]:
        return "vague"
    if i in [11,12,13,14,27,28,29,44,45,46]:
        return "contradictory"
    if i in [15,16,17,18,30,31,32,33,47,48,49,50]:
        return "suspicious"
    return "clear"


def run():
    pipeline = V2Pipeline(config={"providers": {}})
    results = []
    for idx, text, rel_path, obj, damage, user in CLAIMS:
        img_path = str(BASE / rel_path.lstrip("/"))
        if not os.path.isfile(img_path):
            print(f"WARNING: {img_path} not found")
            continue
        get_collector().reset()
        try:
            decision = pipeline.process(
                claim_text=text,
                image_paths=[img_path],
                claim_object=obj,
                user_id=user,
            )
        except Exception as e:
            decision = None
            print(f"ERROR claim {idx}: {e}")
        results.append({
            "id": idx,
            "text": text[:60],
            "object": obj,
            "classification": classify_claim(idx),
            "status": decision.claim_status if decision else "ERROR",
            "confidence": round(decision.confidence, 3) if decision else 0.0,
            "severity": decision.severity if decision else "unknown",
            "risk_flags": list(decision.risk_flags) if decision else [],
            "valid_image": bool(decision.valid_image) if decision else False,
            "evidence_met": bool(decision.evidence_standard_met) if decision else False,
            "justification": (decision.justification[:150] if decision else "error"),
        })
    return results


results = run()
stats = {"supported": 0, "contradicted": 0, "not_enough_information": 0, "error": 0}
for r in results:
    s = r["status"]
    if s in stats:
        stats[s] += 1
    else:
        stats["error"] += 1

by_class = {}
for r in results:
    c = r["classification"]
    by_class.setdefault(c, {"supported": 0, "contradicted": 0, "not_enough_information": 0, "total": 0})
    by_class[c][r["status"]] = by_class[c].get(r["status"], 0) + 1
    by_class[c]["total"] += 1

print("\n" + "="*60)
print("VERIFYIQ REALITY TEST — 50 CLAIMS WITH IMAGES")
print("="*60)
print(f"\nOVERALL: {json.dumps(stats, indent=2)}")
print(f"\nBY CLASSIFICATION:")
for c, s in by_class.items():
    print(f"  {c:15s}: {s['supported']} supported, {s['contradicted']} contradicted, {s['not_enough_information']} insufficient")

print("\n\nDETAILED RESULTS:")
print(f"{'ID':>4} {'Class':14s} {'Status':24s} {'Conf':>5} {'Sev':10s} {'Images':>6} {'Evid':>5} {'Risk Flags'}")
print("-"*120)
for r in results:
    flags = ", ".join(r["risk_flags"][:3])
    print(f"{r['id']:>4} {r['classification']:14s} {r['status']:24s} {r['confidence']:>5.2f} {r['severity']:10s} {str(r['valid_image']):>6} {str(r['evidence_met']):>5} {flags}")

with open(Path(__file__).parent / "reality_test_results2.json", "w") as f:
    json.dump({"results": results, "stats": stats, "by_class": by_class}, f, indent=2)
print("\nSaved to reality_test_results2.json")
