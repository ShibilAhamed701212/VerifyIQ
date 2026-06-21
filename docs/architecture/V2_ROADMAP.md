# VerifyIQ V2 — Implementation Roadmap

**VerifyIQ is an AI agent framework, not a model.** All vision observations come from external VLMs configured by the user. The roadmap reflects this architecture — observation providers are plug-in components, and the core pipeline is provider-agnostic.

## Phase Overview

| Phase | Module | Effort | Priority | Status |
|-------|--------|--------|----------|--------|
| 1 | V2 Project scaffolding | S | P0 | DONE |
| 2 | VisionProvider ABC | S | P0 | DONE |
| 3 | Gemini provider | M | P0 | DONE |
| 4 | Observation data models | S | P0 | DONE |
| 5 | Multi-model observation layer | M | P0 | DONE |
| 6 | Consensus engine | S | P0 | DONE |
| 7 | Fraud detection (image, metadata, behavioral) | M | P0 | DONE |
| 8 | Evidence recommender | S | P0 | DONE |
| 9 | Conversation analyzer | M | P0 | DONE |
| 10 | Confidence calibrator | S | P0 | DONE |
| 11 | V1 adapter layer | M | P0 | DONE |
| 12 | Critic | S | P0 | DONE |
| 13 | Explainability tracer | S | P0 | DONE |
| 14 | Observability (metrics + trace persistence) | S | P0 | DONE |
| 15 | Security sanitizer | S | P0 | DONE |
| 16 | Pipeline orchestrator | M | P0 | DONE |

## Remaining Work

| Phase | Module | Effort | Priority | Status |
|-------|--------|--------|----------|--------|
| 17 | OpenRouter provider implementation | M | P1 | TODO |
| 18 | Local VLM provider (Qwen2.5-VL-7B) | L | P2 | TODO |
| 19 | YOLOv8n object part detection | M | P1 | TODO |
| 20 | Production FastAPI server | L | P1 | TODO |
| 21 | Claim memory store | M | P1 | TODO |
| 22 | Hidden test evaluation | S | P0 | TODO |
| 23 | Weighted consensus voting | S | P2 | TODO |
| 24 | Test-time augmentation | M | P2 | TODO |
| 25 | Provider ecosystem expansion | M | P2 | TODO |

---

## Phase Details

### Phase 1: V2 Project Scaffolding
**Effort:** S | **Priority:** P0 | **Status:** DONE

Create the `code/v2/` directory structure with all sub-packages:
- `v2/__init__.py`
- `v2/models/`, `v2/providers/`, `v2/consensus/`, `v2/fraud/`, `v2/evidence/`, `v2/conversation/`, `v2/confidence/`, `v2/critic/`, `v2/explainability/`, `v2/observability/`, `v2/security/`
- Each sub-package gets `__init__.py`

### Phase 2: VisionProvider ABC
**Effort:** S | **Priority:** P0 | **Status:** DONE

- Define `VisionProvider` abstract base class in `v2/providers/base.py`
- Methods: `_check_availability()`, `analyze()`, `is_available()`
- Error convention: never raise, always return `ObservationReport(all_failed=True)`

### Phase 3: Gemini Provider
**Effort:** M | **Priority:** P0 | **Status:** DONE

- Implement `GeminiProvider` via `google.genai` SDK
- JSON response extraction with regex fallback
- Per-image assessment mapping
- Temperature=0.0 for deterministic output
- Availability check via `GEMINI_API_KEY` env var

### Phase 4: Observation Data Models
**Effort:** S | **Priority:** P0 | **Status:** DONE

- `PerImageAssessment`, `Observation`, `ObservationReport` dataclasses
- All fields with defaults for graceful degradation

### Phase 5: Multi-Model Observation Layer
**Effort:** M | **Priority:** P0 | **Status:** DONE

- `_run_observation()` in `V2Pipeline`
- Iterates all providers, collects observations
- Sets `primary_model` to first successful provider
- Records observation metrics

### Phase 6: Consensus Engine
**Effort:** S | **Priority:** P0 | **Status:** DONE

- `ConsensusEngine.evaluate()` in `v2/consensus/engine.py`
- Agreement score computation
- Model disagreement tracking
- Uncertainty calculation

### Phase 7: Fraud Detection
**Effort:** M | **Priority:** P0 | **Status:** DONE

- `ImageFraudDetector` — SHA-256 dedup, screenshot/phot-of-photo detection
- `MetadataFraudDetector` — EXIF editing, camera mismatch, timestamp analysis
- `BehavioralFraudDetector` — claim frequency, image reuse, escalation patterns

### Phase 8: Evidence Recommender
**Effort:** S | **Priority:** P0 | **Status:** DONE

- `EvidenceRecommender.recommend()` in `v2/evidence/recommender.py`
- Eight recommendation templates
- Keyword-based matching from evidence reason string

### Phase 9: Conversation Analyzer
**Effort:** M | **Priority:** P0 | **Status:** DONE

- `ConversationAnalyzer.analyze()` in `v2/conversation/analyzer.py`
- Negation, uncertainty, retraction, sarcasm, contradiction, changing claims detection
- Regex-based retraction detection
- Risk flag aggregation

### Phase 10: Confidence Calibrator
**Effort:** S | **Priority:** P0 | **Status:** DONE

- `ConfidenceCalibrator.calibrate()` in `v2/confidence/calibrator.py`
- Multi-signal formula: consensus + fraud + evidence + conversation
- Four routing thresholds

### Phase 11: V1 Adapter Layer
**Effort:** M | **Priority:** P0 | **Status:** DONE

- Four adapter classes wrapping V1 components
- `V1RuleAdapter`, `V1SeverityAdapter`, `V1EvidenceAdapter`, `V1ParserAdapter`
- Pure function semantics — no state modification

### Phase 12: Critic
**Effort:** S | **Priority:** P0 | **Status:** DONE

- `V2Critic.review()` in `v2/critic/v2_critic.py`
- Six consistency check categories
- Returns `PASS` or `REVIEW_REQUIRED` with issue codes

### Phase 13: Explainability Tracer
**Effort:** S | **Priority:** P0 | **Status:** DONE

- `DecisionTracer.trace()` in `v2/explainability/tracer.py`
- Structured `DecisionTrace` with why_supported, why_contradicted, evidence_trace, confidence_trace, fraud_trace, decision_trace
- Human-readable justification string assembly

### Phase 14: Observability
**Effort:** S | **Priority:** P0 | **Status:** DONE

- `MetricsCollector` — per-module timing, success/failure recording
- `TraceLogger` — JSON trace persistence to `.v2_traces/`
- `PipelineMetrics` dataclass for structured metric output

### Phase 15: Security Sanitizer
**Effort:** S | **Priority:** P0 | **Status:** DONE

- `InputSanitizer` with static methods
- Claim text injection pattern stripping (regex-based)
- Image path traversal prevention (pathlib resolve check)
- CSV injection prevention (formula char prefixing)
- Filename sanitization (dangerous char removal)

### Phase 16: Pipeline Orchestrator
**Effort:** M | **Priority:** P0 | **Status:** DONE

- `V2Pipeline` class in `v2/pipeline.py`
- All 10 layers wired in sequence
- Config-driven provider initialization
- Per-layer metric recording
- Error isolation per layer

---

## Remaining Phases

### Phase 17: OpenRouter Provider
**Effort:** M | **Priority:** P1 | **Status:** TODO

Implement full `OpenRouterProvider.analyze()` to call OpenRouter API for models like Qwen2.5-VL-72B. Requires `OPENROUTER_API_KEY`, HTTP POST with JSON payload, response parsing matching Gemini's schema.

**Dependencies:** Phase 2 (VisionProvider ABC), Phase 4 (observation models)

### Phase 18: Local VLM Provider
**Effort:** L | **Priority:** P2 | **Status:** TODO

Implement `LocalVLMProvider.analyze()` for Qwen2.5-VL-7B local inference. Requires:
- Model download (7B params, ~14GB RAM)
- Inference server (ollama or transformers)
- Response parsing matching V2 schema
- CPU fallback mode for degraded-but-functional inference

**Dependencies:** Phase 2, Phase 4

### Phase 19: YOLOv8n Object Part Detection
**Effort:** M | **Priority:** P1 | **Status:** TODO

Integrate Ultralytics YOLOv8n for bounding-box-level object part detection:
- `pip install ultralytics`
- Download `yolov8n.pt` (~6MB)
- Fine-tune on dataset images for damage-relevant classes
- Add as preprocessing step before VLM observation
- Pass YOLO detections as additional context in VLM prompts
- Cross-reference YOLO part labels with VLM-reported object_part

**Dependencies:** Phase 5
**Success criteria:** YOLO detects object parts with >70% mAP on held-out images. Object part mismatch detection improves by 15%.

### Phase 20: Production FastAPI Server
**Effort:** L | **Priority:** P1 | **Status:** TODO

Build production API server wrapping V2Pipeline:
- `POST /v2/analyze` — single claim analysis
- `POST /v2/claim` — full pipeline
- `POST /v2/batch` — batch processing
- `GET /v2/health` — health check
- `GET /v2/metrics` — pipeline metrics
- Rate limiting, API key auth, structured error responses
- Async support via `asyncio` or `ThreadPoolExecutor`

**Dependencies:** Phase 16 (pipeline orchestrator)
**Success criteria:** Server starts, handles concurrent requests, returns proper error codes.

### Phase 21: Claim Memory Store
**Effort:** M | **Priority:** P1 | **Status:** TODO

Build in-memory claim history store with optional persistence:
- User claim history tracking across sessions
- Image hash cache for cross-claim deduplication
- Behavioral fraud pre-loading from persistent store
- SQLite-backed persistence optional

**Dependencies:** Phase 7 (behavioral fraud)
**Success criteria:** Behavioral fraud detects image reuse and escalation patterns across API sessions.

### Phase 22: Hidden Test Evaluation
**Effort:** S | **Priority:** P0 | **Status:** TODO

Evaluate V2 pipeline on 100 hidden test claims:
- Run V2Pipeline on `dataset/claims.csv`
- Generate `output_v2.csv`
- Compare against V1 baseline
- Produce category-level accuracy breakdowns

**Dependencies:** Phase 16
**Success criteria:** V2 accuracy > V1 accuracy on all metrics.

### Phase 23: Weighted Consensus Voting
**Effort:** S | **Priority:** P2 | **Status:** TODO

Replace naive agreement ratio with confidence-weighted voting:
- Weight each model assessment by its confidence
- Compute weighted mode for damage_type, object_part
- Confidence-weighted agreement score
- Model-specific confidence calibration curves

**Dependencies:** Phase 6
**Success criteria:** Consensus accuracy improves 5% vs unweighted agreement.

### Phase 24: Test-Time Augmentation
**Effort:** M | **Priority:** P2 | **Status:** TODO

Apply image transformations before observation:
- Brightness/contrast adjustment
- Rotation (±10°)
- Sharpening
- Histogram equalization
- Aggregate per-variant results with mode voting
- Variance-based confidence penalty

**Dependencies:** Phase 5
**Success criteria:** Damage detection recall improves 10% on low-quality images.

### Phase 25: Provider Ecosystem Expansion
**Effort:** M | **Priority:** P2 | **Status:** TODO

Expand the provider abstraction layer to support additional VLM backends:
- **Anthropic Claude Vision** — via Anthropic API for multimodal analysis
- **GPT-4o Vision** — via OpenAI API for damage assessment
- **Custom provider SDK** — documented interface for third-party providers
- **Community provider registry** — contribution template for new providers

**Dependencies:** Phase 2 (VisionProvider ABC)
**Success criteria:** At least 2 new providers implemented following the same `VisionProvider` ABC contract. Provider implementation guide published.
