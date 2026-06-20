# VerifyIQ V2 — 10-Layer Pipeline Architecture

**VerifyIQ is a production-oriented AI agent framework for multimodal claim verification.** It performs reasoning, risk analysis, fraud detection, and decision-making using observations supplied by external vision providers (VLMs). Users configure their own VLM. The VLM is only the observation layer — all reasoning, consensus, fraud detection, confidence calibration, and decisions happen in VerifyIQ's deterministic pipeline layers.

## High-Level Architecture

```
                                   ┌──────────────────────┐
                                   │   Input (Claim +     │
                                   │   Images + User ID)  │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 0: Security   │
                                   │  Sanitizer           │
                                   │  (prompt injection,  │
                                   │   path traversal,    │
                                   │   CSV injection)     │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 1: Observation│
                                   │  (Multi-model VLM)   │
                                   │                      │
                                   │  ┌────┐ ┌────┐ ┌───┐ │
                                   │  │Gemi│ │O.R.│ │Loc│ │
                                   │  │nini│ │outer│ │VLM│ │
                                   │  └────┘ └────┘ └───┘ │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 2: Consensus   │
                                   │  Scoring & Agreement │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 3: Fraud       │
                                   │  ┌──────┐ ┌─────┐   │
                                   │  │Image │ │Meta │   │
                                   │  │Fraud │ │Fraud│   │
                                   │  └──┬───┘ └──┬──┘   │
                                   │  ┌──────┐    │      │
                                   │  │Behav.│◄───┘      │
                                   │  │Fraud │           │
                                   │  └──────┘           │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 4: Evidence    │
                                   │  Recommendation      │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 5: Conversation │
                                   │  Analysis             │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 6: Confidence  │
                                   │  Calibration          │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 7: V1 Rule     │
                                   │  Adapter              │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 8: Critic      │
                                   │  Consistency Checks  │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 9: Decision    │
                                   │  Assembly             │
                                   └──────────┬───────────┘
                                              │
                                   ┌──────────▼───────────┐
                                   │  Layer 10: Explain-   │
                                   │  ability & Output     │
                                   └──────────────────────┘
```

## Design Principles

1. **V1 is frozen.** V2 exists entirely under `code/v2/`. The only bridge is `V1RuleAdapter`, `V1SeverityAdapter`, `V1EvidenceAdapter`, and `V1ParserAdapter` — each wrapping a V1 component as a pure function. No V1 file is imported or modified by V2 outside these adapters.

2. **Independent failure domains.** Every layer is wrapped in its own try/except. A crash in any layer produces degraded-but-valid output. No layer crash propagates.

3. **Multi-model observation.** V2 supports multiple vision providers (Gemini, OpenRouter, local VLM) through a common `VisionProvider` ABC. Each provider is queried independently; results are merged in the Consensus layer.

4. **Observability by default.** Every layer records latency, success/failure state, and error context to a `MetricsCollector`. The `DecisionTracer` produces structured trace data for every decision.

---

## Layer Details

### Layer 0: Security Sanitizer

**File:** `code/v2/security/sanitizer.py`

**Purpose:** Sanitize all inputs before any pipeline processing.

**Rationale:** Prompt injection is the primary threat to VLM-based systems. User claim text is interpolated into model prompts — without sanitization, a malicious user could inject `ignore previous instructions` and bypass the system prompt entirely.

**Implementation:**
- `sanitize_claim_text()`: Strips known injection patterns (ignore/forget instructions, system prompt overrides) via regex and enforces a 1000-character hard length limit. Wraps claim text with instruction boundaries.
- `sanitize_image_path()`: Resolves paths against a base directory to prevent `../../etc/passwd` traversal.
- `sanitize_csv_field()`: Prefixes formula-starting characters (=, +, -, @, |) with a leading quote to prevent CSV injection.
- `sanitize_filename()`: Removes dangerous characters (`<>:"/\|?*` and control characters) from filenames.

### Layer 1: Observation (Multi-Model)

**Files:**
- `code/v2/providers/base.py` — VisionProvider ABC
- `code/v2/providers/gemini_provider.py` — Gemini provider
- `code/v2/providers/openrouter_provider.py` — OpenRouter provider (stub)
- `code/v2/providers/local_vlm_provider.py` — Local VLM provider (stub)
- `code/v2/models/observation.py` — Observation data models

**Purpose:** Query one or more external vision providers (VLMs) for per-image assessments of damage type, object part, image quality, and confidence. This is the only layer that contacts a VLM — all subsequent layers are pure reasoning.

**Provider Abstraction:**

```
VisionProvider (ABC)
├── GeminiProvider        — google.genai, requires GEMINI_API_KEY
├── OpenRouterProvider    — OpenRouter API, requires OPENROUTER_API_KEY (stub)
└── LocalVLMProvider      — Local inference (stub, for Qwen2.5-VL-7B)
```

Each provider:
- Checks availability independently (`_check_availability`)
- Returns `ObservationReport` with `all_failed=True` on any error — never raises
- Reports per-image assessments via `PerImageAssessment` dataclass

**Multi-model design:** The pipeline iterates all registered providers, calling each in sequence. A provider failure is caught silently — remaining providers still execute. The `primary_model` is set to the first model that succeeds.

**PerImageAssessment fields:**
- `damage_visible`, `damage_type`, `object_part`
- `confidence` (model's self-reported confidence)
- `is_clear`, `angle_sufficient`, `lighting_adequate` (image quality signals)
- `issues`, `error` (degradation tracking)

**Rationale for multi-model:**
- Eliminates single-VLM blind spots (different models catch different damage types)
- Graceful degradation when one API is down
- Enables consensus scoring in Layer 2
- Supports cost/accuracy tradeoffs (fast Gemini + slow but accurate OpenRouter)
- Decouples observation from reasoning — providers can be swapped without changing pipeline logic

### Layer 2: Consensus

**File:** `code/v2/consensus/engine.py`

**Purpose:** Compare outputs from multiple models and produce an agreement score, overall confidence, and uncertainty metric.

**Consensus scoring methodology:**

1. If 0 models succeeded → `agreement_score=0.0`, `confidence=0.0`, `uncertainty=1.0`
2. If 1 model succeeded → `agreement_score=1.0`, confidence = mean of that model's per-image assessments. Effectively single-model mode.
3. If 2+ models succeeded:
   - Compare `damage_type` and `object_part` across models per image
   - Record `ModelDisagreement` entries for each conflicting field
   - `agreement_score = total_agreements / total_checks`
   - `uncertainty = 1.0 - agreement_score`
   - `confidence = mean of all assessment confidences`

**Rationale:** Simple agreement ratio provides an interpretable, deterministic signal. Weighted voting (by model confidence) was considered but rejected for V2 initial release — naive agreement is more transparent and easier to debug.

### Layer 3: Fraud Detection

**Files:**
- `code/v2/fraud/image_fraud.py` — ImageFraudDetector
- `code/v2/fraud/metadata_fraud.py` — MetadataFraudDetector
- `code/v2/fraud/behavioral_fraud.py` — BehavioralFraudDetector
- `code/v2/models/fraud.py` — Fraud data models

**Purpose:** Detect fraudulent claims through three independent detection modules.

**Image Fraud:**
- SHA-256 hash comparison for exact duplicate detection
- Aspect-ratio + edge-band analysis for screenshot detection
- Edge-filter analysis for photo-of-photo detection
- Weighted scoring: 0.4 for duplicates, 0.3 for screenshot, 0.3 for photo-of-photo

**Metadata Fraud:**
- EXIF parsing via Pillow for editing software, camera model, timestamps
- Flags: `edited_image` (0.3 weight), `timestamp_mismatch` (0.3), `camera_mismatch` (0.2), `no_exif` (0.1)

**Behavioral Fraud:**
- Tracks claim history per user (loaded from CSV)
- Detects: repeated claims (>3 → 0.3 weight), image reuse (0.4 weight), severity escalation pattern (0.2 weight)
- Severity escalation: compares current damage type against historical claims using a severity order scale

**Aggregation:** `overall_fraud_score = max(image, metadata, behavioral scores)`. This is conservative — the highest signal wins. `high_risk` is set when overall > 0.5.

**Rationale:** Three independent detectors provide defense in depth. Image fraud catches tampering, metadata fraud catches digital editing, behavioral fraud catches systematic abuse patterns. The max-aggregation ensures the strongest signal is never diluted.

### Layer 4: Evidence Recommendation

**File:** `code/v2/evidence/recommender.py`

**Purpose:** When the evidence standard is not met, recommend specific missing evidence types to the user.

**Implementation:** Maps keywords from the evidence reason string (e.g., "blurry", "angle", "light") to structured `EvidenceRecommendation` objects with priority levels. Eight recommendation templates cover clear image, angle, close-up, side view, interior view, sharpness, lighting, and low confidence.

**Rationale:** Provides actionable feedback rather than a generic "evidence insufficient" flag. This mirrors real insurance claims workflows where adjusters request specific additional images.

### Layer 5: Conversation Analysis

**File:** `code/v2/conversation/analyzer.py`

**Purpose:** Analyze claim text for linguistic signals of fraudulent or unreliable claims.

**Detection methods:**
- **Negation:** Keyword matching against a curated set of negation words
- **Uncertainty:** Matching against uncertainty markers ("maybe", "perhaps", "not sure")
- **Retraction:** Regex patterns for claim retraction language ("actually no", "on second thought", "correction")
- **Sarcasm:** Overly positive language in a damage context ("great", "fantastic", "wonderful")
- **Contradiction:** Damage type claimed then negated ("dent" then "no dent")
- **Changing claims:** Multiple damage types mentioned in the conversation

**Risk flags:** `claim_retraction`, `conversation_conflict`, `uncertain_claim`, `possible_sarcasm`

**Rationale:** Claim text is a rich signal for fraud detection. Retractions are high-severity flags. Contradictions suggest unreliable reporting. These signals feed into confidence calibration and critic consistency checks.

### Layer 6: Confidence Calibration

**File:** `code/v2/confidence/calibrator.py`

**Purpose:** Combine multiple pipeline signals into a single calibrated confidence score.

**Confidence formula:**

```
final = base + agreement_boost - fraud_penalty + evidence_boost - conv_penalty
```

Where:
- `base` = model confidence (or 0.3 fallback if 0)
- `agreement_boost` = agreement_score * 0.15
- `fraud_penalty` = overall_fraud_score * 0.3
- `evidence_boost` = 0.1 if met, -0.1 if not
- `conv_penalty` = 0.2 (retraction) + 0.15 (contradiction) + 0.1 (uncertainty)

**Routing thresholds:**
- > 0.90 → `auto`
- 0.75-0.90 → `fast_review`
- 0.50-0.75 → `manual_review`
- < 0.50 → `evidence_request`

**Rationale:** The formula weights fraud penalty higher (0.3x) than agreement boost (0.15x) — fraud signals are treated as more informative than model agreement. Evidence standard met provides an asymmetric boost (0.1 vs -0.1), incentivizing sufficient evidence. The routing thresholds align with industry claim handling workflows.

### Layer 7: V1 Rule Adapter

**File:** `code/v2/v1_adapter.py`

**Purpose:** Bridge between V2's multi-model pipeline and V1's deterministic rule engine, severity engine, evidence checker, and claim parser.

**Adapter pattern:**

```
V2 Pipeline                    V1 (frozen)
    │                              │
    ├── V1RuleAdapter ─────────► RuleEngine
    ├── V1SeverityAdapter ─────► SeverityEngine
    ├── V1EvidenceAdapter ─────► EvidenceChecker
    └── V1ParserAdapter ───────► ClaimParser
```

Each adapter:
- Wraps a V1 component as a pure function
- Is the ONLY code that imports V1 modules
- Exception-handles V1 calls to prevent V1 failures from crashing V2
- Passes V2 data structures converted to V1-compatible dicts

**Rationale:** V1's rule engine, severity engine, and evidence checker are mature, deterministic, and tested. Rewriting them for V2 would duplicate effort and risk regression. The adapter pattern allows V2 to benefit from V1's strengths while adding multi-model observation, fraud detection, consensus, and critic layers around it.

### Layer 8: Critic

**File:** `code/v2/critic/v2_critic.py`

**Purpose:** Post-processing consistency checks on the assembled decision.

**Checks performed:**
- Status consistency: `supported` cannot have `unknown` issue type or unmet evidence standard
- Fraud consistency: high fraud score with `supported` verdict is contradictory
- Conversation consistency: retracted/contradictory claim with `supported` verdict
- Consensus consistency: low agreement with definitive verdict, all models failed without risk flags
- Severity consistency: high severity with low confidence

**Output:** `"PASS"` or `"REVIEW_REQUIRED"` with a list of issue codes.

**Rationale:** The critic catches edge cases that individual pipeline layers cannot detect. A claim may pass each layer independently but produce an inconsistent final decision. The critic is the last line of defense before output.

### Layer 9: Decision Assembly

**File:** `code/v2/pipeline.py` (`_assemble_decision`)

**Purpose:** Combine all layer outputs into the final `V2Decision` dataclass.

**Assembly logic:**
1. Overwrite confidence with calibrated value
2. Merge risk flags from fraud and conversation layers
3. Add `manual_review_required` for high fraud or zero successful models
4. Run DecisionTracer for explainability trace
5. If critic returned `REVIEW_REQUIRED`, add `manual_review_required` and append critic issues to justification

### Layer 10: Explainability

**Files:**
- `code/v2/explainability/tracer.py` — DecisionTracer
- `code/v2/observability/tracing.py` — TraceLogger (persistence)
- `code/v2/observability/metrics.py` — MetricsCollector

**Purpose:** Produce structured, human-readable explanations for every decision.

**DecisionTrace fields:**
- `why_supported`: List of reasons when claim is supported
- `why_contradicted`: List of reasons when claim is contradicted
- `evidence_trace`: Models consulted, evidence standard status, missing evidence
- `confidence_trace`: Breakdown of confidence components
- `fraud_trace`: Fraud flags raised
- `decision_trace`: Final status, confidence, routing

**Rationale:** Explainability is not optional for insurance claim systems. Every decision must be auditable. The trace is persisted via TraceLogger to `.v2_traces/` for offline review.

## Data Flow Summary

```
claim_text, image_paths, user_id
    │
    ▼
Sanitizer (Layer 0)
    │
    ▼
Observation (Layer 1) ──► PerImageAssessment[]
    │
    ▼
Consensus (Layer 2) ──► agreement_score, confidence, uncertainty
    │
    ├──► ImageFraud (Layer 3) ──► duplicate/screenshot detection
    ├──► MetadataFraud (Layer 3) ──► EXIF analysis
    └──► BehavioralFraud (Layer 3) ──► claim history analysis
    │
    ▼
Evidence Recommender (Layer 4) ──► missing evidence suggestions
    │
    ▼
Conversation Analyzer (Layer 5) ──► retraction/contradiction detection
    │
    ▼
Confidence Calibrator (Layer 6) ──► final_confidence, routing
    │
    ▼
V1 Adapter (Layer 7) ──► V1 RuleEngine → claim_status
    │
    ▼
Critic (Layer 8) ──► consistency checks → PASS/REVIEW_REQUIRED
    │
    ▼
Decision Assembly (Layer 9) ──► V2Decision
    │
    ▼
DecisionTracer (Layer 10) ──► structured justification + trace
```

## Error Boundaries

| Layer | Fallback | Graceful Degradation |
|-------|----------|---------------------|
| All providers fail | `ObservationReport(all_failed=True)` | Empty observations |
| Consensus | `agreement_score=0, uncertainty=1.0` | Single-model fallback |
| Fraud | `FraudReport()` with zero scores | No fraud signals |
| Evidence | `evidence_standard_met=False` | No recommendations |
| Conversation | `ConversationReport()` with no flags | No conversation signals |
| V1 Adapter | `claim_status="not_enough_information"` | Graceful V1 failure |
| Critic | Issues returned as strings, not exceptions | Continues with uncriticized output |
| DecisionTracer | Empty trace, basic justification | Degraded explainability |
