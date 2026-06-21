# Performance Profile

## Measurement Environment

| Parameter | Value |
|-----------|-------|
| Platform | Windows, Python 3.12.10 |
| Processor | Intel (local workstation) |
| Measurement | time.perf_counter, single-claim |
| Dataset | user_004 from sample_claims.csv (ideal vision, no real images) |

## Startup Time

| Phase | Time | % of Total |
|-------|------|------------|
| V1 imports (config, parser, rule, risk, evidence, severity, agent, validator, utils) | 32ms | 8.5% |
| V2 imports (pipeline, adapters, analyzer) | 233ms | 62.1% |
| PIL import | 31ms | 8.3% |
| pytesseract import | 79ms | 21.1% |
| **Total import time** | **375ms** | 100% |

**Key finding:** V2 imports dominate startup (233ms). pytesseract adds 79ms when loaded.

## Per-Claim Latency (Ideal Vision, Static Eval)

| Phase | Time | % of Total |
|-------|------|------------|
| Parsing | 15.375ms | 78.5% |
| RiskAnalyzer (V1RiskAdapter) | 2.018ms | 10.3% |
| ConversationAnalyzer | <0.001ms | <0.1% |
| ConsensusEngine | <0.001ms | <0.1% |
| ConfidenceCalibrator | <0.001ms | <0.1% |
| V1RuleAdapter | <0.001ms | <0.1% |
| RiskMerger | <0.001ms | <0.1% |
| **Total per-claim** | **~19.6ms** | 100% |

## RiskMerger Microbenchmark

| Scenario | Time |
|----------|------|
| Single call (hybrid mode, 4 flag groups) | ~2μs |
| 1,000 calls | 2.20ms avg |

RiskMerger is NOT a bottleneck. It adds ~2μs per claim.

## VLM Provider Latency (Estimated)

| Provider | Estimated Latency | Notes |
|----------|-------------------|-------|
| Gemini (with API key) | 1-3s per image | Network-bound |
| OpenRouter | 2-5s per image | Network-bound |
| Local VLM | 0.5-2s per image | GPU-dependent |
| Static eval (ideal vision) | 0s | Synthetic data |

## Bottleneck Analysis

| Bottleneck | Impact | Phase | Mitigation |
|------------|--------|-------|------------|
| **V2 imports** | 233ms startup | Initialization | Lazy-load rarely used modules |
| **pytesseract import** | 79ms startup | Initialization | Move to lazy import inside `text_detector.py` |
| **Claim parsing** | 15ms per claim | Per-claim | Parser is deterministic — no optimization needed |
| **RiskAnalyzer** | 2ms per claim | Per-claim | Already fast for static eval |
| **VLM Provider** | 1-5s per image | Per-image | Network-bound; production concern |

## Object Creation Profile

| Object | Creation Cost | Per Claim? |
|--------|---------------|------------|
| V1RuleAdapter | 0.1ms | Yes (new each call in validator) |
| V1RiskAdapter | 0.2ms | Yes (new each call in validator) |
| V2 V1RiskAdapter (reuse) | 0.0ms | No (import once, call many) |
| RiskMerger | 0.01ms | Yes (new each call) |

## Recommended Optimizations

1. **Lazy-load pytesseract** in `code/cv/text_detector.py` — saves 79ms on every startup that doesn't use OCR
2. **Cache V1RuleAdapter** in validator — reused across calls, no need to re-instantiate
3. **RiskMerger is already optimal** — 2μs per call, no work needed
4. **VLM providers** are the real bottleneck in production (1-5s per claim) but cannot be optimized without changing providers or batching

## Estimated Real-World Latency (Production)

| Component | Time |
|-----------|------|
| VLM observation (1-3 images) | 2-10s |
| Claim parsing | 15ms |
| Fraud detection (file I/O) | 50-200ms |
| Conversation analysis | 1ms |
| Consensus | 1ms |
| Confidence calibration | 1ms |
| V1RuleAdapter + RiskAnalyzer | 2ms |
| RiskMerger | 0.002ms |
| **Total per claim** | **~2-10s** (dominated by VLM) |
| **Total per claim (no VLM)** | **~20ms** |
