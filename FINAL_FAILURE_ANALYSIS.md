# Failure Analysis: 13 V2 Mismatches on Sample Claims

> **Note:** VerifyIQ is an AI agent framework that performs reasoning using observations from external vision providers (VLMs). Results in this document assume an operational vision provider. VerifyIQ does not contain a proprietary VLM — users configure their own (Gemini, OpenRouter, local models, etc.).

## Overview

V2 mismatches 13 of 20 sample claims when compared against human-verified ground truth. Every mismatch is confined to the `risk_flags` field — all structural fields (`claim_status`, `issue_type`, `object_part`, `severity`, `evidence_standard_met`, `valid_image`) remain correct.

This document provides a claim-by-claim root cause analysis.

---

## Classification Legend

| Root Cause | Code | Description |
|------------|------|-------------|
| Risk analyzer gap | RAG | V1 RiskAnalyzer module not adapted to V2 |
| Conversation enhancement | CE | V2 ConversationAnalyzer detects signal not in ground truth |
| Dual gap | DG | Both missing V1 flags and extra V2 flags present |

| Error Type | Description |
|------------|-------------|
| Regression | V2 loses a signal V1 had (architectural gap) |
| Enhancement | V2 adds a signal that is valid but not in original ground truth |
| No fault | Flag difference is neutral or inconclusive |

---

## Failure 1: user_003

**Expected output:**
```json
{
  "claim_status": "supported",
  "risk_flags": ["blurry_image"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "supported",
  "risk_flags": []
}
```

**Missing flags:** `blurry_image`
**Extra flags:** none

**Root cause:** V1 RiskAnalyzer detects blur via image validation pipeline. V2 has no `RiskAnalyzer` adapter and no equivalent image-quality assessment. The claim image is genuinely blurry, and this is a real risk signal the system should surface.

**Classification:** RAG — Risk analyzer gap
**Error type:** Regression
**Recommendation:** Port image blur detection into V2's vision pipeline or add a post-processing step.

---

## Failure 2: user_004

**Expected output:**
```json
{
  "claim_status": "supported",
  "risk_flags": []
}
```

**Actual V2 output:**
```json
{
  "claim_status": "supported",
  "risk_flags": ["uncertain_claim"]
}
```

**Missing flags:** none
**Extra flags:** `uncertain_claim`

**Root cause:** V2's `ConversationAnalyzer` detects hedging language. User_004's claim text is: *"I think the windshield is cracked"* — a clear uncertainty marker. V1's ground truth did not include uncertainty as a risk flag, and V1's RiskAnalyzer did not flag it.

**Classification:** CE — Conversation enhancement
**Error type:** Enhancement (valid extra signal)
**Recommendation:** This flag is factually correct. Consider adding `uncertain_claim` to the ground truth standard, or suppress it if the standard requires minimal flag sets.

---

## Failure 3: user_005

**Expected output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["manual_review_required", "user_history_risk"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": []
}
```

**Missing flags:** `manual_review_required`, `user_history_risk`
**Extra flags:** none

**Root cause:** V1's `RiskAnalyzer` checks `user_history` for user_005, who has past rejected claims. This triggers both `user_history_risk` and (via escalation) `manual_review_required`. V2 has no user-history access or equivalent pipeline.

**Classification:** RAG — Risk analyzer gap
**Error type:** Regression
**Recommendation:** Implement user history lookup in V2, or design an API for the conversation layer to query historical user state.

---

## Failure 4: user_006

**Expected output:**
```json
{
  "claim_status": "not_enough_information",
  "risk_flags": ["damage_not_visible", "wrong_angle"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "not_enough_information",
  "risk_flags": ["evidence_insufficient", "uncertain_claim"]
}
```

**Missing flags:** `damage_not_visible`, `wrong_angle`
**Extra flags:** `evidence_insufficient`, `uncertain_claim`

**Root cause:** Dual gap. V1's RiskAnalyzer inspects the image and determines damage is not visible and the image angle is wrong — both image-quality signals. V2 instead analyzes conversation and evidence sufficiency, producing `evidence_insufficient` (from rule engine) and `uncertain_claim` (from conversation analyzer). The two systems flag orthogonal aspects of the same claim.

**Classification:** DG — Dual gap (RAG + CE)
**Error type:** Regression + Enhancement
**Recommendation:** Addressing the image-quality gap (missing flags) is architectural. The extra flags are valid but partial substitutes.

---

## Failure 5: user_008

**Expected output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["manual_review_required", "user_history_risk"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["uncertain_claim"]
}
```

**Missing flags:** `manual_review_required`, `user_history_risk`
**Extra flags:** `uncertain_claim`

**Root cause:** Same pattern as user_005 missing flags, combined with ConversationAnalyzer triggering on user_008's uncertainty markers. User_008 has past rejected claims (V1 signal).

**Classification:** DG — Dual gap (RAG + CE)
**Error type:** Regression + Enhancement
**Recommendation:** User history lookup is the blocking gap.

---

## Failure 6: user_011

**Expected output:**
```json
{
  "claim_status": "supported",
  "risk_flags": []
}
```

**Actual V2 output:**
```json
{
  "claim_status": "supported",
  "risk_flags": ["uncertain_claim"]
}
```

**Missing flags:** none
**Extra flags:** `uncertain_claim`

**Root cause:** User_011's claim contains uncertainty keywords ("maybe", "I'm not sure"). V2 ConversationAnalyzer flags this. V1 did not have uncertainty detection.

**Classification:** CE — Conversation enhancement
**Error type:** Enhancement
**Recommendation:** Accept as a genuine improvement. The flag is valid and useful for downstream routing.

---

## Failure 7: user_012

**Expected output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["wrong_object", "wrong_object_part"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["object_part_mismatch"]
}
```

**Missing flags:** `wrong_object`, `wrong_object_part`
**Extra flags:** `object_part_mismatch`

**Root cause:** Dual gap. V1's RiskAnalyzer determines the user claims about a different object type and a different part than what is shown. V2's ConversationAnalyzer detects a part-level mismatch but doesn't have the domain rules to determine "wrong object" (entirely wrong product type). The V2 `object_part_mismatch` is a partial, weaker signal.

**Classification:** DG — Dual gap (RAG + CE)
**Error type:** Regression + Enhancement
**Recommendation:** The `object_part_mismatch` flag is directionally correct but less specific than V1's two-flag approach. Requires domain-specific object classification rules to match V1.

---

## Failure 8: user_018

**Expected output:**
```json
{
  "claim_status": "supported",
  "risk_flags": []
}
```

**Actual V2 output:**
```json
{
  "claim_status": "supported",
  "risk_flags": ["uncertain_claim"]
}
```

**Missing flags:** none
**Extra flags:** `uncertain_claim`

**Root cause:** User_018 uses hedging language. ConversationAnalyzer triggers.

**Classification:** CE — Conversation enhancement
**Error type:** Enhancement
**Recommendation:** Same as user_011. Valid signal.

---

## Failure 9: user_020

**Expected output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["manual_review_required", "user_history_risk"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": []
}
```

**Missing flags:** `manual_review_required`, `user_history_risk`
**Extra flags:** none

**Root cause:** V1 RiskAnalyzer flags user_020's history. V2 has no user history access.

**Classification:** RAG — Risk analyzer gap
**Error type:** Regression
**Recommendation:** Implement user history API or port RiskAnalyzer history checks.

---

## Failure 10: user_031

**Expected output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["manual_review_required", "user_history_risk", "wrong_object", "wrong_object_part"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["object_part_mismatch", "uncertain_claim"]
}
```

**Missing flags:** `manual_review_required`, `user_history_risk`, `wrong_object`, `wrong_object_part`
**Extra flags:** `object_part_mismatch`, `uncertain_claim`

**Root cause:** The most severe mismatch. Four missing flags from RiskAnalyzer gap, plus two conversation-derived extra flags. User_031 has both user history risk and a misidentified object. V2 detects only the conversation-level part mismatch and uncertainty, missing the domain-level wrong-object determination and history-based escalation.

**Classification:** DG — Dual gap (RAG + CE)
**Error type:** Regression + Enhancement
**Recommendation:** This claim demonstrates the full scope of the V2 gap. Requires both user-history integration and domain-specific object classification.

---

## Failure 11: user_032

**Expected output:**
```json
{
  "claim_status": "supported",
  "risk_flags": ["manual_review_required"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "supported",
  "risk_flags": []
}
```

**Missing flags:** `manual_review_required`
**Extra flags:** none

**Root cause:** V1 RiskAnalyzer flags this claim for manual review (specific risk threshold met). V2 has no risk-threshold scoring. User_032's claim text and image are otherwise clean.

**Classification:** RAG — Risk analyzer gap
**Error type:** Regression
**Recommendation:** Risk scoring threshold logic must be ported to V2.

---

## Failure 12: user_033

**Expected output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["manual_review_required", "user_history_risk"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["uncertain_claim"]
}
```

**Missing flags:** `manual_review_required`, `user_history_risk`
**Extra flags:** `uncertain_claim`

**Root cause:** Pattern identical to user_008. User history risk not detected. Conversation uncertainty detected.

**Classification:** DG — Dual gap (RAG + CE)
**Error type:** Regression + Enhancement
**Recommendation:** Same as user_008.

---

## Failure 13: user_034

**Expected output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["manual_review_required", "text_instruction_present", "user_history_risk", "wrong_object", "wrong_object_part"]
}
```

**Actual V2 output:**
```json
{
  "claim_status": "contradicted",
  "risk_flags": ["object_part_mismatch"]
}
```

**Missing flags:** `manual_review_required`, `text_instruction_present`, `user_history_risk`, `wrong_object`, `wrong_object_part`
**Extra flags:** `object_part_mismatch`

**Root cause:** Highest missing-flag count (5). V1 RiskAnalyzer determines the user submitted text instructions instead of evidence (`text_instruction_present`), has past rejected claims, and describes the wrong object and part. V2 detects only the conversation-level part mismatch. The `text_instruction_present` flag is a particularly notable gap — it represents a V1 business rule that has no analog in V2.

**Classification:** DG — Dual gap (RAG + CE)
**Error type:** Regression + Enhancement
**Recommendation:** The `text_instruction_present` flag is a business logic rule that could be ported independently. The remaining gaps (user history, wrong object/part) require architectural changes.

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total mismatches | 13 |
| Pure RiskAnalyzer gap (RAG only) | 5 (user_003, 005, 020, 032) — plus user_034 is primarily RAG |
| Pure Conversation enhancement (CE only) | 3 (user_004, 011, 018) |
| Dual gap (RAG + CE) | 5 (user_006, 008, 012, 031, 033) |
| Mismatches with missing flags only | 4 (user_003, 005, 020, 032) |
| Mismatches with extra flags only | 3 (user_004, 011, 018) |
| Mismatches with both missing and extra | 6 (user_006, 008, 012, 031, 033, 034) |

## Root Cause Distribution

| Root Cause | Claims | % of failures |
|------------|--------|--------------|
| Missing RiskAnalyzer (RAG) | 10 of 13 | 77% |
| Conversation enhancement (CE) | 8 of 13 | 62% |
| Both RAG and CE present | 5 of 13 | 38% |

## Recommendation Summary

1. **Immediate (portable):** Port `blurry_image` detection to vision pipeline. Port `text_instruction_present` business rule. Either adopt or suppress `uncertain_claim` as a standard flag.
2. **Medium-term (design change):** Implement user-history query API so V2 can access past claim data. Add domain-specific object classification rules (`wrong_object`, `wrong_object_part`, `object_part_mismatch`).
3. **Long-term (architectural):** Decide whether to reintroduce a V1-compatible RiskAnalyzer module or evolve V2's ConversationAnalyzer to cover the full flag ontology. The current 9-flag gap between V1 (20+ flags) and V2 (~8 flags) is inherent to the architecture design.
