# VerifyIQ Examples

Quick-start examples for the [VerifyIQ](https://github.com/verifyiq/verifyiq) multimodal claim verification platform.

## Prerequisites

```bash
pip install verifyiq
```

Or run from the repo root:

```bash
cd hackerrank-orchestrate-june26
```

## Examples

| File | What it shows |
|------|--------------|
| `01_quickstart.py` | Parse a claim text and evaluate it with the V1 RuleEngine using ideal vision input. |
| `02_v1_pipeline.py` | Full V1 pipeline: load Config, run ClaimParser, EvidenceChecker, RuleEngine, SeverityEngine, and DecisionAgent on a row from `sample_claims.csv`. |
| `03_v2_pipeline.py` | Initialize V2Pipeline and process a claim. Degrades gracefully — no API key required. |
| `04_security.py` | Demonstrate InputSanitizer: prompt injection detection, path traversal blocking, CSV injection prevention, and filename sanitization. |

## Running

All examples run standalone:

```bash
python examples/01_quickstart.py
python examples/02_v1_pipeline.py
python examples/03_v2_pipeline.py
python examples/04_security.py
```

Run from any directory — they add the repo to `sys.path` automatically.

## API Key Requirements

| Example | API key needed? |
|---------|----------------|
| `01_quickstart` | No — uses ideal vision input |
| `02_v1_pipeline` | No — uses expected values from sample CSV as vision input |
| `03_v2_pipeline` | No — degrades to empty observation when providers are unavailable |
| `04_security` | No — pure local logic |

To run V2 with real vision models, set `GEMINI_API_KEY` or `OPENROUTER_API_KEY` in your environment.
