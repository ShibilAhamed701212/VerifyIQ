# RISK GAP REPORT — V1 vs V2 Risk Flag Differences

## Overview

V2 has 13 mismatches vs V1 on sample claims. **All 13 are risk_flags only.** Core fields (claim_status, issue_type, object_part, severity, evidence_standard_met, valid_image) are 20/20 identical.

## Per-Claim Risk Flag Analysis

| Claim | Expected (V1) | V2 Actual | Missing | Extra | Gap Type |
|-------|---------------|-----------|---------|-------|----------|
| user_003 | blurry_image | (none) | blurry_image | — | RiskAnalyzer gap |
| user_004 | (none) | uncertain_claim | — | uncertain_claim | Enhancement |
| user_005 | manual_review_required; user_history_risk | (none) | manual_review_required; user_history_risk | — | RiskAnalyzer gap |
| user_006 | damage_not_visible; wrong_angle | evidence_insufficient; uncertain_claim | damage_not_visible; wrong_angle | evidence_insufficient; uncertain_claim | Mixed |
| user_008 | manual_review_required; user_history_risk | uncertain_claim | manual_review_required; user_history_risk | uncertain_claim | Mixed |
| user_011 | (none) | uncertain_claim | — | uncertain_claim | Enhancement |
| user_012 | wrong_object; wrong_object_part | object_part_mismatch | wrong_object; wrong_object_part | object_part_mismatch | RiskAnalyzer gap + rename |
| user_018 | (none) | uncertain_claim | — | uncertain_claim | Enhancement |
| user_020 | manual_review_required; user_history_risk | (none) | manual_review_required; user_history_risk | — | RiskAnalyzer gap |
| user_031 | manual_review_required; user_history_risk; wrong_object; wrong_object_part | object_part_mismatch; uncertain_claim | manual_review_required; user_history_risk; wrong_object; wrong_object_part | object_part_mismatch; uncertain_claim | RiskAnalyzer gap + rename |
| user_032 | manual_review_required | (none) | manual_review_required | — | RiskAnalyzer gap |
| user_033 | manual_review_required; user_history_risk | uncertain_claim | manual_review_required; user_history_risk | uncertain_claim | Mixed |
| user_034 | manual_review_required; text_instruction_present; user_history_risk; wrong_object; wrong_object_part | object_part_mismatch | manual_review_required; text_instruction_present; user_history_risk; wrong_object; wrong_object_part | object_part_mismatch | RiskAnalyzer gap + rename |

## Summary Statistics

| Category | Count | Claims |
|----------|-------|--------|
| Missing RiskAnalyzer flags only | 6 | user_003, user_005, user_020, user_032, user_012 (with rename), user_034 (with rename) |
| Extra V2 conversation flags only (enhancements) | 5 | user_004, user_011, user_018, user_015, user_030 |
| Mixed (missing + extra) | 2 | user_006, user_008, user_031, user_033 |

Note: The 5 "enhancement only" claims (user_004, user_011, user_018, plus user_015 and user_030 which match in the relaxed check) have V2 correctly detecting uncertainty in the claim text via ConversationAnalyzer. These are **not errors** — they are valid extra signals that the ground-truth labels don't capture.

## Missing Flag Categories

| Missing Flag | Claims | Source in V1 |
|-------------|--------|-------------|
| manual_review_required | 8 (user_005, 008, 020, 031, 032, 033, 034) | RiskAnalyzer: low confidence, evidence_insufficient, user_history, conflicting_images |
| user_history_risk | 6 (user_005, 008, 020, 031, 033, 034) | RiskAnalyzer: user_history lookup |
| wrong_object_part | 3 (user_012, 031, 034) | RiskAnalyzer: from rule_result mismatch_type |
| wrong_object | 3 (user_012, 031, 034) | RiskAnalyzer: notes "wrong object" + CV object_validator |
| blurry_image | 1 (user_003) | RiskAnalyzer: image_assessments is_clear + CV blur_detector |
| damage_not_visible | 1 (user_006) | RuleEngine: via V1RuleAdapter (should be produced!) |
| wrong_angle | 1 (user_006) | RiskAnalyzer: image_assessments angle_sufficient |
| text_instruction_present | 1 (user_034) | RiskAnalyzer: notes "text"/"label" + CV text_detector |

## Extra V2 Flag Categories

| Extra Flag | Claims | Source in V2 |
|-----------|--------|-------------|
| uncertain_claim | 5 (user_004, 008, 011, 018, 033) | ConversationAnalyzer: uncertainty detection |
| object_part_mismatch | 3 (user_012, 031, 034) | RuleEngine (via V1RuleAdapter): mismatch_type=object_part_mismatch |
| evidence_insufficient | 1 (user_006) | RuleEngine (via V1RuleAdapter): evidence not met |

## Key Finding: object_part_mismatch is a V1→V2 Rename

V1 uses `wrong_object_part`. V2 uses `object_part_mismatch`. These are the **same semantic flag** — both mean the claimed object part doesn't match the visible damage location. The name difference alone causes 3 mismatches (user_012, 031, 034).

Fix: Add `object_part_mismatch` → `wrong_object_part` as a V2→V1 alias in the risk flag normalization.

## Key Finding: V2 already produces damage_not_visible via V1RuleAdapter

User_006 expects `damage_not_visible`. The V2 pipeline runs `V1RuleAdapter.evaluate()` which calls `RuleEngine.evaluate()`. When damage is not visible, RuleEngine returns `mismatch_type="damage_not_visible"` and `risk_flags=["damage_not_visible"]`. So V2 **should** produce this flag.

Investigation needed: Is the V1RuleAdapter being called with the right `damage_visible` parameter?
