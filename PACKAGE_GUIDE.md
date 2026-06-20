# VerifyIQ Package Guide

> How VerifyIQ is packaged, distributed, and installed.

---

## Package Architecture

```
verifyiq/                        # Canonical Python package
├── __init__.py                  # Package metadata, version
├── __main__.py                  # CLI entry point (verifyiq command)
├── v1/__init__.py               # Wrapper — re-exports from code/
└── v2/__init__.py               # Wrapper — re-exports from code/v2/
```

The package is a **thin wrapper layer** over the existing `code/` and `code/v2/` directories. It uses `sys.path` injection to point at the canonical source files. No files are moved, copied, or duplicated.

## Installation

### From source (development)

```bash
git clone https://github.com/verifyiq/verifyiq.git
cd verifyiq
pip install -e ".[dev]"
pip install -r code/requirements.txt
pytest code/tests/ code/v2/tests/
```

### From PyPI (future)

```bash
pip install verifyiq
```

## Extras

| Extra | Dependencies | Use Case |
|-------|-------------|----------|
| (core) | Pillow, tqdm | Core V1 + V2 pipeline |
| dev | pytest, ruff, mypy | Development |
| docs | mkdocs, mkdocs-material | Documentation |
| api | fastapi, uvicorn, pydantic | REST API server |
| dashboard | streamlit, plotly, pandas | Streamlit dashboard |
| gemini | google-genai | Google Gemini provider |

## Import Paths

```python
# Core package
import verifyiq
print(verifyiq.__version__)

# V1 pipeline
from verifyiq.v1 import Config, RuleEngine, ClaimParser

# V2 pipeline
from verifyiq.v2 import V2Pipeline, V2Decision, InputSanitizer

# Direct V1 import (still works — unchanged)
from code.config import Config
from code.rule_engine import RuleEngine

# Direct V2 import (still works — unchanged)
from code.v2.pipeline import V2Pipeline
```

## Key Design Decisions

1. **No file duplication:** The `verifyiq/` package is a wrapper layer. All source code lives in `code/` and `code/v2/`.
2. **Backward compatibility:** All existing import paths (`from code.*`, `from code.v2.*`) continue to work unchanged.
3. **sys.path injection:** The wrapper uses the same pattern as `code/__init__.py` — inject `code/` into `sys.path` and re-export.
4. **No V1/V2 modification:** Neither `code/` nor `code/v2/` files are modified by the package.

## Build

```bash
python -m build          # Creates dist/*.tar.gz and dist/*.whl
python -m twine check dist/*  # Validate package
```

## Test

```bash
pytest code/tests/       # 58 V1 tests
pytest code/v2/tests/    # 49 V2 tests
pytest code/tests/ code/v2/tests/  # All 107 tests
```

## CLI

```bash
verifyiq version         # Show version
verifyiq evaluate        # Run static evaluation on sample claims
verifyiq analyze         # Analyze a single claim (TODO)
verifyiq benchmark       # Run benchmarks (TODO)
```
