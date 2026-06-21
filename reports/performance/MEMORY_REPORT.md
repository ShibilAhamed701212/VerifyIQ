# Memory Analysis

## Process Memory

| Metric | Value |
|--------|-------|
| RSS (after all imports) | 24.6 MB |
| VMS | 15.3 MB |
| Python version | 3.12.10 |

**Note**: psutil not available for deeper analysis. Measurements are process-level only.

## Code Size Distribution

| Category | Count | Total Size | Avg Size |
|----------|-------|------------|----------|
| Python files (all) | 105 | 406,746 bytes | 3,873 bytes |
| Python files (production) | ~35 | ~250,000 bytes | ~7,100 bytes |
| Python files (tests) | 18 | ~40,000 bytes | ~2,200 bytes |
| Python files (validation scripts) | 9 | ~180,000 bytes | ~20,000 bytes |
| Markdown files (all) | 99 | 909,008 bytes | 9,181 bytes |
| Markdown files (root) | ~55 | ~750,000 bytes | ~13,600 bytes |

## Large Files

| File | Size | Notes |
|------|------|-------|
| `validate_v1_vs_v2.py` | 35,302 bytes | Largest Python file — report generation + 3-mode comparison |
| `validate_hidden_tests.py` | 32,282 bytes | Hidden test simulation |
| `validate_fraud.py` | 22,666 bytes | Fraud validation |
| `validate_conversation.py` | 22,227 bytes | Conversation validation |
| `validate_confidence.py` | 21,909 bytes | Confidence analysis |
| `adversarial_evaluation/generate_claims.py` | 19,822 bytes | Claim generation |
| `code/vision_analyzer.py` | 14,039 bytes | Largest production file (Gemini prompts + handling) |
| `code/v2/pipeline.py` | 13,817 bytes | Pipeline orchestrator |

## Object Retention Patterns

| Pattern | File | Issue |
|---------|------|-------|
| **Unclean temp storage** | `code/image_preprocessor.py:18` | `_cleanup_dirs: list[Path] = []` grows unbounded — never emptied |
| **Hash cache** | `code/v2/fraud/image_fraud.py:11` | `_hash_cache: dict[str, str]` grows with unique images — intentional, acceptable |
| **Claim history cache** | `code/v2/fraud/behavioral_fraud.py:10` | `_claim_history: dict[str, list[dict]]` grows with unique users — intentional, acceptable |

## Memory Risk Assessment

| Risk | Level | Description |
|------|-------|-------------|
| Memory leak (image_preprocessor) | **LOW** | `_cleanup_dirs` grows but only one call per claim; trivial leak |
| Memory leak (fraud caches) | **NONE** | Caches are bounded by unique images/users |
| Large image loading | **MEDIUM** | No explicit size limit on loaded images; PIL decodes full-res |
| VLM response retention | **LOW** | Single-claim processing; GC collects between claims |
| Markdown report bloat | **LOW** | 99 .md files at 909KB is non-trivial but not a runtime issue |

## Recommendations

1. **Fix `_cleanup_dirs` in `image_preprocessor.py`** — either implement `__del__` cleanup or remove the list
2. **Add image size limit** — warn/clamp images > 10MB before PIL decoding
3. **Archive stale .md reports** — move to archive/ directory to reduce repo size
4. **Memory is not a concern** — 24.6 MB RSS is minimal for a production service
