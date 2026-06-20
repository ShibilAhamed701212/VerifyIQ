# VerifyIQ — Project Identity

> **VerifyIQ is a production-oriented AI agent framework for multimodal claim verification. It performs reasoning, risk analysis, fraud detection, and decision-making using observations supplied by external vision providers (VLMs). Users configure their own VLM — Gemini, OpenRouter, local models, or custom providers. VerifyIQ does not contain a proprietary vision model.**

---

## 1. What VerifyIQ Is

VerifyIQ is an **AI agent framework** — a structured system that orchestrates observation, reasoning, and decision-making for claim verification. It does not contain or embed a vision model. Instead, it provides:

- A **pluggable provider interface** for connecting any VLM (Gemini, OpenRouter, GPT-4o Vision, Qwen-VL, MiniCPM-V, InternVL, or custom)
- A **deterministic reasoning engine** that evaluates observations against claim requirements
- A **risk analysis system** that flags fraud indicators, inconsistencies, and quality issues
- A **severity engine** that maps damage types to severity levels
- A **fully explainable output** with traceable justification chains

**Key distinction:** VLMs provide observations. VerifyIQ performs reasoning and decisions.

## 2. Why an Agent Framework, Not a Model

Building a proprietary vision model for claim verification would be expensive, fragile, and quickly outdated. The VLM landscape evolves rapidly — every quarter brings better models with improved visual reasoning, lower cost, and broader capabilities. Locking into a single model would mean locking into today's capabilities.

By architecting VerifyIQ as an agent framework with a pluggable provider layer, we:

- **Future-proof** the system — swap in better VLMs as they become available
- **Let users choose** their provider based on cost, accuracy, latency, or privacy requirements
- **Enable comparison** — run the same claims through multiple providers and compare results
- **Support local models** for air-gapped or privacy-sensitive deployments
- **Avoid VLM lock-in** — no single provider dependency in the core reasoning layer

## 3. Why Deterministic Reasoning

The core reasoning engine — `RuleEngine`, `RiskAnalyzer`, `SeverityEngine`, and `OutputValidator` — is built from deterministic components whose behavior is fully specified by code, not inferred from a model.

**Strengths.** Deterministic components produce the same output for the same input every time. This is non-negotiable when the output is a claim decision. We can unit-test every decision path, audit any verdict by re-running the pipeline, and guarantee that a bug fix improves behavior predictably. There is no hallucination risk inside the rule engine, no prompt-drift, no API version skew affecting core logic.

**Weaknesses.** Deterministic code cannot handle genuinely novel edge cases. If a claim arrives with a damage type or object part outside the known taxonomy, the rule engine defaults to `not_enough_information`. It has no intuition, no world knowledge, and no capacity to generalize. That is a deliberate tradeoff: we prefer a clean "I don't know" over a confident wrong answer.

## 4. Why VLM + Rules Instead of End-to-End LLM

A pure end-to-end VLM approach — show an image, ask "is this claim valid?", get a yes/no — is tempting but fundamentally unsuitable for production verification.

**The VLM is an observer, not a judge.** We confine the VLM to a single responsibility — extracting structured observations from images. The decision-making layer is self-contained, testable offline, and immune to model deprecations or service outages. Changing the VLM provider changes only the quality of observations, never the decision logic.

**Rules give guaranteed behavior.** The `RuleEngine.evaluate` method enumerates six decision paths, each with explicit preconditions, and returns one of three statuses. There is no ambiguity, no temperature-dependent variance, no chance of a model refusing to answer.

**Rules cost nothing per inference.** The reasoning engine adds zero API cost and near-zero latency. All API spend goes to the VLM provider for observation extraction.

The tradeoff is expressiveness. A VLM can reason about a cracked windshield while noting rust patterns and an expired inspection sticker in a single holistic judgment. Our rule engine cannot. It decomposes claims into atomic comparisons — damage type, object part, confidence threshold — and composes them mechanically. For the narrow domain of structured claim verification, this decomposition is sufficient and vastly more reliable.

## 5. Why Reliability Matters

A verification system that crashes on bad input is worse than no system at all. Every claim must produce some output, even when components fail.

Every component call inside `ClaimProcessor.process_claim` is individually wrapped in `try/except` blocks with sensible fallback outputs. If the VLM provider throws (service down, rate limited, malformed response), we get a degraded vision result with `damage_visible: false` and a diagnostic note. If `RuleEngine` fails, we produce a `not_enough_information` verdict. If `DecisionAgent.build_output_row` encounters an inconsistency, `fallback_output` guarantees a structurally valid row.

`Safe Mode` is a first-class architectural constraint. `ImageValidator` rejects corrupt files before they reach the pipeline. `SubmissionCritic` post-processes every row to catch contradictions. `OutputValidator._consistency_check` performs per-row sanity enforcement. Reliability is layered, overlapping, and non-negotiable.

## 6. Why Explainability Matters

Every VerifyIQ decision carries a `claim_status_justification` string that reconstructs the reasoning. The justification is constructed from the actual decision path taken by the rule engine, not a post-hoc rationalization. A judge or auditor can trace exactly how a verdict was reached.

We expose the full decision context in every output row: `evidence_standard_met_reason`, `risk_flags`, `issue_type`, `object_part`, `severity`, `supporting_image_ids`. Nothing is hidden behind a model call that cannot be inspected.

Black-box decisions are unacceptable in domains where money and trust are at stake. VerifyIQ's architecture makes auditing tractable because the justification was built step-by-step, not generated by a black box.

## 7. What VerifyIQ Is Not

| Misconception | Reality |
|---|---|
| "VerifyIQ is an AI model" | VerifyIQ is an agent framework. It does not contain a proprietary vision model. Users bring their own VLM. |
| "VerifyIQ makes autonomous insurance decisions" | VerifyIQ produces structured recommendations with confidence levels. Human review can be configured for borderline cases. |
| "VerifyIQ only works with Gemini" | Gemini is one of many supported providers. The provider interface is pluggable. |
| "VerifyIQ is a black-box classifier" | Every decision includes a full traceable justification chain. |
| "VerifyIQ is a pure LLM system" | The decision engine is deterministic. VLMs are used only for observation extraction. |

## 8. Long-Term Vision

VerifyIQ's current architecture is a foundation, not a ceiling. The long-term vision includes:

**Multi-provider consensus.** Run multiple VLMs in parallel and reach consensus. If providers disagree, detect the conflict and escalate.

**Real-time processing.** Replace the current sequential batch loop with parallel claim evaluation, streaming vision results, and progressive output construction.

**Automated fraud detection networks.** Graph-based fraud detection: shared IPs, device fingerprints, cross-claim image similarity, behavioral anomaly detection.

**Cross-claim consistency checking.** Pattern detection across a single claimant's history. Surface correlations to human reviewers.

**Self-improving rule engines.** Feedback loop comparing predictions against human review outcomes to tune thresholds and discover new compatible damage type pairs.

These are long-term directions. The short-term priority is correctness, reliability, and auditability. A system that does not crash, does not hallucinate, and can explain every answer is the prerequisite for any of these future capabilities.
