# VerifyIQ Open-Source Structure

> **VerifyIQ is a production-oriented AI agent framework for multimodal claim verification. It performs reasoning, risk analysis, fraud detection, and decision-making using observations supplied by external vision providers (VLMs). Users configure their own VLM — Gemini, OpenRouter, local models, or custom providers. VerifyIQ does not contain a proprietary vision model.**

> Architecture and migration plan for transforming VerifyIQ from a competition
> repository into a long-term open-source project.

---

## Table of Contents

1. [Current Structure](#1-current-structure)
2. [Future Structure](#2-future-structure)
3. [Migration Plan — 3 Stages](#3-migration-plan--3-stages)
4. [Package Design](#4-package-design)
5. [Testing Architecture](#5-testing-architecture)
6. [Research and Assets](#6-research-and-assets)
7. [Final Review](#7-final-review)

---

## 1. Current Structure

### Root Level — 46 entries

```
./
├── AGENTS.md                         # Agent orchestration rules (competition)
├── ATTRIBUTIONS.md                   # Third-party licenses
├── PROJECT_IDENTITY.md               # Project philosophy
├── README.md                         # Main README (330 lines)
├── problem_statement.md              # Challenge description (competition)
├── chat_transcript.txt               # Development transcript (competition)
│
├── code/                             # V1 production pipeline — 58 tests, 20/20 eval
│   ├── claim_parser.py
│   ├── claim_processor.py
│   ├── config.py
│   ├── cv/                           # blur_detector, crop_detector, object_validator, text_detector
│   ├── decision_agent.py
│   ├── evaluation/                   # 9 files (evaluators, static_evaluate)
│   ├── evidence_checker.py
│   ├── image_preprocessor.py
│   ├── image_validator.py
│   ├── main.py
│   ├── output_validator.py
│   ├── prompts.py
│   ├── risk_analyzer.py
│   ├── rule_engine.py
│   ├── severity_engine.py
│   ├── submission_critic.py
│   ├── tests/                        # 8 test files, 58 tests
│   ├── utils.py
│   ├── v2/                           # V2 production pipeline — 49 tests
│   │   ├── pipeline.py
│   │   ├── v1_adapter.py
│   │   ├── models/                   # 7 data models
│   │   ├── providers/                # 4 VLM providers
│   │   ├── consensus/                # Consensus engine
│   │   ├── fraud/                    # 3 detectors
│   │   ├── evidence/                 # Evidence recommender
│   │   ├── conversation/             # Conversation analyzer
│   │   ├── confidence/               # Confidence calibrator
│   │   ├── critic/                   # Cross-layer critic
│   │   ├── explainability/           # Decision tracer
│   │   ├── observability/            # Metrics + tracing
│   │   ├── security/                 # Input sanitizer
│   │   ├── localization/             # Research doc
│   │   └── tests/                    # 10 test files, 49 tests
│   ├── __init__.py
│   ├── requirements.txt
│   └── README.md
│
├── dataset/                          # Competition data (unchanged, reference-only)
│   ├── sample_claims.csv
│   ├── claims.csv
│   ├── evidence_requirements.csv
│   ├── user_history.csv
│   └── images/                       # sample/ (20), test/ (44)
│
├── output.csv                        # Generated output (competition)
│
├── docs/                             # Documentation (9 files)
│   ├── ARCHITECTURE.md
│   ├── EVALUATION.md
│   ├── RELIABILITY.md
│   ├── REPRODUCIBILITY.md
│   ├── SECURITY.md
│   ├── ADVERSARIAL_TESTING.md
│   ├── JUDGE_INTERVIEW.md
│   ├── WINNING_REVIEW.md
│   └── superpowers/
│       ├── plans/                    # 2 execution plans
│       └── specs/                    # (empty)
│
├── reports/                          # Competition evaluation reports (13 files)
├── submission/                       # Judge submission package (10 files)
├── adversarial_evaluation/           # Adversarial testing (6 files)
├── development/                      # Agent session history (2 files)
├── archive/                          # Superseded reference docs (3 files)
│
├── validate_confidence.py            # Validation harnesses (7 files)
├── validate_conversation.py
├── validate_fraud.py
├── validate_hidden_tests.py
├── validate_performance.py
├── validate_reliability.py
├── validate_v1_vs_v2.py
│
├── V1_VS_V2.md                       # Post-fix comparison report
├── V1_VS_V2_POSTFIX.md
├── CONFIDENCE_ANALYSIS.md
├── CONVERSATION_EVALUATION.md
├── FRAUD_EVALUATION.md
├── HIDDEN_TEST_SIMULATION.md
├── PERFORMANCE_REPORT.md
├── RELIABILITY_VALIDATION.md
├── TRANSCRIPT_VALIDATION.md
├── FINAL_COMPETITION_ANALYSIS.md
├── FINAL_DEPLOYMENT_RECOMMENDATION.md
├── FINAL_INTERVIEW.md
├── FINAL_PANEL_EVALUATION.md
├── FINAL_VERDICT_V2.md
│
├── V2_ARCHITECTURE.md                # V2 design docs (7 files)
├── V2_API.md
├── V2_COMPETITIVE_ANALYSIS.md
├── V2_IMPLEMENTATION_PLAN.md
├── V2_MODULES.md
├── V2_ROADMAP.md
├── V2_SECURITY.md
│
├── .gitignore
└── .pytest_cache/
```

### Structural Observations

| Attribute | Value |
|-----------|-------|
| Total root-level entries | 46 |
| Root-level `.md` files | 26 |
| Root-level `.py` scripts | 7 |
| V1 source files | ~16 `.py` |
| V2 source files | ~25 `.py` |
| Total tests | 107 (58 V1 + 49 V2) |
| Competition reports | 13 in `reports/`, 9 in `docs/`, 10 in `submission/` |
| Package config | `code/requirements.txt` only — no `pyproject.toml`, no `setup.py` |
| Docker/deployment | None |

### Key Architectural Principle: External VLMs

VerifyIQ is an **AI agent framework**, not a vision model. The VLM provider abstraction is central to the architecture:

- **VLM as observer**: VLMs extract structured observations from images (damage type, object part, quality metrics). They do not make decisions.
- **Framework as judge**: The deterministic rule engine, risk analyzer, and severity engine evaluate observations against claim requirements and produce verdicts.
- **Pluggable provider interface**: The `BaseVLMProvider` ABC (in `code/v2/providers/base.py`) defines the contract. Any VLM that implements `analyze_images(paths, claim_text) -> dict` can be used.
- **Provider-specific SDKs are optional dependencies**: `google-genai` (Gemini), `httpx` (OpenRouter), `openai` (GPT-4o Vision) — each is an install-time extra, never a core dependency.
- **The quality of image understanding depends entirely on the configured vision provider.** Better VLMs produce better observations, which lead to more accurate decisions.

### Problems to Solve

1. **No pip-installable package** — no `pyproject.toml`, `setup.py`, or `setup.cfg`
2. **Flat namespace** — V1 and V2 coexist under `code/` with no clear boundary for consumers
3. **Competition artifacts mixed with library code** — reports, validation scripts, docs at root
4. **No dev/prod dependency separation** — single `requirements.txt` for V1 only
5. **No extendability surface** — no plugin system, no public API, no typed interfaces
6. **No deployment artifacts** — no Docker, docker-compose, or CI/CD configuration
7. **No examples or tutorials** — no `examples/`, no quickstart, no notebooks

---

## 2. Future Structure

### Design Principles

- **Preserve everything** — competition artifacts are frozen reference material
- **No duplication** — V1 and V2 are not copied into the new layout; they are symlinked or imported
- **Pip-installable** — `pip install verifyiq` works for the core library
- **Extras-based** — `verifyiq[api]`, `verifyiq[dashboard]`, `verifyiq[dev]`
- **Migration-safe** — every stage has a rollback; nothing is deleted until frozen
- **Community-ready** — CONTRIBUTING, issue templates, PR templates, code of conduct

### Proposed Layout

```
./
│
├── verifyiq/                              # ← Canonical Python package
│   ├── __init__.py                        # Package metadata, version
│   ├── __main__.py                        # `python -m verifyiq` entry point
│   ├── _version.py                        # Single source of truth for version
│   │
│   ├── core/                              # Shared interfaces and base classes
│   │   ├── __init__.py
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   ├── vlm_provider.py            # VisionProvider ABC (moved from v2/providers/base.py)
│   │   │   ├── fraud_detector.py          # FraudDetector ABC
│   │   │   ├── evidence_checker.py        # EvidenceChecker ABC
│   │   │   └── plugin.py                  # Plugin ABC
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── claim.py                   # Shared claim data model
│   │   │   ├── evidence.py                # Shared evidence model
│   │   │   └── decision.py                # Shared decision model
│   │   ├── config.py                      # Unified configuration
│   │   ├── exceptions.py                  # Custom exception hierarchy
│   │   └── registry.py                    # Plugin/detector/provider registry
│   │
│   ├── v1/                                # V1 pipeline wrapper
│   │   ├── __init__.py
│   │   ├── pipeline.py                    # Thin wrapper referencing code/ modules
│   │   ├── adapter.py                     # Canonical V1RuleAdapter, V1SeverityAdapter, etc.
│   │   └── tests/                         # V1 test wrappers (pytest imports from code/tests/)
│   │
│   ├── v2/                                # V2 production pipeline
│   │   ├── __init__.py
│   │   ├── pipeline.py                    # 10-layer orchestrator (moved from code/v2/)
│   │   ├── v1_adapter.py                  # Bridge to V1 (moved from code/v2/)
│   │   ├── models/                        # 7 data models (moved)
│   │   ├── providers/                     # VLM providers (moved)
│   │   ├── consensus/                     # Consensus engine (moved)
│   │   ├── fraud/                         # 3 detectors (moved)
│   │   ├── evidence/                      # Evidence recommender (moved)
│   │   ├── conversation/                  # Conversation analyzer (moved)
│   │   ├── confidence/                    # Confidence calibrator (moved)
│   │   ├── critic/                        # Cross-layer critic (moved)
│   │   ├── explainability/                # Decision tracer (moved)
│   │   ├── observability/                 # Metrics + tracing (moved)
│   │   ├── security/                      # Input sanitizer (moved)
│   │   └── localization/                  # Research doc (moved)
│   │
│   ├── api/                               # FastAPI service (Phase 2)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── analyze.py
│   │   │   ├── batch.py
│   │   │   ├── evaluate.py
│   │   │   └── health.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── models.py                  # Pydantic request/response models
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── rate_limit.py
│   │
│   ├── dashboard/                          # Streamlit dashboard (Phase 3)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── pages/
│   │   │   ├── analyze.py
│   │   │   ├── compare.py
│   │   │   └── traces.py
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── uploader.py
│   │       ├── results.py
│   │       └── charts.py
│   │
│   ├── plugins/                            # Plugin system (Phase 4)
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── gemini.py
│   │   │   ├── openrouter.py
│   │   │   └── local_vlm.py
│   │   ├── detectors/
│   │   │   ├── __init__.py
│   │   │   ├── image_hash.py
│   │   │   ├── metadata.py
│   │   │   └── behavioral.py
│   │   ├── rules/
│   │   │   ├── __init__.py
│   │   │   └── v1_rules.py
│   │   └── critics/
│   │       ├── __init__.py
│   │       └── v2_critic.py
│   │
│   ├── benchmarks/                         # Benchmark framework (Phase 5)
│   │   ├── __init__.py
│   │   ├── runner.py
│   │   ├── metrics.py
│   │   ├── datasets/
│   │   │   ├── __init__.py
│   │   │   ├── sample.py
│   │   │   ├── adversarial.py
│   │   │   └── synthetic.py
│   │   └── reports/
│   │       ├── __init__.py
│   │       └── generator.py
│   │
│   ├── tests/                              # Integration and cross-module tests
│   │   ├── __init__.py
│   │   ├── integration/
│   │   │   ├── test_v1_v2_parity.py        # V1 vs V2 comparison
│   │   │   ├── test_pipeline_end_to_end.py
│   │   │   └── test_api_endpoints.py
│   │   ├── api/
│   │   │   ├── test_analyze.py
│   │   │   ├── test_health.py
│   │   │   └── test_batch.py
│   │   └── performance/
│   │       ├── test_latency.py
│   │       └── test_throughput.py
│   │
│   └── examples/                           # Usage examples (Phase 12)
│       ├── __init__.py
│       ├── 01_quickstart.py
│       ├── 02_custom_provider.py
│       ├── 03_batch_processing.py
│       ├── 04_fraud_detection.py
│       └── 05_api_client.py
│
├── code/                                   # ← FROZEN: original V1 (reference only)
│   ├── (unchanged — 25 entries)
│   └── v2/                                 # ← FROZEN: original V2 (reference only)
│       └── (unchanged — 19 entries)
│
├── dataset/                                # ← FROZEN: competition data
│   └── (unchanged)
│
├── docs/                                   # Consolidated documentation
│   ├── README.md                           # Project overview
│   ├── ARCHITECTURE.md                     # System architecture
│   ├── API.md                              # API reference
│   ├── SECURITY.md                         # Security model
│   ├── DEPLOYMENT.md                       # Deployment guide
│   ├── CONTRIBUTING.md                     # Contribution guide
│   ├── CODE_OF_CONDUCT.md                  # Community standards
│   ├── tutorials/
│   │   ├── quickstart.md
│   │   └── advanced.md
│   ├── specs/                              # Design documents
│   │   ├── 2026-06-20-open-source-structure.md
│   │   └── (future specs)
│   └── research/                           # Research publications
│       ├── 01-explainable-claim-verification.md
│       └── (future papers)
│
├── reports/                                # ← FROZEN: competition reports
│   ├── (unchanged — 13 files)
│   ├── V1_VS_V2.md
│   └── (competition evaluation reports)
│
├── submission/                             # ← FROZEN: judge submission
│   └── (unchanged — 10 files)
│
├── adversarial_evaluation/                 # ← FROZEN: adversarial testing
│   └── (unchanged)
│
├── development/                            # ← FROZEN: agent history
│   └── (unchanged)
│
├── archive/                                # ← FROZEN: superseded docs
│   └── (unchanged)
│
├── research/                               # Research artifacts
│   ├── papers/
│   │   ├── arxiv/
│   │   └── drafts/
│   ├── experiments/
│   │   ├── ablation_studies/
│   │   ├── provider_comparison/
│   │   └── confidence_calibration/
│   └── notebooks/
│       ├── 01_claim_analysis.ipynb
│       ├── 02_confidence_analysis.ipynb
│       ├── 03_provider_comparison.ipynb
│       └── 04_adversarial_analysis.ipynb
│
├── assets/                                 # Media and design assets
│   ├── diagrams/
│   │   ├── architecture.png
│   │   ├── pipeline.png
│   │   ├── v1_vs_v2_comparison.png
│   │   └── decision_tree.png
│   ├── screenshots/
│   │   ├── dashboard_analyze.png
│   │   ├── dashboard_compare.png
│   │   └── dashboard_traces.png
│   └── branding/
│       ├── logo.svg
│       └── banner.png
│
├── docker/                                 # Container definitions
│   ├── Dockerfile                          # Production image
│   ├── Dockerfile.gpu                      # GPU-enabled image
│   ├── Dockerfile.dev                      # Development image
│   ├── docker-compose.yml                  # Full stack
│   └── .dockerignore
│
├── scripts/                                # Build and automation scripts
│   ├── setup.sh                            # Environment setup
│   ├── run_tests.sh                        # Test runner
│   ├── run_lint.sh                         # Linting
│   ├── build_docs.sh                       # Documentation builder
│   ├── deploy.sh                           # Deployment script
│   └── validate_submission.sh              # Competition validator
│
├── pyproject.toml                          # Package metadata & build config
├── setup.cfg                               # Tool configuration
├── setup.py                                # Legacy setup script
├── requirements.txt                        # Core runtime dependencies
├── requirements-dev.txt                    # Development dependencies
├── MANIFEST.in                             # Package manifest
├── Makefile                                # Task automation
├── .github/                                # GitHub configuration
│   ├── workflows/
│   │   ├── ci.yml                          # Continuous integration
│   │   ├── publish.yml                     # PyPI publish
│   │   └── docs.yml                        # Docs deploy
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── config.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── .gitignore                              # Updated ignores
├── .pre-commit-config.yaml                 # Pre-commit hooks
├── LICENSE                                  # Open-source license
└── CODEOWNERS                              # Code ownership
```

---

## 3. Migration Plan — 3 Stages

### Stage 1: Foundation (No Breaking Changes)

**Goal:** Create the package skeleton without touching any existing code.

| Step | Action | Risk | Rollback |
|------|--------|------|----------|
| 1.1 | Create `verifyiq/` package skeleton | None (new directory) | `rm -rf verifyiq/` |
| 1.2 | Create `pyproject.toml`, `setup.cfg`, `setup.py` | None (new files) | `git revert` |
| 1.3 | Create `verifyiq/core/interfaces/` with ABC stubs | None (new files) | `rm -rf verifyiq/core/` |
| 1.4 | Create `verifyiq/core/models/` with shared dataclasses | Low — must not conflict with existing models | `git revert` |
| 1.5 | Create `verifyiq/core/config.py` as unified config loader | Low — must not change `code/config.py` | `git revert` |
| 1.6 | Create `verifyiq/core/registry.py` (empty registry) | None (new file) | `rm` |
| 1.7 | Create `verifyiq/__init__.py` and `verifyiq/__main__.py` | None (new files) | `rm` |
| 1.8 | Create `verifyiq/_version.py` with `__version__ = "0.1.0"` | None (new file) | `rm` |
| 1.9 | Create `docker/`, `scripts/`, `.github/`, `assets/`, `research/` | None (new directories) | `rm -rf` |
| 1.10 | Create `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` | None (new files) | `git revert` |

**Verification:** `pip install -e .` succeeds; `python -c "import verifyiq; print(verifyiq.__version__)"` works.

**Duration:** ~2 hours

**Dependencies:** None

**Tests affected:** None (no existing code changed)

---

### Stage 2: V1 Integration

**Goal:** Create `verifyiq/v1/` as a thin wrapper around `code/` without modifying it.

**Design:**

```python
# verifyiq/v1/__init__.py
"""VerifyIQ V1 — frozen competition pipeline.

All modules reference the canonical `code/` directory via path injection.
No file in `code/` is modified or duplicated.
"""
import sys
from pathlib import Path

_CODE_DIR = Path(__file__).resolve().parent.parent.parent / "code"
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from code.config import Config
from code.rule_engine import RuleEngine
from code.severity_engine import SeverityEngine
from code.evidence_checker import EvidenceChecker
from code.claim_parser import ClaimParser
from code.risk_analyzer import RiskAnalyzer
```

| Step | Action | Risk | Rollback |
|------|--------|------|----------|
| 2.1 | Create `verifyiq/v1/__init__.py` with path-injecting imports | Low — path injection is fragile | `rm -rf verifyiq/v1/` |
| 2.2 | Create `verifyiq/v1/__init__.py` that re-exports all public symbols | Low — pure re-export | `git revert` |
| 2.3 | Create `verifyiq/v1/adapter.py` — canonical adapter layer (import from `code/v2/v1_adapter.py`) | Low — pure re-export | `git revert` |
| 2.4 | Create `verifyiq/v1/tests/` — wrapper that runs `code/tests/` | Low — pytest can import from `code/tests/` | `rm -rf verifyiq/v1/tests/` |
| 2.5 | Add `verifyiq[v1]` extra to `pyproject.toml` | None | `git revert` |

**Verification:**
```python
from verifyiq.v1 import Config, RuleEngine, SeverityEngine
from verifyiq.v1.adapter import V1RuleAdapter
```
All import cleanly. All 58 V1 tests pass via `pytest verifyiq/v1/tests/`.

**Duration:** ~3 hours

**Dependencies:** Stage 1 complete

**Tests affected:**
- `code/tests/` — unchanged, still pass at 58/58
- `verifyiq/v1/tests/` — new wrappers, must also pass at 58/58

---

### Stage 3: V2 Integration

**Goal:** Move V2 source files into `verifyiq/v2/` and update imports.

**Approach:** Hard-link (or copy) source files from `code/v2/` into `verifyiq/v2/`, then update internal imports to use `verifyiq.` prefix.

| Step | Action | Risk | Rollback |
|------|--------|------|----------|
| 3.1 | Copy `code/v2/` → `verifyiq/v2/` | Low — pure file copy | `rm -rf verifyiq/v2/` |
| 3.2 | Update internal imports in `verifyiq/v2/` from `code.v2.` → `verifyiq.v2.` | Medium — must update every cross-reference | `git revert` |
| 3.3 | Update adapter imports in `verifyiq/v2/v1_adapter.py` to use `verifyiq.v1.` | Medium — adapter is the V1→V2 bridge | `git revert` |
| 3.4 | Relocate tests: `code/v2/tests/` → `verifyiq/v2/tests/` with import updates | Medium — tests import the modules they test | `git revert` |
| 3.5 | Update `code/v2/` to import from `verifyiq/v2/` (bidirectional compat) | Medium — circular import risk | `git revert` |
| 3.6 | Add `verifyiq[v2]` extra to `pyproject.toml` | None | `git revert` |

**Verification:**
```python
from verifyiq.v2 import V2Pipeline
from verifyiq.v2.models import V2Decision
```
All import cleanly. All 49 V2 tests pass via `pytest verifyiq/v2/tests/`.

**Duration:** ~4 hours

**Dependencies:** Stages 1 + 2 complete

**Tests affected:**
- `code/v2/tests/` — may need import updates if V2 modules moved
- `verifyiq/v2/tests/` — relocated tests, must pass 49/49

### Migration Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Broken import chain | Medium | High | Test each import after every file move; maintain bidirectional compat during transition |
| V1 path injection breaks | Low | Critical | Use `sys.path` injection only as fallback; prefer absolute imports |
| Circular imports (V1↔V2 adapter) | Medium | Medium | Keep adapter as standalone bridge; never import V1 from V2 core modules |
| Test duplication | Low | Low | `verifyiq/v*/tests/` are wrappers referencing canonical tests; no file copy |
| `code/` import breaks | Low | Critical | Never modify `code/`; wrapper layer only adds, never changes |

### Rollback Strategy

Each stage is independently revertible:

- **Stage 1 rollback:** `git revert` all new directory/file additions
- **Stage 2 rollback:** `rm -rf verifyiq/v1/` — `code/` is untouched
- **Stage 3 rollback:** `rm -rf verifyiq/v2/` — `code/v2/` is untouched (or `git revert`)

The original `code/` and `code/v2/` are NEVER modified during migration. At any point, the original test commands still work:
```
pytest code/tests/        # 58/58 always
pytest code/v2/tests/     # 49/49 always
```

---

## 4. Package Design

### `pyproject.toml` — Core Configuration

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "verifyiq"
version = "0.1.0"
description = "AI Agent Framework for Multi-Modal Claim Verification"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.10"

authors = [
    { name = "VerifyIQ Contributors" },
]

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Security",
]

keywords = [
    "multimodal", "claim-verification", "fraud-detection",
    "vlm", "agent-framework", "vision-provider", "insurance", "explainable-ai",
]

dependencies = [
    "Pillow>=10.0.0",
    "tqdm>=4.65.0",
]

[project.optional-dependencies]
v1 = []  # V1 wrapped from code/ — no additional deps
v2 = [
    "Pillow>=10.0.0",
    "tqdm>=4.65.0",
]
api = [
    "fastapi>=0.110.0",
    "uvicorn>=0.27.0",
    "pydantic>=2.0.0",
    "python-multipart>=0.0.9",
]
dashboard = [
    "streamlit>=1.30.0",
    "plotly>=5.18.0",
    "pandas>=2.0.0",
]
gemini = [
    "google-genai>=1.0.0",
]
openrouter = [
    "httpx>=0.27.0",
    "websockets>=12.0",
]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
    "black>=24.0.0",
    "isort>=5.13.0",
    "build>=1.0.0",
    "twine>=5.0.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.5.0",
    "mkdocstrings>=0.24.0",
]
all = [
    "verifyiq[v1,v2,api,dashboard,gemini,openrouter,dev,docs]",
]

[project.urls]
Homepage = "https://github.com/verifyiq/verifyiq"
Documentation = "https://verifyiq.readthedocs.io"
Source = "https://github.com/verifyiq/verifyiq"
Issues = "https://github.com/verifyiq/verifyiq/issues"

[tool.setuptools.packages.find]
include = ["verifyiq*"]
exclude = ["verifyiq/tests*"]

[tool.setuptools.package-data]
"verifyiq" = ["py.typed"]

[tool.pytest.ini_options]
testpaths = [
    "code/tests",
    "code/v2/tests",
    "verifyiq/v1/tests",
    "verifyiq/v2/tests",
    "verifyiq/tests",
]
addopts = "-v --tb=short"

[tool.ruff]
target-version = "py310"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.10"
strict = false
ignore_missing_imports = true

[tool.coverage.run]
source = ["verifyiq"]
omit = ["*/tests/*"]
```

### Dependency Groups

| Extra | Dependencies | Use Case |
|-------|-------------|----------|
| (core) | Pillow, tqdm | Minimal V1 inference |
| `v2` | Pillow, tqdm | V2 pipeline |
| `api` | FastAPI, uvicorn, pydantic | REST API server |
| `dashboard` | Streamlit, plotly, pandas | Interactive dashboard |
| `gemini` | google-genai | Google Gemini provider |
| `openrouter` | httpx, websockets | Multi-model routing |
| `dev` | pytest, ruff, mypy, pre-commit, black, isort, build, twine | Development |
| `docs` | mkdocs, mkdocs-material, mkdocstrings | Documentation |
| `all` | Everything above | Full install |

### Installation Options

```bash
# Core (V1 inference)
pip install verifyiq

# V2 pipeline
pip install verifyiq[v2]

# API server
pip install verifyiq[api]

# Full development
pip install verifyiq[all]

# Editable development install
pip install -e ".[dev]"
```

---

## 5. Testing Architecture

### Test Ownership

| Test Suite | Location | Owner | Migration |
|-----------|----------|-------|-----------|
| V1 unit tests | `code/tests/` (8 files, 58 tests) | V1 pipeline | Stay; `verifyiq/v1/tests/` wraps them |
| V2 unit tests | `code/v2/tests/` (10 files, 49 tests) | V2 pipeline | Stay; `verifyiq/v2/tests/` wraps them |
| V1 static eval | `code/evaluation/static_evaluate.py` | Competition | Stay; reference only |
| V2 validation | Root `validate_*.py` (7 scripts) | Competition | Stay; reference only |

### Future Test Locations (under verifyiq/)

```
verifyiq/tests/
├── __init__.py
├── integration/                     # End-to-end cross-module tests
│   ├── __init__.py
│   ├── test_v1_v2_parity.py         # Ensures V2 output matches V1 on sample claims
│   ├── test_pipeline_end_to_end.py  # Full pipeline with mock providers
│   └── test_consensus_agreement.py  # Multi-model consensus correctness
├── api/                             # API endpoint tests
│   ├── __init__.py
│   ├── test_analyze.py
│   ├── test_health.py
│   ├── test_batch.py
│   └── test_auth.py
└── performance/                     # Performance benchmark tests
    ├── __init__.py
    ├── test_latency.py              # Per-claim latency thresholds
    └── test_throughput.py           # Concurrent request handling
```

### Test Separation Rules

1. **V1 tests in `code/tests/` are NEVER moved or modified** — they are competition artifacts
2. **V2 tests in `code/v2/tests/` are NEVER moved or modified** — they are competition artifacts
3. **`verifyiq/v1/tests/` wrappers** import and run V1 tests via pytest's `--rootdir` or explicit test collection
4. **`verifyiq/v2/tests/`** are copies with updated `verifyiq.` imports (or wrappers)
5. **New integration/API/performance tests** are added to `verifyiq/tests/`
6. **All 107 original tests must pass** at all times during and after migration

### CI Test Matrix

```yaml
# .github/workflows/ci.yml (future)
jobs:
  v1-tests:
    run: pytest code/tests/              # 58 tests, always
  v2-tests:
    run: pytest code/v2/tests/           # 49 tests, always
  verifyiq-tests:
    run: pytest verifyiq/tests/          # New integration tests
  lint:
    run: ruff check verifyiq/
  typecheck:
    run: mypy verifyiq/
```

---

## 6. Research and Assets

### `research/` Directory

```
research/
├── papers/                             # Publication drafts
│   ├── arxiv/                          # Published/submitted papers
│   └── drafts/                         # In-progress manuscripts
├── experiments/                        # Reproducible experiment code
│   ├── ablation_studies/
│   │   ├── README.md
│   │   ├── run_ablation.py
│   │   └── results/
│   ├── provider_comparison/
│   │   ├── README.md
│   │   ├── compare_providers.py
│   │   └── results/
│   └── confidence_calibration/
│       ├── README.md
│       ├── calibrate.py
│       └── results/
└── notebooks/                          # Jupyter notebooks
    ├── 01_claim_analysis.ipynb
    ├── 02_confidence_analysis.ipynb
    ├── 03_provider_comparison.ipynb
    └── 04_adversarial_analysis.ipynb
```

### `assets/` Directory

```
assets/
├── diagrams/                           # Architecture and flow diagrams
│   ├── architecture.png                # High-level system architecture
│   ├── pipeline.png                    # V2 10-layer pipeline flow
│   ├── v1_vs_v2_comparison.png         # Side-by-side comparison
│   ├── decision_tree.png               # V1 rule engine decision tree
│   └── data_flow.png                   # Data flow diagram
├── screenshots/                        # Dashboard screenshots
│   ├── dashboard_analyze.png           # Analysis view
│   ├── dashboard_compare.png           # V1 vs V2 comparison view
│   └── dashboard_traces.png            # Decision traces view
└── branding/                           # Project branding
    ├── logo.svg                        # Vector logo
    ├── logo.png                        # Raster logo
    └── banner.png                      # GitHub social banner
```

### Relationship to Existing Docs

| New Directory | Source Material | Relationship |
|-------------|----------------|-------------|
| `research/papers/` | `docs/` reports + V2 docs | Synthesized from competition findings |
| `research/experiments/` | `validate_*.py` scripts | Formalized into reproducible experiments |
| `research/notebooks/` | New (from scratch) | Tutorial-style interactive analysis |
| `assets/diagrams/` | New (created from architecture) | Visual representations of existing docs |
| `assets/screenshots/` | New (captured from dashboard) | Product previews |
| `assets/branding/` | New (designed) | Project identity materials |

---

## 7. Final Review

### As Open-Source Maintainer

**Strengths:**

1. **Comprehensive test coverage** — 107 tests across 18 test files covering both pipelines
2. **Clean architecture** — clear V1↔V2 separation via adapter pattern; 10-layer V2 pipeline is well-modularized
3. **Production features** — fraud detection, conversation analysis, confidence calibration, security sanitization, explainability — all present
4. **Competition validation** — 20/20 static evaluation on sample claims; hidden test 81.5% relaxed match
5. **Rich documentation** — 26+ design docs, architecture docs, competitive analysis, security docs
6. **Pluggable VLM provider system** — Gemini provider with fallback chain; OpenRouter, GPT-4o Vision, Qwen-VL, MiniCPM-V, and local VLM adapters available. The provider interface is the cornerstone of the agent framework architecture.
7. **No tech debt from competition** — V1 is frozen; V2 is purpose-built; no hackathon shortcuts in production code

**Risks:**

1. **Complexity barrier** — 49 files in V2 alone is intimidating for new contributors; needs clear onboarding
2. **VLM dependency** — core functionality depends on external VLM providers with rate limits and costs. This is by design (VerifyIQ is a framework, not a model), but means users must budget for provider API costs.
3. **No active community** — single-contributor project at launch; sustainability is uncertain
4. **Niche domain** — insurance claim verification is a specific vertical; broad appeal is limited
5. **Competition IP questions** — the problem statement and dataset may have usage restrictions
6. **No CI/CD** — no automated testing, linting, or deployment pipeline yet
7. **No package published** — not on PyPI; no versioning convention established

**Next steps (post-migration):**

1. Publish initial `0.1.0` to PyPI (test PyPI first)
2. Set up GitHub Actions CI (lint + test + coverage)
3. Write CONTRIBUTING.md with onboarding guide
4. Create issue templates for bug reports and feature requests
5. Publish architecture diagrams to `assets/`
6. Set up ReadTheDocs for automated documentation deployment
7. Add a `quickstart.py` to `examples/` that works with `pip install verifyiq`
8. Recruit 2-3 external contributors before expanding scope

### As PyPI Reviewer

**Package readiness assessment:**

| Criterion | Status | Notes |
|-----------|--------|-------|
| `pyproject.toml` | Design complete | Not yet created |
| `setup.cfg` | Design complete | Not yet created |
| README | Existing (330 lines) | Needs update for open-source audience |
| License | Not selected | Recommend MIT |
| Dependencies | Identified | Core lightweight; extras for optional features |
| Type hints | Partial | V1 has minimal types; V2 has typed dataclasses |
| Documentation | Extensive | Competition-focused; needs user-focused rewrite |
| Tests | 107 passing | Needs CI integration |
| Entry point | Designed | `verifyiq/__main__.py` |
| Version | Designed | `0.1.0` |

**Recommendation:** Ready for `0.1.0` dev release after Stage 1 migration. Not yet ready for `1.0.0` — needs:
- Stable public API surface
- Comprehensive type hints
- User-focused documentation
- At least one external contributor review

### As GitHub Maintainer

**Repository health assessment:**

| Metric | Current | Target (3 months) |
|--------|---------|-------------------|
| Stars | 0 (private) | 50-100 |
| Contributors | 1 | 3-5 |
| Open issues | 0 | 5-10 (health signal) |
| PRs merged | 0 | 10-20 |
| CI passing | N/A | 100% |
| Coverage | ~65% (manual) | >80% (automated) |
| Documentation | Competition-focused | User + contributor focused |
| Release cadence | None | Monthly |

**Repository setup checklist:**

- [ ] Add `LICENSE` (MIT recommended)
- [ ] Add `CODE_OF_CONDUCT.md` (Contributor Covenant)
- [ ] Add `CONTRIBUTING.md` with development setup
- [ ] Create `.github/ISSUE_TEMPLATE/` (bug + feature)
- [ ] Create `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] Create `.github/workflows/ci.yml`
- [ ] Add `CODEOWNERS`
- [ ] Add `.pre-commit-config.yaml`
- [ ] Add `SECURITY.md` (vulnerability reporting)
- [ ] Configure GitHub Pages or ReadTheDocs
- [ ] Add GitHub social preview image

### Summary Assessment

| Dimension | Score (1-10) | Notes |
|-----------|-------------|-------|
| **Code quality** | 8 | Clean architecture, well-tested, but V1 has minimal typing |
| **Architecture** | 9 | Adapter pattern, layered V2, clear boundaries |
| **Test coverage** | 8 | 107 tests, good module coverage, needs integration tests |
| **Documentation** | 7 | Extensive but competition-focused; needs user rewrite |
| **Package readiness** | 4 | Design complete but no pyproject.toml, setup.py, or CI |
| **Community readiness** | 2 | No contributing guide, templates, or license yet |
| **Research value** | 7 | Novel architecture; papers possible on multimodal verification |
| **Production readiness** | 5 | Feature-complete but no deployment, monitoring, or scaling docs |
| **Overall** | **6.5** | Strong foundation; Stage 1 migration unlocks 0.1.0 release |

**Final verdict:** The project has a strong technical foundation. The immediate priority is Stage 1 migration (package skeleton, build config, CI) which requires zero changes to existing code. Stage 2 and Stage 3 can proceed independently once the package infrastructure is stable. The project is approximately 2 weeks of part-time work away from a publishable 0.1.0 release.
