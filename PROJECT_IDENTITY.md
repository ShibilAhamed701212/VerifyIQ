# VerifyIQ — Project Identity

## 1. Why VerifyIQ Exists

Insurance and retail damage claim verification remains stubbornly manual. An adjuster reads a written claim, inspects photos, cross-references policy requirements, and makes a judgment call. The process is slow — days or weeks per claim — and inconsistent: two adjusters can reach opposite conclusions on the same evidence. At scale, this costs insurers billions in operational overhead, disputed payouts, and undetected fraud.

VerifyIQ exists to automate this pipeline. By combining structured claim parsing, computer vision, deterministic rule evaluation, and risk analysis, we make damage verification faster, fairer, and auditable. Every claim produces a verdict in seconds, not days, with a traceable justification chain that survives regulatory scrutiny.

## 2. Why Deterministic AI

We chose a primarily deterministic architecture because verification demands repeatability. Our pipeline — `ClaimProcessor` orchestrating `RuleEngine`, `RiskAnalyzer`, `SeverityEngine`, and `OutputValidator` — is built from components whose behavior is fully specified by code, not inferred from a model.

**Strengths.** Deterministic components produce the same output for the same input every time. This is non-negotiable when the output is a claim decision. We can unit-test every decision path, audit any verdict by re-running the pipeline, and guarantee that a bug fix improves behavior predictably. There is no hallucination risk inside the rule engine, no prompt-drift, no API version skew affecting core logic.

**Weaknesses.** Deterministic code cannot handle genuinely novel edge cases. If a claim arrives with a damage type or object part outside the known taxonomy, the rule engine defaults to `not_enough_information`. It has no intuition, no world knowledge, and no capacity to generalize. That is a deliberate tradeoff: we prefer a clean "I don't know" over a confident wrong answer.

## 3. Why Rules Instead of Pure LLMs

A pure end-to-end VLM approach — show an image, ask "is this claim valid?", get a yes/no — is tempting but fundamentally unsuitable for production verification.

Rules give us **guaranteed behavior**. The `RuleEngine.evaluate` method enumerates six decision paths, each with explicit preconditions, and returns one of three statuses: `supported`, `contradicted`, or `not_enough_information`. There is no ambiguity, no temperature-dependent variance, no chance of a model refusing to answer.

Rules cost **nothing per inference**. Running 44 claims through the rule engine adds zero API cost and near-zero latency. An equivalent LLM-based decision layer would cost dollars per evaluation cycle and introduce minutes of sequential latency.

Rules eliminate **API dependency for core logic**. The VLM is confined to a single responsibility — extracting observations from images via `VisionAnalyzer.analyze_images`. We use it for perception, not judgment. The decision-making layer is self-contained, testable offline, and immune to model deprecations or service outages.

The tradeoff is expressiveness. A VLM can reason about a cracked windshield while noting rust patterns and an expired inspection sticker in a single holistic judgment. Our rule engine cannot. It decomposes claims into atomic comparisons — damage type, object part, confidence threshold — and composes them mechanically. For the narrow domain of structured claim verification, this decomposition is sufficient and vastly more reliable.

## 4. Why Reliability Matters

A verification system that crashes on bad input is worse than no system at all — it creates a backlog, frustrates users, and erodes trust. Every claim must produce some output, even when components fail.

This principle drives several architectural decisions in VerifyIQ. Every component call inside `ClaimProcessor.process_claim` is individually wrapped in `try/except` blocks with sensible fallback outputs. If `VisionAnalyzer` throws because Gemini is down, we get a degraded vision result with `damage_visible: false` and a diagnostic note, not an unhandled exception. If `RuleEngine` fails, we produce a `not_enough_information` verdict with the error message captured. If `DecisionAgent.build_output_row` encounters an inconsistency, the `fallback_output` method guarantees a structurally valid row.

`Safe Mode` is not a backup plan — it is a first-class architectural constraint. `ImageValidator` rejects corrupt files before they reach the pipeline. `SubmissionCritic` post-processes every row to catch contradictions the pipeline missed. `OutputValidator._consistency_check` performs per-row sanity enforcement. Reliability is layered, overlapping, and non-negotiable.

## 5. Why Explainability Matters

Every VerifyIQ decision carries a `claim_status_justification` string that reconstructs the reasoning. The justification is not a post-hoc rationalization — it is constructed from the actual decision path taken by the rule engine. A judge or auditor can read: "Claimed crack on windshield. Visible scratch on door. Evidence standard satisfied with confidence 0.92. Consistency: status=supported incompatible with issue_type=none."

We expose the full decision context in every output row: `evidence_standard_met_reason`, `risk_flags`, `issue_type`, `object_part`, `severity`, `supporting_image_ids`. Nothing is hidden behind a model call that cannot be inspected.

Black-box decisions are unacceptable in domains where money and trust are at stake. An insurer needs to explain to a customer why their windshield replacement claim was denied. A regulator needs to audit 10,000 decisions for bias. VerifyIQ's architecture makes this tractable because the justification was built step-by-step, not generated by a black box.

## 6. Long-Term Vision

VerifyIQ's current architecture is a foundation, not a ceiling. The long-term vision includes:

**Multi-model vision.** Drop the single-VLM dependency by running multiple vision models (OpenCV heuristics, specialized small VLMs, Gemini as ensemble leader) and reaching consensus. If one model disagrees, the system should detect the conflict and escalate rather than degrade.

**Real-time processing.** Replace the current sequential batch loop with parallel claim evaluation, streaming vision results, and progressive output construction. A customer should upload a photo and get a preliminary verdict within seconds.

**Automated fraud detection networks.** Move beyond claim-count-based user history analysis toward graph-based fraud detection: shared IPs, device fingerprints, cross-claim image similarity, and behavioral anomaly detection across the entire claim corpus.

**Cross-claim consistency checking.** A single claimant submitting five windshield claims in six months should trigger automated pattern detection. VerifyIQ should surface this correlation to human reviewers without being explicitly programmed with the rule.

**Self-improving rule engines.** The rule engine's compatibility mappings and confidence thresholds are currently static. A feedback loop — comparing predictions against human review outcomes — could tune thresholds, discover new compatible damage type pairs, and surface taxonomy gaps for human curation.

These are long-term directions. The short-term priority is correctness, reliability, and auditability. A system that does not crash, does not hallucinate, and can explain every answer is the prerequisite for any of these future capabilities.
