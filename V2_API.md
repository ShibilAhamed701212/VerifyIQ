# VerifyIQ V2 — API Design Document

> **Status: Design only. Not implemented.**
>
> These endpoints are planned for Phase 20 (Production FastAPI Server).
> V2 currently operates via the `V2Pipeline.process()` Python method only.

**VerifyIQ is an AI agent framework — it does not contain a built-in VLM.** All vision observations come from external providers (Gemini, OpenRouter, Local VLM) configured by the user. The API reflects provider availability and health state in every response.

## Provider States

Each vision provider can be in one of these states:

| State | Meaning |
|-------|---------|
| `available` | Provider is reachable and responding |
| `unavailable` | Provider cannot be reached (API key missing, network error, rate limited) |
| `circuit_open` | Circuit breaker open after repeated failures; auto-recovers after cooldown |
| `degraded` | Provider responds but with reduced capability (e.g., local VLM on CPU) |

## Operating Modes

The system operates in one of three modes, controlled by `VERIFYIQ_MODE`:

| Mode | VLM Required? | Behavior When VLM Unavailable |
|------|---------------|-------------------------------|
| `production` (default) | Yes | Refuses startup. Never silently degrades. |
| `demo` | No | Accepts claims without vision; flags `vision_unavailable`; all decisions `not_enough_information` |
| `research` | No | Same as demo + every claim gets `manual_review_required` |

When a VLM is unavailable during operation, the pipeline sets the `vision_unavailable` risk flag on the decision output and confidence drops to floor value (0.07–0.20).

## Base URL

```
https://api.verifyiq.io/v2
```

## Authentication

API key via `X-API-Key` header. (Not yet implemented — no auth layer exists in V2.)

## Endpoints

---

### `POST /v2/analyze`

Analyze images for a single claim. Returns per-image assessments from all available vision providers.

**Request:**

```json
{
  "claim_text": "My car has a dent on the front bumper",
  "claim_object": "car",
  "image_paths": [
    "/images/bumper_1.jpg",
    "/images/bumper_2.jpg"
  ],
  "user_id": "user_042",
  "providers": ["gemini"]
}
```

**Response (200):**

```json
{
  "claim_id": "clm_20260620_abc123",
  "primary_model": "gemini-2.0-flash",
  "observations": [
    {
      "model_name": "gemini-2.0-flash",
      "provider": "gemini",
      "success": true,
      "assessments": [
        {
          "image_path": "/images/bumper_1.jpg",
          "damage_visible": true,
          "damage_type": "dent",
          "object_part": "bumper",
          "confidence": 0.92,
          "is_clear": true,
          "angle_sufficient": true,
          "lighting_adequate": true
        }
      ],
      "latency_ms": 2340.5
    }
  ],
  "all_failed": false
}
```

**Error (400):**

```json
{
  "error": "invalid_request",
  "message": "At least one image_path is required",
  "code": "MISSING_IMAGE_PATHS"
}
```

**Rate limit (429):**

```json
{
  "error": "rate_limited",
  "message": "Rate limit exceeded. Try again in 30 seconds.",
  "retry_after_seconds": 30,
  "code": "RATE_LIMITED"
}
```

---

### `POST /v2/claim`

Full claim verification pipeline. Runs all 10 layers and returns the final decision.

**Request:**

```json
{
  "claim_text": "Customer: I noticed a crack on my laptop screen\nSupport: Can you upload photos?\nCustomer: Yes, here they are",
  "claim_object": "laptop",
  "image_paths": [
    "/images/screen_1.jpg",
    "/images/screen_2.jpg"
  ],
  "user_id": "user_042",
  "evidence_requirements": [
    {
      "object_type": "laptop",
      "applies_to": "screen",
      "requirement_text": "Clear photo showing the full screen with the damage visible"
    }
  ],
  "options": {
    "providers": ["gemini", "openrouter"],
    "fraud_detection": true,
    "conversation_analysis": true,
    "include_trace": true
  }
}
```

**Response (200):**

```json
{
  "claim_id": "clm_20260620_def456",
  "claim_status": "supported",
  "issue_type": "crack",
  "object_part": "screen",
  "severity": "medium",
  "confidence": 0.87,
  "routing": "fast_review",
  "evidence_standard_met": true,
  "supporting_image_ids": ["screen_1.jpg"],
  "risk_flags": [],
  "justification": "Supported because: Damage type 'crack' observed in images; Object part 'screen' matches claimed part; No significant fraud signals detected; Model agreement: 100% | Confidence: 0.87 (fast_review)",
  "trace": {
    "why_supported": [
      "Damage type 'crack' observed in images",
      "Object part 'screen' matches claimed part",
      "No significant fraud signals detected",
      "Model agreement: 100%"
    ],
    "why_contradicted": [],
    "evidence_trace": [
      "Models consulted: 1",
      "Models succeeded: 1",
      "Evidence standard met: True"
    ],
    "confidence_trace": [
      "Model confidence: 0.85",
      "Agreement boost: 0.15",
      "Fraud penalty: 0.0",
      "Evidence adjustment: 0.1",
      "Routing: fast_review"
    ],
    "fraud_trace": [
      "No fraud flags raised"
    ],
    "decision_trace": [
      "Final status: supported",
      "Final confidence: 0.87",
      "Routing: fast_review"
    ]
  },
  "metrics": {
    "total_latency_ms": 4521.3,
    "module_timings": [
      {"module": "observation", "latency_ms": 2340.5, "success": true},
      {"module": "consensus", "latency_ms": 0.3, "success": true},
      {"module": "fraud", "latency_ms": 120.1, "success": true},
      {"module": "evidence", "latency_ms": 1.2, "success": true},
      {"module": "conversation", "latency_ms": 0.8, "success": true},
      {"module": "confidence", "latency_ms": 0.2, "success": true},
      {"module": "v1_rule_adapter", "latency_ms": 0.5, "success": true}
    ]
  }
}
```

**Error (502):**

```json
{
  "error": "pipeline_error",
  "message": "All vision providers failed",
  "code": "ALL_PROVIDERS_FAILED",
  "partial_result": null
}
```

**Degraded response (200 with vision_unavailable flag):**

When operating in demo or research mode with no VLM available, the claim endpoint returns a partial decision:

```json
{
  "claim_id": "clm_20260620_def789",
  "claim_status": "not_enough_information",
  "confidence": 0.07,
  "routing": "manual_review",
  "evidence_standard_met": false,
  "risk_flags": ["vision_unavailable"],
  "justification": "Image analysis temporarily unavailable. All decisions are text-only. Vision provider (VLM) is not reachable.",
  "metrics": {
    "total_latency_ms": 15.2,
    "module_timings": [
      {"module": "observation", "latency_ms": 0.0, "success": false},
      {"module": "consensus", "latency_ms": 0.1, "success": true},
      {"module": "fraud", "latency_ms": 5.2, "success": true},
      {"module": "evidence", "latency_ms": 0.3, "success": false},
      {"module": "conversation", "latency_ms": 0.5, "success": true},
      {"module": "confidence", "latency_ms": 0.1, "success": true}
    ],
    "note": "Observation layer skipped — no vision provider available"
  }
}
```

---

### `POST /v2/batch`

Batch processing of multiple claims. Accepts an array of claim requests.

**Request:**

```json
{
  "claims": [
    {
      "claim_id": "claim_01",
      "claim_text": "Customer: My package arrived torn",
      "claim_object": "package",
      "image_paths": ["/images/pkg_1.jpg"],
      "user_id": "user_001"
    },
    {
      "claim_id": "claim_02",
      "claim_text": "Customer: There is a dent on my car door",
      "claim_object": "car",
      "image_paths": ["/images/car_1.jpg"],
      "user_id": "user_002"
    }
  ],
  "parallel": true
}
```

**Response (200):**

```json
{
  "batch_id": "batch_20260620_ghi789",
  "total_claims": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "claim_id": "claim_01",
      "status": 200,
      "decision": { "...claim_status etc..." }
    },
    {
      "claim_id": "claim_02",
      "status": 200,
      "decision": { "...claim_status etc..." }
    }
  ],
  "aggregate_metrics": {
    "total_latency_ms": 6540.2,
    "avg_latency_per_claim_ms": 3270.1
  }
}
```

**Error (partial failure - 200 with errors):**

```json
{
  "batch_id": "batch_20260620_ghi789",
  "total_claims": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    { "claim_id": "claim_01", "status": 200, "decision": { "..." } },
    { "claim_id": "claim_02", "status": 200, "decision": { "..." } },
    { "claim_id": "claim_03", "status": 502, "error": "ALL_PROVIDERS_FAILED" }
  ]
}
```

---

### `GET /v2/health`

System health check. Returns provider availability and pipeline status.

**Response (200):**

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "providers": {
    "gemini": {"available": true, "model": "gemini-2.0-flash"},
    "openrouter": {"available": false, "model": "qwen/qwen2.5-vl-72b-instruct"},
    "local_vlm": {"available": true, "model": "qwen2.5-vl-7b"}
  },
  "pipeline_ready": true,
  "uptime_seconds": 86400,
  "last_error": null
}
```

**Degraded (200):**

```json
{
  "status": "degraded",
  "version": "2.0.0",
  "providers": {
    "gemini": {"available": false, "model": "gemini-2.0-flash"},
    "openrouter": {"available": false},
    "local_vlm": {"available": true, "model": "qwen2.5-vl-7b"}
  },
  "pipeline_ready": true,
  "warnings": ["No API-based providers available. Using local VLM only."]
}
```

---

### `GET /v2/metrics`

Pipeline performance metrics since last reset.

**Response (200):**

```json
{
  "total_claims_processed": 150,
  "total_latency_ms": 675000.0,
  "avg_latency_per_claim_ms": 4500.0,
  "module_breakdown_ms": {
    "observation": {"total": 351000.0, "avg": 2340.0, "failures": 3},
    "consensus": {"total": 45.0, "avg": 0.3, "failures": 0},
    "fraud": {"total": 18000.0, "avg": 120.0, "failures": 0},
    "evidence": {"total": 180.0, "avg": 1.2, "failures": 0},
    "conversation": {"total": 120.0, "avg": 0.8, "failures": 0},
    "confidence": {"total": 30.0, "avg": 0.2, "failures": 0},
    "v1_rule_adapter": {"total": 75.0, "avg": 0.5, "failures": 0}
  },
  "model_failures": [
    "observation: all_providers_failed"
  ],
  "fraud_detections": 12,
  "routing_distribution": {
    "auto": 45,
    "fast_review": 60,
    "manual_review": 30,
    "evidence_request": 15
  },
  "cache_hits": 89,
  "cache_misses": 61
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `MISSING_IMAGE_PATHS` | 400 | No image paths provided |
| `INVALID_CLAIM_TEXT` | 400 | Claim text empty or malformed |
| `INVALID_CLAIM_OBJECT` | 400 | Unrecognized claim object type |
| `TOO_MANY_IMAGES` | 400 | More than 10 images per claim |
| `IMAGE_TOO_LARGE` | 400 | Image exceeds 10MB limit |
| `UNSUPPORTED_IMAGE_FORMAT` | 400 | Image format not in allowed list |
| `PATH_TRAVERSAL_DETECTED` | 400 | Image path attempts directory escape |
| `RATE_LIMITED` | 429 | Too many requests |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `ALL_PROVIDERS_FAILED` | 502 | No vision provider returned results (production mode only; demo/research modes return degraded 200 with `vision_unavailable`) |
| `PIPELINE_ERROR` | 500 | Internal pipeline failure |
| `BATCH_TOO_LARGE` | 400 | More than 100 claims in batch |

## Rate Limiting

| Tier | Limit | Window |
|------|-------|--------|
| Free | 10 requests/min | 1 minute |
| Pro | 100 requests/min | 1 minute |
| Enterprise | 1000 requests/min | 1 minute |

Rate limit headers included in all responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

> Note: Rate limiting is not yet implemented. Current V2 has no API layer.
