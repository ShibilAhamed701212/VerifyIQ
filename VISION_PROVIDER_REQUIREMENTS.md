# VerifyIQ — Vision Provider Requirements

**VerifyIQ is an AI agent framework — it does not contain a built-in VLM.** All vision observations come from external Vision Language Models (VLMs) that you configure. This document explains how to set up and manage vision providers.

---

## No Bundled VLM

VerifyIQ does not ship with, embed, or bundle any VLM. You must provide your own vision provider:

- **Gemini** (Google) — recommended primary provider
- **OpenRouter** — multi-model API access
- **Local VLM** — offline inference (Qwen2.5-VL-7B or compatible)

Without a configured provider, VerifyIQ runs in **degraded mode**:
- All decisions return `not_enough_information`
- The `vision_unavailable` risk flag is set
- Confidence drops to floor value (0.07–0.20)

---

## Supported Providers

### 1. Gemini (Recommended Primary)

| Attribute | Value |
|-----------|-------|
| Provider ID | `gemini` |
| Model | `gemini-2.0-flash` |
| API Key | `GEMINI_API_KEY` |
| SDK | `google.genai` |
| Status | Fully implemented |
| Latency | ~2–4s per image |

**Setup:**

```bash
export GEMINI_API_KEY="your-api-key-here"
```

VerifyIQ reads `GEMINI_API_KEY` at startup. If the key is missing or invalid, the Gemini provider reports as unavailable and the pipeline falls through to the next provider in the priority chain.

**Availability check:**
- Checks that `GEMINI_API_KEY` is set and non-empty
- Performs a lightweight API ping (not a full inference call)
- Returns `available: true/false`

### 2. OpenRouter

| Attribute | Value |
|-----------|-------|
| Provider ID | `openrouter` |
| Models | `qwen/qwen2.5-vl-72b-instruct`, `google/gemini-2.0-flash-001`, etc. |
| API Key | `OPENROUTER_API_KEY` |
| Protocol | HTTP POST with JSON payload |
| Status | **Stub** — implementation planned (Phase 17) |

**Setup:**

```bash
export OPENROUTER_API_KEY="your-api-key-here"
export OPENROUTER_MODEL="qwen/qwen2.5-vl-72b-instruct"
```

**When implemented:** OpenRouter will provide access to multiple VLM backends through a single API, enabling cost/accuracy tradeoffs and geographic redundancy.

### 3. Local VLM (Offline)

| Attribute | Value |
|-----------|-------|
| Provider ID | `local_vlm` |
| Model | `qwen2.5-vl:7b` (via ollama) or compatible |
| RAM | ~14GB for Qwen2.5-VL-7B |
| Status | **Stub** — implementation planned (Phase 18) |

**Setup (via ollama):**

```bash
# Install ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the VLM model
ollama pull qwen2.5-vl:7b

# Test inference
ollama run qwen2.5-vl:7b
```

**Hardware requirements:**
- GPU recommended (NVIDIA with 8GB+ VRAM)
- CPU fallback available (degraded mode, ~30s per image)
- 14GB+ system RAM

---

## Fallback Modes

VerifyIQ supports three operating modes controlled by the `VERIFYIQ_MODE` environment variable:

### Production Mode (`production` — default)

**VLM required to start.** The system refuses startup if no vision provider is reachable.

```bash
export VERIFYIQ_MODE=production
```

Behavior:
- All providers checked at startup
- If all unavailable → startup fails with clear error message
- During operation, provider failures trigger circuit breakers
- Never silently degrades — either accurate or failing loudly

### Demo Mode (`demo`)

**No VLM required.** Accepts all claims without vision analysis. Useful for frontend development, UI testing, and demonstrating non-vision features.

```bash
export VERIFYIQ_MODE=demo
```

Behavior:
- Accepts all claims without vision analysis
- Returns text-only parsing results
- All decisions: `not_enough_information`
- Risk flag: `vision_unavailable` set on every claim
- Justification states: *"Image analysis temporarily unavailable."*
- No misleading messages — never claims images were submitted when they weren't

### Research Mode (`research`)

**No VLM required.** Same as demo mode, but every claim also gets `manual_review_required`.

```bash
export VERIFYIQ_MODE=research
```

Behavior:
- Same degraded output as demo mode
- Additionally sets `manual_review_required` on every claim
- Intended for academic study of system behavior without vision
- Benchmarking text-only features

---

## Production Mode Requirements

For production deployment, you need:

1. **At least one operational VLM** (Gemini recommended)
2. **API key** set via environment variable
3. **Network access** to the provider's API endpoint
4. **Rate limit awareness** — see throughput limits below

| Provider | Typical Limit | Mitigation |
|----------|---------------|------------|
| Gemini | 60 req/min (free), 1000+ (paid) | Batching, caching |
| OpenRouter | Varies by model | Multi-model routing |
| Local VLM | Hardware-bound | Load balancing |

---

## Provider Priority Chain

When multiple providers are configured, the pipeline uses this priority order:

```
Gemini → OpenRouter → Local VLM
```

**How it works:**
1. Pipeline starts with the highest-priority provider (Gemini)
2. If that provider fails (unavailable, error, circuit open), it moves to the next
3. All available providers are queried in parallel for multi-model observation
4. Results are merged in the Consensus layer

---

## Circuit Breaker Behavior

Each provider has an independent circuit breaker:

| Parameter | Default | Description |
|-----------|---------|-------------|
| Failure threshold | 3 | Consecutive failures before circuit opens |
| Cooldown period | 60s | Time before automatic retry |
| State | `CLOSED` | Normal operation — requests pass through |
| State | `OPEN` | Failure threshold exceeded — requests blocked |
| State | `HALF_OPEN` | Cooldown expired — one test request allowed |

**Behavior:**
- Circuit opens after 3 consecutive provider failures
- During open circuit, the provider is skipped (not called)
- After 60s cooldown, circuit transitions to HALF_OPEN
- One test request is allowed — success closes the circuit, failure reopens it
- Circuit state is logged via MetricsCollector for observability
- Failed calls never crash the pipeline

---

## Example Docker Compose

```yaml
version: "3.8"

services:
  verifyiq:
    build: .
    ports:
      - "8000:8000"
    environment:
      - VERIFYIQ_MODE=production
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - OPENROUTER_MODEL=qwen/qwen2.5-vl-72b-instruct
    volumes:
      - ./dataset:/app/dataset
      - ./output:/app/output
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/v2/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Optional: local VLM inference server
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  ollama_data:
```

With the ollama sidecar, you can enable the local VLM provider by adding:

```yaml
    environment:
      - LOCAL_VLM_URL=http://ollama:11434
      - LOCAL_VLM_MODEL=qwen2.5-vl:7b
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Set Gemini key | `export GEMINI_API_KEY="sk-..."` |
| Set OpenRouter key | `export OPENROUTER_API_KEY="sk-..."` |
| Run in production | `export VERIFYIQ_MODE=production` |
| Run in demo | `export VERIFYIQ_MODE=demo` |
| Run in research | `export VERIFYIQ_MODE=research` |
| Check provider health | `GET /v2/health` |
| Launch with ollama | `ollama pull qwen2.5-vl:7b && ollama serve` |
| Test without VLM | `VERIFYIQ_MODE=demo python code/main.py` |
