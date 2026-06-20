# Contributing to VerifyIQ

> **VerifyIQ is a production-oriented AI agent framework for multimodal claim verification. It performs reasoning, risk analysis, fraud detection, and decision-making using observations supplied by external vision providers (VLMs). Users configure their own VLM — Gemini, OpenRouter, local models, or custom providers. VerifyIQ does not contain a proprietary vision model.**

Welcome! We're thrilled you're interested in contributing to VerifyIQ, the multi-modal claim verification agent framework. Whether you're fixing a bug, adding a new vision provider, or improving documentation, your help makes this project better for everyone.

> **Note on project state:** VerifyIQ is transitioning from a competition submission to an open-source package. Some tooling referenced below (`verifyiq/` package, `pyproject.toml`, CI/CD, `.pre-commit-config.yaml`) is being rolled out as part of Stage 1 of the open-source migration. If these tools aren't available yet, the core workflow still works: fork, install deps manually, run tests with `pytest`, and submit a PR.

---

## Table of Contents

- [Project Philosophy](#project-philosophy)
- [Development Workflow](#development-workflow)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Testing Requirements](#testing-requirements)
- [Coding Standards](#coding-standards)
- [Documentation Standards](#documentation-standards)
- [Review Requirements](#review-requirements)

---

## Project Philosophy

VerifyIQ is built on four foundational principles:

**Deterministic where possible.** The V1 rule engine (`code/`) uses pure functions with no randomness — identical inputs always produce identical outputs. This guarantees reproducibility and makes debugging straightforward. The entire V1 pipeline (claim parsing → evidence checking → rule engine → risk analysis → severity → output validation) is a chain of deterministic transforms.

**Extensible where valuable.** V2 (`code/v2/`) introduces a 10-layer pipeline with a plugin-based provider system (Gemini, OpenRouter, local VLM). Adding a new VLM provider means implementing the `BaseVLMProvider` interface — nothing else needs to change. The consensus engine, fraud detectors, and confidence calibrator all follow the same open-for-extension, closed-for-modification pattern.

**Security by default.** Every input is sanitized before processing. Image validation checks size, format, and integrity before any analysis. The security layer (`code/v2/security/sanitizer.py`) strips dangerous payloads before they reach any pipeline stage. Safe Mode ensures that even if a component fails, the pipeline produces a valid degraded output rather than crashing.

**Explainability as a first-class concern.** The `DecisionTrace` system (`code/v2/explainability/tracer.py`) records every decision, observation, and confidence score in a structured trace. Every output includes a human-readable justification chain — so claimants, reviewers, and auditors always understand why a decision was made.

**Provider extensibility.** VerifyIQ is an AI agent framework, not a proprietary model. The provider abstraction (`BaseVLMProvider`) makes it straightforward to add new vision providers. See [Adding a Vision Provider](#adding-a-vision-provider) below.

**Competition rigor.** The project includes 107 tests (58 V1 + 49 V2) validated against ground truth across two independent evaluation pipelines. Changes must not regress this passing baseline.

---

## Development Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/your-username/verifyiq.git
cd verifyiq
```

### 2. Set Up Virtual Environment

VerifyIQ requires **Python 3.10+**.

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

The future package structure uses extras for modular dependency groups:

```bash
pip install -e ".[dev]"
```

If you're working from the current repository layout, install directly:

```bash
pip install -r code/requirements.txt
pip install pytest pytest-cov ruff mypy pre-commit
```

### 4. Set Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"   # optional
```

Never hardcode secrets. The provider system reads credentials from environment variables only.

### 5. Run Tests

V1 tests (58 tests — deterministic rule engine):

```bash
pytest code/tests/ -v
```

V2 tests (49 tests — 10-layer pipeline):

```bash
pytest code/v2/tests/ -v
```

All tests:

```bash
pytest code/tests/ code/v2/tests/ -v
```

With coverage:

```bash
pytest code/tests/ code/v2/tests/ --cov=code --cov-report=term-missing
```

### 6. Make Changes

- Create a feature branch from `main` (see Pull Request Process).
- Follow the coding standards in this guide.
- Keep changes focused — one logical change per branch.

### 7. Add Tests

Every new feature or bug fix must include tests. See [Testing Requirements](#testing-requirements).

### 8. Run Linter

```bash
ruff check verifyiq/
```

Fix any violations before submitting. The project follows PEP 8 with a 100-character line limit.

### 9. Run Type Checker

```bash
mypy verifyiq/
```

All public functions must have type annotations, and mypy must pass with no errors.

### 10. Submit a Pull Request

Push your branch and open a PR against `main`. See [Pull Request Process](#pull-request-process).

---

## Pull Request Process

### Branching

Create a feature branch from `main`:

```bash
git checkout main
git pull origin main
git checkout -b feat/my-feature-name
```

Use a descriptive prefix:

| Prefix     | Purpose                        |
|------------|--------------------------------|
| `feat/`    | New feature                    |
| `fix/`     | Bug fix                        |
| `docs/`    | Documentation                   |
| `refactor/`| Code restructuring             |
| `test/`    | Adding or updating tests       |
| `chore/`   | Tooling, dependencies, config  |

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

Examples:

```
feat(providers): add Anthropic VLM provider
fix(pipeline): handle empty observation list in consensus engine
test(security): add sanitizer edge case tests
docs(api): update provider interface documentation
```

Keep commits atomic — one logical change per commit.

### Before Submitting

- [ ] All tests pass (`pytest code/tests/ code/v2/tests/`)
- [ ] Linter passes (`ruff check verifyiq/`)
- [ ] Type checker passes (`mypy verifyiq/`)
- [ ] No commented-out code
- [ ] Tests added or updated for the change
- [ ] Documentation updated if user-facing
- [ ] Branch is up to date with `main`

### PR Description Template

```markdown
## Summary

Briefly describe what this PR does and why.

## Related Issues

Closes #<issue-number>

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactor
- [ ] Test update

## Testing

Describe how you tested this change.

## Checklist

- [ ] Tests pass
- [ ] Linter passes
- [ ] Type checker passes
- [ ] Docs updated (if applicable)
- [ ] No secrets committed
```

---

## Adding a Vision Provider

VerifyIQ's pluggable provider architecture makes it easy to add support for new VLMs. This is one of the most valuable contributions you can make.

### Provider Interface

Every vision provider implements `BaseVLMProvider` (see `code/v2/providers/base.py`):

```python
from abc import ABC, abstractmethod

class BaseVLMProvider(ABC):
    @abstractmethod
    def analyze_images(self, image_paths: list[str], claim_text: str) -> dict:
        """Extract structured observations from images using a VLM.
        
        Returns a dict with: damage_visible, damage_type, object_part,
        confidence, image_quality, supporting_images, per_image_assessments.
        """
```

### Steps to Add a Provider

1. **Create a new module** in `code/v2/providers/` named `<name>_provider.py`
2. **Subclass `BaseVLMProvider`** and implement `analyze_images`
3. **Handle provider-specific authentication** via environment variables
4. **Add error handling**: network failures, rate limits, malformed responses should all produce degraded output (never crash)
5. **Add tests** in `code/v2/tests/` — mock the provider API to test observation parsing
6. **Register the provider** in the provider registry (`code/v2/providers/__init__.py`)
7. **Add optional dependency** to `pyproject.toml` (e.g., `verifyiq[my-provider]`)
8. **Update documentation** — add the provider to README.md provider table

### Testing a New Provider

```python
# tests/test_my_provider.py
from unittest.mock import patch
from code.v2.providers.my_provider import MyProvider

def test_my_provider_parses_observations():
    provider = MyProvider(api_key="test-key")
    with patch.object(provider, "_call_api") as mock_call:
        mock_call.return_value = '{"damage": "dent", "part": "door"}'
        result = provider.analyze_images(["test.jpg"], "dent on door")
        assert result["damage_type"] == "dent"
```

## Issue Reporting

### Bug Reports

When filing a bug report, include:

- **Reproduction steps**: Minimal, complete example that triggers the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What happens instead
- **Environment**: Python version, OS, dependency versions (`pip freeze`)

```markdown
**Steps to reproduce:**
1. Run `python code/main.py --input dataset/test_claims.csv`
2. Observe output for claim_id=42

**Expected:** claim_status should be "supported"
**Actual:** claim_status is "contradicted"

**Environment:**
- Python 3.11.4
- Windows 11
- google-genai 1.2.0
```

### Feature Requests

When requesting a feature, include:

- **Use case**: What problem are you solving?
- **Proposed solution**: How would you like it to work?
- **Alternatives considered**: What else have you thought of?
- **Impact**: Would this affect the V1 deterministic guarantee? V2 provider interface?

### Questions

Before opening a question, check:

- [README.md](README.md) — project overview and quick start
- [docs/](./docs/) — architecture, evaluation, security guides
- [Existing issues](https://github.com/your-org/verifyiq/issues) — your question may already be answered

If you still need help, open an issue with the `question` label.

---

## Testing Requirements

### Coverage

All new code must have tests. This is not optional.

### What to Test

- **Success paths**: Does the code work as intended?
- **Failure paths**: Does it handle errors gracefully?
- **Edge cases**: Empty inputs, `None` values, malformed data, boundary conditions
- **Security**: Input sanitization, injection attempts, oversized payloads

### Test Style

- Use `pytest` as the test runner
- Use pytest fixtures for shared setup (providers, config, sample data)
- Mock external APIs (Gemini, OpenRouter) — never call real APIs in tests
- Name test files `test_<module>.py` and place them in the appropriate `tests/` directory

Example:

```python
import pytest
from unittest.mock import patch
from code.v2.providers.gemini_provider import GeminiProvider


@pytest.fixture
def provider():
    return GeminiProvider(api_key="test-key")


@patch("code.v2.providers.gemini_provider.genai")
def test_gemini_provider_extracts_observations(mock_genai, provider):
    mock_genai.Client.return_value.models.generate_content.return_value.text = '{"damage": "dent"}'
    result = provider.analyze("test_image.jpg", "What damage do you see?")
    assert result["damage"] == "dent"


def test_gemini_provider_handles_empty_response(provider):
    with patch.object(provider, "_call_api", return_value=None):
        result = provider.analyze("empty.jpg", "Describe")
        assert result == {}
```

### Running the Full Suite

Before every PR:

```bash
pytest code/tests/ code/v2/tests/ -v --tb=short
```

All 107 tests must pass.

---

## Coding Standards

### Style

- Follow **PEP 8**
- Maximum line length: **100 characters**
- Use **4 spaces** per indentation level (no tabs)

### Type Hints

Use type hints for all public functions:

```python
def analyze_image(path: str, prompt: str) -> dict[str, Any]:
    ...
```

### Data Models

Use `dataclasses` for data models:

```python
from dataclasses import dataclass


@dataclass
class Observation:
    damage_type: str | None
    confidence: float
    source: str
```

### Function Design

- **One responsibility per function.** If a function does more than one thing, split it.
- **Prefer clarity over cleverness.** Write code that is easy to read, not code that is short.
- **Descriptive variable names.** `damage_type` not `dt`, `evidence_score` not `es`.

### What Not to Do

- No commented-out code. Delete it.
- No print statements in production code. Use the logging module.
- No bare `except:` clauses. Catch specific exceptions.
- No mutable default arguments.

### Pre-commit Hooks

The project uses pre-commit to enforce standards automatically:

```bash
pre-commit install
```

Configuration is in `.pre-commit-config.yaml` — it runs ruff and mypy on every commit.

---

## Documentation Standards

### Docstrings

All public APIs require docstrings in **Google style**:

```python
def analyze_image(path: str, prompt: str) -> dict[str, Any]:
    """Analyze an image using a VLM provider.

    Args:
        path: Absolute or relative path to the image file.
        prompt: The analysis prompt to send to the VLM.

    Returns:
        A dictionary of extracted observations keyed by observation type.

    Raises:
        FileNotFoundError: If the image path does not exist.
        ProviderError: If the VLM provider fails.

    Examples:
        >>> analyze_image("photo.jpg", "What damage is visible?")
        {'damage_type': 'dent', 'confidence': 0.95}
    """
```

### Documentation Updates

- **README changes**: If your change affects how users interact with VerifyIQ, update `README.md`.
- **Architecture Decision Records**: Significant design decisions (new provider interface, pipeline restructuring, dependency changes) should be recorded as ADRs in `docs/adr/`.

### Runnable Examples

Docstring examples should be runnable with `doctest`:

```bash
python -m doctest code/v2/providers/gemini_provider.py -v
```

---

## Review Requirements

### Approval

- At least one maintainer must approve the PR before merge.
- For significant architectural changes, two maintainers are required.

### Automated Checks

All must pass before merge:

- [ ] All 107 tests pass
- [ ] `ruff check verifyiq/` passes with no violations
- [ ] `mypy verifyiq/` passes with no errors
- [ ] Coverage does not decrease below the current baseline

### Review Criteria

Reviewers will check:

- Does the code do what it claims?
- Are there sufficient tests (success, failure, edge cases)?
- Is the code idiomatic and maintainable?
- Are security best practices followed?
- Is documentation updated to match?
- Are there no Critical or Important issues unresolved?

### Merge

Once approved and all checks pass, a maintainer will merge the PR.

---

## Questions?

Open a [Discussion](https://github.com/your-org/verifyiq/discussions) or join our community chat.

Thank you for contributing to VerifyIQ!
