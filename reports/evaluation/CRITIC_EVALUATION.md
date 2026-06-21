# Critic Evaluation Report

> **Note:** VerifyIQ is an AI agent framework that performs reasoning using observations from external vision providers (VLMs). Results in this document assume an operational vision provider. VerifyIQ does not contain a proprietary VLM — users configure their own (Gemini, OpenRouter, local models, etc.).

## 1. Overview

The codebase contains two independent critic layers operating at different stages of the pipeline:

- **V1 Submission Critic** (`code/submission_critic.py`): Post-processes CSV output rows, *mutating* them to fix inconsistencies. Runs as a final validation pass over the entire output dataset.
- **V2 Critic** (`code/v2/critic/v2_critic.py`): Checks pipeline-level consistency across layers (status, fraud, conversation, consensus, severity). Returns `PASS` or `REVIEW_REQUIRED` — it does **not** mutate decisions.

Additionally, `code/evaluation/evaluate.py` is the ground-truth comparison harness and `code/evaluation/error_analysis.py` classifies mismatches.

---

## 2. V1 Submission Critic

**File:** `code/submission_critic.py`

**Role:** Post-processes every row of `output.csv`. Mutates rows in-place to enforce consistency rules. Called by `main.py` as a final pass before writing CSV output.

### Checks Performed

| Check | Code | Action |
|-------|------|--------|
| **Unknown issue/severity/part without review flag** | `_fix_unknown_without_review_flag` | Adds `manual_review_required` if `issue_type`/`severity`/`object_part` is unknown and status is not `not_enough_information` |
| **Supported + damage=none** | `_fix_contradiction_detected_supported_with_no_damage` | Mutates `claim_status → contradicted` |
| **Supported + damage=unknown** | Same function | Mutates `claim_status → not_enough_information` |
| **Contradicted + valid damage_type + evidence not met** | Same function | Mutates `claim_status → not_enough_information` |
| **Supported + claim_mismatch flag** | `_fix_contradiction_supported_with_conflict` | Mutates `claim_status → contradicted` |
| **Critical flags without manual_review** | `_fix_missing_manual_review` | Adds `manual_review_required` when `possible_manipulation`, `non_original_image`, or `user_history_risk` present |
| **Missing required fields** | `_ensure_required_fields` | Fills empty fields with `""` |

### Design Philosophy

The V1 submission critic is **reactive and destructive** — it assumes the pipeline can produce logically inconsistent outputs and fixes them. It rebuilds the CSV spec: exactly 14 columns, valid enum ranges for `claim_status`, `risk_flags` serialized as semicolons, etc.

### What It Catches (Real Errors)

- **supported + damage=none** (issue_type="none"): A logical impossibility. If there is no damage, you cannot support the claim. The critic downgrades to `contradicted`. This is a genuine model error.
- **supported + unknown damage**: If the model doesn't know what damage exists but says "supported", this is unsafe. Downgrades to `not_enough_information`.
- **Critical risk flags without manual_review**: Ensures human review is mandatory for manipulation, non-original images, and flagged user histories.

### What It Misses

- **Supported without evidence** (evidence_standard_met=false): The submission critic does not check this combination — it only checks `evidence_standard_met` in the context of `contradicted + valid damage_type`. A `supported` claim with unmet evidence standard passes through.
- **High fraud with supported verdict**: No fraud-awareness at the submission level.
- **Conversation anomalies with supported verdict**: No awareness of retraction/contradiction signals.
- **Consensus failures**: No awareness of model agreement or model failures.

### False Positive Rate

FP rate is effectively **zero** when the pipeline produces valid data — each fix is a deterministic logical rule. However, the critic introduces **false positives in the sense of over-correction**: if a claim truly is `supported` with `issue_type=none` (edge-case: "there is no damage but here is proof the item is intact"), the critic incorrectly downgrades to `contradicted`. In the current dataset, this never occurs — all sample claims with `none` damage are genuinely contradicted.

---

## 3. V2 Critic (V2Critic)

**File:** `code/v2/critic/v2_critic.py`

**Role:** Post-processing consistency checks on the assembled `V2Decision` using cross-layer signals. Runs in pipeline Layer 8. Returns `("PASS", [])` or `("REVIEW_REQUIRED", [issue_codes])`. **Does not mutate** — it only flags.

### Check 1: Status Consistency

| Condition | Issue Code | Triggers When |
|-----------|-----------|---------------|
| `supported` + `issue_type in ("none", "unknown")` | `supported_with_invalid_issue` | Pipeline says "supported" but damage type is unknown or none |
| `supported` + `not evidence_standard_met` | `supported_without_evidence` | Pipeline says "supported" but no evidence was submitted that meets the standard |
| `contradicted` + `issue_type == "unknown"` | `contradicted_with_unknown_type` | Pipeline says "contradicted" but doesn't know what damage was expected |

**Catch real errors?** Yes — `supported_without_evidence` is a genuine safety issue. `supported_with_invalid_issue` mirrors the V1 submission critic's strongest check.

**False positives?** `contradicted_with_unknown_type` can fire when the claim parser extracts no damage type but the VLM sees a different damage type, leading to a correct `contradicted` based on mismatch. The critic flags this as suspicious even though the RuleEngine made a valid decision.

**What it misses:** `contradicted` with `issue_type=none` — the critic only checks `issue_type="unknown"` for contradicted cases, not `"none"`. Also does not check whether `not_enough_information` has a valid reason.

### Check 2: Fraud Consistency

| Condition | Issue Code | Triggers When |
|-----------|-----------|---------------|
| `high_risk` + `supported` | `high_fraud_with_supported_verdict` | Fraud detection says high risk but verdict supports the claim |
| `overall_fraud_score > 0.5` + no `manual_review_required` in risk_flags | `high_fraud_without_manual_review` | High fraud score escaped manual review requirement |

**Catch real errors?** Yes — the pipeline decision assembly (`_assemble_decision`) already adds `manual_review_required` when `fraud.high_risk` is true (pipeline.py:302-303). But if risk_flags are overwritten or filtered later, this check catches the bypass. The `high_fraud_with_supported_verdict` check catches the rare case where the fraud layer flags a claim but the rule engine still returns "supported" — a genuine conflict.

**False positives?** `high_fraud_with_supported_verdict` can fire when the fraud score is legitimate (e.g., image reuse from a multi-claim household) but the damage itself is genuine. The V1 rule engine's deterministic logic is correct, but the critic sees the fraud signal as contradictory.

**What it misses:** Does not check whether fraud signals were *processed at all*. If all three fraud detectors silently failed, `FraudReport()` defaults to zero scores, so `overall_fraud_score=0` and `high_risk=False` — no check triggers. A fraud detection outage is invisible to the critic.

### Check 3: Conversation Consistency

| Condition | Issue Code | Triggers When |
|-----------|-----------|---------------|
| `has_retraction` + `supported` | `retracted_claim_with_supported_verdict` | Claim text contains retraction language but verdict is supported |
| `has_contradictions` + `supported` | `contradictory_claim_with_supported_verdict` | Claim text contradicts itself but verdict is supported |

**Catch real errors?** Yes — this is the most consistently triggered check in validation runs (the primary trigger in 20-sample evaluations). A retracted claim being "supported" is a genuine logical inconsistency.

**False positives?** By design — the critique is conservative. A customer might say "I think there's a dent... actually no, wait, it's a scratch" (retraction + correction) and the corrected version is genuinely supported. The critic flags these cases because conversational uncertainty is treated as requiring human review. The V1_VS_V2 report explicitly documents this: *"V2 extra flags are genuine signals not in ground truth"*. The architect prefers over-flagging to under-flagging.

**What it misses:** Does not check `has_sarcasm` or `has_uncertainty` as triggers for review. Sarcasm is treated as low-severity and not escalated. Does not check whether the conversation report was empty because the analyzer failed (silent failure — same pattern as fraud).

### Check 4: Consensus Consistency

| Condition | Issue Code | Triggers When |
|-----------|-----------|---------------|
| `agreement_score < 0.5` + `claim_status != "not_enough_information"` | `low_agreement_with_definitive_verdict` | Models disagree strongly but pipeline gives a definitive (supported/contradicted) verdict |
| `models_succeeded == 0` + no risk_flags | `all_models_failed_without_risk_flags` | All models crashed but nothing flags this as suspicious |

**Catch real errors?** `all_models_failed_without_risk_flags` catches a dangerous state — the pipeline made a decision despite zero model outputs. The decision assembly (pipeline.py:304-305) *should* add `manual_review_required` when `models_succeeded == 0`, but if risk_flags are later cleared, this catch fires.

**False positives?** `low_agreement_with_definitive_verdict` can fire even in single-model mode (only one provider available). The `ConsensusEngine` sets `agreement_score=1.0` for single-model scenarios, but if the observation layer produces no usable data, `agreement_score` can still be low. In practice, with no API keys (degraded mode), the observation layer returns empty observations, consensus defaults to `agreement_score=0.0`, and the claim_status from the V1 rule adapter could still be `not_enough_information` — which the check correctly skips.

**What it misses:** Does not check for `agreement_score` in the 0.5-0.7 range with a definitive verdict — a moderate disagreement might still warrant review. Also does not check `unanimous=true` against evidence quality.

### Check 5: Severity Consistency

| Condition | Issue Code | Triggers When |
|-----------|-----------|---------------|
| `severity == "high"` + `confidence < 0.5` | `high_severity_with_low_confidence` | Pipeline assigns high severity but has low confidence |

**Catch real errors?** Yes — classifying damage as high-severity (e.g., cracked windshield affecting safety) with low confidence is a legitimate concern for manual review.

**False positives?** Confidence calibration operates independently of severity assignment. A claim could have `severity=high` (based on damage type) and `confidence < 0.5` (based on evidence quality), producing a high-severity claim that genuinely needs review — the critic is correct to flag this.

**What it misses:** Does not check the reverse — `low severity + high confidence` is not flagged (this is fine — low severity doesn't need extra review). Does not check `high severity + low agreement` or `high severity + high fraud`.

---

## 4. Evaluation Framework (`evaluate.py` + `error_analysis.py`)

### `code/evaluation/evaluate.py`

This is the **ground-truth comparison** layer, not a consistency critic. It:

1. Runs the pipeline (via `ClaimProcessor`) on `sample_claims.csv` which has known expected outputs
2. Compares predicted vs expected across 7 fields: `evidence_standard_met`, `risk_flags`, `issue_type`, `object_part`, `claim_status`, `valid_image`, `severity`
3. Calculates per-status precision/recall/f1, overall accuracy, risk flag accuracy
4. Treats compatible issue types (glass_shatter↔crack, stain↔water_damage) as non-errors

It is an **external validation tool**, not a run-time check. It does not influence pipeline behavior or output.

### `code/evaluation/error_analysis.py`

Classifies mismatches from the evaluation into categories: `damage type mismatch`, `object part mismatch`, `evidence issue`, `risk flag issue`, `confidence issue`, `other`. Generates a grouped error report. Used for development debugging, not production QC.

---

## 5. Critic Coverage Matrix

### Error Types vs Detection

| Error Type | V1 Submission Critic | V2Critic | Evaluation Harness |
|------------|---------------------|----------|-------------------|
| Supported + no damage type | **Catches** (mutates → contradicted) | **Catches** (flags REVIEW_REQUIRED) | Detected as mismatch |
| Supported + unknown damage | **Catches** (mutates → not_enough_info) | **Catches** (flags REVIEW_REQUIRED) | Detected as mismatch |
| Supported + no evidence | **Misses** | **Catches** (supported_without_evidence) | Detected as mismatch |
| Supported + high fraud | **Misses** (no fraud awareness) | **Catches** (high_fraud_with_supported_verdict) | Not in ground truth* |
| Supported + retraction/contradiction | **Misses** (no conversation awareness) | **Catches** (retracted/contradictory) | Not in ground truth* |
| Contradicted + unknown damage type | **Misses** | **Catches** (contradicted_with_unknown_type) | Detected as mismatch |
| Contradicted + valid damage + no evidence | **Catches** (mutates → not_enough_info) | **Misses** | Detected as mismatch |
| Low agreement + definitive verdict | **Misses** (no consensus awareness) | **Catches** (low_agreement) | Not in ground truth* |
| All models failed, no risk flags | **Misses** | **Catches** (all_models_failed) | Not in ground truth* |
| High severity + low confidence | **Misses** | **Catches** (high_severity_low_conf) | Not in ground truth* |
| Critical flags without manual_review | **Catches** (adds flag) | **Misses** (decoupled check) | Not in ground truth* |
| Missing required CSV fields | **Catches** (fills empties) | **Misses** (operates on objects, not CSV rows) | Would break evaluation |
| claim_mismatch + supported | **Catches** (mutates → contradicted) | **Misses** (no check for this flag) | Detected as mismatch |
| Completely degraded fraud/conversation | **Misses** (no awareness) | **Misses** (silent fallback → defaults) | N/A |

*\*Ground truth labels in sample_claims.csv do not include fraud, conversation, or consensus signals.*

### Detection Strengths

| Critic | Primary Strengths |
|--------|------------------|
| **V1 Submission Critic** | CSV-level data integrity, field presence, serialization consistency, logical status→damage rules, critical risk flag enforcement |
| **V2 Critic** | Cross-layer signal conflict detection (status vs fraud vs conversation vs consensus vs severity), model failure detection, evidence gap detection |
| **Both combined** | Nearly complete coverage of status-damage consistency (with overlap); complementary on fraud/conversation/consensus (V2) and CSV integrity (V1) |

### Detection Gaps (Missed by Both)

| Gap | Risk | Why Missed |
|-----|------|-----------|
| Fraud/conversation detector silent failures | Pipeline could process claims with no fraud/conversation signals without warning | Both critics assume these layers produce valid reports; no "did this layer actually run?" check |
| Rate-limiting/API degradation | Pipeline silently degrades without alerting operators | Neither critic has external health-check awareness |
| Concurrent access races (MetricsCollector singleton) | Metrics corruption under concurrency | Neither critic checks thread safety |
| Memory leaks | Gradual degradation over large batches | Neither critic monitors resource usage |
| Confidence drift | Confidence calibration depends on all 5 signals; if one drops silently, the critic doesn't catch it | Critic only checks `confidence < 0.5` with `high severity`, not confidence-value plausibility |

### False Warning Rates

| Critic | Estimated FP Rate | Notes |
|--------|-------------------|-------|
| **V1 Submission Critic** | 0% on current data | Pure deterministic logic applied to structured data; no ambiguity in the rules |
| **V2Critic — supported_with_invalid_issue** | Modest | Overlaps with V1 submission critic; both catch the same condition in different forms |
| **V2Critic — high_fraud_with_supported_verdict** | Low-Moderate | Fraud signals can trigger even when damage is genuine (image reuse in multi-claim household) |
| **V2Critic — retracted/contradictory claim** | **Moderate-High (by design)** | Architect explicitly accepts this: "the critic may over-flag on claims where the RuleEngine correctly determines supported despite conversation uncertainty" |
| **V2Critic — low_agreement_with_definitive** | Low | In single-model mode (no API keys), agreement_score defaults to 1.0 so rarely triggers; in multi-model mode, low agreement + definitive verdict is genuinely suspicious |
| **V2Critic — high_severity_low_confidence** | Low | A genuinely useful safety check; severity and confidence derive from independent sources |

---

## 6. V2Critic Specific Scoring (from validation runs)

| Issue | Detection Accuracy | Notes |
|-------|-------------------|-------|
| `supported_with_invalid_issue` | Correctly flags supported claims where issue_type is none/unknown. Overlaps with V1 submission critic. | In 20-sample evaluation, no V2 output has `supported + none/unknown` because V1's RuleEngine prevents this combination |
| `supported_without_evidence` | Flags the dangerous "supported but no evidence" state. | Correctly triggers when evidence_standard_met=false and status=supported |
| `contradicted_with_unknown_type` | Flags contradicted claims with unknown issue_type. | May produce false warnings when VLM sees different damage than the ClaimParser extracted |
| `high_fraud_with_supported_verdict` | Cross-layer fraud+status conflict detection. | FP risk when fraud is legitimate (image reuse) but damage is genuine |
| `high_fraud_without_manual_review` | Backstop for pipeline decision assembly. | Redundant with pipeline's own check (pipeline.py:302-303) but useful as defense-in-depth |
| `retracted_claim_with_supported_verdict` | **Primary V2 critic trigger on ideal-vision 20-sample run.** | Most consistently activated check; by-design conservative |
| `contradictory_claim_with_supported_verdict` | Companion to retraction check. | Same design philosophy |
| `low_agreement_with_definitive_verdict` | Model disagreement safety check. | Rarely triggers in single-model degraded mode; intended for multi-model production |
| `all_models_failed_without_risk_flags` | Pipeline silence detection. | Defense-in-depth — pipeline assembly should already add manual_review_required for this case |
| `high_severity_with_low_confidence` | Severity-confidence mismatch. | Independent signal cross-check; no overlap with other critics |

---

## 7. Recommendations

1. **Add fraud/conversation detector health check to V2Critic**: Check whether `FraudReport` and `ConversationReport` contain any non-default values, flagging if all detectors returned empty results. Currently, a silent failure in fraud or conversation is invisible to both critics.

2. **V1 submission critic should check `evidence_standard_met + supported`**: This is a blind spot. A `supported` claim with `evidence_standard_met=false` passes through the submission critic uncorrected.

3. **Add `has_sarcasm` to V2Critic conversation checks**: Sarcasm is currently detected but never escalated. While it's low-severity, combining it with high fraud scores could indicate manipulation attempts.

4. **V2Critic should check for `high_fraud + high_severity`** even when confidence is adequate — fraud + severity is a more dangerous combination than severity + low confidence.

5. **Consider making V2Critic issues influence confidence calibration**: Currently the critic only adds `manual_review_required` to risk_flags. If the critic could feed back into confidence (e.g., `confidence -= 0.1` for each REVIEW_REQUIRED issue), the routing would better reflect cross-layer inconsistency.
