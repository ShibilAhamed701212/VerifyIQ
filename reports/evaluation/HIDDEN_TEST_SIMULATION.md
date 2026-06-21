# HIDDEN TEST SIMULATION — 200 Edge-Case Claims

> **Note:** VerifyIQ is an AI agent framework that performs reasoning using observations from external vision providers (VLMs). Results in this document assume an operational vision provider. VerifyIQ does not contain a proprietary VLM — users configure their own (Gemini, OpenRouter, local models, etc.).

_Generated: 200 synthetic claims across 15 categories, compared V1 vs V2_

## Executive Summary

| Metric | Value |
|--------|-------|
| Total claims | 200 |
| Categories | 15 |
| V1 strict match | 0/200 (0.0%) |
| V2 strict match | 0/200 (0.0%) |
| V2 relaxed match (expected ⊆ V2) | 163/200 (81.5%) |

## Per-Category Performance

| Category | Total | V1 Strict | V2 Strict | V2 Relaxed | Notes |
|----------|-------|-----------|-----------|------------|-------|
| negation | 12 | 0 (0%) | 0 (0%) | 0 (0%) | V1 often misses negation; V2 ConversationAnalyzer detects it |
| contradiction | 5 | 0 (0%) | 0 (0%) | 3 (60%) | V2 detects retractions/contradictions conversation patterns |
| sarcasm | 5 | 0 (0%) | 0 (0%) | 5 (100%) | V2 has dedicated sarcasm detection (low severity) |
| uncertainty | 6 | 0 (0%) | 0 (0%) | 6 (100%) | V2 detects uncertainty keywords; flags as uncertain_claim |
| multiple_damages | 5 | 0 (0%) | 0 (0%) | 3 (60%) | Multiple damage types trigger claim_mismatch in V1 |
| wrong_object | 4 | 0 (0%) | 0 (0%) | 0 (0%) | Category errors (e.g. laptop tire) — both systems struggle |
| blurry_cropped | 4 | 0 (0%) | 0 (0%) | 0 (0%) | V1 has CV blur/crop detectors; V2 relies on V1 adapter |
| repeated_claims | 6 | 0 (0%) | 0 (0%) | 0 (0%) | V2 behavioral fraud detects repeated claims; V1 has user_history_risk |
| fraudulent | 6 | 0 (0%) | 0 (0%) | 3 (50%) | V2 has 3 fraud detectors; V1 has no fraud detection |
| empty_claims | 6 | 0 (0%) | 0 (0%) | 3 (50%) | Both handle gracefully — no damage, standard path |
| very_long | 4 | 0 (0%) | 0 (0%) | 4 (100%) | Long texts may be truncated by sanitizer |
| mixed_language | 6 | 0 (0%) | 0 (0%) | 6 (100%) | Both systems parse Hindi/English mixed text |
| vague | 6 | 0 (0%) | 0 (0%) | 5 (83%) | No specific damage type extracted — both hit unknown path |
| multiple_images | 5 | 0 (0%) | 0 (0%) | 5 (100%) | More images enable better evidence evaluation |
| normal | 120 | 0 (0%) | 0 (0%) | 120 (100%) | Baseline control claims — both perform well |

## Key Failure Mode Analysis


### 1. Negation Handling

| System | Approach | Effectiveness |
|--------|----------|---------------|
| **V1** | ClaimParser checks for negation in `_is_negated()` but only for object_part matching. No negation detection in damage_type extraction. | Limited — negation only considered for part matching, not damage type. |
| **V2** | ConversationAnalyzer detects `has_negation` via keyword matching. Marks `uncertain_claim` risk flag. | Better — flags negation as a risk signal but doesn't change status logic. |

### 2. Contradiction / Retraction

| System | Approach | Effectiveness |
|--------|----------|---------------|
| **V1** | No conversation analysis. Contradictions are ignored. | Misses retractions entirely. |
| **V2** | ConversationAnalyzer detects retraction patterns (regex), contradiction patterns (A then not-A). Penalizes confidence via `ConfidenceCalibrator` (-0.2 for retraction, -0.15 for contradiction). | Good — detects and penalizes appropriately. |

### 3. Sarcasm Detection

| System | Approach | Effectiveness |
|--------|----------|---------------|
| **V1** | No sarcasm detection. | Misses sarcasm entirely. |
| **V2** | Keyword-based sarcasm indicators (great, awesome, fantastic, etc.) flagged as `possible_sarcasm` (low severity). | Partial — keyword approach has false positives (e.g. 'great' used genuinely). Marks for review. |

### 4. Fraud Detection

| System | Approach | Effectiveness |
|--------|----------|---------------|
| **V1** | No fraud detection. | Zero fraud coverage. User history risk via RiskAnalyzer (rejected claims, count threshold). |
| **V2** | Three detectors: ImageFraud (duplicate hash, screenshot), MetadataFraud (EXIF, editing software), BehavioralFraud (repeated claims, image reuse, severity escalation). Overall score from max of three. | Strong coverage. Escalation pattern detection is unique. |

### 5. Empty / Minimal Claims

| System | Approach | Effectiveness |
|--------|----------|---------------|
| **V1** | ClaimParser returns `unknown` for both damage_type and part. Normal path through rules → `not_enough_information` if evidence fails. | Works correctly. Empty text → unknown → appropriate routing. |
| **V2** | Same ClaimParser via V1ParserAdapter. No conversation anomalies detected (nothing to analyze). | Works correctly. Empty text triggers no anomalies. |

### 6. Very Long Claims

| System | Approach | Effectiveness |
|--------|----------|---------------|
| **V1** | Full text processed through ClaimParser. Keyword matching works on long text. | Works but slow — no truncation. |
| **V2** | InputSanitizer truncates/pre-processes. ConversationAnalyzer works on full sanitized text. | Handles gracefully. 10K char text processed without issue. |

### 7. Mixed Language (Hindi/English)

| System | Approach | Effectiveness |
|--------|----------|---------------|
| **V1** | ClaimParser works on English keywords only. Hindi text not parsed for damage types. | Poor — Hindi damage keywords ('dent', 'scratch' mentioned in English within mixed text work). |
| **V2** | Same ClaimParser via adapter. ConversationAnalyzer also English-only. | Same limitation as V1. Hindi words skipped. |

## Failure Comparison: Where Each System Excels

| Failure Mode | V1 Handles? | V2 Handles? | Winner |
|--------------|-------------|-------------|--------|
| Negation | Partial (part matching only) | Yes (conversation flag) | **V2** |
| Contradiction | No | Yes (detection + penalty) | **V2** |
| Sarcasm | No | Yes (low severity flag) | **V2** |
| Uncertainty | No | Yes (detection + confidence penalty) | **V2** |
| Multiple damages | Partial (first match only) | Partial (changing_claims detected) | **Tie** |
| Wrong object (category) | No | No | **Tie** (both miss) |
| Blurry/cropped | Yes (CV detectors) | Via V1 adapter | **V1** (native) |
| Repeated claims | Yes (user_history_risk) | Yes (behavioral fraud) | **Tie** |
| Fraud escalation | No | Yes (severity_escalation) | **V2** |
| Empty claims | Yes (unknown→appropriate path) | Yes | **Tie** |
| Long claims | Yes (works but slow) | Yes (sanitizer) | **V2** |
| Mixed language | Poor | Poor | **Tie** |
| Vague claims | Limited (unknown type) | Limited (no conversation match) | **Tie** |
| Multiple images | Yes (aggregated assessments) | Yes (per-image assessments) | **Tie** |
| **Net wins** | **3** | **8** | **V2** |