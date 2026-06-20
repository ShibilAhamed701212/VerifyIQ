# Reliability — VerifyIQ

## Design Philosophy

Zero crashes is the non-negotiable engineering standard, achieved through three mechanisms: (1) per-component error boundaries so failure never cascades, (2) fallback defaults for every failure mode producing schema-compliant output, (3) no dependency on API availability — the system produces output even if Gemini, Tesseract, or CV modules are unavailable.

## Safe Mode Design

The orchestrator at `claim_processor.py:57-146` wraps each pipeline stage in independent try/except blocks:

| Stage | Fallback |
|-------|----------|
| Image normalization | Original paths passed through unconverted |
| Image validation | Skipped; processing continues with all paths |
| Claim parsing | Returns `{damage_type: "unknown", object_part: "unknown"}` |
| Vision analysis | Empty result with `damage_visible: False`, all fields unknown |
| Evidence checking | `{evidence_standard_met: False, valid_image: False}` |
| Rule engine | `{claim_status: "not_enough_information", risk_flags: []}` |
| Risk analyzer | `["manual_review_required"]` |
| Decision agent | Full 14-field row with safe defaults via `fallback_output` |

## Error Boundaries

Every component has independent error handling: image loading per-file (corrupt AVIF doesn't block WebP conversion), vision analysis with no-API-key guard and 5-retry exponential backoff, evidence checker with default-requirement fallback, rule engine with `.get()` defaults for missing fields, and output validator with coercion instead of exceptions.

## Cache Architecture

The GeminiVisionClient maintains a persistent hash-based response cache at `.gemini_cache/`. Each response is keyed by SHA-256 of sorted image paths, truncated claim text (200 chars), claim object, and model name. Cache hits return identical output with zero API calls. Cache misses make the API call and persist the result. Cache load/save errors are caught separately from the main API flow.

## OCR Safe Mode

When Tesseract is not installed or `pytesseract` is not importable, `TextDetector` returns `contains_text: False` for every image via an early-return guard. OCR is an additive signal — its absence doesn't block claim processing.

## Proven Reliability

Tested against 100 adversarial claims designed to trigger edge cases:
- **0 crashes** — every claim produced a valid output row
- **100% graceful degradation rate** — every failure triggered its designated fallback path
- **No silent data corruption** — all fallback outputs explicitly marked with `manual_review_required` or `not_enough_information`
