# Dual Risk Architecture

## RiskMerger — Mode-Aware Risk Flag Classification

The `RiskMerger` class (`code/v2/risk_merger.py`) is the final piece that enables V2 to simultaneously achieve **maximum competition accuracy** and **preserve production intelligence**.

### Problem

V2's pipeline produces more risk flag types than V1:
- **13 V1-compatible flag types** (from V1RiskAdapter)
- **17 V2-only enhancement flags** (conversation analysis, fraud detection, internal passthrough)

For competition scoring, these enhancement flags cause exact-match failures because the ground-truth labels only contain V1 flags.

### Solution

RiskMerger classifies every flag into two categories and supports three output modes:

```
                         ┌─────────────────────┐
                         │    All Risk Flags    │
                         │  (from all sources)  │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         │    RiskMerger        │
                         │    classify()        │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────┴───────┐ ┌────┴────┐ ┌────────┴────────┐
            │  competition  │ │enhanced │ │    hybrid      │
            │   flags only  │ │all flags│ │both groups     │
            └───────────────┘ └─────────┘ └─────────────────┘
```

### Flag Classification

| Category | Flags | Source |
|----------|-------|--------|
| **V1-compatible** (13 types) | blurry_image, cropped_or_obstructed, low_light_or_glare, wrong_angle, wrong_object, wrong_object_part, damage_not_visible, claim_mismatch, possible_manipulation, non_original_image, text_instruction_present, user_history_risk, manual_review_required | V1 RiskAnalyzer (via V1RiskAdapter) |
| **Conversation enhancement** (4) | uncertain_claim, conversation_conflict, possible_sarcasm, claim_retraction | V2 ConversationAnalyzer |
| **V1 internal passthrough** (2) | evidence_insufficient, low_confidence | V1RuleAdapter (RiskAnalyzer filters these) |
| **Fraud detection** (11) | duplicate_image, screenshot_detected, photo_of_photo, edited_image, timestamp_mismatch, camera_mismatch, no_exif, exif_read_error, frequent_claims, image_reuse, severity_escalation | V2 FraudDetectors |

### Mode Definitions

| Mode | Output | Use Case |
|------|--------|----------|
| `competition` | V1-compatible flags only | Leaderboard submission; exact-match scoring |
| `enhanced` | All flags | Production deployment; full intelligence |
| `hybrid` | `{competition_flags, enhancement_flags, all_flags}` | Research, debugging, A/B comparison |

### API

```python
from code.v2.risk_merger import RiskMerger

# Classify existing flags
merged = RiskMerger("hybrid")
result = merged.merge(["uncertain_claim", "blurry_image", "duplicate_image"])
# → {"competition_flags": ["blurry_image"],
#     "enhancement_flags": ["duplicate_image", "uncertain_claim"],
#     "all_flags": ["blurry_image", "duplicate_image", "uncertain_claim"]}

# Competition mode: V1-compatible only
competition = RiskMerger("competition").merge(result["all_flags"])
# → ["blurry_image"]

# Enhanced mode: all flags
enhanced = RiskMerger("enhanced").merge(result["all_flags"])
# → ["blurry_image", "duplicate_image", "uncertain_claim"]
```

### Integration

RiskMerger is **not wired into `pipeline.py`** — it's a pure utility class used by the evaluation harness (`validate_v1_vs_v2.py`). This preserves the existing V2 architecture while adding mode-aware output selection.

To integrate into production, a user would call `RiskMerger.merge()` at the pipeline output boundary based on the deployment mode.
