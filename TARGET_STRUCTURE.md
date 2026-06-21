# Target Structure — VerifyIQ

Generated: 2026-06-20

## Principle

A GitHub visitor should see:

```
README.md
verifyiq/
docs/
tests/
examples/
api/
dashboard/
```

within 10 seconds. The repo must feel like an open-source Python package, not a hackathon submission.

---

## Source Code

### Current
```
verifyiq/               # stubs only (__init__, __main__)
  v1/__init__.py
  v2/__init__.py

code/                   # V1 source (FROZEN)
  __init__.py + 15 .py files
  cv/ (4 .py files)
  evaluation/ (5 .py + 3 .md)
  tests/ (8 test files)

code/v2/                # V2 source
  __init__.py + 12 .py files
  confidence/
  consensus/
  conversation/
  critic/
  decision/
  evidence/
  explainability/
  fraud/
  localization/
  models/
  observability/
  providers/
  security/
  tests/ (12 test files)

api/main.py
dashboard/app.py, run.py
```

### Proposed
```
verifyiq/               # full installed package
  __init__.py
  __main__.py
  v1/                   # V1 modules (symlink/copy from code/)
  v2/                   # V2 pipeline (moved from code/v2/)
  core/                 # shared base classes
  providers/            # VLM provider ABC + implementations
  security/             # sanitizer, validation
  observability/        # logging, metrics, tracing
  persistence/          # SQLite
  review/               # review queue

api/
  main.py
  __init__.py

dashboard/
  app.py
  run.py
  __init__.py

code/                   # PRESERVED frozen V1 (read-only reference)

archive/
  competition_v1/       # code/ moves here after approval
```

---

## Tests

### Current
```
code/tests/             # 8 V1 tests
code/v2/tests/          # 12 V2 tests (135 cases)
```

### Proposed
```
tests/
  __init__.py
  v1/                   # 8 V1 tests
  v2/                   # 12 V2 tests (135 cases)
  conftest.py
```

---

## Documentation

### Current
```
Root: 56 *.md
docs/: 8 *.md
code/v2/: 5 *.md (SYSTEM_HEALTH, SECURITY_V2, etc.)
```

### Proposed
```
docs/
  README.md
  ARCHITECTURE.md
  API.md
  SECURITY.md
  PRODUCTION.md
  EVALUATION.md
  OPEN_SOURCE.md
  DEPLOYMENT.md
  DEVELOPMENT.md
  competition/          # archived competition docs
  superpowers/          # dev plans (keep)
```

---

## Reports

### Current
```
Root: 48 report *.md
reports/: 13 *.md
code/evaluation/: 3 *.md
```

### Proposed
```
reports/
  evaluation/           # accuracy, reliability, robustness, etc.
  production/           # deployment readiness, production review
  security/             # security audits
  performance/          # code audits, optimization plans
  competition/          # competition analysis, FINAL_* files
  open_source/          # scorecards, maturity
  archive/              # superseded reports
```

---

## Examples

### Current
```
examples/
  01_quickstart.py
  02_v1_pipeline.py
  03_v2_pipeline.py
  04_security.py
  README.md
  providers/
    README.md
    gemini_example.py
    openrouter_example.py
    local_vlm_example.py
```

### Proposed
```
examples/
  README.md
  basic/                # 01_quickstart, 02_v1, 03_v2, 04_security
  providers/            # gemini, openrouter, local_vlm
  api/                  # REST API usage example
  batch/                # batch processing example
```

---

## Scripts & Config

### Current
```
deploy.ps1, deploy.sh
check_health.py
docker-compose.yml
Dockerfile, Dockerfile.gpu
pyproject.toml
.github/workflows/
```

### Proposed
```
scripts/
  deploy.ps1
  deploy.sh
  check_health.py

docker/
  Dockerfile
  Dockerfile.gpu
  docker-compose.yml

.github/workflows/      # keep
pyproject.toml           # keep root
```

---

## Temporary Files (Validation Scripts)

### Current
```
reality_test.py, reality_test2.py, reality_test3.py
reality_test_results.json, reality_test_results2.json
validate_confidence.py, validate_conversation.py
validate_fraud.py, validate_hidden_tests.py
validate_performance.py, validate_reliability.py
validate_v1_vs_v2.py
```

### Proposed
```
research/validation/    # move there, not deleted
```

---

## Summary: Before → After

| Directory | Before | After |
|-----------|--------|-------|
| Root .md files | 56 | ~7 (README, CONTRIBUTING, CHANGELOG, LICENSE, etc.) |
| `verifyiq/` | 2 stubs | Full package |
| `code/` | V1 + V2 + evals + tests | V1 only (FROZEN, then → archive/) |
| `code/v2/` | V2 pipeline | → `verifyiq/v2/` |
| `docs/` | 8 files | 10 folders |
| `reports/` | 13 files | 7 subfolders |
| `tests/` | split (code/tests, code/v2/tests) | unified `tests/v1/`, `tests/v2/` |
| `examples/` | flat | organized subfolders |
| `scripts/` | (none) | deploy + health scripts |
| `docker/` | (none) | Docker files |
| `research/` | (none) | validation scripts + research |
| `.gitignore` | minimal | generated artifacts + sensitive |

---

## Phased Execution Order

1. Create target directories
2. Copy V2 source → `verifyiq/v2/` (preserve originals)
3. Move docs → `docs/` subfolders
4. Move reports → `reports/` subfolders
5. Copy tests → `tests/v1/`, `tests/v2/`
6. Organize examples
7. Create scripts/, docker/, research/ dirs
8. Update imports and pyproject.toml
9. Validate: 135 tests, API, dashboard, package imports
10. Delete stale originals only after validation
