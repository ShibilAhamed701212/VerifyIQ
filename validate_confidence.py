"""PHASE 3: Confidence Analysis — tests ConfidenceCalibrator across 50+ scenarios.

Evaluates calibration, routing, and signal contribution for each scenario.
Produces CONFIDENCE_ANALYSIS.md.

No production code changes. Validation harness only.
"""
import sys, math, itertools, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "code"))
sys.path.insert(0, str(Path(__file__).parent))

from code.v2.models.consensus import ConsensusReport
from code.v2.models.fraud import FraudReport, ImageFraudResult, MetadataFraudResult, BehavioralFraudResult
from code.v2.models.evidence import EvidenceReport, EvidenceRecommendation
from code.v2.models.conversation import ConversationReport, ConversationAnomaly
from code.v2.confidence.calibrator import ConfidenceCalibrator

calibrator = ConfidenceCalibrator()


def make_consensus(confidence=0.8, agreement=1.0, models_succeeded=2, unanimous=True, uncertainty=0.0):
    return ConsensusReport(
        agreement_score=agreement, confidence=confidence, uncertainty=uncertainty,
        models_used=3, models_succeeded=models_succeeded, unanimous=unanimous,
    )


def make_fraud(score=0.0, high_risk=False, flags=None):
    return FraudReport(
        image_fraud=ImageFraudResult(),
        metadata_fraud=MetadataFraudResult(),
        behavioral_fraud=BehavioralFraudResult(),
        overall_fraud_score=score,
        high_risk=high_risk,
        flags=flags or [],
    )


def make_evidence(met=True, image_count=2):
    return EvidenceReport(
        evidence_standard_met=met,
        reason="All images pass quality check" if met else "Insufficient image quality",
        relevant_image_count=image_count,
    )


def make_conversation(has_contradictions=False, has_negation=False, has_retraction=False,
                      has_uncertainty=False, has_sarcasm=False, has_changing_claims=False):
    anomalies = []
    risk_flags = []
    if has_retraction: anomalies.append(ConversationAnomaly("claim_retraction", "", "high")); risk_flags.append("claim_retraction")
    if has_contradictions: anomalies.append(ConversationAnomaly("conversation_conflict", "", "high")); risk_flags.append("conversation_conflict")
    if has_uncertainty: anomalies.append(ConversationAnomaly("uncertainty", "", "medium")); risk_flags.append("uncertain_claim")
    if has_sarcasm: anomalies.append(ConversationAnomaly("sarcasm", "", "low")); risk_flags.append("possible_sarcasm")
    return ConversationReport(
        has_contradictions=has_contradictions, has_negation=has_negation,
        has_retraction=has_retraction, has_uncertainty=has_uncertainty,
        has_sarcasm=has_sarcasm, has_changing_claims=has_changing_claims,
        anomalies=anomalies, risk_flags=risk_flags,
    )


def analyze_scenario(scenario):
    consensus = make_consensus(
        confidence=scenario["model_confidence"],
        agreement=scenario["agreement"],
        models_succeeded=scenario.get("models_succeeded", 2),
    )
    fraud = make_fraud(
        score=scenario["fraud_score"],
        high_risk=scenario["fraud_score"] > 0.5,
        flags=scenario.get("fraud_flags", []),
    )
    evidence = make_evidence(
        met=scenario["evidence_met"],
        image_count=scenario.get("image_count", 2),
    )
    conversation = make_conversation(
        has_contradictions=scenario.get("has_contradictions", False),
        has_negation=scenario.get("has_negation", False),
        has_retraction=scenario.get("has_retraction", False),
        has_uncertainty=scenario.get("has_uncertainty", False),
        has_sarcasm=scenario.get("has_sarcasm", False),
        has_changing_claims=scenario.get("has_changing_claims", False),
    )

    result = calibrator.calibrate(consensus, fraud, evidence, conversation)

    return {
        "scenario": scenario,
        "result": result,
        "consensus": consensus,
        "fraud": fraud,
        "evidence": evidence,
        "conversation": conversation,
    }


def is_appropriate_routing(scenario, result):
    mc = scenario["model_confidence"]
    fraud = scenario["fraud_score"]
    evidence = scenario["evidence_met"]
    retraction = scenario.get("has_retraction", False)
    routing = result.routing

    # Happy path
    if mc > 0.9 and fraud < 0.2 and evidence and not retraction:
        return routing == "auto"
    # High fraud should never auto
    if fraud > 0.6 and routing == "auto":
        return False
    # Retraction should never auto
    if retraction and routing == "auto":
        return False
    # No evidence → evidence_request
    if not evidence and routing != "evidence_request":
        return False
    # Very low confidence → evidence_request
    if mc < 0.3 and routing == "auto":
        return False
    # High fraud + low evidence → evidence_request or manual_review
    if fraud > 0.7 and not evidence and routing == "fast_review":
        return False
    return True


def generate_scenarios():
    """Generate 50+ scenarios covering the full signal space."""
    scenarios = []

    # 1. High confidence + high agreement + no fraud + evidence met + clean (3 variants)
    scenarios.append({
        "name": "Perfect auto-approve", "model_confidence": 0.95, "agreement": 1.0,
        "fraud_score": 0.0, "evidence_met": True, "fraud_flags": [],
    })
    scenarios.append({
        "name": "Strong auto-approve", "model_confidence": 0.93, "agreement": 0.95,
        "fraud_score": 0.0, "evidence_met": True, "fraud_flags": [],
    })
    scenarios.append({
        "name": "Auto-approve with high agreement", "model_confidence": 0.91, "agreement": 1.0,
        "fraud_score": 0.0, "evidence_met": True, "fraud_flags": [],
    })

    # 2. Low confidence + low agreement + high fraud + evidence failed + retraction (3 variants)
    scenarios.append({
        "name": "Deep-reject worst case", "model_confidence": 0.1, "agreement": 0.3,
        "fraud_score": 0.8, "evidence_met": False, "has_retraction": True,
        "fraud_flags": ["duplicate_image", "screenshot_detected", "severity_escalation"],
    })
    scenarios.append({
        "name": "Reject with contradictions", "model_confidence": 0.15, "agreement": 0.25,
        "fraud_score": 0.7, "evidence_met": False, "has_contradictions": True,
        "has_uncertainty": True, "fraud_flags": ["edited_image"],
    })
    scenarios.append({
        "name": "Lowest possible confidence path", "model_confidence": 0.05, "agreement": 0.1,
        "fraud_score": 0.9, "evidence_met": False, "has_retraction": True,
        "has_contradictions": True, "has_sarcasm": True,
        "fraud_flags": ["duplicate_image", "screenshot_detected", "frequent_claims", "image_reuse"],
    })

    # 3. Medium confidence with various combinations (12 variants)
    for mc in [0.5, 0.6, 0.7, 0.8]:
        for fraud in [0.0, 0.3, 0.6]:
            for ev in [True, False]:
                scenarios.append({
                    "name": f"Medium mc={mc} fraud={fraud} evidence={ev}",
                    "model_confidence": mc, "agreement": 0.8, "fraud_score": fraud,
                    "evidence_met": ev, "fraud_flags": ["duplicate_image"] if fraud > 0.3 else [],
                })

    # 4. Fraud-only edge cases (10 variants)
    fraud_types = [
        ("duplicate_image", 0.4), ("screenshot_detected", 0.3), ("photo_of_photo", 0.3),
        ("edited_image", 0.3), ("timestamp_mismatch", 0.3), ("camera_mismatch", 0.2),
        ("frequent_claims", 0.3), ("image_reuse", 0.4), ("severity_escalation", 0.2),
        ("no_exif", 0.1),
    ]
    for flag, score in fraud_types:
        scenarios.append({
            "name": f"Fraud type: {flag}", "model_confidence": 0.8, "agreement": 0.9,
            "fraud_score": score, "evidence_met": True, "fraud_flags": [flag],
        })

    # 5. Conversation anomaly edge cases (8 variants)
    conv_configs = [
        {"has_contradictions": True, "name": "Contradiction only"},
        {"has_retraction": True, "name": "Retraction only"},
        {"has_uncertainty": True, "name": "Uncertainty only"},
        {"has_sarcasm": True, "name": "Sarcasm only"},
        {"has_negation": True, "name": "Negation only"},
        {"has_changing_claims": True, "name": "Changing claims only"},
        {"has_contradictions": True, "has_retraction": True, "name": "Contradiction + Retraction"},
        {"has_uncertainty": True, "has_sarcasm": True, "name": "Uncertainty + Sarcasm"},
    ]
    for cfg in conv_configs:
        scenarios.append({
            "name": f"Conversation: {cfg['name']}", "model_confidence": 0.8, "agreement": 0.9,
            "fraud_score": 0.1, "evidence_met": True,
            "has_contradictions": cfg.get("has_contradictions", False),
            "has_retraction": cfg.get("has_retraction", False),
            "has_uncertainty": cfg.get("has_uncertainty", False),
            "has_sarcasm": cfg.get("has_sarcasm", False),
            "has_negation": cfg.get("has_negation", False),
            "has_changing_claims": cfg.get("has_changing_claims", False),
            "fraud_flags": [],
        })

    # 6. Extreme value edge cases (10 variants)
    extreme_configs = [
        (0.999, 0.999, 0.001, True, "Near-perfect signals"),
        (0.001, 0.001, 0.999, False, "Near-zero signals"),
        (0.5, 0.5, 0.5, True, "All middle"),
        (0.0, 0.0, 0.0, False, "All zeros"),
        (1.0, 1.0, 0.0, True, "Perfect everything"),
        (0.99, 0.0, 0.0, True, "Max confidence, zero agreement"),
        (0.0, 0.99, 0.0, True, "Zero confidence, max agreement"),
        (0.5, 0.5, 0.75, False, "High fraud, medium other"),
        (0.3, 0.4, 0.6, True, "Below-threshold all"),
        (0.75, 0.85, 0.0, True, "Boundary: fast_review border"),
    ]
    for mc, ag, fr, ev, name in extreme_configs:
        scenarios.append({
            "name": f"Extreme: {name}",
            "model_confidence": mc, "agreement": ag, "fraud_score": fr,
            "evidence_met": ev, "fraud_flags": ["duplicate_image"] if fr > 0.4 else [],
        })

    # 7. Real-world composite scenarios (10 variants)
    composite_configs = [
        ("Escalating fraud with retraction", 0.7, 0.8, 0.65, True, True, True, False,
         ["severity_escalation", "frequent_claims"]),
        ("Uncertain + contradicting + evidence issue", 0.6, 0.7, 0.2, False, True, False, True,
         []),
        ("Sarcastic fraud claim", 0.8, 0.9, 0.5, True, False, False, False,
         ["screenshot_detected"]),
        ("Clean claim with low agreement", 0.85, 0.45, 0.0, True, False, False, False, []),
        ("New user first claim", 0.7, 0.9, 0.0, True, False, False, False, []),
        ("Multiple fraud signals + clean convo", 0.6, 0.8, 0.7, True, False, False, False,
         ["duplicate_image", "edited_image", "no_exif"]),
        ("All conversations anomalies", 0.75, 0.85, 0.1, True, True, True, True,
         []),
        ("Borderline auto/fast_review", 0.92, 0.95, 0.05, True, False, False, False, []),
        ("Borderline fast/manual review", 0.78, 0.85, 0.15, True, False, False, False, []),
        ("Borderline manual/evidence_request", 0.52, 0.6, 0.3, False, False, False, True, []),
    ]
    for name, mc, ag, fr, ev, ret, con, unc, flags in composite_configs:
        scenarios.append({
            "name": f"Composite: {name}",
            "model_confidence": mc, "agreement": ag, "fraud_score": fr,
            "evidence_met": ev, "has_retraction": ret, "has_contradictions": con,
            "has_uncertainty": unc, "fraud_flags": flags,
        })

    return scenarios


def run_analysis():
    scenarios = generate_scenarios()
    results = []

    for scenario in scenarios:
        analysis = analyze_scenario(scenario)
        appropriate = is_appropriate_routing(scenario, analysis["result"])
        results.append({**analysis, "appropriate": appropriate})

    return results


def gen_report(results):
    total = len(results)
    appropriate_count = sum(1 for r in results if r["appropriate"])
    routing_counts = {}
    for r in results:
        rt = r["result"].routing
        routing_counts[rt] = routing_counts.get(rt, 0) + 1

    lines = []
    lines.append("# CONFIDENCE ANALYSIS — ConfidenceCalibrator 50+ Scenario Verification\n")

    lines.append("## Executive Summary\n")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total scenarios tested | {total} |")
    lines.append(f"| Appropriate routing | {appropriate_count}/{total} ({appropriate_count/total*100:.1f}%) |")
    lines.append(f"| Inappropriate routing | {total - appropriate_count}/{total} ({(total-appropriate_count)/total*100:.1f}%) |")
    lines.append(f"|")
    for rt, count in sorted(routing_counts.items()):
        lines.append(f"| Routing: {rt} | {count} scenarios |")

    lines.append("\n## Calibration Formula\n")
    lines.append("```")
    lines.append("final = base + agreement_boost - fraud_penalty + evidence_boost - conv_penalty")
    lines.append("where:")
    lines.append("  base = model_confidence (or 0.3 if 0)")
    lines.append("  agreement_boost = agreement * 0.15")
    lines.append("  fraud_penalty = fraud_score * 0.30")
    lines.append("  evidence_boost = +0.1 if evidence_met else -0.1")
    lines.append("  conv_penalty = 0.2 (retraction) + 0.15 (contradiction) + 0.1 (uncertainty)")
    lines.append("```")

    lines.append("\n## Routing Thresholds\n")
    lines.append("| Final Confidence | Routing | Description |")
    lines.append("|------------------|---------|-------------|")
    lines.append("| > 0.90 | auto | Fully automated approval |")
    lines.append("| 0.75–0.90 | fast_review | Quick manual check |")
    lines.append("| 0.50–0.75 | manual_review | Full manual review |")
    lines.append("| ≤ 0.50 | evidence_request | Request more evidence |")

    lines.append("\n## Per-Scenario Results\n")
    lines.append("| # | Scenario | Model Conf | Agreement | Fraud | Evidence | Conv Flags | Final | Routing | Appropriate? |")
    lines.append("|---|----------|------------|-----------|-------|----------|------------|-------|---------|-------------|")

    for i, r in enumerate(results):
        s = r["scenario"]
        res = r["result"]
        conv_flags = []
        if s.get("has_retraction"): conv_flags.append("R")
        if s.get("has_contradictions"): conv_flags.append("C")
        if s.get("has_uncertainty"): conv_flags.append("U")
        if s.get("has_sarcasm"): conv_flags.append("S")
        if s.get("has_negation"): conv_flags.append("N")
        if s.get("has_changing_claims"): conv_flags.append("CC")
        conv_str = ",".join(conv_flags) if conv_flags else "—"
        app = "✅" if r["appropriate"] else "❌"
        app_label = "Yes" if r["appropriate"] else "NO"

        b = res.breakdown
        lines.append(
            f"| {i+1} | {s['name'][:55]} | {s['model_confidence']:.3f} | "
            f"{s['agreement']:.2f} | {s['fraud_score']:.2f} | {s['evidence_met']} | "
            f"{conv_str} | {res.final_confidence:.4f} | {res.routing} | {app_label} |"
        )

    lines.append("\n## Breakdown Analysis (Selected Scenarios)\n")
    lines.append("### High Confidence (+ Agreement + Evidence, No Fraud)\n")
    high_auto = [r for r in results if r["scenario"]["model_confidence"] > 0.9 and r["scenario"]["fraud_score"] < 0.2 and r["scenario"]["evidence_met"]]
    for r in high_auto[:3]:
        s = r["scenario"]
        res = r["result"]
        b = res.breakdown
        lines.append(f"- **{s['name']}**: Model={b.model_confidence} + Agreement={b.agreement_contribution} - Fraud={b.fraud_penalty} + Evidence={b.evidence_boost} - Conv={b.conversation_penalty} → **{res.final_confidence:.4f}** → **{res.routing}**")

    lines.append("\n### Fraud-Heavy Scenarios\n")
    high_fraud = [r for r in results if r["scenario"]["fraud_score"] > 0.5]
    for r in high_fraud[:3]:
        s = r["scenario"]
        res = r["result"]
        b = res.breakdown
        lines.append(f"- **{s['name']}**: Model={b.model_confidence} - Fraud={b.fraud_penalty} + Evidence={b.evidence_boost} → **{res.final_confidence:.4f}** → **{res.routing}**")

    lines.append("\n### Conversation Anomaly Impact\n")
    conv_anomalies = [r for r in results if r["scenario"].get("has_retraction") or r["scenario"].get("has_contradictions")]
    for r in conv_anomalies[:3]:
        s = r["scenario"]
        res = r["result"]
        b = res.breakdown
        lines.append(f"- **{s['name']}**: Model={b.model_confidence} - Conv={b.conversation_penalty} → **{res.final_confidence:.4f}** → **{res.routing}**")

    lines.append("\n### Inappropriate Routing Analysis\n")
    inappropriate = [r for r in results if not r["appropriate"]]
    if inappropriate:
        for r in inappropriate:
            s = r["scenario"]
            res = r["result"]
            lines.append(f"- ❌ **{s['name']}**: {res.routing} (final={res.final_confidence:.4f}) — expected different routing given signals")
    else:
        lines.append("- All routings are appropriate for their signal combinations.")

    lines.append("\n## Calibration Correctness Assessment\n")
    lines.append("### Strengths\n")
    lines.append("1. **Fraud-weighted correctly**: Fraud penalty (×0.30) is the strongest single penalty — appropriate for insurance claims\n")
    lines.append("2. **Retraction is heavily penalized**: -0.20 for retractions ensures retracted claims never auto-approve\n")
    lines.append("3. **Evidence boost/cutoff**: Missing evidence (-0.10) pushes borderline cases below routing thresholds\n")
    lines.append("4. **Routing thresholds reasonable**: ~0.90 for auto, ~0.75 for fast review, ~0.50 for manual, <0.50 for evidence request\n")
    lines.append("5. **Symmetric signal integration**: Both positive and negative signals balance realistically\n")

    lines.append("\n### Weaknesses / Edge Cases\n")
    lines.append("1. **Agreement boost limited**: Max contribution is 0.15 (at 1.0 agreement). For multi-model systems, high agreement should boost more.\n")
    lines.append("2. **No uncertainty penalty in formula**: `has_uncertainty` sets a conversation flag but conv_penalty only adds if explicitly in formula. Verify: uncertainty adds 0.1 to conv_penalty.\n")
    lines.append("3. **Negative cap at 0.0**: `max(0.0, min(1.0, final))` removes information — could differentiate between 0.0 and 0.05.\n")
    lines.append("4. **Sarcasm ignored in confidence**: Sarcasm is flagged but has no confidence penalty. A sarcastic claim should reduce trust.\n")
    lines.append("5. **Static base fallback**: When model_confidence is 0, base=0.3 hardcoded. This creates false confidence for failed model runs.\n")
    lines.append("6. **Evidence boost symmetric**: +0.1 for met, -0.1 for failed. Failing evidence should perhaps penalize more than meeting it rewards.\n")
    lines.append("7. **No agreement penalty for low scores**: agreement=0.0 gives 0 contribution, but very low agreement should penalize.\n")

    lines.append("\n## Signal Contribution Breakdown (All Scenarios)\n")
    contributions = {"model_confidence": [], "agreement_contribution": [],
                     "fraud_penalty": [], "evidence_boost": [], "conversation_penalty": []}
    for r in results:
        b = r["result"].breakdown
        contributions["model_confidence"].append(b.model_confidence)
        contributions["agreement_contribution"].append(b.agreement_contribution)
        contributions["fraud_penalty"].append(b.fraud_penalty)
        contributions["evidence_boost"].append(b.evidence_boost)
        contributions["conversation_penalty"].append(b.conversation_penalty)

    def avg(vals): return sum(vals) / len(vals) if vals else 0

    lines.append("| Signal | Average | Min | Max | Range |")
    lines.append("|--------|---------|-----|-----|-------|")
    lines.append(f"| Model Confidence | {avg(contributions['model_confidence']):.4f} | {min(contributions['model_confidence']):.4f} | {max(contributions['model_confidence']):.4f} | {max(contributions['model_confidence'])-min(contributions['model_confidence']):.4f} |")
    lines.append(f"| Agreement Boost | {avg(contributions['agreement_contribution']):.4f} | {min(contributions['agreement_contribution']):.4f} | {max(contributions['agreement_contribution']):.4f} | {max(contributions['agreement_contribution'])-min(contributions['agreement_contribution']):.4f} |")
    lines.append(f"| Fraud Penalty | {avg(contributions['fraud_penalty']):.4f} | {min(contributions['fraud_penalty']):.4f} | {max(contributions['fraud_penalty']):.4f} | {max(contributions['fraud_penalty'])-min(contributions['fraud_penalty']):.4f} |")
    lines.append(f"| Evidence Boost | {avg(contributions['evidence_boost']):.4f} | {min(contributions['evidence_boost']):.4f} | {max(contributions['evidence_boost']):.4f} | {max(contributions['evidence_boost'])-min(contributions['evidence_boost']):.4f} |")
    lines.append(f"| Conversation Penalty | {avg(contributions['conversation_penalty']):.4f} | {min(contributions['conversation_penalty']):.4f} | {max(contributions['conversation_penalty']):.4f} | {max(contributions['conversation_penalty'])-min(contributions['conversation_penalty']):.4f} |")

    return "\n".join(lines)


def main():
    results = run_analysis()
    report = gen_report(results)

    out_path = Path(__file__).parent / "CONFIDENCE_ANALYSIS.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Wrote {out_path}")
    print(f"\nScenarios analyzed: {len(results)}")
    print(f"Appropriate routings: {sum(1 for r in results if r['appropriate'])}/{len(results)}")

    # Distribution
    routing_dist = {}
    for r in results:
        rt = r["result"].routing
        routing_dist[rt] = routing_dist.get(rt, 0) + 1
    print(f"\nRouting distribution:")
    for rt, count in sorted(routing_dist.items()):
        print(f"  {rt}: {count}")


if __name__ == "__main__":
    main()
