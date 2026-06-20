# VerifyIQ CI/CD Pipeline Design

## Overview

Greenfield CI/CD design for **VerifyIQ** — a multi-modal claim verification platform (Python 3.10+, open-source). The pipeline runs on GitHub Actions and covers testing (three suites), linting, documentation, and release. VLM API calls (Gemini) are expensive and rate-limited — all tests mock them so CI never calls production APIs.

---

## Workflow 1: `tests.yml`

### Trigger Conditions

| Trigger | Branch | Notes |
|---|---|---|
| `push` | `main`, `develop` | Full test suite |
| `pull_request` | `main` | Required status check before merge |
| `workflow_dispatch` | any | Manual trigger for ad-hoc runs |

### Concurrency

```yaml
concurrency:
  group: tests-${{ github.head_ref || github.ref }}
  cancel-in-progress: true
```

Cancel any in-progress run for the same branch to save minutes.

---

### Job 1a: `v1-tests`

**Runner:** `ubuntu-latest`  
**Matrix:** `[3.10, 3.11, 3.12]`  
**Expected runtime:** ~1 min  
**Expected result:** 58/58 passing

#### Steps

1. **Checkout** — `actions/checkout@v4`
2. **Setup Python** — `actions/setup-python@v5` with `python-version: ${{ matrix.python-version }}`
3. **Cache pip** — `actions/cache@v4` keyed on `requirements-v1.txt` hash and Python version
   - Restores `~/.cache/pip`
   - Falls back to `pip install` on cache miss
4. **Install V1 dependencies**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r code/requirements-v1.txt
   pip install pytest pytest-cov
   ```
5. **Run V1 tests with coverage**
   ```bash
   pytest code/tests/ -v --tb=short --cov=code --cov-report=xml:coverage-v1.xml
   ```
6. **Upload coverage** — `actions/upload-artifact@v4` with `coverage-v1.xml`

#### Failure handling

- Test failure → job fails, annotates PR with `::error::` messages
- `continue-on-error: false` (default) — blocks merge

---

### Job 1b: `v2-tests`

**Runner:** `ubuntu-latest`  
**Matrix:** `[3.10, 3.11, 3.12]`  
**Expected runtime:** ~2 min  
**Expected result:** 49/49 passing

#### Steps

1. **Checkout**
2. **Setup Python** (matrix)
3. **Cache pip** — keyed on `requirements-v2.txt` + dev extras hash
4. **Install V2 + dev dependencies**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r code/v2/requirements-v2.txt
   pip install pytest pytest-cov
   ```
5. **Run V2 tests with coverage**
   ```bash
   pytest code/v2/tests/ -v --tb=short --cov=code/v2 --cov-report=xml:coverage-v2.xml
   ```
6. **Upload coverage**

#### Failure handling

- Same as v1-tests: fail on first red test
- Independent from v1-tests (runs in parallel)

---

### Job 1c: `integration-tests`

**Runner:** `ubuntu-latest`  
**Python version:** `3.11` (single, no matrix — integration tests are slower)  
**Expected runtime:** ~3 min  
**Expected result:** all passing

#### Steps

1. **Checkout**
2. **Setup Python** (3.11)
3. **Cache pip** — keyed on merged dependency hash
4. **Install all dependencies**
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r code/requirements-v1.txt
   pip install -r code/v2/requirements-v2.txt
   pip install pytest pytest-cov
   # Install future verifyiq package extras:
   # pip install ".[dev]"
   ```
5. **Run integration tests**
   ```bash
   pytest verifyiq/tests/ -v --tb=short --cov=verifyiq --cov-report=xml:coverage-int.xml
   ```
6. **Upload coverage**

#### Failure handling

- Fail on test failure
- Runs after v1-tests and v2-tests complete (unblocked, not sequential — no `needs` dependency)
- If API-key-gated tests exist: skip with `@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"))`

---

### Environment Variables & Secrets

| Variable | Scope | Required? | Notes |
|---|---|---|---|
| `GEMINI_API_KEY` | `integration-tests` | No (tests are mocked) | Only needed if unmocked e2e tests are added later |
| `COVERAGE_THRESHOLD` | All test jobs | No | Optional: enforce min coverage % |

Secrets stored in GitHub repo → Settings → Secrets and variables → Actions.

---

### API-Key-Gated Tests (Mock Strategy)

Since VLM API calls are expensive and rate-limited:

1. **All unit tests mock Gemini responses** using `unittest.mock.patch` or `pytest-mock`
2. **CI never holds a real `GEMINI_API_KEY`** — the secret is optional
3. Tests decorated with `@pytest.mark.gemini_api` are **skipped** when the key is absent:
   ```python
   @pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
   ```
4. A future scheduled workflow (cron) can run unmocked e2e tests weekly

---

## Workflow 2: `lint.yml`

### Trigger Conditions

| Trigger | Branch | Notes |
|---|---|---|
| `push` | `main`, `develop` | |
| `pull_request` | `main` | Required status check |
| `workflow_dispatch` | any | |

### Concurrency

```yaml
concurrency:
  group: lint-${{ github.head_ref || github.ref }}
  cancel-in-progress: true
```

---

### Job 2a: `ruff`

**Runner:** `ubuntu-latest`  
**Python:** `3.11`  
**Expected runtime:** ~15 s

#### Steps

1. **Checkout**
2. **Setup Python** (3.11)
3. **Install ruff**
   ```bash
   pip install ruff
   ```
4. **Run linter**
   ```bash
   ruff check verifyiq/ code/ code/v2/
   ```

#### Failure handling

- Fail on any lint error
- PR blocked until lint passes

---

### Job 2b: `mypy`

**Runner:** `ubuntu-latest`  
**Python:** `3.11`  
**Expected runtime:** ~30 s

#### Steps

1. **Checkout**
2. **Setup Python** (3.11)
3. **Install mypy + project dependencies** (for `.pyi` stub resolution)
   ```bash
   pip install mypy
   pip install -r code/requirements-v1.txt    # if stubs needed
   ```
4. **Run type checker** (relaxed — not `--strict`)
   ```bash
   mypy verifyiq/ code/ code/v2/
   ```
   *Use relaxed config initially (skipping `--strict`) to allow gradual typing adoption. Add `--strict` once coverage improves.*

#### Failure handling

- Fail on type errors
- Exclude known-untyped 3rd-party libs via `mypy.ini`:
  ```ini
  [mypy]
  ignore_missing_imports = True
  ```

---

### Job 2c: `format-check`

**Runner:** `ubuntu-latest`  
**Python:** `3.11`  
**Expected runtime:** ~15 s

#### Steps

1. **Checkout**
2. **Setup Python**
3. **Install black**
   ```bash
   pip install black
   ```
4. **Check formatting**
   ```bash
   black --check verifyiq/ code/ code/v2/
   ```

#### Failure handling

- Fail on formatting violations (suggest running `black .`)
- PR blocked until formatted

---

## Workflow 3: `docs.yml`

### Trigger Conditions

| Trigger | Branch | Notes |
|---|---|---|
| `push` | `main` | Only deploy from main |
| `workflow_dispatch` | `main` | Manual re-deploy |

---

### Job 3a: `build-docs`

**Runner:** `ubuntu-latest`  
**Expected runtime:** ~1.5 min

#### Steps

1. **Checkout**
2. **Setup Python** (3.11)
3. **Install mkdocs + theme**
   ```bash
   pip install mkdocs mkdocs-material
   ```
4. **Build docs**
   ```bash
   mkdocs build
   ```
5. **Deploy to GitHub Pages**
   ```yaml
   - uses: peaceiris/actions-gh-pages@v3
     with:
       github_token: ${{ secrets.GITHUB_TOKEN }}
       publish_dir: ./site
   ```

#### Failure handling

- Fail on build errors (broken include, missing page)
- Deploy skipped on failure

---

### Job 3b: `link-check`

**Runner:** `ubuntu-latest`  
**Expected runtime:** ~30 s

#### Steps

1. **Checkout**
2. **Setup Python**
3. **Install link checker**
   ```bash
   pip install linkchecker
   ```
4. **Run link check**
   ```bash
   linkchecker docs/ --recursive --no-warnings
   ```

#### Failure handling

- Fail on broken links
- Runs in parallel with `build-docs` (no dependency)

---

## Workflow 4: `release.yml`

### Trigger Conditions

| Trigger | Tag Pattern | Notes |
|---|---|---|
| `push` | `v*.*.*` (e.g. `v1.2.3`) | Semver tags only |
| `workflow_dispatch` | any | Manual override with version input |

---

### Job 4a: `build`

**Runner:** `ubuntu-latest`  
**Expected runtime:** ~30 s

#### Steps

1. **Checkout**
2. **Setup Python** (3.11)
3. **Install build**
   ```bash
   pip install build
   ```
4. **Build package**
   ```bash
   python -m build
   ```
5. **Upload build artifact** — `actions/upload-artifact@v4` with `dist/`

#### Failure handling

- Fail on build error (invalid `pyproject.toml`, missing README, etc.)

---

### Job 4b: `publish`

**Runner:** `ubuntu-latest`  
**Needs:** `build`  
**Expected runtime:** ~30 s

#### Steps

1. **Download build artifact** — `actions/download-artifact@v4`
2. **Publish to TestPyPI (dry-run first)**
   ```bash
   pip install twine
   twine upload --repository-url https://test.pypi.org/legacy/ dist/* -u __token__ -p ${{ secrets.TEST_PYPI_TOKEN }} --skip-existing
   ```
3. **Publish to PyPI**
   ```bash
   twine upload dist/* -u __token__ -p ${{ secrets.PYPI_TOKEN }}
   ```

#### Environment Variables & Secrets

| Secret | Required | Description |
|---|---|---|
| `PYPI_TOKEN` | Yes | PyPI API token (with upload scope) |
| `TEST_PYPI_TOKEN` | Recommended | TestPyPI API token for dry-run |

#### Failure handling

- Fail on upload error (duplicate version, auth failure)
- `needs: build` ensures only successfully-built packages are published

---

### Job 4c: `github-release`

**Runner:** `ubuntu-latest`  
**Needs:** `publish`  
**Expected runtime:** ~1 min

#### Steps

1. **Create GitHub Release**
   ```yaml
   uses: softprops/action-gh-release@v2
   with:
     tag_name: ${{ github.ref_name }}
     name: Release ${{ github.ref_name }}
     body_path: CHANGELOG.md  # or auto-generate from commits
     draft: false
     prerelease: contains(github.ref_name, '-')
     files: |
       dist/*
   ```

#### Failure handling

- Fail on release creation error
- `needs: publish` ensures release only happens after PyPI upload succeeds

---

## Additional Considerations

### Handling API-Key-Gated Tests

- All CI test jobs use **mocked VLM API responses** (via `unittest.mock`)
- Tests that truly require a real API key are marked with `@pytest.mark.gemini_api`
- CI always runs without `GEMINI_API_KEY` — these tests are skipped
- **Scheduled workflow** (cron: weekly) can run unmocked e2e tests with a real key:
  ```yaml
  on:
    schedule:
      - cron: "0 6 * * 1"  # Every Monday 06:00 UTC
  ```

### Handling Long-Running Benchmarks

- Do **not** include benchmarks in the main `tests.yml`
- Create a separate **benchmarks.yml** workflow:
  - Trigger: `push` to `develop`, or `workflow_dispatch`
  - Runs on a single high-performance runner
  - Expected runtime: ~20–30 min
  - Results posted as a PR comment or commit status (not blocking)

### Concurrency Limits

All three main workflows (`tests.yml`, `lint.yml`, `docs.yml`) include:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true
```
This cancels in-progress runs for the same branch on new pushes, saving action minutes.

### Required Status Checks for PR Merge

Configure in GitHub → Settings → Branches → `main` branch protection rule:

| Check | Required | Notes |
|---|---|---|
| `v1-tests (3.10)` | Yes | At least one Python version |
| `v2-tests (3.10)` | Yes | At least one Python version |
| `integration-tests` | Yes | |
| `ruff` | Yes | |
| `mypy` | Yes | |
| `format-check` | Yes | |

*Optionally require all matrix versions to pass* for stricter enforcement.

### Cost Considerations (GitHub Actions Free Tier)

| Resource | Free Tier Limit | Expected Monthly Usage |
|---|---|---|
| Action minutes (Linux) | 2,000 min/month | ~500–1,000 min |
| Concurrent jobs | 20 | 3–6 (fine) |
| Storage (artifacts) | 500 MB | ~50 MB |

**Estimated monthly minutes:**
- **Tests per push:** `v1` (1 min × 3 versions = 3) + `v2` (2 min × 3 versions = 6) + `integration` (3 min) = **~12 min**
- **Lint per push:** ~1 min
- **Docs per push (main only):** ~2 min
- **Release per tag:** ~3 min
- **~40 pushes/day × 22 days × 1 min avg** ≈ 880 min/month → well within free tier

If usage grows, switch to a self-hosted runner or reduce matrix to `[3.10, 3.12]`.

---

## Summary

| Metric | Value |
|---|---|
| **Total expected CI runtime per push** | **~5–7 min** (parallel: tests + lint run simultaneously) |
| **Monthly action minutes estimate** | **~500–1,000 min** (within free tier of 2,000) |
| **Recommended GitHub secrets** | `GEMINI_API_KEY` (optional), `PYPI_TOKEN`, `TEST_PYPI_TOKEN` |
| **Recommended branch protection** | Require status checks (v1-tests, v2-tests, integration-tests, ruff, mypy, format-check); require PR reviews; prevent force-push to `main` |
| **Workflows** | `tests.yml`, `lint.yml`, `docs.yml`, `release.yml` + optional `benchmarks.yml` (scheduled) |
