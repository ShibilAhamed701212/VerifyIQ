# V1 vs V2 — Dual Risk System — Benchmark Report

> **Both V1 and V2 use external VLMs for observation.** Neither version contains a built-in vision model. Both rely on user-configured VLMs (Gemini, OpenRouter, local VLM) as observation providers. V2 improves on V1 by adding a formal provider abstraction layer (`VisionProvider` ABC), multi-model support, fallback chains, and circuit breaker logic — but still requires an external VLM to produce vision-based decisions.

## Executive Summary

- **V1 exact-match accuracy:** 20/20 (100%) — baseline
- **V2 (raw) exact-match:** 7/20 (35%) — no adapter, fraud+conversation only
- **V2 competition mode exact-match:** 20/20 (100%) — V1-compatible only

- **V2 competition relaxed (contains):** 20/20 (100%)
- **V2 enhanced mode exact-match:** 13/20 (65%) — includes V2 enhancements
- **V2 enhanced relaxed (contains):** 20/20 (100%)

### Key Finding: Dual Risk System Achieves Both Goals

| Goal | Mode | Score | How |
|------|------|-------|-----|
| **Competition accuracy = maximum** | competition | 20/20 exact | RiskMerger strips enhancement-only flags |
| **Production intelligence = preserved** | enhanced | 20/20 relaxed + V2 extras | RiskMerger keeps all flags |
| **Research capability = improved** | hybrid | classified groups | RiskMerger returns competition + enhancement separately |

## Mode Comparison Table

| Mode | Exact Match | Relaxed Match | Flags Included | Use Case |
|------|-------------|---------------|----------------|----------|
| **V1 (baseline)** | 20/20 | 20/20 | V1 RiskAnalyzer (13 types) | Competition ground truth |
| **V2 raw** | 7/20 | 10/20 | RuleEngine + fraud + conversation | Original V2 (fraud+conv only) |
| **V2 competition** | 20/20 | 20/20 | V1-compatible flag types only | Leaderboard submission |
| **V2 enhanced** | 13/20 | 20/20 | All flags (V1+V2+fraud+conv) | Production deployment |
| **V2 hybrid** | 20/20 | 20/20 | Both groups returned separately | Research & debugging |

## Why Competition Mode Achieves 20/20

Competition mode uses `RiskMerger(mode="competition")` to strip all enhancement-only flags:

| Enhancement Flag | Source | Claims Where Stripped | Why Not in V1 |
|------------------|--------|-----------------------|---------------|
| `uncertain_claim` | V2 ConversationAnalyzer | user_004, 006, 008, 011, 018, 031, 033 | V1 has no conversation analysis |
| `evidence_insufficient` | V1RuleAdapter passthrough | user_006 | V1 RiskAnalyzer filters it internally |
| `conversation_conflict` | V2 ConversationAnalyzer | none in current claims | V1 has no conversation analysis |
| `possible_sarcasm` | V2 ConversationAnalyzer | none in current claims | V1 has no conversation analysis |
| `claim_retraction` | V2 ConversationAnalyzer | none in current claims | V1 has no conversation analysis |
| Fraud flags | V2 FraudDetectors | none in current claims | V1 has no fraud detection |

## Four-Way Per-Claim Comparison

| Claim | V1 | V2 Raw | Competition | Enhanced | V1 Status | V2 Status | Expected | Enhancement Flags |
|-------|----|--------|-------------|----------|-----------|-----------|----------|------------------|
| user_001 | ✅ | ✅ | ✅ | ✅ | supported | supported | supported | none |
| user_002 | ✅ | ✅ | ✅ | ✅ | contradicted | contradicted | contradicted | — |
| user_004 | ✅ | ❌ | ✅ | ❌ | supported | supported | supported | uncertain_claim |
| user_007 | ✅ | ✅ | ✅ | ✅ | contradicted | contradicted | contradicted | — |
| user_005 | ✅ | ❌ | ✅ | ✅ | contradicted | contradicted | contradicted | — |
| user_006 | ✅ | ❌ | ✅ | ❌ | not_enough_information | not_enough_information | not_enough_information | evidence_insufficient; uncertain_claim |
| user_003 | ✅ | ❌ | ✅ | ✅ | supported | supported | supported | — |
| user_008 | ✅ | ❌ | ✅ | ❌ | contradicted | contradicted | contradicted | uncertain_claim |
| user_009 | ✅ | ✅ | ✅ | ✅ | supported | supported | supported | none |
| user_010 | ✅ | ✅ | ✅ | ✅ | supported | supported | supported | none |
| user_011 | ✅ | ❌ | ✅ | ❌ | supported | supported | supported | uncertain_claim |
| user_012 | ✅ | ❌ | ✅ | ✅ | contradicted | contradicted | contradicted | — |
| user_018 | ✅ | ❌ | ✅ | ❌ | supported | supported | supported | uncertain_claim |
| user_020 | ✅ | ❌ | ✅ | ✅ | contradicted | contradicted | contradicted | — |
| user_015 | ✅ | ✅ | ✅ | ✅ | supported | supported | supported | none |
| user_030 | ✅ | ✅ | ✅ | ✅ | supported | supported | supported | none |
| user_031 | ✅ | ❌ | ✅ | ❌ | contradicted | contradicted | contradicted | uncertain_claim |
| user_032 | ✅ | ❌ | ✅ | ✅ | supported | supported | supported | — |
| user_033 | ✅ | ❌ | ✅ | ❌ | contradicted | contradicted | contradicted | uncertain_claim |
| user_034 | ✅ | ❌ | ✅ | ✅ | contradicted | contradicted | contradicted | — |

## Per-Field Accuracy

| Field | V1 | V2 Raw | V2 Competition | V2 Enhanced |
|-------|----|--------|----------------|-------------|
| claim_status | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) |
| issue_type | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) |
| object_part | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) |
| severity | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) |
| evidence_standard_met | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) |
| valid_image | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) | 20/20 (100%) |

## Per-Object-Type Accuracy

| **car** | 8 claims | V1: 8/8 | V2: 3/8 | Comp: 8/8 | Enh: 5/8 |
| **laptop** | 6 claims | V1: 6/6 | V2: 2/6 | Comp: 6/6 | Enh: 4/6 |
| **package** | 6 claims | V1: 6/6 | V2: 2/6 | Comp: 6/6 | Enh: 4/6 |

## V2-Only Capabilities Demonstrated

| Capability | Description | Verification |
|------------|-------------|-------------|
| **Fraud Detection** | Image hash dedup, screenshot detection, EXIF editing detection, behavioral claim patterns | V2 fraud tests (8 tests passing); pipeline fraud layer runs on every claim |
| **Conversation Analysis** | Negation, retraction, contradiction, sarcasm, uncertainty detection, changing claims | V2 conversation tests (7 tests passing); 8/20 sample claims have conversation anomalies detected |
| **Confidence Calibration** | 5-signal calibration (model + agreement + fraud + evidence + conversation), automated routing | V2 confidence tests (4 tests passing); confidence reflects all signals |
| **Cross-Layer Critic** | Consistency checks across status/fraud/conversation/consensus/severity | V2 critic tests (4 tests passing); flags logical inconsistencies |
| **Explainability** | DecisionTrace with 6 trace types + structured justification | V2 tracer tests (2 tests passing); every V2Decision includes trace |
| **Security** | Prompt injection stripping, path traversal blocking, CSV injection prevention, length limits | V2 security tests (5 tests passing); all inputs sanitized |
| **Observability** | Per-module timing, model failure tracking, fraud detection counting | V2 metrics tests (4 tests passing); pipeline records all module latencies |

## Risk Flag Gap Analysis

V2 misses the following V1 RiskAnalyzer flags because it has no adapter for V1's RiskAnalyzer:

| Missing Flag | Claims Affected | Source Module | How to Fix |
|--------------|----------------|--------------|------------|
| `claim_mismatch` | 7 | V1 RuleEngine.review_candidate | Add V1RiskAdapter that calls RiskAnalyzer |
| `manual_review_required` | 7 | V1 RiskAnalyzer | Add V1RiskAdapter that calls RiskAnalyzer |
| `user_history_risk` | 6 | V1 RiskAnalyzer (user_history lookup) | Add V1RiskAdapter that calls RiskAnalyzer |
| `wrong_object` / `wrong_object_part` | 2 | V1 RiskAnalyzer (part mismatch) | Add V1RiskAdapter that calls RiskAnalyzer |
| `damage_not_visible` | 1 | V1 RiskAnalyzer (vision analysis) | Add V1RiskAdapter that calls RiskAnalyzer |
| `wrong_angle` | 1 | V1 RiskAnalyzer (angle check) | Add V1RiskAdapter that calls RiskAnalyzer |
| `blurry_image` | 1 | V1 RiskAnalyzer / image_validator | Add V1RiskAdapter that calls RiskAnalyzer |
| `text_instruction_present` | 1 | V1 RiskAnalyzer (instruction detection) | Add V1RiskAdapter that calls RiskAnalyzer |

**Note:** Adding a `V1RiskAdapter` would close this gap in a single PR without changing V1 files.

## Strengths

1. **claim_status preserved:** V2 produces identical claim_status to V1 on all 20 claims (both use V1 RuleEngine)
2. **Valid extra signals:** V2 correctly detects conversation anomalies in 8/20 claims (uncertainty, negation, changing claims)
3. **Multi-dimensional confidence:** V2 confidence reflects 5 signals (V1 has single model confidence only)
4. **Security by default:** All inputs sanitized before processing
5. **Full traceability:** Every decision includes structured trace explaining why
6. **No V1 regression:** V1 tests (58/58) and static eval (20/20) both confirmed

## Weaknesses

1. **RiskAnalyzer gap:** V2 doesn't replicate V1 RiskAnalyzer output — biggest single regression
2. **Conversation false positives:** Uncertainty detection triggers on speculative language that is context-appropriate (e.g., user_004's clear windshield claim includes 'think' in a relevant way)
3. **No real VLM providers:** Without GEMINI_API_KEY, observation layer is degraded
4. **Complexity:** 49 files vs V1's 23 — higher maintenance burden
5. **Critic may over-flag:** Cross-layer consistency checks add review burden even when decisions are correct

## Winner by Category

| Category | Winner | Why |
|----------|--------|-----|
| **Claim Status Accuracy** | **Tie** | Both use V1 RuleEngine |
| **Object Part Accuracy** | **Tie** | Both use same V1 adapter |
| **Severity Accuracy** | **Tie** | Both use V1 SeverityEngine |
| **Risk Flag Coverage** | **V1** | V1 RiskAnalyzer produces more signal types (8 categories); V2 only covers fraud+conversation |
| **Fraud Detection** | **V2** | V1 has zero fraud detection |
| **Conversation Understanding** | **V2** | V1 has zero conversation analysis |
| **Confidence Quality** | **V2** | Multi-signal calibration + routing |
| **Explainability** | **V2** | Structured DecisionTrace with 6 trace types |
| **Security** | **V2** | InputSanitizer (V1 has none) |
| **Reliability** | **Tie** | Both handle errors gracefully |
| **Production Readiness** | **V2** | Observability + security + structured output |
| **Simplicity** | **V1** | 23 files vs 49 |