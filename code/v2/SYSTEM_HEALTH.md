# VerifyIQ System Health

**VerifyIQ is an AI agent framework, not a model.** It performs reasoning, fraud detection, and decision-making using observations from external VLMs that users configure. The table below distinguishes between pipeline components (always available) and VLM-dependent features (require a configured vision provider).

## What Works

| Component | Status | Notes |
|-----------|--------|-------|
| Claim text parsing | ✅ Works | Extracts damage type, object part from conversation text |
| Rule engine (V1) | ✅ Works | Classifies claims when evidence is available |
| Fraud detection (no EXIF) | ✅ Works | Detects missing metadata on images |
| Fraud detection (behavioral) | ✅ Works | Repeated claims, frequency anomalies |
| Conversation analysis | ✅ Works | Detects sarcasm, retractions, uncertainty |
| Prompt injection protection | ✅ Works | Sanitizer blocks known patterns |
| Path traversal protection | ✅ Works | Prevents directory escape |
| CSV injection protection | ✅ Works | Sanitizes formula prefixes |
| API platform | ✅ Works | 9 FastAPI endpoints |
| Metrics & monitoring | ✅ Works | Latency tracking, health checks |
| Persistence (SQLite) | ✅ Works | Claims, decisions, fraud events stored |
| Review queue | ✅ Works | Human-in-the-loop review management |
| Batch processing | ✅ Works | Multi-threaded with error isolation |
| Rate limiting | ✅ Works | Sliding window + exponential backoff |
| Docker deployment | ✅ Works | Multi-stage build, healthcheck |

## What Does Not Work (Without VLM)

| Component | Status | Notes |
|-----------|--------|-------|
| Image analysis (VLM) | ❌ Fails | Requires Gemini, OpenRouter, or Local VLM |
| Damage visibility detection | ❌ Fails | No VLM = no image analysis = can't see damage |
| Evidence standard evaluation | ❌ Fails | Can't verify images match claimed damage |
| Supported/Contradicted decisions | ❌ Fails | Cannot make visual determinations |
| Confidence calibration | ❌ Fails | Defaults to floor value (0.07–0.20) |

## Degraded Modes

### Demo Mode (`VERIFYIQ_MODE=demo`)

Accepts all claims without vision analysis. Returns text-only parsing results. All decisions will be `not_enough_information` with `vision_unavailable` flag. Justification clearly states: *"Image analysis temporarily unavailable."* No misleading messages.

**Use case**: Frontend development, UI testing, demonstration of non-vision features.

### Research Mode (`VERIFYIQ_MODE=research`)

Same as demo, but every claim also gets `manual_review_required`. Intended for studying system behavior without vision.

**Use case**: Academic research, pipeline analysis, benchmarking text-only features.

### Production Mode (`VERIFYIQ_MODE=production` — default)

**Refuses startup** if no vision provider is reachable. Fails with a clear error message. Never silently degrades.

**Use case**: Real deployment where claim verification must be accurate.

## State Transitions

```
Startup
  ├── Provider check passes → AVAILABLE
  │     └── Normal operation
  ├── Primary fails, fallback works → DEGRADED
  │     └── Continues with warning
  └── All providers fail → UNAVAILABLE
        ├── production mode → REJECT STARTUP
        ├── demo mode → Accept, flag "vision_unavailable"
        └── research mode → Accept, flag both flags
```

During operation, each provider has a circuit breaker:
- 3 consecutive failures → circuit opens for 60s
- After cooldown → circuit closes automatically
- Failed calls do not crash the pipeline

## False Confidence Prevention

Before this build, the system would silently produce `not_enough_information` with the misleading justification *"No images were submitted"* even when images were provided. All 16 risk categories would uniformly flag `evidence_insufficient` and `manual_review_required`, giving reviewers no useful signal.

Now:
- **No silent degradation.** System state is checked at startup and before every claim.
- **No misleading explanations.** *"Image analysis temporarily unavailable"* replaces *"No images were submitted"* when VLM is unreachable.
- **No false confidence.** Confidence remains at floor value (0.07–0.20) and is explicitly tagged with `vision_unavailable`.
- **Clear failure mode.** Production mode refuses startup. Demo/research modes clearly label all output as vision-free.
