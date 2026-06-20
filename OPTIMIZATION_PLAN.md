# Optimization Plan

## Principles

- Allowed: lazy imports, caching, faster loops, object reuse, startup optimization
- NOT allowed: architecture changes, model changes, feature changes
- Every optimization includes: expected gain, risk assessment, affected files

---

## OPT-1: Lazy-Load pytesseract

**Description**: Move `import pytesseract` from top-level to inside `detect()` method in `code/cv/text_detector.py`.

**Expected gain**: -79ms startup time (21% faster) when OCR path not used.

**Risk**: VERY LOW — pytesseract is only used inside `detect()`. Moving the import inside the method has no behavioral change.

**Files affected**: `code/cv/text_detector.py` line 3

**Implementation**:
```python
# Before:
import pytesseract

class TextDetector:
    def detect(self, image_path):
        ...
        text = pytesseract.image_to_string(...)

# After:
class TextDetector:
    def detect(self, image_path):
        import pytesseract
        ...
        text = pytesseract.image_to_string(...)
```

---

## OPT-2: Lazy-Load google-genai

**Description**: Move `from google import genai` from top-level to inside `analyze()` method in `code/vision_analyzer.py`.

**Expected gain**: -50ms startup time (~13%) when VLM not used.

**Risk**: VERY LOW — only used inside `analyze()`.

**Files affected**: `code/vision_analyzer.py`

---

## OPT-3: Cache V1RuleAdapter Instance

**Description**: In `validate_v1_vs_v2.py`, `run_v2()`, `run_v2_with_adapter()`, and `run_v2_mode()` each create a new `V1RuleAdapter()` and `V1RiskAdapter()` per claim. Create them once and reuse.

**Expected gain**: ~0.3ms per claim (negligible for 20 claims, but scales to 30ms for 100 claims).

**Risk**: VERY LOW — adapter instances are stateless.

**Files affected**: `validate_v1_vs_v2.py`, `code/v2/pipeline.py`

---

## OPT-4: Remove Dead `import sys` in main.py

**Description**: Remove unused `import sys` from `code/main.py`.

**Expected gain**: Negligible (~0.1μs). Cleanliness improvement.

**Risk**: NONE — `sys` is never referenced.

**Files affected**: `code/main.py:9`

---

## OPT-5: Remove Dead `defaultdict` Import in metrics.py

**Description**: Remove unused `from collections import defaultdict` from `code/v2/observability/metrics.py`.

**Expected gain**: Negligible. Cleanliness improvement.

**Risk**: NONE — `defaultdict` never constructed.

**Files affected**: `code/v2/observability/metrics.py:2`

---

## OPT-6: Remove Dead `Optional` Imports

**Description**: Remove unused `from typing import Optional` from `code/v2/models/consensus.py` and `code/v2/observability/tracing.py`.

**Expected gain**: Negligible. Cleanliness improvement.

**Risk**: NONE — `Optional` never used.

**Files affected**: `code/v2/models/consensus.py:2`, `code/v2/observability/tracing.py:4`

---

## OPT-7: Implement `_cleanup_dirs` in image_preprocessor.py

**Description**: Currently `_cleanup_dirs` grows unbounded. Either:
- a) Add `__del__` or context manager cleanup
- b) Remove the list entirely (it's dead storage)

**Expected gain**: Prevents potential memory leak in long-running processes.

**Risk**: LOW — dead code, no behavioral change from cleanup or removal.

**Files affected**: `code/image_preprocessor.py`

---

## OPT-8: RiskMerger Already Optimal

**Description**: RiskMerger takes ~2μs per call. No optimization needed.

**Files affected**: None.

---

## Summary

| Opt | Description | Gain | Risk | LOC Changed | Effort |
|-----|-------------|------|------|-------------|--------|
| 1 | Lazy pytesseract | -79ms startup (~21%) | Very Low | 2 | 5 min |
| 2 | Lazy google-genai | -50ms startup (~13%) | Very Low | 2 | 5 min |
| 3 | Cache adapters | ~0.3ms/claim | Very Low | 4 | 5 min |
| 4 | Remove dead import | 0.1μs | None | 1 | 1 min |
| 5 | Remove dead import | 0.1μs | None | 1 | 1 min |
| 6 | Remove dead imports | 0.1μs | None | 2 | 1 min |
| 7 | Fix _cleanup_dirs | Prevents leak | Low | 5 | 10 min |

**Total effort**: ~30 minutes. **Total startup gain**: -129ms (34% faster).
**Total per-claim gain**: Negligible (<0.5ms). All other bottlenecks are VLM-bound.

## Priority Order

1. OPT-1 + OPT-2 (biggest startup wins, lowest risk)
2. OPT-4 + OPT-5 + OPT-6 (trivial cleanup, zero risk)
3. OPT-7 (preventative, low priority)
4. OPT-3 (negligible gain, lowest priority)
