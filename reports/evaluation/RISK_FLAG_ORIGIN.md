# RISK FLAG ORIGIN — V1 Risk Flag Source Classification

## All V1 Risk Flags and Their Origins

| Flag | Module | Logic | Status |
|------|--------|-------|--------|
| blurry_image | **RiskAnalyzer** | `is_clear=False` in image_assessments + CV BlurDetector override | V2 missing |
| cropped_or_obstructed | **RiskAnalyzer** | `is_cropped=True` in image_assessments + CV CropDetector override | V2 missing |
| low_light_or_glare | **RiskAnalyzer** | `lighting_adequate=False` in image_assessments | V2 missing |
| wrong_angle | **RiskAnalyzer** | `angle_sufficient=False` in image_assessments | V2 missing |
| damage_not_visible | **RuleEngine** → RiskAnalyzer | RuleEngine produces mismatch_type="damage_not_visible" + risk_flags=["damage_not_visible"]; RiskAnalyzer adds it from _user_claimed_damage() check | V2 via V1RuleAdapter |
| claim_mismatch | **RuleEngine** → RiskAnalyzer | RuleEngine mismatch_type="claim_mismatch" + RiskAnalyzer from conflicting_images | V2 via V1RuleAdapter |
| wrong_object_part | **RuleEngine** → RiskAnalyzer | RuleEngine mismatch_type="object_part_mismatch" → RiskAnalyzer renames to "wrong_object_part" | V2 via V1RuleAdapter (as object_part_mismatch) |
| wrong_object | **RiskAnalyzer** | notes "wrong object" + CV ObjectValidator | V2 missing |
| manual_review_required | **RiskAnalyzer** | Multiple paths: low confidence, evidence_insufficient, conflicting_images, user_history, CV wrong_object | V2 missing |
| user_history_risk | **RiskAnalyzer** | history_flags, last_90_days > 3, rejected > 2 | V2 missing |
| possible_manipulation | **RiskAnalyzer** | notes: "photoshopped", "edited", "manipulated", "altered" | V2 missing |
| non_original_image | **RiskAnalyzer** | notes: "screenshot", "stock photo", "stock image", "template", "non-original" | V2 missing |
| text_instruction_present | **RiskAnalyzer** | notes "text"/"label" + CV TextDetector | V2 missing |

## Classification by Source Type

### Parser Derived
None. The ClaimParser provides damage_type and object_part, but doesn't directly produce risk flags. Its output feeds RuleEngine which produces mismatch flags.

### Evidence Derived
- `evidence_insufficient` (RuleEngine internal → becomes manual_review_required in RiskAnalyzer)

### Rule Derived (RuleEngine)
| Flag | Produced by RuleEngine? | Reaches Output? |
|------|------------------------|-----------------|
| evidence_insufficient | Yes (mismatch_type) | Filtered by RiskAnalyzer → manual_review_required |
| damage_not_visible | Yes (mismatch_type + risk_flags) | Yes (RiskAnalyzer keeps it) |
| claim_mismatch | Yes (mismatch_type + risk_flags) | Yes (RiskAnalyzer keeps it) |
| object_part_mismatch | Yes (mismatch_type + risk_flags) | Renamed by RiskAnalyzer → wrong_object_part |
| low_confidence | Yes (risk_flags) | Filtered by RiskAnalyzer → manual_review_required |

### Risk Analyzer Derived
| Flag | Input Dependencies |
|------|--------------------|
| blurry_image | image_assessments[].is_clear, CV BlurDetector |
| cropped_or_obstructed | image_assessments[].is_cropped, CV CropDetector |
| low_light_or_glare | image_assessments[].lighting_adequate |
| wrong_angle | image_assessments[].angle_sufficient |
| manual_review_required | confidence, evidence_result, conflicting_images, user_history, CV wrong_object |
| user_history_risk | user_history dict |
| possible_manipulation | image_analysis notes |
| non_original_image | image_analysis notes |
| wrong_object | image_analysis notes, CV ObjectValidator |
| text_instruction_present | image_analysis notes, CV TextDetector |

### Severity Derived
None.

## V2 Flag Origins

| V2 Flag | Source | V1 Equivalent |
|---------|--------|---------------|
| uncertain_claim | ConversationAnalyzer | No V1 equivalent (V2 enhancement) |
| possible_sarcasm | ConversationAnalyzer | No V1 equivalent (V2 enhancement) |
| claim_retraction | ConversationAnalyzer | No V1 equivalent (V2 enhancement) |
| conversation_conflict | ConversationAnalyzer | No V1 equivalent (V2 enhancement) |
| object_part_mismatch | RuleEngine (via V1RuleAdapter) | wrong_object_part (V1 rename) |
| evidence_insufficient | RuleEngine (via V1RuleAdapter) | → manual_review_required (V1) |
| damage_not_visible | RuleEngine (via V1RuleAdapter) | damage_not_visible (same) |
| claim_mismatch | RuleEngine (via V1RuleAdapter) | claim_mismatch (same) |
| duplicate_image | ImageFraudDetector | No V1 equivalent (V2 enhancement) |
| screenshot_detected | ImageFraudDetector | No V1 equivalent (V2 enhancement) |
| edited_image | MetadataFraudDetector | No V1 equivalent (V2 enhancement) |
| camera_mismatch | MetadataFraudDetector | No V1 equivalent (V2 enhancement) |
| timestamp_mismatch | MetadataFraudDetector | No V1 equivalent (V2 enhancement) |
| frequent_claims | BehavioralFraudDetector | → user_history_risk (partial) |
| image_reuse | BehavioralFraudDetector | No V1 equivalent (V2 enhancement) |
| severity_escalation | BehavioralFraudDetector | No V1 equivalent (V2 enhancement) |
| manual_review_required | Pipeline (fraud/consensus/critic) | manual_review_required (same) |

## Flag Equivalence Map

| V1 Flag | V2 Equivalent(s) | Normalization Rule |
|---------|------------------|-------------------|
| wrong_object_part | object_part_mismatch | ALIAS: normalize both to "wrong_object_part" |
| claim_mismatch | claim_mismatch | SAME: already identical |
| damage_not_visible | damage_not_visible | SAME: already identical |
| manual_review_required | manual_review_required | SAME: already identical |
| user_history_risk | frequent_claims (partial) | PARTIAL: frequent_claims covers some of user_history_risk |
| blurry_image | (missing) | NEEDED: only from RiskAnalyzer |
| cropped_or_obstructed | (missing) | NEEDED: only from RiskAnalyzer |
| low_light_or_glare | (missing) | NEEDED: only from RiskAnalyzer |
| wrong_angle | (missing) | NEEDED: only from RiskAnalyzer |
| wrong_object | (missing) | NEEDED: only from RiskAnalyzer |
| possible_manipulation | (missing) | NEEDED: only from RiskAnalyzer |
| non_original_image | (missing) | NEEDED: only from RiskAnalyzer |
| text_instruction_present | (missing) | NEEDED: only from RiskAnalyzer |
