# Results — VerifyIQ

## Static Evaluation

| Metric | Result |
|--------|--------|
| Accuracy | 20/20 (100%) |
| Claims | 20 (with ideal vision injection) |
| Runtime | ~5 seconds |
| API calls | 0 |

Static evaluation injects ideal vision results to test the deterministic pipeline in isolation. Three identical runs each produced 20/20 — zero variance.

## Unit Tests

| Test Suite | Tests |
|------------|-------|
| `test_parser.py` | ClaimParser negation, keyword matching |
| `test_rule_engine.py` | RuleEngine 6 decision paths, compatible types |
| `test_risk_flags.py` | Risk flag whitelist validation |
| `test_cv.py` | Blur, crop, object detection |
| `test_utils.py` | Text extraction utilities |
| `test_validator.py` | Output consistency checks |
| `test_critic.py` | Submission post-processing |
| `test_image_validator.py` | Image validation logic |
| **Total** | **58/58 passing** |

## Adversarial Testing

100 adversarial claims designed to trigger edge cases — missing images, all-format images, corrupt files, oversized files, empty claims, contradictory claims, user history extremes, API quota exhaustion.

- **0 crashes** — every claim produced a valid output row
- **100% graceful degradation** — every failure triggered its designated fallback path
- **No silent data corruption** — all fallback outputs marked with `manual_review_required`

## Production Processing

44 actual claims processed through the full pipeline:

- **44/44 claims processed** (100% completion)
- **1 degraded output** (user_047 — Gemini 503 caught by Safe Mode)
- **Runtime:** ~6:00
- **API cost:** ~$0.01

## Per-Status Breakdown (20 Sample Claims)

| Status | Claims |
|--------|--------|
| Supported | 10 |
| Contradicted | 9 |
| Not Enough Information | 1 |

## Executive Scorecard

| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Architecture | 7/10 | 12% | 0.84 |
| Reliability | 7/10 | 15% | 1.05 |
| Explainability | 9/10 | 8% | 0.72 |
| Production Readiness | 6/10 | 10% | 0.60 |
| Evaluation | 9/10 | 15% | 1.35 |
| Security | 5/10 | 10% | 0.50 |
| Testing | 7/10 | 10% | 0.70 |
| Innovation | 3/10 | 10% | 0.30 |
| Interview Readiness | 7/10 | 5% | 0.35 |
| Winning Potential | 6/10 | 5% | 0.30 |
| **Total** | | **100%** | **67.1/100** |
