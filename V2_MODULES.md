# VerifyIQ V2 — Module Catalog

**VerifyIQ is an AI agent framework.** Modules fall into two categories:
- **VLM-dependent** (require an external vision provider): Observation (Layer 1)
- **Pure reasoning** (deterministic, no VLM needed): All other layers (Layers 2–10)

The `providers/` package is the abstraction layer that decouples VerifyIQ from any specific VLM. The pipeline never calls a VLM directly — it always goes through the `VisionProvider` ABC.

## Package: `code/v2/`

### Root

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `pipeline.py` | 10-layer pipeline orchestrator | `V2Pipeline` | All V2 modules, V1 adapters | IMPLEMENTED |
| `v1_adapter.py` | Bridges V2 to frozen V1 components | `V1RuleAdapter`, `V1SeverityAdapter`, `V1EvidenceAdapter`, `V1ParserAdapter` | `code.rule_engine`, `code.severity_engine`, `code.evidence_checker`, `code.claim_parser` | IMPLEMENTED |

### `code/v2/models/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `observation.py` | Vision model output data models | `PerImageAssessment`, `Observation`, `ObservationReport` | — | IMPLEMENTED |
| `consensus.py` | Multi-model agreement data | `ModelDisagreement`, `ConsensusReport` | — | IMPLEMENTED |
| `fraud.py` | Fraud detection result models | `ImageFraudResult`, `MetadataFraudResult`, `BehavioralFraudResult`, `FraudReport` | — | IMPLEMENTED |
| `evidence.py` | Evidence recommendation models | `EvidenceRecommendation`, `EvidenceReport` | — | IMPLEMENTED |
| `conversation.py` | Conversation analysis models | `ConversationAnomaly`, `ConversationReport` | — | IMPLEMENTED |
| `confidence.py` | Confidence breakdown and routing | `ConfidenceBreakdown`, `ConfidenceReport` | — | IMPLEMENTED |
| `decision.py` | Final decision and trace models | `DecisionTrace`, `V2Decision` | — | IMPLEMENTED |

### `code/v2/providers/` — Provider Abstraction Layer

The provider abstraction layer decouples VerifyIQ from any specific VLM. The pipeline calls `VisionProvider.analyze()` without knowing whether the backend is Gemini, OpenRouter, or a local model. This design:
- **Eliminates vendor lock-in** — providers are plug-and-play
- **Enables multi-model observation** — multiple providers run in parallel
- **Isolates failures** — one provider failing never crashes the pipeline
- **Supports fallback chains** — Gemini → OpenRouter → Local VLM

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `base.py` | Abstract base for all vision providers | `VisionProvider` (ABC) | `code.v2.models.observation` | IMPLEMENTED |
| `gemini_provider.py` | Gemini API vision analysis | `GeminiProvider` | `google.genai`, `PIL`, `VisionProvider` | IMPLEMENTED |
| `openrouter_provider.py` | OpenRouter multi-model vision (stub) | `OpenRouterProvider` | `VisionProvider` | STUB |
| `local_vlm_provider.py` | Local VLM inference (stub, Qwen2.5-VL-7B) | `LocalVLMProvider` | `VisionProvider` | STUB |

> **VLM boundary:** Only `providers/*` and `observation.py` models are VLM-dependent. Every module below is pure deterministic reasoning — no VLM calls.

### `code/v2/consensus/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `engine.py` | Multi-model agreement scoring | `ConsensusEngine` | `code.v2.models.observation`, `code.v2.models.consensus` | IMPLEMENTED |

### `code/v2/fraud/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `image_fraud.py` | Duplicate, screenshot, and photo-of-photo detection | `ImageFraudDetector` | `PIL`, `hashlib` | IMPLEMENTED |
| `metadata_fraud.py` | EXIF editing software, camera, and timestamp analysis | `MetadataFraudDetector` | `PIL`, `PIL.ExifTags` | IMPLEMENTED |
| `behavioral_fraud.py` | Claim frequency, image reuse, and escalation patterns | `BehavioralFraudDetector` | `csv`, `hashlib` | IMPLEMENTED |

### `code/v2/evidence/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `recommender.py` | Missing evidence recommendation generation | `EvidenceRecommender` | `code.v2.models.evidence` | IMPLEMENTED |

### `code/v2/conversation/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `analyzer.py` | Claim text linguistic analysis | `ConversationAnalyzer` | `re`, `code.v2.models.conversation` | IMPLEMENTED |

### `code/v2/confidence/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `calibrator.py` | Multi-signal confidence calibration | `ConfidenceCalibrator` | All V2 report models | IMPLEMENTED |

### `code/v2/critic/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `v2_critic.py` | Post-processing consistency checks | `V2Critic` | All V2 report models | IMPLEMENTED |

### `code/v2/explainability/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `tracer.py` | Structured decision trace generation | `DecisionTracer` | All V2 report models | IMPLEMENTED |

### `code/v2/observability/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `metrics.py` | Per-module latency and success tracking | `MetricsCollector`, `PipelineMetrics`, `ModuleTiming` | `time`, `dataclasses` | IMPLEMENTED |
| `tracing.py` | JSON trace persistence to disk | `TraceLogger` | `json`, `code.v2.models.decision` | IMPLEMENTED |

### `code/v2/security/`

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `__init__.py` | Package marker | — | — | IMPLEMENTED |
| `sanitizer.py` | Input sanitization (injection, traversal, CSV) | `InputSanitizer` | `re`, `pathlib` | IMPLEMENTED |

### Ad-hoc / Planning

| File | Purpose | Key Classes | Dependencies | Status |
|------|---------|-------------|--------------|--------|
| `code/v2/localization/research.md` | YOLO/Grounding DINO/SAM2 integration research | — | — | RESEARCH |

## Summary

| Status | Count |
|--------|-------|
| IMPLEMENTED | 26 files |
| STUB | 2 files |
| RESEARCH | 1 file |
| **Total** | **29 files** |
