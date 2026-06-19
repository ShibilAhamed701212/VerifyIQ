# Multi-Modal Evidence Review System

## Overview

This system processes damage claims across three object types: **cars**, **laptops**, and **packages**. It analyses submitted images using Gemini Vision, cross-references the findings with the user's claim text and history, and outputs a deterministic decision for each claim.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key**:
   ```bash
   export GEMINI_API_KEY="your-api-key"
   ```

3. **Place dataset**: Ensure the `dataset/` folder (with `claims.csv`, `user_history.csv`, `evidence_requirements.csv`, and `images/`) is in the project root.

## Usage

### Run on Full Test Set
```bash
python code/main.py
```
Reads `dataset/claims.csv` and writes `output.csv`.

### Run Evaluation on Sample Set
```bash
python code/evaluation/evaluate.py
```
Runs on `dataset/sample_claims.csv`, compares against expected outputs, and generates `evaluation/evaluation_report.md`.

## Configuration

Edit `code/config.py` to adjust:
- Vision model (`vision_model`)
- API endpoints
- Processing limits
- Risk flag thresholds

## Architecture

```
main.py                 # Orchestrator
  claim_processor.py    # Core claim pipeline
    claim_parser.py     # Deterministic claim text parser
    vision_analyzer.py  # Gemini vision client
    evidence_checker.py # Semantic evidence standard checker
    rule_engine.py      # Deterministic claim-vs-image verification rules
    risk_analyzer.py    # Risk flags & severity
    severity_engine.py  # Deterministic severity mapping
    decision_agent.py   # Final output row builder
    output_validator.py # Schema and enum enforcement
  evaluation/
    evaluate.py         # Evaluation runner
    error_analysis.py   # Grouped error report generator
```

## Updated Decision Flow

```
Vision Analysis
  -> Claim Parser
  -> Semantic Evidence Checker
  -> Rule Engine
  -> Risk Analyzer
  -> Decision Agent
  -> Output Validation
  -> output.csv
```

Only `decision_agent.py` builds the final output row. The rule engine compares claimed issue and part against visible issue and part, applies confidence thresholds, and emits an explainable intermediate decision.

## Key Features

- **Deterministic**: Temperature = 0, structured JSON output
- **Crash-proof**: Each claim processed independently; failures produce fallback rows
- **Optimized**: Retry logic, configurable limits, minimal API calls
- **Grounded**: All decisions based on visual evidence + provided data
