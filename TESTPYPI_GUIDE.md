# TestPyPI Guide

> How to publish and verify VerifyIQ on TestPyPI.

---

## Prerequisites

- [ ] PyPI account registered at https://test.pypi.org/account/register/
- [ ] PyPI API token created (scope: entire account, or project-specific)
- [ ] `twine` installed: `pip install twine build`

## Build

```bash
# From repository root
python -m build
```

Expected output:
```
Successfully built dist/verifyiq-0.1.0-dev.tar.gz
                   dist/verifyiq-0.1.0-dev-py3-none-any.whl
```

## Verify Build

```bash
python -m twine check dist/*
```

Expected output:
```
Checking dist/verifyiq-0.1.0-dev.tar.gz: PASSED
Checking dist/verifyiq-0.1.0-dev-py3-none-any.whl: PASSED
```

## Upload to TestPyPI

```bash
python -m twine upload --repository testpypi dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: `pypi-` followed by your API token

Or use a `.pypirc` file:
```ini
[testpypi]
username = __token__
password = pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Verify Installation

Install from TestPyPI in a clean environment:

```bash
# Create a virtual environment
python -m venv /tmp/verifyiq-test
source /tmp/verifyiq-test/bin/activate  # Linux/Mac
# OR
/tmp/verifyiq-test\Scripts\activate     # Windows

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ verifyiq

# Also install dependencies (TestPyPI doesn't resolve dependencies automatically)
pip install Pillow tqdm
```

Test:

```bash
python -c "import verifyiq; print(verifyiq.__version__)"
python -c "from verifyiq.v1 import Config; print('V1 OK')"
python -c "from verifyiq.v2 import V2Pipeline; print('V2 OK')"
```

## Troubleshooting

### Issue: TestPyPI fails to resolve dependencies

TestPyPI doesn't proxy PyPI dependencies. Either:
1. Install dependencies manually after: `pip install Pillow tqdm`
2. Use `--extra-index-url`: `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ verifyiq`

### Issue: Version already exists

TestPyPI does NOT allow re-uploading the same version. Increment:
```
0.1.0-dev → 0.1.0-dev.1 → 0.1.0-dev.2
```

### Issue: Package name conflict

`verifyiq` is not taken on TestPyPI as of June 2026. If it becomes taken:
1. Use a scoped name: `verifyiq-core` or `verifyiq-platform`
2. Update pyproject.toml `[project].name` accordingly

## Upload to Production PyPI

Only when ready for public release:

```bash
python -m twine upload dist/*
```

Replace `--repository testpypi` with no argument (defaults to PyPI).

## Automation (Future)

Once CI/CD is set up, releases are automated via GitHub Actions:

```yaml
# .github/workflows/release.yml (trigger: tag push v*)
jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: python -m build
      - run: python -m twine upload dist/*
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
```
