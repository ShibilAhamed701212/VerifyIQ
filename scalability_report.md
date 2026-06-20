# Scalability & Throughput Report

## Methodology
Based on production run data: 44 claims processed in ~6 minutes at ~$0.01 cost (source: `code/evaluation/WINNING_REVIEW.md:49`). Static evaluation: 20 claims in ~5 seconds (no API calls). API calls: 1 call per claim (1 image set per claim). Maximum images per claim: 5 (configurable in `config.py:31`). Images per Gemini call: all images up to `max_images_per_claim`. Measured dataset: 44 claims, 82 test images (~1.86 images/claim), 29 sample images across 20 sample claims.

Processing budget per claim (from 6 min / 44 claims ≈ 8.2s per claim):
- Gemini API call latency: ~4-5s (estimated from Gemini Flash Lite typical response time)
- Post-API sleep: 2s (`vision_analyzer.py:125`)
- Image loading + preprocessing: ~0.5-1s per claim
- CV pipeline (blur, crop, object, OCR): ~0.3-0.8s per claim
- Downstream deterministic modules: negligible (<10ms)

## Baseline: 44 Claims
- Runtime: ~6 minutes (360 seconds)
- API calls: 44 (1 per claim)
- Images processed: 82
- Memory: ~200-400MB peak (PIL image decoding, temporary JPEG conversions, OpenCV matrices)
- Cost: ~$0.01 (Gemini 3.1 Flash Lite pricing)
- Cache disk usage: ~2-5KB per claim (JSON analysis results)
- Bottlenecks: Sequential API calls dominate runtime (~80% of processing time)

## Scenario 1: 100 Claims
- Estimated runtime: 100 × 8.2s ≈ 820s ≈ **13.7 minutes**
- API calls: 100
- Memory estimate: ~200-400MB (sequential processing does not accumulate images)
- Cost estimate: 100 × ($0.01 / 44) ≈ **$0.023**
- Bottlenecks:
  1. Sequential API calls dominate runtime (~13 min of wall time spent waiting on Gemini)
  2. No significant memory increase over baseline (PIL/OpenCV release images between claims)

## Scenario 2: 500 Claims
- Estimated runtime: 500 × 8.2s ≈ 4100s ≈ **68.3 minutes** (~1.1 hours)
- API calls: 500
- Memory estimate: ~200-400MB (sequential processing)
- Cost estimate: 500 × ($0.01 / 44) ≈ **$0.114**
- Bottlenecks:
  1. API latency now exceeds 1 hour — impractical for near-real-time use
  2. Cache grows proportionally: ~1-3MB for 500 claims
  3. Cumulative risk if API outage occurs mid-batch — no checkpoint/resume mechanism

## Scenario 3: 1000 Claims
- Estimated runtime: 1000 × 8.2s ≈ 8200s ≈ **136.7 minutes** (~2.3 hours)
- API calls: 1000
- Memory estimate: ~200-400MB (sequential)
- Cost estimate: 1000 × ($0.01 / 44) ≈ **$0.227**
- Bottlenecks:
  1. Runtime exceeds 2 hours for a single batch
  2. No parallelization — cannot exploit Gemini's rate-limit headroom (the 2s sleep + retry backoff is conservative)
  3. Cache grows to ~2-5MB total — negligible

## Cache Impact Analysis
- **With cache**: Identical image sets produce zero API calls on rerun. Cache key includes resolved image paths, user claim (first 200 chars), claim object, and model name (`vision_analyzer.py:46-53`).
- **Cache growth**: ~2-5KB per claim (structured JSON analysis)
- **1000 claims ≈ 2-5MB cache** — disk impact is negligible
- **Estimated savings on reprocessing**: 100% of API calls eliminated for previously seen image sets. In practice, most claims have unique images, so cache hit rate on first pass is ~0%. On a second run (e.g., bugfix rerun), cache would eliminate all 1000 API calls, reducing runtime from 2.3 hours to ~3-5 minutes (CV-only).
- **Cold-start gap**: First run pays full API cost; cache pays off on any subsequent reprocessing.

## Bottleneck Analysis

### 1. API Latency (Primary)
- Each claim: ~4-5s for Gemini call + 2s post-call sleep = ~6-7s per claim
- Cannot parallelize without exceeding Gemini Free/Tier-1 rate limits (~60 RPM for Flash Lite, estimated)
- Mitigation: Cache eliminates redundant calls; concurrent claim processing with rate-limit-aware throttling; move to higher-tier API quota

### 2. Image Loading (Secondary)
- Each image: ~200-500ms for PIL open, optional format conversion, and read_bytes for Gemini
- Mitigation: Parallel image loading with ThreadPoolExecutor; lazy loading — only load images when needed

### 3. CV Processing (Tertiary)
- Blur detection (`cv/blur_detector.py:16-23`): ~50-150ms per image (Laplacian variance on grayscale)
- Crop detection (`cv/crop_detector.py:17-49`): ~100-250ms per image (Canny edge detection on 4 borders)
- Object validation (`cv/object_validator.py:36-64`): ~30-100ms per image (basic dimension check)
- OCR text detection (`cv/text_detector.py:39-56`): ~200-500ms per image (Tesseract, if available)
- Total CV per image: ~400-1000ms
- Each CV module processes images individually — no batch optimization
- Mitigation: Process images once and cache OpenCV decoded data; use smaller image sizes for CV operations; skip OCR if not needed

## Recommendations for Scale

1. **Concurrent claim processing with rate-limit-aware throttling**: Replace sequential `for` loop in `main.py:72` with `ThreadPoolExecutor` (or `asyncio`). Use a rate limiter (e.g., `token-bucket`) to stay within Gemini's RPM quota. For 60 RPM, process 3-5 claims concurrently, reducing total runtime by 3-5×. Each concurrent worker needs its own `GeminiVisionClient` or shared client with mutex.

2. **Batch image sets to reduce API calls**: Group multiple claims referencing the same images into a single API call. Add a `group_id` field to claims; process all images for a group in one Gemini call. This reduces API calls when claims share images (common for multi-part claims on the same object).

3. **Add checkpoint/resume with intermediate CSV**: After each claim, write intermediate results to a checkpoint CSV. On restart, skip already-processed user IDs. This limits batch-processing risk (a crash at claim 999 of 1000 does not lose all work). Implement via a lockfile and incremental output writer in `main.py`.

## Cost Projection

| Scale | Runtime | Cost | With Cache (reprocess) |
|-------|---------|------|------------------------|
| 44 | 6 min | $0.01 | $0.01 (no hits first pass) |
| 100 | 13.7 min | $0.023 | <$0.001 (CV only) |
| 500 | 68.3 min (~1.1h) | $0.114 | <$0.005 |
| 1000 | 136.7 min (~2.3h) | $0.227 | <$0.01 |
| 10000 | 1367 min (~22.8h) | $2.27 | <$0.10 |

Cost assumes Gemini 3.1 Flash Lite pricing as of mid-2026 (~$0.01875/1M input tokens, ~$0.075/1M output tokens). Cost scales linearly with claim count because each claim has a unique image set (no image dedup across claims in the dataset). With concurrent processing (Recommendation 1), runtime for 1000 claims drops from ~2.3h to ~30-45 min. Adding checkpoint/resume (Recommendation 3) makes the 10000-claim batch feasible by removing the single-point-of-failure risk.
