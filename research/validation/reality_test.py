"""Reality test: 50 unseen claims through VerifyIQ V2."""
import json, sys, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
os.environ["GEMINI_API_KEY"] = "test_key"  # Needed for provider init, won't be called

from code.v2.pipeline import V2Pipeline
from code.v2.observability.metrics import get_collector

# 50 completely unseen claims — never in sample, evaluation, or adversarial data
CLAIMS = [
    # === CARS (1-18) ===
    # Clear/easy
    ("1", "There is a dent on my front bumper after I hit a pole.", ["car"], "dent", "user001"),
    ("2", "The rear bumper has a large scratch from a parking incident.", ["car"], "scratch", "user002"),
    ("3", "Windshield cracked after a rock hit it on the highway.", ["car"], "crack", "user003"),
    ("4", "My headlight is shattered after someone hit my car in the lot.", ["car"], "glass_shatter", "user004"),
    ("5", "The side mirror is completely broken off.", ["car"], "broken_part", "user005"),
    # Vague
    ("6", "Something is wrong with my car door.", ["car"], "unknown", "user006"),
    ("7", "The car got damaged somehow.", ["car"], "unknown", "user007"),
    ("8", "I need to file a claim for my vehicle.", ["car"], "unknown", "user008"),
    ("9", "There's some issue with the front area of the car.", ["car"], "unknown", "user009"),
    ("10", "My car was hit but I don't know where.", ["car"], "unknown", "user010"),
    # Contradictory
    ("11", "The hood is dented but there is absolutely no damage to the hood.", ["car"], "unknown", "user011"),
    ("12", "My windshield is both cracked and perfectly fine.", ["car"], "unknown", "user012"),
    ("13", "The front bumper needs replacement but nothing happened to it.", ["car"], "unknown", "user013"),
    ("14", "Taillight is shattered but the car is undamaged.", ["car"], "unknown", "user014"),
    # Suspicious
    ("15", "I scratched all four doors and the roof — please cover everything.", ["car"], "scratch", "user015"),
    ("16", "Third claim this week. The fender is dented again.", ["car"], "dent", "user016"),
    ("17", "My bumper has a crack. I hit nothing. It just appeared.", ["car"], "crack", "user017"),
    ("18", "The body has multiple dents everywhere. Total replacement needed.", ["car"], "dent", "user018"),
    # === LAPTOPS (19-36) ===
    # Clear/easy
    ("19", "My laptop screen is cracked from the corner.", ["laptop"], "crack", "user019"),
    ("20", "The keyboard has a broken key from a spill.", ["laptop"], "broken_part", "user020"),
    ("21", "The hinge snapped when I closed the lid.", ["laptop"], "broken_part", "user021"),
    ("22", "Water damaged the trackpad and it no longer clicks.", ["laptop"], "water_damage", "user022"),
    # Vague
    ("23", "Something is broken on my laptop.", ["laptop"], "unknown", "user023"),
    ("24", "The laptop screen area has an issue.", ["laptop"], "unknown", "user024"),
    ("25", "My device was damaged in shipping.", ["laptop"], "unknown", "user025"),
    ("26", "There might be a problem with the lid.", ["laptop"], "unknown", "user026"),
    # Contradictory
    ("27", "Screen is cracked but works fine with no visible damage.", ["laptop"], "unknown", "user027"),
    ("28", "The entire laptop is destroyed except it looks brand new.", ["laptop"], "unknown", "user028"),
    ("29", "Keyboard is missing keys. All keys are present.", ["laptop"], "unknown", "user029"),
    # Suspicious
    ("30", "My laptop was working before the flight but after landing it was broken. I did not drop it.", ["laptop"], "unknown", "user030"),
    ("31", "Fifth claim this year. The screen cracked again.", ["laptop"], "crack", "user031"),
    ("32", "The water damage was already there when I opened the box. I did not spill anything.", ["laptop"], "water_damage", "user032"),
    ("33", "I need a full replacement. The laptop has dents on every surface.", ["laptop"], "dent", "user033"),
    # Edge cases
    ("34", "The laptop was stolen but I have pictures from before.", ["laptop", "stolen"], "unknown", "user034"),
    ("35", "I dropped coffee on the keyboard last week. It still works but some keys stick.", ["laptop"], "water_damage", "user035"),
    ("36", "The screen flickers sometimes. Might be loose connection.", ["laptop"], "unknown", "user036"),
    # === PACKAGES (37-50) ===
    # Clear/easy
    ("37", "The box arrived crushed on the corner.", ["package"], "crushed_packaging", "user037"),
    ("38", "The package has a water stain from rain during delivery.", ["package"], "stain", "user038"),
    ("39", "The seal is torn and the contents fell out.", ["package"], "torn_packaging", "user039"),
    ("40", "The package side is completely crushed.", ["package"], "crushed_packaging", "user040"),
    # Vague
    ("41", "Something is wrong with the packaging.", ["package"], "unknown", "user041"),
    ("42", "The item was not in good condition when I got it.", ["package"], "unknown", "user042"),
    ("43", "I received a damaged delivery today.", ["package"], "unknown", "user043"),
    # Contradictory
    ("44", "The box is both crushed and in perfect condition.", ["package"], "unknown", "user044"),
    ("45", "The seal was broken but nothing could have fallen out.", ["package"], "unknown", "user045"),
    ("46", "Stains all over but nothing was spilled on it.", ["package"], "unknown", "user046"),
    # Suspicious
    ("47", "I order expensive items every week and every single one arrives damaged.", ["package"], "unknown", "user047"),
    ("48", "Eighth damaged shipment this month from same address.", ["package"], "unknown", "user048"),
    ("49", "The outer box is crushed but the inner item is fine. Still want full refund.", ["package"], "unknown", "user049"),
    ("50", "Multiple items in same box all have different damage types.", ["package"], "unknown", "user050"),
]

def classify_claim(idx, text, obj, cat):
    """Classify claim type for analysis."""
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
    for idx, text, objects, damage, user in CLAIMS:
        obj = objects[0]
        get_collector().reset()
        try:
            decision = pipeline.process(
                claim_text=text,
                image_paths=[],
                claim_object=obj,
                user_id=user,
            )
            meta = get_collector().get_metrics() if hasattr(get_collector(), 'get_metrics') else {}
        except Exception as e:
            decision = None
            meta = {"error": str(e)}
        results.append({
            "id": idx,
            "text": text,
            "object": obj,
            "damage_hint": damage,
            "user": user,
            "classification": classify_claim(idx, text, obj, ""),
            "status": decision.claim_status if decision else "ERROR",
            "confidence": round(decision.confidence, 3) if decision else 0.0,
            "severity": decision.severity if decision else "unknown",
            "risk_flags": list(decision.risk_flags) if decision else [],
            "valid_image": bool(decision.valid_image) if decision else False,
            "evidence_met": bool(decision.evidence_standard_met) if decision else False,
            "justification": decision.justification[:120] if decision else "error",
            "latency_ms": round(getattr(meta, 'total_latency_ms', 0), 1) if not isinstance(meta, dict) else 0.0,
        })
    return results

if __name__ == "__main__":
    results = run()
    print(json.dumps(results, indent=2))
    print("\n\n=== SUMMARY ===")
    stats = {"supported": 0, "contradicted": 0, "not_enough_information": 0, "error": 0}
    for r in results:
        s = r["status"]
        if s in stats:
            stats[s] += 1
        else:
            stats["error"] += 1
    print(json.dumps(stats, indent=2))
    by_class = {}
    for r in results:
        c = r["classification"]
        if c not in by_class:
            by_class[c] = {"supported": 0, "contradicted": 0, "not_enough_information": 0, "total": 0}
        by_class[c][r["status"]] = by_class[c].get(r["status"], 0) + 1
        by_class[c]["total"] += 1
    print("\n=== BY CLASSIFICATION ===")
    print(json.dumps(by_class, indent=2))
    with open(Path(__file__).parent / "reality_test_results.json", "w") as f:
        json.dump({"results": results, "stats": stats, "by_class": by_class}, f, indent=2)
    print("\nSaved to reality_test_results.json")
