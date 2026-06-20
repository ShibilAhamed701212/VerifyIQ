# CONFIDENCE ANALYSIS — ConfidenceCalibrator 50+ Scenario Verification

> **Note:** VerifyIQ is an AI agent framework that performs reasoning using observations from external vision providers (VLMs). Results in this document assume an operational vision provider. VerifyIQ does not contain a proprietary VLM — users configure their own (Gemini, OpenRouter, local models, etc.).

## Executive Summary

| Metric | Value |
|--------|-------|
| Total scenarios tested | 68 |
| Appropriate routing | 59/68 (86.8%) |
| Inappropriate routing | 9/68 (13.2%) |
|
| Routing: auto | 29 scenarios |
| Routing: evidence_request | 14 scenarios |
| Routing: fast_review | 7 scenarios |
| Routing: manual_review | 18 scenarios |

## Calibration Formula

```
final = base + agreement_boost - fraud_penalty + evidence_boost - conv_penalty
where:
  base = model_confidence (or 0.3 if 0)
  agreement_boost = agreement * 0.15
  fraud_penalty = fraud_score * 0.30
  evidence_boost = +0.1 if evidence_met else -0.1
  conv_penalty = 0.2 (retraction) + 0.15 (contradiction) + 0.1 (uncertainty)
```

## Routing Thresholds

| Final Confidence | Routing | Description |
|------------------|---------|-------------|
| > 0.90 | auto | Fully automated approval |
| 0.75–0.90 | fast_review | Quick manual check |
| 0.50–0.75 | manual_review | Full manual review |
| ≤ 0.50 | evidence_request | Request more evidence |

## Per-Scenario Results

| # | Scenario | Model Conf | Agreement | Fraud | Evidence | Conv Flags | Final | Routing | Appropriate? |
|---|----------|------------|-----------|-------|----------|------------|-------|---------|-------------|
| 1 | Perfect auto-approve | 0.950 | 1.00 | 0.00 | True | — | 1.0000 | auto | Yes |
| 2 | Strong auto-approve | 0.930 | 0.95 | 0.00 | True | — | 1.0000 | auto | Yes |
| 3 | Auto-approve with high agreement | 0.910 | 1.00 | 0.00 | True | — | 1.0000 | auto | Yes |
| 4 | Deep-reject worst case | 0.100 | 0.30 | 0.80 | False | R | 0.0000 | evidence_request | Yes |
| 5 | Reject with contradictions | 0.150 | 0.25 | 0.70 | False | C,U | 0.0000 | evidence_request | Yes |
| 6 | Lowest possible confidence path | 0.050 | 0.10 | 0.90 | False | R,C,S | 0.0000 | evidence_request | Yes |
| 7 | Medium mc=0.5 fraud=0.0 evidence=True | 0.500 | 0.80 | 0.00 | True | — | 0.7200 | manual_review | Yes |
| 8 | Medium mc=0.5 fraud=0.0 evidence=False | 0.500 | 0.80 | 0.00 | False | — | 0.5200 | manual_review | NO |
| 9 | Medium mc=0.5 fraud=0.3 evidence=True | 0.500 | 0.80 | 0.30 | True | — | 0.6300 | manual_review | Yes |
| 10 | Medium mc=0.5 fraud=0.3 evidence=False | 0.500 | 0.80 | 0.30 | False | — | 0.4300 | evidence_request | Yes |
| 11 | Medium mc=0.5 fraud=0.6 evidence=True | 0.500 | 0.80 | 0.60 | True | — | 0.5400 | manual_review | Yes |
| 12 | Medium mc=0.5 fraud=0.6 evidence=False | 0.500 | 0.80 | 0.60 | False | — | 0.3400 | evidence_request | Yes |
| 13 | Medium mc=0.6 fraud=0.0 evidence=True | 0.600 | 0.80 | 0.00 | True | — | 0.8200 | fast_review | Yes |
| 14 | Medium mc=0.6 fraud=0.0 evidence=False | 0.600 | 0.80 | 0.00 | False | — | 0.6200 | manual_review | NO |
| 15 | Medium mc=0.6 fraud=0.3 evidence=True | 0.600 | 0.80 | 0.30 | True | — | 0.7300 | manual_review | Yes |
| 16 | Medium mc=0.6 fraud=0.3 evidence=False | 0.600 | 0.80 | 0.30 | False | — | 0.5300 | manual_review | NO |
| 17 | Medium mc=0.6 fraud=0.6 evidence=True | 0.600 | 0.80 | 0.60 | True | — | 0.6400 | manual_review | Yes |
| 18 | Medium mc=0.6 fraud=0.6 evidence=False | 0.600 | 0.80 | 0.60 | False | — | 0.4400 | evidence_request | Yes |
| 19 | Medium mc=0.7 fraud=0.0 evidence=True | 0.700 | 0.80 | 0.00 | True | — | 0.9200 | auto | Yes |
| 20 | Medium mc=0.7 fraud=0.0 evidence=False | 0.700 | 0.80 | 0.00 | False | — | 0.7200 | manual_review | NO |
| 21 | Medium mc=0.7 fraud=0.3 evidence=True | 0.700 | 0.80 | 0.30 | True | — | 0.8300 | fast_review | Yes |
| 22 | Medium mc=0.7 fraud=0.3 evidence=False | 0.700 | 0.80 | 0.30 | False | — | 0.6300 | manual_review | NO |
| 23 | Medium mc=0.7 fraud=0.6 evidence=True | 0.700 | 0.80 | 0.60 | True | — | 0.7400 | manual_review | Yes |
| 24 | Medium mc=0.7 fraud=0.6 evidence=False | 0.700 | 0.80 | 0.60 | False | — | 0.5400 | manual_review | NO |
| 25 | Medium mc=0.8 fraud=0.0 evidence=True | 0.800 | 0.80 | 0.00 | True | — | 1.0000 | auto | Yes |
| 26 | Medium mc=0.8 fraud=0.0 evidence=False | 0.800 | 0.80 | 0.00 | False | — | 0.8200 | fast_review | NO |
| 27 | Medium mc=0.8 fraud=0.3 evidence=True | 0.800 | 0.80 | 0.30 | True | — | 0.9300 | auto | Yes |
| 28 | Medium mc=0.8 fraud=0.3 evidence=False | 0.800 | 0.80 | 0.30 | False | — | 0.7300 | manual_review | NO |
| 29 | Medium mc=0.8 fraud=0.6 evidence=True | 0.800 | 0.80 | 0.60 | True | — | 0.8400 | fast_review | Yes |
| 30 | Medium mc=0.8 fraud=0.6 evidence=False | 0.800 | 0.80 | 0.60 | False | — | 0.6400 | manual_review | NO |
| 31 | Fraud type: duplicate_image | 0.800 | 0.90 | 0.40 | True | — | 0.9150 | auto | Yes |
| 32 | Fraud type: screenshot_detected | 0.800 | 0.90 | 0.30 | True | — | 0.9450 | auto | Yes |
| 33 | Fraud type: photo_of_photo | 0.800 | 0.90 | 0.30 | True | — | 0.9450 | auto | Yes |
| 34 | Fraud type: edited_image | 0.800 | 0.90 | 0.30 | True | — | 0.9450 | auto | Yes |
| 35 | Fraud type: timestamp_mismatch | 0.800 | 0.90 | 0.30 | True | — | 0.9450 | auto | Yes |
| 36 | Fraud type: camera_mismatch | 0.800 | 0.90 | 0.20 | True | — | 0.9750 | auto | Yes |
| 37 | Fraud type: frequent_claims | 0.800 | 0.90 | 0.30 | True | — | 0.9450 | auto | Yes |
| 38 | Fraud type: image_reuse | 0.800 | 0.90 | 0.40 | True | — | 0.9150 | auto | Yes |
| 39 | Fraud type: severity_escalation | 0.800 | 0.90 | 0.20 | True | — | 0.9750 | auto | Yes |
| 40 | Fraud type: no_exif | 0.800 | 0.90 | 0.10 | True | — | 1.0000 | auto | Yes |
| 41 | Conversation: Contradiction only | 0.800 | 0.90 | 0.10 | True | C | 0.8550 | fast_review | Yes |
| 42 | Conversation: Retraction only | 0.800 | 0.90 | 0.10 | True | R | 0.8050 | fast_review | Yes |
| 43 | Conversation: Uncertainty only | 0.800 | 0.90 | 0.10 | True | U | 0.9050 | auto | Yes |
| 44 | Conversation: Sarcasm only | 0.800 | 0.90 | 0.10 | True | S | 1.0000 | auto | Yes |
| 45 | Conversation: Negation only | 0.800 | 0.90 | 0.10 | True | N | 1.0000 | auto | Yes |
| 46 | Conversation: Changing claims only | 0.800 | 0.90 | 0.10 | True | CC | 1.0000 | auto | Yes |
| 47 | Conversation: Contradiction + Retraction | 0.800 | 0.90 | 0.10 | True | R,C | 0.6550 | manual_review | Yes |
| 48 | Conversation: Uncertainty + Sarcasm | 0.800 | 0.90 | 0.10 | True | U,S | 0.9050 | auto | Yes |
| 49 | Extreme: Near-perfect signals | 0.999 | 1.00 | 0.00 | True | — | 1.0000 | auto | Yes |
| 50 | Extreme: Near-zero signals | 0.001 | 0.00 | 1.00 | False | — | 0.0000 | evidence_request | Yes |
| 51 | Extreme: All middle | 0.500 | 0.50 | 0.50 | True | — | 0.5250 | manual_review | Yes |
| 52 | Extreme: All zeros | 0.000 | 0.00 | 0.00 | False | — | 0.2000 | evidence_request | Yes |
| 53 | Extreme: Perfect everything | 1.000 | 1.00 | 0.00 | True | — | 1.0000 | auto | Yes |
| 54 | Extreme: Max confidence, zero agreement | 0.990 | 0.00 | 0.00 | True | — | 1.0000 | auto | Yes |
| 55 | Extreme: Zero confidence, max agreement | 0.000 | 0.99 | 0.00 | True | — | 0.5485 | manual_review | Yes |
| 56 | Extreme: High fraud, medium other | 0.500 | 0.50 | 0.75 | False | — | 0.2500 | evidence_request | Yes |
| 57 | Extreme: Below-threshold all | 0.300 | 0.40 | 0.60 | True | — | 0.2800 | evidence_request | Yes |
| 58 | Extreme: Boundary: fast_review border | 0.750 | 0.85 | 0.00 | True | — | 0.9775 | auto | Yes |
| 59 | Composite: Escalating fraud with retraction | 0.700 | 0.80 | 0.65 | True | R,C | 0.3750 | evidence_request | Yes |
| 60 | Composite: Uncertain + contradicting + evidence issue | 0.600 | 0.70 | 0.20 | False | R,U | 0.2450 | evidence_request | Yes |
| 61 | Composite: Sarcastic fraud claim | 0.800 | 0.90 | 0.50 | True | — | 0.8850 | fast_review | Yes |
| 62 | Composite: Clean claim with low agreement | 0.850 | 0.45 | 0.00 | True | — | 1.0000 | auto | Yes |
| 63 | Composite: New user first claim | 0.700 | 0.90 | 0.00 | True | — | 0.9350 | auto | Yes |
| 64 | Composite: Multiple fraud signals + clean convo | 0.600 | 0.80 | 0.70 | True | — | 0.6100 | manual_review | Yes |
| 65 | Composite: All conversations anomalies | 0.750 | 0.85 | 0.10 | True | R,C,U | 0.4975 | evidence_request | Yes |
| 66 | Composite: Borderline auto/fast_review | 0.920 | 0.95 | 0.05 | True | — | 1.0000 | auto | Yes |
| 67 | Composite: Borderline fast/manual review | 0.780 | 0.85 | 0.15 | True | — | 0.9625 | auto | Yes |
| 68 | Composite: Borderline manual/evidence_request | 0.520 | 0.60 | 0.30 | False | U | 0.3200 | evidence_request | Yes |

## Breakdown Analysis (Selected Scenarios)

### High Confidence (+ Agreement + Evidence, No Fraud)

- **Perfect auto-approve**: Model=0.95 + Agreement=0.15 - Fraud=0.0 + Evidence=0.1 - Conv=0.0 → **1.0000** → **auto**
- **Strong auto-approve**: Model=0.93 + Agreement=0.1425 - Fraud=0.0 + Evidence=0.1 - Conv=0.0 → **1.0000** → **auto**
- **Auto-approve with high agreement**: Model=0.91 + Agreement=0.15 - Fraud=0.0 + Evidence=0.1 - Conv=0.0 → **1.0000** → **auto**

### Fraud-Heavy Scenarios

- **Deep-reject worst case**: Model=0.1 - Fraud=0.24 + Evidence=-0.1 → **0.0000** → **evidence_request**
- **Reject with contradictions**: Model=0.15 - Fraud=0.21 + Evidence=-0.1 → **0.0000** → **evidence_request**
- **Lowest possible confidence path**: Model=0.05 - Fraud=0.27 + Evidence=-0.1 → **0.0000** → **evidence_request**

### Conversation Anomaly Impact

- **Deep-reject worst case**: Model=0.1 - Conv=0.2 → **0.0000** → **evidence_request**
- **Reject with contradictions**: Model=0.15 - Conv=0.25 → **0.0000** → **evidence_request**
- **Lowest possible confidence path**: Model=0.05 - Conv=0.35 → **0.0000** → **evidence_request**

### Inappropriate Routing Analysis

- ❌ **Medium mc=0.5 fraud=0.0 evidence=False**: manual_review (final=0.5200) — expected different routing given signals
- ❌ **Medium mc=0.6 fraud=0.0 evidence=False**: manual_review (final=0.6200) — expected different routing given signals
- ❌ **Medium mc=0.6 fraud=0.3 evidence=False**: manual_review (final=0.5300) — expected different routing given signals
- ❌ **Medium mc=0.7 fraud=0.0 evidence=False**: manual_review (final=0.7200) — expected different routing given signals
- ❌ **Medium mc=0.7 fraud=0.3 evidence=False**: manual_review (final=0.6300) — expected different routing given signals
- ❌ **Medium mc=0.7 fraud=0.6 evidence=False**: manual_review (final=0.5400) — expected different routing given signals
- ❌ **Medium mc=0.8 fraud=0.0 evidence=False**: fast_review (final=0.8200) — expected different routing given signals
- ❌ **Medium mc=0.8 fraud=0.3 evidence=False**: manual_review (final=0.7300) — expected different routing given signals
- ❌ **Medium mc=0.8 fraud=0.6 evidence=False**: manual_review (final=0.6400) — expected different routing given signals

## Calibration Correctness Assessment

### Strengths

1. **Fraud-weighted correctly**: Fraud penalty (×0.30) is the strongest single penalty — appropriate for insurance claims

2. **Retraction is heavily penalized**: -0.20 for retractions ensures retracted claims never auto-approve

3. **Evidence boost/cutoff**: Missing evidence (-0.10) pushes borderline cases below routing thresholds

4. **Routing thresholds reasonable**: ~0.90 for auto, ~0.75 for fast review, ~0.50 for manual, <0.50 for evidence request

5. **Symmetric signal integration**: Both positive and negative signals balance realistically


### Weaknesses / Edge Cases

1. **Agreement boost limited**: Max contribution is 0.15 (at 1.0 agreement). For multi-model systems, high agreement should boost more.

2. **No uncertainty penalty in formula**: `has_uncertainty` sets a conversation flag but conv_penalty only adds if explicitly in formula. Verify: uncertainty adds 0.1 to conv_penalty.

3. **Negative cap at 0.0**: `max(0.0, min(1.0, final))` removes information — could differentiate between 0.0 and 0.05.

4. **Sarcasm ignored in confidence**: Sarcasm is flagged but has no confidence penalty. A sarcastic claim should reduce trust.

5. **Static base fallback**: When model_confidence is 0, base=0.3 hardcoded. This creates false confidence for failed model runs.

6. **Evidence boost symmetric**: +0.1 for met, -0.1 for failed. Failing evidence should perhaps penalize more than meeting it rewards.

7. **No agreement penalty for low scores**: agreement=0.0 gives 0 contribution, but very low agreement should penalize.


## Signal Contribution Breakdown (All Scenarios)

| Signal | Average | Min | Max | Range |
|--------|---------|-----|-----|-------|
| Model Confidence | 0.6669 | 0.0000 | 1.0000 | 1.0000 |
| Agreement Boost | 0.1148 | 0.0000 | 0.1500 | 0.1500 |
| Fraud Penalty | 0.0825 | 0.0000 | 0.2997 | 0.2997 |
| Evidence Boost | 0.0412 | -0.1000 | 0.1000 | 0.2000 |
| Conversation Penalty | 0.0426 | 0.0000 | 0.4500 | 0.4500 |