# Adversarial Testing

## Overview

100 synthetic adversarial claims across 11 categories were processed through the VerifyIQ pipeline. The evaluation was conducted without a `GEMINI_API_KEY` (degraded Safe Mode), meaning all claims received empty vision analysis. This primarily tests Safe Mode robustness, image validation, and deterministic CV components — not semantic decision-making.

- **Total claims:** 100
- **Pipeline crashes:** 0 (zero crash rate: 10/10)
- **Graceful degradation rate:** 100% (all 100 claims produced valid schema output)
- **Claims with `manual_review_required`:** 100
- **Claims with `damage_not_visible`:** 95

All claims returned `issue_type=unknown` and `claim_status=not_enough_information` because the evidence checker could not validate evidence standards against empty vision results. Full Gemini-powered analysis would produce different (likely more varied) results.

## Categories Tested

### 1. Negation (10 claims)
Claims containing negated damage statements: "There is no dent", "The crack is NOT on the windshield", "I am not reporting any damage."

Results: 10/10 → `not_enough_information`, all with `damage_not_visible;manual_review_required`. The system cannot distinguish "There is a dent" from "There is NO dent" because `risk_analyzer.py:157-166` uses keyword matching on words like "dent", "crack", "scratch" regardless of negation context. The claim parser extracts damage type from text without understanding negation.

### 2. Sarcasm (8 claims)
Sarcastic claims without explicit damage keywords: "Oh great, another perfect delivery", "Love how the bumper fell off", "Brilliant packaging."

Results: 8/8 → `not_enough_information`. Claims without explicit damage keywords (e.g., "fell off", "destroyed") avoided the `damage_not_visible` flag entirely because the keyword list at `risk_analyzer.py:161-164` misses these terms. Two claims received `text_instruction_present` from the CV text detector.

### 3. Contradictory Conversations (10 claims)
Dialogue where the customer retracts or contradicts their original claim: "windshield shattered → actually maybe not even a crack → just a scratch."

Results: 10/10 → `not_enough_information`. The claim parser at `claim_parser.py` extracts the first or dominant damage type without tracking contradiction across dialogue turns. The system has no conversation-state awareness.

### 4. Misleading Claims (10 claims)
Claiming water damage when lines on a screen suggest a crack, or claiming a dent when visible damage is a scratch.

Results: 10/10 → `not_enough_information`. Without Gemini, the system cannot verify any claim against image content. The parser extracts whatever damage type the user asserted.

### 5. OCR Attacks (8 claims)
Images containing text overlays, watermarks, stamps, and annotations intended to confuse the VLM.

Results: 8/8 → `not_enough_information`. The CV text detector at `cv/text_detector.py:39-56` flagged some images with `text_instruction_present` (e.g., claims 040, 046). However, without Gemini, the system cannot distinguish between "DAMAGE CONFIRMED" and "FOR REFERENCE ONLY" text content.

### 6. Wrong Objects (10 claims)
Laptop claims paired with car images, car claims with package images, etc.

Results: 10/8 → `not_enough_information`. The `ObjectValidator` CV component (`risk_analyzer.py:137-142`) detects wrong objects deterministically, but only for claims with real images — claims referencing missing/nonexistent paths (5 of 10) skip object validation entirely.

### 7. Low Evidence (10 claims)
No images, single blurry images, wrong angles, insufficient lighting, pixelated images.

Results: 10/10 → `not_enough_information`. The evidence checker rejects all claims in Safe Mode because every vision field is `"unknown"`. The blur detector flagged one claim with `blurry_image`. The system cannot distinguish "genuinely insufficient evidence" from "API unavailable."

### 8. Conflicting Images (8 claims)
Images showing different damage types, inconsistent backgrounds, photos taken at different times.

Results: 8/8 → `not_enough_information`. The `conflicting_images` flag at `risk_analyzer.py:75-77` depends on Gemini's per-image assessment, which was empty. No claim received `claim_mismatch` from image inconsistency.

### 9. History Fraud (10 claims)
Fabricated user IDs (`user_hf_001` through `user_hf_010`) with high-claim-count patterns and suspicious history.

Results: 10/10 → `not_enough_information`. The fabricated user IDs have no entries in `user_history.csv`, so `_get_user_history()` at `claim_processor.py:54-55` returns `None` and no `user_history_risk` flag is raised. History fraud detection only works for known user IDs.

### 10. Image Text Manipulation (8 claims)
Photoshopped text, annotations, measurement markers, stamps, and information overlays on images.

Results: 8/8 → `not_enough_information`. The CV text detector flagged some with `text_instruction_present`, but the `possible_manipulation` flag (set at `risk_analyzer.py:84-85` based on Gemini notes containing "photoshopped", "edited", "manipulated", or "altered") was never triggered. The deterministic CV layer catches text presence but not manipulation.

### 11. Non-Original Images (8 claims)
Screenshots, stock photos, rephotographed images, photos of photos, insurance report screenshots.

Results: 8/8 → `not_enough_information`. The `non_original_image` flag at `risk_analyzer.py:86-87` requires Gemini notes containing "screenshot", "stock photo", "stock image", "template", or "non-original". Without Gemini, no claim received this flag. This is the most critical detection gap in Safe Mode — non-original images are a major fraud vector.

## Key Findings

- **Crash resistance: 10/10** — Zero crashes across all 100 adversarial claims. Every component call in `claim_processor.py:57-160` is individually wrapped in try/except with sensible fallback defaults. The Gemini retry loop at `vision_analyzer.py:115-137` has an upper bound of 5 attempts with exponential backoff.
- **Graceful degradation: 10/10** — Every claim produces valid output conforming to the output schema. `OutputValidator` at `output_validator.py:36-65` coerces invalid enum values to safe defaults. `SubmissionCritic` at `submission_critic.py:20-38` post-processes all rows for contradictions. No malformed output escaped.
- **Adversarial detection without Gemini: 0/10** — Non-original images, manipulation, conflicting evidence, wrong objects, OCR attacks, sarcasm, negation, contradictory conversations, misleading claims — all produced the same `not_enough_information` verdict with `manual_review_required`.
- **Output consistency checks:** `OutputValidator._consistency_check()` at `output_validator.py:67-100` and `SubmissionCritic` functions at `submission_critic.py:47-107` caught potential logical contradictions (e.g., `supported` with `issue_type=none` → `contradicted`; critical risk flags without `manual_review_required` → add it).

## Robustness Score Summary

| Component | Score | Notes |
|-----------|-------|-------|
| Crash resistance | 10/10 | Zero crashes, per-component try/except |
| Graceful degradation | 10/10 | Valid schema output on every claim |
| Adversarial detection | 0/10 | No detection without Gemini |
| Edge case handling | 5/10 | Handles consistently but never distinguishes |
| **Overall** | **4.5/10** | Safe Mode only; would improve with Gemini |

**Critical recommendation:** With a `GEMINI_API_KEY` enabled, the system would likely score significantly higher on adversarial detection (potentially 6-7/10) because Gemini provides the semantic layer needed to detect negation, sarcasm, manipulation, non-originality, and conflicting evidence. Deterministic adversarial defenses — heuristic image origin checks, conversation coherence analysis, user history pattern matching — should be added as a second layer that operates independently of the VLM.
