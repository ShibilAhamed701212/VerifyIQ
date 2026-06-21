# Release Checklist

> Steps to verify a VerifyIQ release before publishing.

---

## Pre-Release Checklist

### 1. Tests

- [ ] V1 tests pass: `pytest code/tests/ -v --tb=short`
  - Expected: 58/58 passing
- [ ] V2 tests pass: `pytest code/v2/tests/ -v --tb=short`
  - Expected: 49/49 passing
- [ ] All tests pass: `pytest code/tests/ code/v2/tests/ -v --tb=short`
  - Expected: 107/107 passing

### 2. Imports

- [ ] Package imports: `python -c "import verifyiq; print(verifyiq.__version__)"`
- [ ] V1 imports: `python -c "from verifyiq.v1 import Config, RuleEngine"`
- [ ] V2 imports: `python -c "from verifyiq.v2 import V2Pipeline, V2Decision"`
- [ ] V1 direct imports still work: `python -c "from code.config import Config"`
- [ ] V2 direct imports still work: `python -c "from code.v2.pipeline import V2Pipeline"`

### 3. CLI

- [ ] `verifyiq version` shows correct version
- [ ] `verifyiq evaluate` runs and completes

### 4. Packaging

- [ ] Build succeeds: `python -m build`
- [ ] Wheel validates: `python -m twine check dist/*`
- [ ] Install from wheel works:
  ```bash
  pip install dist/verifyiq-*.whl
  python -c "import verifyiq; print(verifyiq.__version__)"
  ```

### 5. Examples

- [ ] `python examples/01_quickstart.py` runs
- [ ] `python examples/02_v1_pipeline.py` runs
- [ ] `python examples/03_v2_pipeline.py` runs
- [ ] `python examples/04_security.py` runs

### 6. Docker

- [ ] Docker build: `docker build -t verifyiq:test .`
- [ ] Docker run: `docker run --rm verifyiq:test verifyiq version`

### 7. Documentation

- [ ] README.md is up to date
- [ ] CHANGELOG.md has release entry
- [ ] Version number updated in pyproject.toml and VERSION

### 8. CI

- [ ] tests.yml passes on GitHub
- [ ] lint.yml passes on GitHub

### 9. Repository

- [ ] No secrets committed (check .env, API keys)
- [ ] .gitignore covers all generated files
- [ ] LICENSE file present
- [ ] All source files have license headers (optional)

---

## Release Process

### For dev releases (0.x.x-dev)

```bash
# 1. Update version
echo "0.1.0-dev" > VERSION
# Update pyproject.toml version field

# 2. Build
python -m build

# 3. Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# 4. Verify TestPyPI install
pip install --index-url https://test.pypi.org/simple/ verifyiq

# 5. Tag
git tag v0.1.0-dev
git push origin v0.1.0-dev
```

### For stable releases (1.x.x)

```bash
# 1. Ensure all checklist items pass
# 2. Update CHANGELOG.md
# 3. Update version in pyproject.toml and VERSION
# 4. Build and verify
# 5. Upload to PyPI
# 6. Tag and push
# 7. Create GitHub Release
```

---

## Version Policy

- **0.x.x:** Pre-release — API may change without notice
- **1.x.x:** Stable — backward-compatible within major version
- See GOVERNANCE.md for full versioning policy

## Rollback

```bash
# Revert version
git revert <release-commit>
git push origin main

# Remove PyPI release (if needed)
python -m twine upload --repository pypi --skip-existing dist/*
```
