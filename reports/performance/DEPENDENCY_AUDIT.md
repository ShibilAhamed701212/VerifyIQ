# Dependency Audit

## Production Dependencies (pyproject.toml)

| Package | Version | Required By | Classification |
|---------|---------|-------------|----------------|
| `Pillow` | >=10.0.0 | code/cv/*, code/v2/fraud/*, code/image_validator.py | **REQUIRED** — Image processing |
| `tqdm` | >=4.65.0 | code/evaluation/evaluate.py | **REQUIRED** — Progress bars for evaluation |

## Optional Dependencies (pyproject.toml)

| Group | Package | Classification |
|-------|---------|----------------|
| `dev` | pytest>=8.0.0 | **DEVELOPMENT** — Test runner |
| `dev` | pytest-cov>=5.0.0 | **DEVELOPMENT** — Coverage |
| `dev` | ruff>=0.3.0 | **DEVELOPMENT** — Linting |
| `dev` | mypy>=1.8.0 | **DEVELOPMENT** — Type checking |
| `docs` | mkdocs>=1.5.0 | **DEVELOPMENT** — Documentation |
| `docs` | mkdocs-material>=9.5.0 | **DEVELOPMENT** — Documentation theme |
| `api` | fastapi>=0.110.0 | **OPTIONAL** — REST API |
| `api` | uvicorn>=0.27.0 | **OPTIONAL** — ASGI server |
| `api` | pydantic>=2.0.0 | **OPTIONAL** — Data validation |
| `dashboard` | streamlit>=1.30.0 | **OPTIONAL** — Dashboard |
| `dashboard` | plotly>=5.18.0 | **OPTIONAL** — Charts |
| `dashboard` | pandas>=2.0.0 | **OPTIONAL** — Data manipulation |
| `gemini` | google-genai>=1.0.0 | **OPTIONAL** — Gemini provider |

## Additional Runtime Dependencies (Not in pyproject.toml)

| Package | Used By | Classification | Notes |
|---------|---------|----------------|-------|
| `pytesseract` | `code/cv/text_detector.py` | **OPTIONAL** — OCR | Not in any dependency group; requires Tesseract system binary |
| `opencv-python` (cv2) | `code/cv/*` | **OPTIONAL** — CV | Only used if available; safe fallback exists |
| `google-generativeai` | `code/vision_analyzer.py` | **OPTIONAL** — VLM | Older API; replaced by `google-genai` |

## Undeclared Dependencies

| Package | Used In | Issue |
|---------|---------|-------|
| `pytesseract` | `code/cv/text_detector.py` | **NOT IN ANY DEPENDENCY GROUP.** Must be added to `pyproject.toml` or documented as external system dependency. |
| `opencv-python` | `code/cv/*` | Not listed but imported via `try/except ImportError` — graceful fallback exists |
| `google-generativeai` | `code/vision_analyzer.py` | Legacy package — `google-genai` is in `[gemini]` group |
| `psutil` | `reports/` (analysis scripts) | Development-only; not in `pyproject.toml` |

## Duplicate Packages

| Package | Duplicates | Notes |
|---------|------------|-------|
| `google-genai` vs `google-generativeai` | Two packages | `google-genai` (new, in pyproject.toml), `google-generativeai` (legacy, imported directly in vision_analyzer.py) |

## Duplicate Dependency Declarations

| Package | Declared In | Also In |
|---------|-------------|---------|
| `Pillow` | `pyproject.toml` | `code/requirements.txt` |
| `tqdm` | `pyproject.toml` | `code/requirements.txt` |
| `google-genai` | `pyproject.toml` | `code/requirements.txt` |

## Dependency Count Summary

| Category | Count | Packages |
|----------|-------|----------|
| REQUIRED (install always) | 2 | Pillow, tqdm |
| OPTIONAL (install by group) | 14 | pytest, pytest-cov, ruff, mypy, mkdocs, mkdocs-material, fastapi, uvicorn, pydantic, streamlit, plotly, pandas, google-genai |
| UNDECLARED (missing from metadata) | 3 | pytesseract, opencv-python, google-generativeai |
| DEVELOPMENT (not for production) | 4 | pytest, pytest-cov, ruff, mypy |
| DUPLICATE DECLARATIONS | 3 | Pillow, tqdm, google-genai (in both pyproject.toml and requirements.txt) |

## Recommendations

| Priority | Action | Reason |
|----------|--------|--------|
| **HIGH** | Add `pytesseract` to `[project.optional-dependencies]` | Currently undeclared |
| **MEDIUM** | Add `opencv-python` to `[project.optional-dependencies]` | Currently undeclared |
| **MEDIUM** | Remove `code/requirements.txt` or sync with `pyproject.toml` | Duplicate declarations cause confusion |
| **LOW** | Remove `google-generativeai` usage in favor of `google-genai` | Legacy package deprecation |
| **LOW** | Add `psutil` to `dev` group | Used by analysis/benchmarking scripts |
