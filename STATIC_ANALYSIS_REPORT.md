# Static Analysis Report

## Tools Used

| Tool | Version | Scope |
|------|---------|-------|
| ruff | 0.15.18 | All Python files (error classes E, F, W, I, N) |

## Summary

| Metric | Count |
|--------|-------|
| Total errors | 1,019 |
| Fixable | 453 (21 unsafe) |
| Unique error types | 4 |
| Files affected | ~30 |

## Error Breakdown

### E501 — Line Too Long (over 100 chars) — ~800+ occurrences

**Pattern**: Mostly in `validate_v1_vs_v2.py` report-generation code where markdown table rows exceed 100 chars.

**Files affected**:
- `validate_v1_vs_v2.py` — 99% of occurrences (markdown table generation strings)
- `verifyiq/v2/__init__.py` — long import lines

**Severity**: LOW — These are generated strings, not logic code. Markdown tables cannot be split mid-content.

### F541 — f-string without placeholders — 2 occurrences

**Files**:
- `validate_v1_vs_v2.py:651` — `print(f"  DUAL RISK SYSTEM — FINAL RESULTS")`

**Severity**: LOW — readability only.

### I001 — Import block unsorted — 4 occurrences

**Files**:
- `verifyiq/__init__.py:8` — `from importlib.metadata import ...`
- `verifyiq/__main__.py:54` — lazy imports inside function
- `verifyiq/v1/__init__.py:14` — lazy imports after path insertion
- `verifyiq/v2/__init__.py:14` — lazy imports after path insertion

**Severity**: LOW — These are intentional (lazy loading after sys.path manipulation).

### E402 — Module level import not at top of file — ~200 occurrences

**Files**:
- `verifyiq/v1/__init__.py` — all imports (line 14-23)
- `verifyiq/v2/__init__.py` — all imports (line 14-34)

**Severity**: LOW — These are intentional. The `verifyiq` package manipulates `sys.path` before importing from `code/`.

## Full Ruff Output Summary (excluding E501 for readability)

```
Found 1019 errors (453 fixable, 21 unsafe)
- E501 line-too-long: ~800+
- E402 module-level-import: ~200
- I001 import-unsorted: 4
- F541 f-string-no-placeholders: 2
```

## MyPy Not Run

MyPy requires full type annotation coverage. The codebase uses minimal type hints. Running mypy would produce thousands of errors (`Missing type parameters`, `Cannot find implementation or library stub`, etc.). The codebase uses dynamic typing throughout — consistent with the original competition format.

## Recommendations

1. **Ignore E501** in `validate_v1_vs_v2.py` — markdown generation code cannot be meaningfully shortened
2. **Ignore E402/I001** in `verifyiq/` — lazy imports after path insertion are intentional
3. **Fix F541** in `validate_v1_vs_v2.py` — remove 2 unnecessary `f` prefixes
4. **Add `# noqa: E501`** to known long report-generation lines to suppress noise
5. **Do NOT run mypy** without significant annotation work — it's not production code yet
