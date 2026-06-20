# VerifyIQ V2 — Implementation Plan for Remaining Work

**VerifyIQ is an AI agent framework.** It does not contain a built-in VLM — all vision observations come from external providers configured by the user. This plan assumes an operational vision provider (Gemini, OpenRouter, or Local VLM) is available. Every phase below lives within the agent framework layer; the provider abstraction layer (`code/v2/providers/`) is the only VLM-dependent component.

## Phase A: YOLOv8n Object Part Detection

**Objective:** Add spatial grounding to V2 observations via YOLOv8n bounding box detection. Cross-reference YOLO-detected object parts with VLM-reported parts to catch misidentification.

**Estimated effort:** M (2-3 days)

**Dependencies:** Phase 5 (multi-model observation layer), `ultralytics` package

**Steps:**

1. **Install dependencies**
   - `pip install ultralytics`
   - Download `yolov8n.pt` pretrained weights (~6MB)

2. **Create YOLO detector module**
   - New file: `code/v2/localization/yolo_detector.py`
   - `YOLODetector` class wrapping `ultralytics.YOLO`
   - Methods: `detect_parts(image_paths)`, `get_part_labels()`, `get_confidence()`
   - Config: confidence threshold (default 0.5), model path

3. **Integrate into observation pipeline**
   - Run YOLO detection before VLM observation
   - Pass detected bounding boxes and labels as additional context in VLM prompt
   - Cross-reference YOLO `object_part` with VLM `object_part`
   - Flag mismatches as potential observation quality issues

4. **Fine-tune on dataset images**
   - Extract training data from `dataset/images/` with ground-truth labels
   - 200 labeled images per object type (car, laptop, package)
   - 50 epochs, batch size 16, learning rate 0.001

5. **Test and validate**
   - Measure mAP on held-out test images (>70% target)
   - Compare object part accuracy with and without YOLO integration
   - Verify no regression on existing V2 pipeline

**Success criteria:**
- YOLO detects object parts with >70% mAP on held-out images
- Object part mismatch detection improves by 15% vs VLM-only
- Pipeline latency increases by <100ms per image (YOLOv8n CPU inference)

---

## Phase B: Production API Server (FastAPI)

**Objective:** Build a production-grade FastAPI server wrapping the V2Pipeline with auth, rate limiting, structured errors, and async support.

**Estimated effort:** L (4-5 days)

**Dependencies:** Phase 16 (pipeline orchestrator), Phase A (YOLO integration optional)

**Steps:**

1. **Create API server skeleton**
   - New file: `code/v2/api/server.py`
   - FastAPI app with CORS middleware
   - Health check endpoint (`GET /v2/health`)
   - Metrics endpoint (`GET /v2/metrics`)

2. **Implement single analysis endpoint**
   - `POST /v2/analyze` — runs observation layer only
   - Accepts `claim_text`, `claim_object`, `image_paths`, `user_id`, `providers`
   - Returns per-image assessments from all available providers

3. **Implement full pipeline endpoint**
   - `POST /v2/claim` — runs all 10 layers
   - Accepts same fields + optional `evidence_requirements`, `options`
   - Returns full `V2Decision` with trace, metrics, justification

4. **Implement batch endpoint**
   - `POST /v2/batch` — processes multiple claims
   - Accepts array of claim requests
   - Configurable parallel/serial processing
   - Returns per-claim results with aggregate metrics

5. **Add authentication**
   - `X-API-Key` header validation
   - API key store (environment variable or file-based)
   - Per-key rate limit tracking

6. **Add rate limiting**
   - Sliding window rate limiter (tiered: free/pro/enterprise)
   - `X-RateLimit-*` response headers
   - 429 error response for exceeded limits

7. **Add structured error handling**
   - Error code enum with human-readable messages
   - Consistent JSON error format
   - Partial results for degraded pipeline runs

8. **Add async support**
   - Wrap V2Pipeline calls in `ThreadPoolExecutor` for non-blocking I/O
   - Optional `asyncio.gather` for parallel batch processing
   - Connection pooling for API-based providers

9. **Write integration tests**
   - `test_api.py` with mock providers
   - Test all endpoints, error codes, rate limiting
   - Test concurrent request handling

**Success criteria:**
- Server starts, handles concurrent requests, returns proper error codes
- All API endpoints functional with documented request/response schemas
- Rate limiting correctly enforces tier limits
- 95th percentile latency <10s per claim (Gemini API bound)

---

## Phase C: Claim Memory Store

**Objective:** Build a claim history store with in-memory + optional SQLite persistence to enable cross-claim fraud detection and user history tracking across API sessions.

**Estimated effort:** M (2-3 days)

**Dependencies:** Phase 7 (behavioral fraud detection)

**Steps:**

1. **Design data model**
   - `ClaimRecord`: `claim_id`, `user_id`, `timestamp`, `image_hashes`, `damage_type`, `object_part`, `status`
   - `UserProfile`: `user_id`, `claim_count`, `image_hashes[]`, `last_claim_timestamp`, `escalation_flag`

2. **Create memory store module**
   - New file: `code/v2/store/memory_store.py`
   - `ClaimMemoryStore` class with thread-safe dicts
   - Methods: `add_claim()`, `get_user_history()`, `check_image_reuse()`, `check_claim_frequency()`
   - TTL-based eviction for stale entries (configurable, default 7 days)

3. **Add optional SQLite persistence**
   - `ClaimStore` SQLite backend via `sqlite3` standard library
   - Schema: `claims(claim_id TEXT PK, user_id TEXT, timestamp REAL, image_hashes TEXT, damage_type TEXT, status TEXT)`
   - Auto-create tables on init

4. **Integrate with behavioral fraud detector**
   - Replace CSV-based history loading with in-memory store
   - `BehavioralFraudDetector` queries memory store instead of parsing CSV
   - Add claim on completion via pipeline hook

5. **Integrate with API server**
   - Initialize store on server startup
   - Pass store reference to V2Pipeline
   - Optional: provide admin endpoint to inspect store state

**Success criteria:**
- Behavioral fraud detects image reuse across API sessions
- Claim frequency anomaly detection works with real-time claim submission
- Store handles 10,000+ claims without memory issues
- SQLite persistence survives server restart

---

## Phase D: Hidden Test Evaluation

**Objective:** Evaluate V2 pipeline accuracy on 100 hidden test claims and compare against V1 baseline.

**Estimated effort:** S (1 day)

**Dependencies:** Phase 16 (pipeline orchestrator)

**Steps:**

1. **Create evaluation script**
   - New file: `code/v2/evaluate.py`
   - Loads `dataset/claims.csv` (100 claims)
   - Runs `V2Pipeline.process()` on each claim
   - Generates `output_v2.csv`

2. **Create comparison script**
   - Compares V2 output vs V1 output (from `output.csv`)
   - Per-field accuracy: `claim_status`, `issue_type`, `object_part`, `severity`, `risk_flags`, `evidence_standard_met`
   - Category-level breakdown: by damage type, object, image quality

3. **Run full evaluation**
   - Execute on 100 test claims
   - Record: accuracy per field, latency per claim, failure count, routing distribution

4. **Generate evaluation report**
   - New file: `code/v2/evaluation/report.md`
   - Table: field-by-field accuracy V1 vs V2
   - Category-specific breakdowns
   - Error case analysis (top failure modes)

**Success criteria:**
- V2 accuracy > V1 accuracy on all metrics
- Pipeline completes all 100 claims without crashes
- Evaluation report documents specific improvements per field

---

## Phase E: Local VLM Deployment (Qwen2.5-VL-7B)

**Objective:** Implement `LocalVLMProvider.analyze()` with a real local VLM (Qwen2.5-VL-7B) to enable offline inference and reduce API dependency.

**Estimated effort:** L (3-4 days)

**Dependencies:** Phase 2 (VisionProvider ABC), `transformers` or `ollama`, ~14GB RAM for model

**Steps:**

1. **Select deployment approach**
   - Option A: `transformers` + `qwen-vl-utils` (full control, heavier)
   - Option B: `ollama` with `qwen2.5-vl:7b` (simpler, lighter)
   - Decision: start with ollama for faster iteration

2. **Set up model**
   - Install ollama
   - Pull `qwen2.5-vl:7b` model
   - Test basic inference with a sample image + prompt

3. **Implement LocalVLMProvider.analyze()**
   - HTTP POST to ollama API endpoint (`http://localhost:11434/api/generate`)
   - Build prompt matching Gemini provider schema
   - Parse JSON response for per-image assessments
   - Handle errors: model not loaded, inference timeout, malformed response

4. **Add CPU fallback**
   - Check for GPU availability
   - If GPU unavailable, run with reduced image resolution (224x224 vs 448x448)
   - Set degraded flag in Observation when running on CPU
   - Adjust confidence penalty for degraded mode

5. **Integration test**
   - Run 10 sample claims through pipeline with LocalVLMProvider
   - Compare output quality vs GeminiProvider
   - Measure inference latency (target: <5s per image on GPU, <30s on CPU)

6. **Update availability check**
   - `_check_availability()` pings ollama health endpoint
   - Returns False if model not loaded or service unavailable

**Success criteria:**
- LocalVLMProvider produces valid `ObservationReport` with per-image assessments
- Pipeline runs entirely offline with local VLM (no API keys needed)
- Inference latency: <5s/image on GPU, <30s/image on CPU (degraded mode)
- Output quality within 10% of GeminiProvider accuracy
