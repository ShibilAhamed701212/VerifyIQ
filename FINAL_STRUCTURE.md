# Final Repository Structure — VerifyIQ

Generated: 2026-06-20

## Top Level (visible in 10 seconds)

```
verifyiq/          ← Python package (pip install verifyiq)
docs/              ← All documentation
tests/             ← All tests (135 cases)
examples/          ← Example scripts
api/               ← FastAPI standalone app
dashboard/         ← Streamlit dashboard
reports/           ← All reports, evaluations, audits
scripts/           ← Deploy and utility scripts
docker/            ← Docker files
research/          ← Research materials, validation scripts
dataset/           ← CSV data and sample images
archive/           ← Historical competition artifacts
submission/        ← Competition submission artifacts
```

## Package: `verifyiq/`

```
verifyiq/
  __init__.py           ← Package version, sys.path for V1 code/
  __main__.py           ← CLI entry point (verifyiq evaluate|version)
  v1/__init__.py        ← V1 wrappers (imports from code/ frozen V1)
  v2/
    __init__.py           ← Public API exports
    pipeline.py           ← V2Pipeline (10-layer orchestrator)
    v1_adapter.py         ← V1→V2 adapter layer
    batch_processor.py    ← Batch processing
    rate_limiter.py       ← Rate limiting
    risk_merger.py        ← Risk flag merging
    tracer.py             ← Decision tracing
    vision_manager.py     ← VisionAvailabilityManager, circuit breaker
    performance.py        ← Performance monitoring
    persistence.py        ← SQLite persistence
    review_queue.py       ← Human-in-the-loop review queue
    startup_validator.py  ← Startup validation (mode checks)
    monitoring.py         ← System monitoring
    models/               ← Data models (decision, observation, etc.)
    confidence/           ← Confidence calibration
    consensus/            ← Multi-model consensus
    conversation/         ← Conversational analysis
    critic/               ← Self-critique module
    decision/             ← Decision logic
    evidence/             ← Evidence recommendation
    explainability/       ← Explainability and tracing
    fraud/                ← Fraud detection modules
    observability/        ← Logging, metrics, tracing
    providers/            ← VLM provider ABC + implementations
    security/             ← Input sanitization
```

## Tests: `tests/` (135 cases)

```
tests/
  v1/                   ← 8 V1 test files (58 test cases)
  v2/                   ← 12 V2 test files (77 test cases)
```

## Documentation: `docs/`

```
docs/
  architecture/         ← ARCHITECTURE, V2_ARCHITECTURE, V2_MODULES, DUAL_RISK
  api/                  ← V2_API
  security/             ← SECURITY, V2_SECURITY, ADVERSARIAL_TESTING
  production/           ← SYSTEM_HEALTH, DEPLOYMENT_READINESS
  evaluation/           ← EVALUATION, RELIABILITY, REPRODUCIBILITY, JUDGE_INTERVIEW, WINNING_REVIEW
  open_source/          ← OPEN_SOURCE_STRUCTURE, COMMUNITY_GUIDE
  deployment/           ← PACKAGE_GUIDE, TESTPYPI_GUIDE, PYPI_STRATEGY, RELEASE_CHECKLIST, CI_CD_DESIGN
  superpowers/          ← Internal development plans
```

## Reports: `reports/`

```
reports/
  evaluation/           ← 20 evaluation reports (confidence, fraud, robustness, etc.)
  production/           ← 5 production reports (deployment, readiness, reviews)
  performance/          ← 12 performance/code audit reports
  competition/          ← 10 competition analysis reports
  open_source/          ← 3 open source maturity reports
  security/             ← (existing security reports)
  archive/              ← Superseded evaluation reports
```

## Examples: `examples/`

```
examples/
  README.md
  01_quickstart.py
  02_v1_pipeline.py
  03_v2_pipeline.py
  04_security.py
  providers/
    README.md
    gemini_example.py
    openrouter_example.py
    local_vlm_example.py
```

## Preserved Root Files

```
README.md                  ← Project identity: "AI agent framework, not a model"
CONTRIBUTING.md            ← Contributor guide
CHANGELOG.md               ← Release history
AGENTS.md                  ← Agent instructions (HackerRank)
ATTRIBUTIONS.md            ← Attributions
problem_statement.md       ← Original challenge
VERSION                    ← Version file
VISION_PROVIDER_REQUIREMENTS.md  ← VLM setup guide
PROJECT_IDENTITY.md        ← Identity document
GOVERNANCE.md              ← Governance framework
pyproject.toml             ← Package config
.gitignore                 ← Git ignore rules
REPOSITORY_AUDIT.md        ← This reorg audit
TARGET_STRUCTURE.md        ← Target structure document
FINAL_STRUCTURE.md         ← This file
CLEANUP_PROPOSAL.md        ← Cleanup recommendations
```

## Frozen: `code/` (V1 — No Modifications)

```
code/                     ← V1 competition system (FROZEN)
  __init__.py + 15 .py files
  cv/ (4 .py files)
  evaluation/ (5 .py files)
  v2/ (preserved original, tests still reference it)
```

## Validation Results

| Check | Status |
|-------|--------|
| 135 tests (tests/v1 + tests/v2) | ✅ Pass (5.10s) |
| 135 tests (original code/tests + code/v2/tests) | ✅ Pass |
| Package imports (`from verifyiq.v2 import V2Pipeline`) | ✅ OK |
| CLI (`verifyiq version`) | ✅ OK |
| API imports (`from api.main import app`) | ✅ OK |
| All V2 modules importable | ✅ OK |
| Dashboard imports | ⚠️ Needs streamlit (optional dep) |
