# Determinism Report — VerifyIQ V1 vs V2

> **Note:** VerifyIQ is an AI agent framework that performs reasoning using observations from external vision providers (VLMs). Results in this document assume an operational vision provider. VerifyIQ does not contain a proprietary VLM — users configure their own (Gemini, OpenRouter, local models, etc.).

## Test Method

Ran `validate_v1_vs_v2.compare()` 5 times in sequence, each with a fresh module reload, on the 20 sample claims with ideal vision data.

## Results

| Run | V1 Exact | V2 Exact | V2 Relaxed |
|-----|----------|----------|------------|
| 1   | 20/20    | 7/20     | 10/20      |
| 2   | 20/20    | 7/20     | 10/20      |
| 3   | 20/20    | 7/20     | 10/20      |
| 4   | 20/20    | 7/20     | 10/20      |
| 5   | 20/20    | 7/20     | 10/20      |

**Verdict: DETERMINISTIC** — all 5 runs produce identical results.

## Why Both Pipelines Are Deterministic

| Component | Why Deterministic |
|-----------|------------------|
| **ClaimParser** | Rule-based keyword extraction — no randomness, no API calls |
| **V1 RuleEngine** | Deterministic rule evaluation — same input → same output |
| **V1 RiskAnalyzer** | Rule-based analysis of image, history, and claim data |
| **V1 SeverityEngine** | Hardcoded severity mapping tables |
| **V1 EvidenceChecker** | Rule-based requirement checking |
| **V1 OutputValidator** | Schema enforcement with fixed value sets |
| **V2 ConversationAnalyzer** | Keyword + regex matching — no randomness |
| **V2 ConfidenceCalibrator** | Formulaic signal integration — 5 input signals → 1 output |
| **V2 Fraud Detectors** | SHA256 hashing, EXIF field matching, history counting — all deterministic |
| **V2 V1 Adapters** | Direct passthrough to deterministic V1 components |
| **V2Critic** | Rule-based consistency checks |
| **DecisionTracer** | Deterministic trace construction |

## No API Call Sources of Non-Determinism

Without real VLM API calls (GEMINI_API_KEY not available), the observation layer uses synthetic "ideal vision" data. The `ConsensusEngine.evaluate()` on a single observation produces a deterministic consensus report. All other providers (OpenRouter, LocalVLM) are stubs that would need real implementation to introduce non-determinism.

## Sources of Potential Non-Determinism (Not Active)

| Source | Would Introduce | Currently Active? |
|--------|----------------|-------------------|
| Gemini API calls | Temperature-dependent outputs | No (no API key) |
| Multi-model consensus | Model output variance | No (stubs only) |
| Random fraud sampling | None implemented | No |
| Time-based decisions | None implemented | No |

## Conclusion

**Both V1 and V2 produce identical outputs on every run.** The pipelines are fully deterministic under static evaluation conditions. With real VLM providers, observation outputs would vary between runs (model temperature, network timing), but the post-observation pipeline (RuleEngine, RiskAnalyzer, Fraud, Conversation, Confidence, Critic, Tracer) remains deterministic given the same inputs.

**Recommendation:** For competition submission, record the deterministic evaluation scores. If using live VLM providers, consider:
- Setting model temperature to 0.0
- Caching observation results
- Running 3+ passes and reporting median/mode
