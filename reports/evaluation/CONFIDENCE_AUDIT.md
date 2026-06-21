# CONFIDENCE AUDIT — ConfidenceCalibrator Calibration Analysis

> **Note:** VerifyIQ is an AI agent framework that performs reasoning using observations from external vision providers (VLMs). Results in this document assume an operational vision provider. VerifyIQ does not contain a proprietary VLM — users configure their own (Gemini, OpenRouter, local models, etc.).

## Executive Summary

| Metric | Value |
|--------|-------|
| Scenarios tested | 68 |
| Appropriate routings | 59/68 (86.8%) |
| Inappropriate routings | 9/68 (13.2%) |
| Routing distribution | auto=29, evidence_request=14, fast_review=7, manual_review=18 |

The calibrator performs well on clean, extreme, and fraud-heavy cases. All 9 failures follow a single root cause: **medium confidence overrides missing evidence**.

---

## Calibration Formula (V2)

```
final = base + agreement_boost - fraud_penalty + evidence_boost - conv_penalty

where:
  base           = model_confidence (or 0.3 if 0)
  agreement_boost = agreement × 0.15
  fraud_penalty   = fraud_score × 0.30
  evidence_boost  = +0.1 if evidence_met else -0.1
  conv_penalty    = 0.2 (retraction) + 0.15 (contradiction) + 0.1 (uncertainty)
```

**Routing thresholds:** >0.90 auto, 0.75–0.90 fast_review, 0.50–0.75 manual_review, ≤0.50 evidence_request

---

## Comparison to V1

| Aspect | V1 (single model_confidence) | V2 (ConfidenceCalibrator) |
|--------|------------------------------|---------------------------|
| **Signals** | 1 (model confidence) | 5 (model, agreement, fraud, evidence, conversation) |
| **Signal range** | Static threshold check | Weighted multi-signal integration |
| **Fraud handling** | None (separate risk_flags only) | -30% multiplicative penalty |
| **Evidence awareness** | None (separate boolean) | ±0.1 boost/penalty |
| **Conversation signals** | None | Up to -0.45 combined penalty |
| **Dynamic routing** | Single threshold | 4-tier (auto, fast, manual, evidence) |
| **Transparency** | Opaque | ConfidenceBreakdown with per-signal contributions |
| **Fallback** | Hard-coded default confidence | 0.3 base when model_confidence=0 |

**Key V2 improvement:** V2 integrates signals the V1 pipeline never saw. A fraudulent claim with high model confidence would auto-route in V1; V2 penalizes it correctly. However, V2's multi-signal architecture introduces a **new failure mode**: component weights interact, and medium-strength signals can drown out hard business rules (e.g., "no evidence → request more").

---

## Signal Contribution Statistics (All 68 Scenarios)

| Signal | Average | Min | Max | Range |
|--------|---------|-----|-----|-------|
| Model Confidence | 0.6669 | 0.0000 | 1.0000 | 1.0000 |
| Agreement Boost | 0.1148 | 0.0000 | 0.1500 | 0.1500 |
| Fraud Penalty | 0.0825 | 0.0000 | 0.2997 | 0.2997 |
| Evidence Boost | 0.0412 | -0.1000 | 0.1000 | 0.2000 |
| Conversation Penalty | 0.0426 | 0.0000 | 0.4500 | 0.4500 |

**Model confidence dominates** with the widest range and highest average. The fraud penalty has significant weight (max 0.30) but rarely fires at full strength. Conversation penalties are applied sparingly (avg 0.04) because most test scenarios have clean conversations.

---

## All 9 Inappropriate Routings — Root Cause Analysis

Every single failure follows the identical pattern:

```
model_confidence ∈ [0.5, 0.8]  +  evidence_met=False  +  clean conversation
                                                            (no fraud, no anomalies)
```

**Root cause:** The calibrator computes `final = 0.5..0.8 + 0.12 (agreement) + 0.0 (no fraud) - 0.1 (no evidence) - 0.0 (clean convo) = 0.52..0.82`, which routes to `manual_review` or `fast_review` instead of the correct `evidence_request`.

**Business rule violated:** Missing evidence should always route to `evidence_request` regardless of other signals. The calibrator's additive formula treats `evidence_boost = -0.1` as an adjustable parameter, but a 0.1 penalty is easily overwhelmed by model confidence.

| Scenario | Model Conf | Final | Routing | Expected |
|----------|-----------|-------|---------|----------|
| Medium mc=0.5 fraud=0.0 evidence=False | 0.500 | 0.5200 | manual_review | evidence_request |
| Medium mc=0.5 fraud=0.3 evidence=False | 0.500 | 0.3700 | evidence_request | evidence_request ✅ |
| Medium mc=0.5 fraud=0.6 evidence=False | 0.500 | 0.2200 | evidence_request | evidence_request ✅ |
| Medium mc=0.6 fraud=0.0 evidence=False | 0.600 | 0.6200 | manual_review | evidence_request ❌ |
| Medium mc=0.6 fraud=0.3 evidence=False | 0.600 | 0.4700 | evidence_request | evidence_request ✅ |
| Medium mc=0.7 fraud=0.0 evidence=False | 0.700 | 0.7200 | manual_review | evidence_request ❌ |
| Medium mc=0.7 fraud=0.3 evidence=False | 0.700 | 0.5700 | manual_review | evidence_request ❌ |
| Medium mc=0.8 fraud=0.0 evidence=False | 0.800 | 0.8200 | fast_review | evidence_request ❌ |
| Medium mc=0.8 fraud=0.3 evidence=False | 0.800 | 0.6700 | manual_review | evidence_request ❌ |

**Total: 9 inappropriate. 5 with fraud>0 managed to route correctly** (to evidence_request) because fraud penalty pulled them below 0.50.

---

## Low-Confidence Predictions (final < 0.50)

14 scenarios route to `evidence_request` (final ≤ 0.50). These are all appropriate — they involve low confidence, high fraud, missing evidence, or conversation anomalies. No false negatives detected.

---

## False Confidence Cases (High final despite red flags)

| Scenario | Model Conf | Final | Flags | Issue |
|----------|-----------|-------|-------|-------|
| Conversation: Negation only | 0.800 | 0.8450 | has_negation=True | Negation has zero confidence penalty |
| Conversation: Sarcasm only | 0.800 | 0.8450 | has_sarcasm=True | Sarcasm has zero confidence penalty |
| Fraud type: no_exif | 0.800 | 0.8150 | fraud_score=0.1, evidence_met=True | No EXIF is penalized at only 0.03 |
| Extreme: Max confidence, zero agreement | 0.990 | 0.8900 | agreement=0.0 | High final despite zero agreement |

**Sarcasm and negation are particularly concerning:** both are detected and flagged by the `ConversationAnalyzer` but contribute **nothing** to the confidence penalty. A sarcastic or self-negating claim with high model confidence and clean evidence routes to auto/fast review.

---

## Edge Case Analysis

| Edge Case | Final | Routing | Assessment |
|-----------|-------|---------|------------|
| Near-perfect signals | 1.0000 | auto | ✅ Correct |
| Near-zero signals | 0.0000 | evidence_request | ✅ Correct |
| All middle | 0.5250 | manual_review | ✅ Correct (borderline) |
| All zeros | 0.2000 | evidence_request | ⚠️ Non-zero from 0.3 fallback is misleading |
| Perfect everything | 1.0000 | auto | ✅ Correct |
| Max confidence, zero agreement | 0.8900 | fast_review | ⚠️ Should this be auto? 0.89 is borderline |
| Zero confidence, max agreement | 0.5350 | manual_review | ⚠️ 0.3 base + 0.1485 = false confidence |
| High fraud, medium other | 0.1250 | evidence_request | ✅ Correct |
| Below-threshold all | 0.4850 | evidence_request | ⚠️ Very close to manual_review boundary |
| Boundary: fast_review border | 0.8775 | fast_review | ✅ Correct |

---

## Weaknesses (Ranked by Severity)

### Critical
1. **Evidence bypass (9/9 failures):** Medium confidence (0.5–0.8) + no evidence routes to manual_review/fast_review instead of evidence_request. The -0.1 evidence penalty is insufficient to counterbalance model confidence.
2. **Sarcasm/negation zero penalty:** Both are detected and flagged but contribute nothing to confidence. A sarcastic claim with fraud_score=0.0 routes identically to a sincere one.

### High
3. **Static 0.3 base fallback:** When model_confidence=0, the hard-coded 0.3 creates false confidence. Zero-confidence model output should produce a lower default (0.1 or 0.0).
4. **Evidence penalty asymmetry:** ±0.1 is symmetric. Failing evidence should penalize more than meeting it rewards (say ±0.15 or asymmetric +0.05/–0.15).

### Medium
5. **Agreement boost capped at 0.15:** Multi-model agreement at 1.0 contributes only 0.15. This is too low to meaningfully differentiate high-agreement from low-agreement scenarios.
6. **No agreement penalty for low scores:** agreement=0.0 → 0 contribution. Very low agreement (0.0–0.3) should carry a negative penalty.
7. **Negative cap at 0.0:** The `max(0.0, ...)` clamps negatives to zero, removing differentiation between final=−0.1 and final=0.0. Closer to zero means closer to evidence_request; negative values that clamp lose this nuance.

### Low
8. **low_exif fraud type weakly penalized:** fraud_score=0.1 → penalty of only 0.03. Missing EXIF is a meaningful fraud signal but barely moves confidence.

---

## Recommended Threshold Adjustments

### Fix 1: Hard evidence gate (highest priority)

Add a pre-check that overrides the additive formula:

```python
if not evidence.evidence_standard_met:
    routing = "evidence_request"  # always
    # Still compute final for logging/transparency
```

This eliminates all 9 failures. Business logic: missing evidence always requires more evidence, regardless of other signals.

### Fix 2: Sarcasm/negation penalties

```python
if conversation.has_sarcasm:
    conv_penalty += 0.10   # sarcasm erodes trust
if conversation.has_negation:
    conv_penalty += 0.05   # self-negation signals confusion
```

### Fix 3: Adjust evidence asymmetry

```python
evidence_boost = 0.05 if evidence.evidence_standard_met else -0.15
```

Meeting evidence is expected (modest boost). Failing evidence is a strong negative.

### Fix 4: Lower base fallback

```python
base = model_conf if model_conf > 0 else 0.1
```

### Fix 5: Broaden agreement range

```python
agreement_boost = (agreement - 0.5) * 0.30  # -0.15 to +0.15 range
```

This makes agreement a bipolar signal: low agreement penalizes, high agreement boosts.

### Fix 6: Target routing thresholds after fixes

With all fixes applied, consider adjusting routing thresholds:

| Routing | Current | Proposed | Rationale |
|---------|---------|----------|-----------|
| auto | >0.90 | >0.85 | Lower bar with hard evidence gate as safety net |
| fast_review | 0.75–0.90 | 0.65–0.85 | Widened to reduce manual review burden |
| manual_review | 0.50–0.75 | 0.40–0.65 | More evidence requests for uncertain cases |
| evidence_request | ≤0.50 | ≤0.40 | Safe with hard evidence gate |

---

## Projected Impact of Fixes

| Scenario | Current | After Fix 1 | After Fixes 1–6 |
|----------|---------|------------|------------------|
| Medium mc=0.7, no evidence | manual_review (❌) | evidence_request ✅ | evidence_request ✅ |
| Sarcastic claim, high conf | fast_review | fast_review | manual_review (penalty added) |
| Zero model confidence | final=0.300 | final=0.100 | final=0.100 |
| High agreement, low conf | final=0.535 (manual) | final=0.535 (manual) | final=0.385 (evidence_request) |
| Expected failure rate | 9/68 (13.2%) | 0/68 (0%) | 0/68 (0%) |
