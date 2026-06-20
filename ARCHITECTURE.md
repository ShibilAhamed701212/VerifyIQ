# Multi-Modal Evidence Review Architecture

## Goal

This solution separates visual fact extraction from claim adjudication. The model observes images; deterministic Python modules make the final decision. This reduces hallucination risk, improves explainability, and makes the system easier to defend in an interview.

## Target Flow

```text
Images + claim
  -> Vision Analyzer (Gemini — observations only)
  -> Claim Parser (keyword matching)
  -> Evidence Checker (quality + angle + part)
  -> Rule Engine (6-path decision tree)
  -> Risk Analyzer (CV modules + history + rule flags)
  -> Decision Agent (assembles output row)
  -> Output Validator (enum enforcement)
  -> output.csv
```

## Component Responsibilities

### Vision Analyzer

File: `code/vision_analyzer.py`

The vision model extracts observations only:

- whether damage is visible
- visible damage type
- visible object part
- image quality
- supporting image IDs
- per-image assessments
- confidence
- notes

It never returns `claim_status`. Final decisions are intentionally outside the model.

### Claim Parser

File: `code/claim_parser.py`

The parser extracts:

- `claimed_damage_type`
- `claimed_object_part`

It uses keyword matching, normalization, phrase checks, and customer-only message filtering. Priority ordering ensures hinge matches before screen (laptop) and seal before side (package). Negation detection (25-char window) prevents false matches on negated keywords. "not sitting" keyword added for broken_part detection.

### Evidence Checker

File: `code/evidence_checker.py`

The evidence requirements file contains natural-language descriptions, not numeric counts. The evidence checker evaluates semantic criteria:

- image quality sufficient (is_clear + quality in good/adequate)
- angle sufficient
- relevant view not cropped or obstructed

Uses vision-detected part as authoritative when available; falls back to parser's claimed part when vision cannot determine. Non-original images set `valid_image=false` but do not affect `evidence_standard_met`.

### Rule Engine

File: `code/rule_engine.py`

The rule engine applies a 6-path deterministic decision tree, checked in order:

```text
Path 1 — evidence_standard_met == false:          not_enough_information
Path 2 — damage_visible == false:                 contradicted (damage_not_visible)
Path 3 — damage_type conflict                     contradicted (claim_mismatch)
  (claimed≠visible, not compatible, unknown→known is conflict)
Path 4 — object_part conflict                     contradicted (object_part_mismatch)
Path 5 — confidence < 0.50                        not_enough_information (low_confidence)
Path 6 — otherwise                                supported
```

Compatible damage type pairs (no conflict):
- `glass_shatter` ↔ `crack`
- `stain` ↔ `water_damage`

Only Path 2 checks `not damage_visible` — Path 3 does not require damage_visible.
All `claim_mismatch` cases produce `contradicted` status (never `not_enough_information`).
`_damage_conflict` returns True when claimed=unknown, visible=known.

### Risk Analyzer

File: `code/risk_analyzer.py`

Risk flags are derived from image quality, rule mismatches, confidence, evidence sufficiency, conflicting images, user history, vision notes keywords, and deterministic CV modules.

CV modules (lazy-initialized) provide additional signals:
- `blur_detector.py` — Laplacian variance threshold 15
- `crop_detector.py` — aspect ratio + edge density
- `text_detector.py` — Tesseract OCR
- `object_validator.py` — dimension profile matching

CV modules **only add flags, never remove** vision-derived flags.

Manual review is required when:

- confidence is below 0.50
- `user_history_risk` is present
- claim_mismatch + user_history_risk combined
- CV detects wrong object
- history_flags contain `manual_review_required`

Internal runtime flags (`evidence_insufficient`, `low_confidence`, `object_part_mismatch`) are filtered from final output. The `_determine_severity` method was identified as dead code (severity recomputed by DecisionAgent) and removed.

### Severity Engine

File: `code/severity_engine.py`

Severity is mapped deterministically from the visible damage type:

- high: `glass_shatter`, `water_damage`
- medium: `crack`, `broken_part`, `missing_part`, `crushed_packaging`, `dent`, `stain`
- low: `scratch`, `torn_packaging`

Object-specific overrides exist (e.g., laptop dent → low).

Severity is boosted one level when the claim text contains boost terms (`severe`, `major`, `extensive`, `large`, `heavy`, `deep`, `significant`, `smashed`), but only for known damage types (not `unknown`). The `non_original_image` risk flag forces severity to `high`.

### Decision Agent

File: `code/decision_agent.py`

The decision agent is the only component that produces the final output row. It combines parser, vision, evidence, rule, risk, and severity outputs into the required CSV schema.

### Output Validator

File: `code/output_validator.py`

The validator enforces allowed enum values and exact output columns before any row reaches `output.csv`.

## Multi-Image Reasoning

Each image receives its own assessment. The vision analyzer aggregates observations using majority-style evidence:

- clear damage images are preferred
- one blurry image cannot override multiple clear images
- conflicting damage types or object parts trigger manual review

## Hallucination Reduction

The model is constrained to visual observations. It cannot directly approve, reject, or classify claim status. Deterministic code compares those observations against the parsed claim and evidence standard.

## Explainability

Every output row includes a reasoning trace in `claim_status_justification`, covering:

- claimed damage and part
- visible damage and part
- supporting images
- evidence standard result
- confidence
- rule decision
- risk flags

## Evaluation

Two evaluation modes:

1. **Static evaluation** (`code/evaluation/static_evaluate.py`) — Uses expected CSV values as ideal Gemini output to test deterministic pipeline independently of the vision model. Achieves 19/20 (95%) exact match across 7 fields on sample claims.

2. **Full evaluation** (`code/evaluation/evaluate.py`) — Runs against live Gemini.

Evaluation outputs:
- `evaluation_report.md` — summary + per-claim results
- `error_report.md` — grouped remaining failures with root cause analysis

Wrong predictions are grouped by likely cause. Current static accuracy: 95%.
