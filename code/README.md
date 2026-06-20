# Multi-Modal Evidence Review System — VerifyIQ

## Overview

This system processes damage claims across three object types: **cars**, **laptops**, and **packages**. It analyses submitted images using Gemini Vision (or ideal-vision simulation for testing), cross-references findings with the user's claim text and history, and outputs a deterministic decision for each claim. Static evaluation achieves 19/20 (95%) exact match across 7 output fields.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key** (required for live Gemini):
   ```bash
   set GEMINI_API_KEY=your-api-key
   ```

3. **Place dataset**: Ensure the `dataset/` folder (with `claims.csv`, `user_history.csv`, `evidence_requirements.csv`, and `images/`) is in the project root.

## Usage

### Run on Full Test Set
```bash
python code/main.py
```
Reads `dataset/claims.csv` and writes `output.csv`.

### Static Evaluation (no API key needed)
```bash
python code/evaluation/static_evaluate.py
```
Uses expected CSV values as ideal Gemini output. Tests deterministic pipeline independently. Reports 19/20 (95%) accuracy.

### Full Evaluation (requires API key)
```bash
python code/evaluation/evaluate.py
```
Runs against live Gemini on `dataset/sample_claims.csv`, compares against expected outputs, generates `evaluation_report.md`.

### Run Tests
```bash
pytest code/tests/ -v
```
39 tests covering parser, rule engine, risk flags, CV detectors, and utils.

## Configuration

Edit `code/config.py` to adjust:
- Vision model (`vision_model`)
- API key (`GEMINI_API_KEY` env var or `api_key` field)
- Processing limits
- Blur detection threshold (in `code/cv/blur_detector.py`)

## Architecture

```
main.py                    # Orchestrator — reads claims, processes each, writes output.csv
  claim_processor.py       # Core claim pipeline coordinator
    claim_parser.py        # Deterministic claim text parser (keyword matching, negation, customer filter)
    vision_analyzer.py     # Gemini vision client (observations only — no claim_status)
    evidence_checker.py    # Semantic evidence standard checker (quality, angle, part)
    rule_engine.py         # 6-path deterministic decision tree
    risk_analyzer.py       # Risk flags from rules, CV modules, vision notes, user history
    severity_engine.py     # Deterministic severity mapping (base + override + boost + risk overrides)
    decision_agent.py      # Final output row builder (assembles all stages into CSV row)
    output_validator.py    # Schema and enum enforcement (allowed values, type coercion)
  cv/
    blur_detector.py       # Laplacian variance blur detection (threshold=15)
    crop_detector.py       # Aspect ratio + edge density crop detection
    text_detector.py       # Tesseract OCR text detection
    object_validator.py    # Dimension profile matching for object verification
  evaluation/
    evaluate.py            # Full evaluation runner (requires API key)
    static_evaluate.py     # Ideal-vision evaluation (no API key needed — 19/20)
    error_analysis.py      # Grouped error report generator
  tests/                   # 39 unit tests
```

## Decision Flow

```
Claim Text + Images
  -> Claim Parser (extract claimed damage + part)
  -> Gemini Vision (observations only: damage type, part, quality, confidence)
  -> Evidence Checker (is image quality sufficient? angle ok? part visible?)
  -> Rule Engine (6-path decision tree:
      evidence_insufficient → not_enough_information
      damage_not_visible    → contradicted
      type_mismatch         → contradicted
      part_mismatch         → contradicted
      low_confidence        → not_enough_information
      match                 → supported)
  -> Risk Analyzer (aggregate flags from rules + CV + history + vision notes)
  -> Decision Agent (assemble output row with severity + reasoning trace)
  -> Output Validator (enforce enums, normalize booleans)
  -> output.csv
```

## Key Design Decisions

- **VLM = observations only**: Gemini never outputs claim_status or policy decisions — prevents hallucination
- **Deterministic rules are authoritative**: Rule engine path ordering decisive; compatible damage type pairs prevent false contradictions
- **CV modules are add-only**: Add risk flags but never remove vision-derived ones
- **Internal runtime flags filtered**: `evidence_insufficient`, `low_confidence`, `object_part_mismatch` are routing-only, never appear in output
- **user_history passed end-to-end**: risk_analyzer receives user_history dict, extracts `user_history_risk` and `manual_review_required` from history_flags
- **Severity from multiple sources**: Base map + object overrides + boost words + risk flag overrides (non_original_image → high)

## Key Features

- **Deterministic**: Temperature = 0, structured JSON output, no random behavior
- **Crash-proof**: Each claim processed independently; failures produce fallback rows
- **Verified**: 39 tests passing, static evaluation 19/20 (95%)
- **Explainable**: Every output includes reasoning trace showing claim→evidence→decision path
