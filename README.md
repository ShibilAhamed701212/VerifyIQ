# VerifyIQ — AI Agent Framework for Claim Verification

[![Tests](https://github.com/verifyiq/verifyiq/actions/workflows/tests.yml/badge.svg)](https://github.com/verifyiq/verifyiq/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## What Is VerifyIQ?

**VerifyIQ is a production-oriented AI agent framework for multimodal claim verification.** It performs reasoning, risk analysis, fraud detection, and decision-making using observations supplied by external vision providers (VLMs). Users configure their own VLM — Gemini, OpenRouter, local models, or custom providers. **VerifyIQ does not contain a proprietary vision model.**

| What VerifyIQ Is | What VerifyIQ Is Not |
|---|---|
| AI agent framework for claim verification | A proprietary AI model or VLM |
| Pluggable observation provider system | An autonomous insurance AI |
| Explainable decision engine with traceable justifications | A black-box classifier |
| Deterministic rule-based verification | A pure LLM/VLM end-to-end system |

---

## Quick Start

```bash
pip install verifyiq               # Core framework
pip install verifyiq[gemini]       # Gemini provider
export GEMINI_API_KEY="your-key"
verifyiq evaluate                  # Run on sample claims
```

See [docs/deployment](docs/deployment/) for Docker, CI/CD, and packaging guides.

---

## Project Structure

```
verifyiq/              ← pip-installable Python package
  v1/                  ← V1 wrappers (frozen competition system)
  v2/                  ← V2 production pipeline
    pipeline.py        ← 10-layer orchestrator
    models/            ← Data models
    providers/         ← VLM provider ABC + implementations
    security/          ← Input sanitization
    observability/     ← Logging, metrics, tracing
    fraud/             ← Fraud detection
    confidence/        ← Confidence calibration
    consensus/         ← Multi-model consensus
    conversation/      ← Conversational analysis
    review_queue.py    ← Human-in-the-loop review
    persistence.py     ← SQLite storage
    vision_manager.py  ← VLM availability with circuit breaker
docs/                  ← All documentation
  architecture/        ← System architecture docs
  api/                 ← API reference
  security/            ← Security and adversarial testing
  production/          ← Production readiness, health
  evaluation/          ← Evaluation methodology
  deployment/          ← CI/CD, Docker, PyPI guides
  open_source/         ← Governance, community guides
tests/                 ← All tests (135 cases)
  v1/                  ← V1 tests (58)
  v2/                  ← V2 tests (77)
examples/              ← Example scripts
  providers/           ← Provider setup examples
api/                   ← FastAPI standalone service
dashboard/             ← Streamlit monitoring dashboard
reports/               ← Evaluation reports, audits, scorecards
scripts/               ← Deploy and utility scripts
docker/                ← Dockerfiles and compose
research/              ← Validation scripts and research
dataset/               ← CSV data and sample images
code/                  ← Frozen V1 system (archived reference)
archive/               ← Historical competition artifacts
submission/            ← Competition submission package
```

---

## Architecture

```
Input Claims.csv → Image Validator → Claim Parser → VLM Provider (external)
                                                      ↓
                              Evidence Checker ← Observation Report
                                      ↓
                              Rule Engine (6 decision paths)
                                      ↓
                              Risk Analyzer → Severity Engine
                                      ↓
                              Output Validator → Output.csv
```

The framework is deterministic where possible. VLMs act as **observers** — they extract visual facts. The rule engine makes **decisions** based on those facts.

---

## Modes

| Mode | Command | Description |
|------|---------|-------------|
| Production | `python -m code.main` | Full pipeline with live VLM provider |
| Demo | `python -m code.evaluation.static_evaluate` | Static evaluation with ideal observations |
| API | `uvicorn api.main:app` | FastAPI service with health/metrics endpoints |
| Dashboard | `streamlit run dashboard/app.py` | Real-time monitoring dashboard |

---

## Testing

```bash
pytest tests/              # 135 tests — all pass
pytest tests/v1/           # V1: parser, rule engine, risk, CV, output
pytest tests/v2/           # V2: pipeline, fraud, confidence, consensus, security, persistence
```

---

## Provider Setup

| Provider | Env Variable | Extras |
|----------|-------------|--------|
| Gemini | `GEMINI_API_KEY` | `verifyiq[gemini]` |
| OpenRouter | `OPENROUTER_API_KEY` | `verifyiq[openrouter]` |
| Local VLM | Local endpoint | Custom |
| Custom | Any | Implement `VisionProvider` ABC |

See [examples/providers/](examples/providers/) and [VISION_PROVIDER_REQUIREMENTS.md](VISION_PROVIDER_REQUIREMENTS.md).

---

## License

MIT License. See [LICENSE](LICENSE) for details.
