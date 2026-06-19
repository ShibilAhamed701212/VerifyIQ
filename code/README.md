# Multi-Modal Evidence Review System

## Overview

This system processes damage claims across three object types: **cars**, **laptops**, and **packages**. It analyses submitted images using a Vision LLM (GPT-4o or Claude 3.5 Sonnet), cross-references with the user's claim text and history, and outputs a deterministic decision for each claim.

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key**:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```
   (For Claude, set `ANTHROPIC_API_KEY` instead.)

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
    vision_analyzer.py  # Vision LLM client
    evidence_requirements.py  # Evidence standard checker
    risk_analyzer.py    # Risk flags & severity
  evaluation/
    evaluate.py         # Evaluation runner
```

## Key Features

- **Deterministic**: Temperature = 0, structured JSON output
- **Crash-proof**: Each claim processed independently; failures produce fallback rows
- **Optimized**: Retry logic, configurable limits, minimal API calls
- **Grounded**: All decisions based on visual evidence + provided data
