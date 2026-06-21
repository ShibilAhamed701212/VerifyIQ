# Risk Mode Comparison

> **Note:** VerifyIQ is an AI agent framework that performs reasoning using observations from external vision providers (VLMs). Results in this document assume an operational vision provider. VerifyIQ does not contain a proprietary VLM — users configure their own (Gemini, OpenRouter, local models, etc.).

## Per-Mode Accuracy on 20 Sample Claims

| Mode | Exact Match | Relaxed Match | Δ from V1 |
|------|-------------|---------------|-----------|
| V1 baseline | 20/20 (100%) | 20/20 (100%) | — |
| V2 raw (no adapter) | 7/20 (35%) | 10/20 (50%) | −13 exact |
| V2 competition | 20/20 (100%) | 20/20 (100%) | 0 |
| V2 enhanced | 13/20 (65%) | 20/20 (100%) | −7 exact |
| V2 hybrid (competition group) | 20/20 (100%) | 20/20 (100%) | 0 |

## Per-Claim Comparison Table

| Claim | V1 | V2 Raw | Competition | Enhanced | Expected | Enhancement Flags |
|-------|----|--------|-------------|----------|----------|------------------|
| user_001 | ✅ | ✅ | ✅ | ✅ | supported | — |
| user_002 | ✅ | ✅ | ✅ | ✅ | contradicted | — |
| user_003 | ✅ | ❌ | ✅ | ❌ | supported | — |
| user_004 | ✅ | ❌ | ✅ | ❌ | supported | uncertain_claim |
| user_005 | ✅ | ❌ | ✅ | ✅ | contradicted | — |
| user_006 | ✅ | ❌ | ✅ | ❌ | not_enough_information | evidence_insufficient; uncertain_claim |
| user_007 | ✅ | ✅ | ✅ | ✅ | contradicted | — |
| user_008 | ✅ | ❌ | ✅ | ❌ | contradicted | uncertain_claim |
| user_009 | ✅ | ✅ | ✅ | ✅ | supported | — |
| user_010 | ✅ | ✅ | ✅ | ✅ | supported | — |
| user_011 | ✅ | ❌ | ✅ | ❌ | supported | uncertain_claim |
| user_012 | ✅ | ❌ | ✅ | ✅ | contradicted | — |
| user_015 | ✅ | ✅ | ✅ | ✅ | supported | — |
| user_018 | ✅ | ❌ | ✅ | ❌ | supported | uncertain_claim |
| user_020 | ✅ | ❌ | ✅ | ✅ | contradicted | — |
| user_030 | ✅ | ✅ | ✅ | ✅ | supported | — |
| user_031 | ✅ | ❌ | ✅ | ❌ | contradicted | uncertain_claim |
| user_032 | ✅ | ❌ | ✅ | ✅ | supported | — |
| user_033 | ✅ | ❌ | ✅ | ❌ | contradicted | uncertain_claim |
| user_034 | ✅ | ❌ | ✅ | ✅ | contradicted | — |

**Key:** Competition mode matches V1 on ALL 20 claims. Enhanced mode fails 7 claims due to enhancement-only flags (`uncertain_claim` × 7, `evidence_insufficient` × 1) that are valid signals not in the ground truth.

## Why Competition Mode Achieves 100%

### Enhancement flags stripped by RiskMerger

| Enhancement Flag | Claims Where Present | Why Stripped |
|------------------|----------------------|--------------|
| `uncertain_claim` | user_004, 006, 008, 011, 018, 031, 033 | V2-only conversation analysis; V1 has no equivalent |
| `evidence_insufficient` | user_006 | V1 internal flag (RiskAnalyzer filters it); V1RuleAdapter passes it through |

### All other risk flags match perfectly

| V1-Compatible Flag | Claims With Flag | Competition Mode Produces It? |
|--------------------|-----------------|-------------------------------|
| claim_mismatch | user_002, 005, 007, 008, 020, 033 | ✅ All 6 |
| damage_not_visible | user_006 | ✅ |
| wrong_angle | user_006 | ✅ |
| blurry_image | user_003 | ✅ |
| wrong_object | user_012, 031, 034 | ✅ All 3 |
| wrong_object_part | user_012, 031, 034 | ✅ All 3 |
| manual_review_required | user_005, 008, 020, 031, 032, 033, 034 | ✅ All 7 |
| user_history_risk | user_005, 008, 020, 031, 033, 034 | ✅ All 6 |
| text_instruction_present | user_034 | ✅ |

## Score Summary by Mode and Claim Object

| Object | Claims | V1 | V2 Raw | Competition | Enhanced |
|--------|--------|----|--------|-------------|----------|
| **car** | 8 | 8/8 (100%) | 3/8 (38%) | 8/8 (100%) | 5/8 (63%) |
| **laptop** | 6 | 6/6 (100%) | 2/6 (33%) | 6/6 (100%) | 4/6 (67%) |
| **package** | 6 | 6/6 (100%) | 2/6 (33%) | 6/6 (100%) | 4/6 (67%) |

## Field-Level Accuracy (All Modes)

All modes achieve 100% on all non-risk fields:
- claim_status: 20/20
- issue_type: 20/20
- object_part: 20/20
- severity: 20/20
- evidence_standard_met: 20/20
- valid_image: 20/20

The only differences between modes are in `risk_flags`.
