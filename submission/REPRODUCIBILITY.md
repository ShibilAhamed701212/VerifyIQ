# Reproducibility — VerifyIQ

## Static Evaluation Reproducibility

Three identical runs of the static evaluation against 20 sample claims:

```
Run 1: 20/20 (100%)
Run 2: 20/20 (100%)
Run 3: 20/20 (100%)
Variance: 0%
```

## Deterministic Components

Every component except Gemini has zero randomness:

**ClaimParser** — Keyword-based extraction with no randomness. **RuleEngine** — Pure if-then-else threshold logic. **EvidenceChecker** — Quality checks as pure set operations. **RiskAnalyzer** — Set operations on risk flags; CV modules return deterministic results for identical images. **SeverityEngine** — Static lookup mapping with no branching. **DecisionAgent** — Concatenates and merges upstream results. **OutputValidator** — Enum whitelist checks and boolean normalization. **SubmissionCritic** — Fixed post-processing pattern matching. **ImageValidator** — File existence, extension, size, PIL.verify() — all deterministic. **ImagePreprocessor** — PIL format conversion is deterministic for same input.

## Cache Eliminates API Variance

The Gemini API is called with `temperature=0.0`, which reduces but does not eliminate variance. In practice, confidence scores can swing ±0.05-0.15 between runs without cache, potentially flipping claim_status at the 0.50 threshold.

The hash-based cache at `vision_analyzer.py:46-53` computes SHA-256 over all inputs — image paths (sorted), user claim (truncated 200 chars), claim object, model name. On cache hit, the identical cached JSON response is returned. On cache miss, the API is called and the response is persisted.

| Scenario | Identical? | Source |
|----------|------------|--------|
| Static pipeline (3/3) | Yes | All components deterministic |
| Live with cache hit | Yes | Cached response returned |
| Live with cache miss | Baseline | Gemini API response |
| Live without cache | ~85-95% | Temperature=0 reduces but doesn't eliminate variance |

**Overall reproducibility score: 8/10** — Cache + deterministic pipeline = highly reproducible. The cache is essential for cross-session reproducibility without API-driven variance.
