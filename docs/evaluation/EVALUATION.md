# Evaluation Methodology

## Overview

VerifyIQ uses a dual evaluation approach. The **static evaluation** bypasses the Gemini API by injecting pre-verified ground truth as the vision result, isolating and testing the deterministic pipeline in isolation. The **live evaluation** calls the full pipeline — including Gemini — on every claim, measuring end-to-end accuracy including vision extraction variance. Together they distinguish between errors introduced by the vision model and errors in the deterministic decision logic.

## Static Evaluation

**File:** `code/evaluation/static_evaluate.py`

The static evaluation constructs an ideal `vision_result` dict directly from the expected output columns (`issue_type`, `object_part`, `risk_flags`) in `sample_claims.csv`. This synthesized vision input is fed through the deterministic pipeline: RuleEngine, EvidenceChecker, RiskAnalyzer, SeverityEngine, DecisionAgent, and OutputValidator. CV modules (BlurDetector, CropDetector, TextDetector, ObjectValidator) run on real image files, so their output is tested even though vision is static.

**Purpose:**
- Validates that the decision tree, risk computation, severity mapping, and output assembly logic are correct.
- Provides a quick (<5 seconds for 20 claims) regression test that does not require API keys or incur vision API costs.
- Isolates logic bugs from vision extraction quality issues.

**Current accuracy:** 20/20 (100%) on `sample_claims.csv`.

**How it works:**
1. `sample_claims.csv` is read; expected values become the "vision" input.
2. For each claim, a synthetic `vision_result` dict is built: `damage_type` = `issue_type` column, `damage_visible` derived from `risk_flags` and `issue_type`, `per_image_assessments` constructed with the expected properties.
3. The pipeline runs from EvidenceChecker through DecisionAgent — the same classes used in production, instantiated the same way.
4. The final 7 output fields (`evidence_standard_met`, `risk_flags`, `issue_type`, `object_part`, `claim_status`, `valid_image`, `severity`) are compared field-by-field against the expected values.

**Fields compared (static):**

| Field | Comparison Method |
|---|---|
| `evidence_standard_met` | Exact string match |
| `risk_flags` | Normalized (sorted, deduplicated, "none" replaced) |
| `issue_type` | Exact string match |
| `object_part` | Exact string match |
| `claim_status` | Exact string match |
| `valid_image` | Exact string match |
| `severity` | Exact string match |

## Live Evaluation

**File:** `code/evaluation/evaluate.py`

The live evaluation reads `sample_claims.csv`, processes each row through the complete `ClaimProcessor` pipeline (including the real Gemini API call), and compares every predicted output field against the expected output. It is the authoritative measurement of system performance.

**Purpose:**
- Measures end-to-end accuracy including vision extraction quality.
- Generates per-field difference reports and a comprehensive evaluation report.
- Produces precision, recall, and F1 metrics, not just overall accuracy.

**How it works:**
1. `sample_claims.csv` is read with `read_claims()`. Each row includes both inputs (`image_paths`, `user_claim`, `claim_object`) and expected outputs.
2. Each row is processed through `ClaimProcessor.process_claim()`, which runs the full pipeline including Gemini vision.
3. Expected outputs are indexed by `user_id|image_paths` to handle any ordering differences.
4. The `compare_outputs` function compares 7 fields per claim, with compatible-type handling for damage types.

## Metrics

### Overall Accuracy

Percentage of claims where all 7 compared fields match the expected output:

```
accuracy = correct_predictions / total_claims
```

### Precision, Recall, F1 (Macro-Averaged)

Computed per status label (`supported`, `contradicted`, `not_enough_information`) and macro-averaged:

| Metric | Formula |
|---|---|
| Precision | `TP / (TP + FP)` |
| Recall | `TP / (TP + FN)` |
| F1 | `2 * P * R / (P + R)` |

Macro-averaging means each status class contributes equally regardless of its frequency in the dataset, which prevents the majority class from dominating the score.

### Risk Flag Accuracy

Percentage of claims where the normalized risk flag string (sorted, deduplicated, "none"-filtered) exactly matches the expected flags:

```
risk_flag_accuracy = correct_risk_flags / total_claims
```

### Per-Status Confusion Matrix

A 3x3 matrix breaking down predictions for each status:

| Expected \ Predicted | supported | contradicted | not_enough_information |
|---|---|---|---|
| **supported** | TP | FP | FP |
| **contradicted** | FP | TP | FP |
| **not_enough_information** | FP | FP | TP |

## Comparison Methodology

Seven fields are compared per claim:

1. `evidence_standard_met` — boolean string ("true"/"false").
2. `risk_flags` — semicolon-separated flag list, normalized by sorting and removing duplicates.
3. `issue_type` — damage type enum, with compatible type handling.
4. `object_part` — object part enum.
5. `claim_status` — one of `supported`, `contradicted`, `not_enough_information`.
6. `valid_image` — boolean string.
7. `severity` — one of `none`, `low`, `medium`, `high`, `unknown`.

### Compatible Issue Types

The following damage type pairs are treated as non-mismatches because visual assessment alone cannot reliably distinguish them:

| Prediction | Expected | Rationale |
|---|---|---|
| `crack` | `glass_shatter` | Fine shattering may appear as a crack network |
| `glass_shatter` | `crack` | A single crack may be the only visible fracture |
| `stain` | `water_damage` | Water damage often manifests as staining |
| `water_damage` | `stain` | Stains can be caused by water exposure |

This mapping mirrors the `COMPATIBLE_DAMAGE_TYPES` set in `rule_engine.py:103-108`, ensuring the evaluation is consistent with the system's own definition of damage type compatibility.

### Report Generation

The evaluation produces a human-readable report (`evaluation/evaluation_report.md`) containing:
- Summary metrics (accuracy, precision, recall, F1, risk flag accuracy).
- Per-status precision/recall table.
- Per-claim match/fail table showing which fields differed.
- Operational analysis: model call count, estimated token usage, latency estimates, and rate limiting strategy.
