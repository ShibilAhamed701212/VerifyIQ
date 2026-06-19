# Multi-Modal Evidence Review Architecture

## Goal

This solution separates visual fact extraction from claim adjudication. The model observes images; deterministic Python modules make the final decision. This reduces hallucination risk, improves explainability, and makes the system easier to defend in an interview.

## Target Flow

```text
Images + claim
  -> Vision Analyzer
  -> Claim Parser
  -> Evidence Checker
  -> Rule Engine
  -> Risk Analyzer
  -> Decision Agent
  -> Output Validator
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

It uses keyword matching, normalization, and phrase checks. This keeps the claim target explicit before visual findings are compared.

### Evidence Checker

File: `code/evidence_checker.py`

The evidence requirements file contains natural-language descriptions, not numeric counts. The evidence checker therefore evaluates semantic criteria:

- claimed part visible
- image quality sufficient
- angle sufficient
- relevant view not cropped or obstructed

It does not rely on image count.

### Rule Engine

File: `code/rule_engine.py`

The rule engine applies deterministic decision rules:

```text
IF damage_visible == false:
    contradicted
ELIF visible_object_part != claimed_object_part:
    contradicted
ELIF visible_damage_type != claimed_damage_type:
    not_enough_information
ELIF confidence < 0.50:
    not_enough_information
ELIF evidence_standard_met == false:
    not_enough_information
ELSE:
    supported
```

This makes every decision path auditable.

### Risk Analyzer

File: `code/risk_analyzer.py`

Risk flags are derived from image quality, rule mismatches, confidence, evidence sufficiency, conflicting images, and user history.

Manual review is required when:

- confidence is below 0.50
- multiple risk flags exist
- images conflict
- user history risk exists

### Severity Engine

File: `code/severity_engine.py`

Severity is mapped deterministically from the visible damage type:

- high: `glass_shatter`, `water_damage`
- medium: `crack`, `broken_part`, `missing_part`, `crushed_packaging`
- low: `dent`, `scratch`, `stain`, `torn_packaging`

Severity is boosted one level when the claim text contains terms such as `severe`, `major`, `extensive`, `large`, `heavy`, `deep`, `significant`, or `smashed`.

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

Evaluation reports:

- accuracy
- precision
- recall
- F1 score
- supported accuracy
- contradicted accuracy
- not-enough-information accuracy
- risk flag accuracy

Wrong predictions are grouped in `code/evaluation/error_report.md` by likely cause.
