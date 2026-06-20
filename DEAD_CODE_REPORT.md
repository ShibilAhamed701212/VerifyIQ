# Dead Code Report

## Classification Key

| Category | Meaning | Action |
|----------|---------|--------|
| SAFE TO REMOVE | Not referenced anywhere; no side effects | Delete |
| REVIEW REQUIRED | Used by external code or has side effects | Investigate first |
| KEEP | Actively used in production paths | No change |

---

## SAFE TO REMOVE — Unused Imports

| File | Line | Import | Why Safe |
|------|------|--------|----------|
| `code/main.py` | 9 | `import sys` | `sys` never referenced in any function body |
| `code/v2/observability/metrics.py` | 2 | `from collections import defaultdict` | Only `list` and `dict` used; `defaultdict` never constructed |
| `code/v2/models/consensus.py` | 2 | `from typing import Optional` | No dataclass field uses `Optional` |
| `code/v2/observability/tracing.py` | 4 | `from typing import Optional` | Only `V2Decision`, `Path`, `str`, `float` used |

## SAFE TO REMOVE — Dead Functions

| File | Function | Line | Why Dead |
|------|----------|------|----------|
| `code/utils.py` | `clamp(value, min_val, max_val)` | 103 | Defined but never called anywhere in codebase |
| `code/evidence_checker.py` | `_part_visible(claimed_part, vision_result, relevant)` | 120 | Private method, never invoked |

## SAFE TO REMOVE — Dead Storage

| File | Issue | Why Dead |
|------|-------|----------|
| `code/image_preprocessor.py:18` | `_cleanup_dirs: List[Path] = []` | Global list accumulates temp dirs but is never read or cleaned |

## SAFE TO REMOVE — Empty/Placeholder Modules

| Module | Content | Impact |
|--------|---------|--------|
| `code/v2/decision/__init__.py` | Single comment: no code | Nothing imports from `code.v2.decision`. No loss. |
| `code/cv/__init__.py` | Empty | Exists only to make `cv/` a package |
| `code/evaluation/__init__.py` | Empty | Exists only to make `evaluation/` a package |
| `code/tests/__init__.py` | Empty | Test package marker |
| `code/v2/tests/__init__.py` | Empty | Test package marker |

## SAFE TO REMOVE — Unreachable Code

| File | Issue | Why Dead |
|------|-------|----------|
| `verifyiq/__main__.py:30` | `"analyze"` subcommand registered but never handled | Falls through silently (exit 0, no effect) |

## REVIEW REQUIRED — Unused Class

| Class | File | Notes |
|-------|------|-------|
| `TraceLogger` | `code/v2/observability/tracing.py` | Defined and exported but never instantiated by pipeline, tests, or production code. Should be reviewed: either integrate into pipeline or remove. |

## REVIEW REQUIRED — Orphaned Standalone Scripts

These are standalone entry points. They are NOT imported by production code but ARE runnable directly. They should be preserved for CI/validation but could be moved to a `scripts/` directory:

- `validate_confidence.py`
- `validate_conversation.py`
- `validate_fraud.py`
- `validate_hidden_tests.py`
- `validate_performance.py`
- `validate_reliability.py`
- `validate_v1_vs_v2.py`
- `adversarial_evaluation/generate_claims.py`
- `adversarial_evaluation/run_adversarial.py`
- `code/evaluation/static_evaluate.py`
- `examples/01_quickstart.py` through `04_security.py`

## KEEP — Everything Else

V1 modules, V2 modules, all adapters, all model definitions, all tests, all evaluations, all reports, all documentation.

## Duplicate Logic (Review Required, Not Delete)

| Function | Files | Recommendation |
|----------|-------|---------------|
| `_parse_flags(raw)` | `output_validator.py`, `submission_critic.py` | Extract to utils |
| `_to_float(value)` | `rule_engine.py`, `vision_analyzer.py`, `risk_analyzer.py` | Extract to utils |
| `_to_bool(value)` | `rule_engine.py`, `vision_analyzer.py` | Extract to utils |
| `normalize_flags()`/`parse_flags()` | `static_evaluate.py`, `validate_v1_vs_v2.py`, `validate_hidden_tests.py` | Extract to shared module |
| `make_ideal_vision()` | `static_evaluate.py`, `validate_v1_vs_v2.py` | Extract to shared module |

## Summary

| Category | Count |
|----------|-------|
| SAFE TO REMOVE (imports) | 4 |
| SAFE TO REMOVE (dead functions) | 2 |
| SAFE TO REMOVE (dead storage) | 1 |
| SAFE TO REMOVE (empty modules) | 3 |
| SAFE TO REMOVE (unreachable code) | 1 |
| REVIEW REQUIRED (unused class) | 1 |
| REVIEW REQUIRED (orphaned scripts) | 11 |
| DUPLICATE LOGIC | 5 patterns |
