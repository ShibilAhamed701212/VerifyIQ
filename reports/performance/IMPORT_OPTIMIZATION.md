# Import Optimization

## Heavy Import Analysis

| Import | Module | Load Time | Occurrences | Lazily Loadable? |
|--------|--------|-----------|-------------|------------------|
| `pytesseract` | `code/cv/text_detector.py` | ~79ms | 1 | ✅ Yes — only used when `text_detector.py` is instantiated |
| `PIL` (Pillow) | Frauds, CV modules | ~31ms | 4 | ✅ Partially — only needed when processing real images |
| `google-genai` | `code/vision_analyzer.py` | ~50ms (est.) | 1 | ✅ Yes — only used when VLM is invoked |
| `openai` | V2 providers | ~40ms (est.) | 1 | ✅ Yes — only used when OpenRouter is invoked |

## Import Time Breakdown

| Scope | Time | % |
|-------|------|---|
| V1 production imports | 32ms | 8.5% |
| V2 production imports | 233ms | 62.1% |
| PIL import | 31ms | 8.3% |
| pytesseract import | 79ms | 21.1% |
| **Total** | **375ms** | 100% |

## Import Cycle Analysis

No circular imports detected. The dependency graph is a DAG:

```
code/config.py (no deps)
code/utils.py (no deps)
code/claim_parser.py (config)
code/rule_engine.py (claim_parser)
code/evidence_checker.py (config)
code/risk_analyzer.py (config, rule_engine)
code/decision_agent.py (all of the above)
    ↓
code/v2/v1_adapter.py (config, rule_engine, severity_engine, evidence_checker, claim_parser)
    ↓
code/v2/pipeline.py (v1_adapter, models, fraud, conversation, consensus, etc.)
    ↓
code/v2/risk_merger.py (standalone — no V1/V2 deps)
```

## Unnecessary Imports (Dead)

| File | Import | Line | Action |
|------|--------|------|--------|
| `code/main.py` | `import sys` | 9 | Not used anywhere |
| `code/v2/observability/metrics.py` | `from collections import defaultdict` | 2 | `defaultdict` never constructed |
| `code/v2/models/consensus.py` | `from typing import Optional` | 2 | No field uses `Optional` |
| `code/v2/observability/tracing.py` | `from typing import Optional` | 4 | Not used |

## Import Order Issues (ruff I001)

| File | Issue |
|------|-------|
| `verifyiq/__init__.py:8` | Import block unsorted |
| `verifyiq/__main__.py:54` | Import block unsorted (function-level) |
| `verifyiq/v1/__init__.py:14` | Imports after sys.path manipulation |
| `verifyiq/v2/__init__.py:14` | Imports after sys.path manipulation |

These are intentional — the lazy-load-after-path-insert pattern is required for the `verifyiq` package to work as a distribution.

## Lazy-Load Opportunities

| Current Import | File | Type | Improvement | Expected Gain |
|----------------|------|------|-------------|---------------|
| `import pytesseract` (top-level) | `code/cv/text_detector.py:3` | Move to method | -79ms startup | ~21% faster startup |
| `from PIL import Image` (multiple) | fraud/, cv/ | Already lazy inside methods | None needed | — |
| `from google import genai` | `code/vision_analyzer.py` | Move to method | -50ms startup | ~13% faster startup |
| `from openai import OpenAI` | V2 providers | Already lazy | None needed | — |

## Recommendations (Sorted by Impact)

1. **HIGH — Lazy-load pytesseract**: Move `import pytesseract` inside `text_detector.py`'s `detect()` method. Saves 79ms on every startup that doesn't use OCR.
2. **HIGH — Lazy-load google-genai**: Move `from google import genai` inside `vision_analyzer.py`'s `analyze()` method. Saves ~50ms.
3. **LOW — Remove dead imports**: Remove 4 unused imports (listed above). Zero risk, minor cleanup.
4. **LOW — Ignore import order flags**: The `verifyiq/` package's lazy imports are intentional.
