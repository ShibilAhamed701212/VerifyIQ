# Adversarial Evaluation Report

## Overview
- Total adversarial claims: 100
- Categories tested: 11
- Pipeline crashes: 0
- Graceful degradations: 100

**Important context:** This adversarial evaluation was run **without GEMINI_API_KEY** (degraded mode). The Gemini vision analyzer returned empty analysis for all claims, causing the entire pipeline to operate in Safe Mode. All 100 claims returned `issue_type=unknown` and `claim_status=not_enough_information` because the evidence checker could not validate evidence standards against empty vision results. The results below primarily test Safe Mode robustness, image validation, and deterministic CV components — not semantic decision-making. Full Gemini-powered analysis would produce different (likely more varied and discerning) results.

## Category Results

### 1. Negation (10 claims)
- Claims tested: "I did NOT say X", "There is NO dent", "The crack is NOT on the windshield", etc.
- Results: 10/10 → `not_enough_information`, all with `damage_not_visible;manual_review_required`
- Failures: System lacks ability to detect negation because it relies entirely on Gemini for semantic understanding. The rule engine's keyword-based `_user_claimed_damage()` method still fires on words like "dent", "crack", "scratch" even when negated, causing `damage_not_visible` flag to be set. The parser extracts claimed damage type from text without understanding negation.
- Assessment: The system cannot distinguish "There is a dent" from "There is NO dent." This is a critical gap that only a VLM or NLU layer can fix.

### 2. Sarcasm (8 claims)
- Claims tested: "Great, another perfect delivery", "Love how the bumper fell off", "Brilliant packaging", etc.
- Results: 8/8 → `not_enough_information`
- Failures: Claims using sarcastic language without explicit damage keywords (e.g., "Love how the bumper fell off") avoided `damage_not_visible` because the keyword matcher didn't trigger. Claims like "Box is completely destroyed" missed keyword "destroyed" entirely. Two claims (adv_sarcasm_014, adv_sarcasm_016) got `text_instruction_present` from the CV text detector.
- Assessment: Sarcasm is completely invisible to the system. The keyword-based damage detector has gaps (missing "destroyed", "fell off", etc.) and no tonality awareness.

### 3. Contradictory Conversations (10 claims)
- Claims tested: Customer says damaged then retracts; multiple changes of story
- Results: 10/10 → `not_enough_information`
- Failures: The claim parser extracts the first or dominant damage type from the conversation text without tracking contradiction across dialogue turns. The system has no conversation-state awareness. Some claims also got `text_instruction_present` and `blurry_image` flags from the deterministic CV checks.
- Assessment: The system is vulnerable to users who walk back claims mid-conversation. A claim that starts with "windshield shattered" and ends with "maybe not even a crack" will still trigger `damage_not_visible` against the originally parsed issue.

### 4. Misleading User Claims (10 claims)
- Claims tested: Claiming water damage when lines are visible (likely cracked screen), dent when scratch, crushed when box is fine
- Results: 10/10 → `not_enough_information`
- Failures: The system cannot verify user claims against image content without Gemini. All claims default to `not_enough_information` because the evidence standard is never met. The parser extracts whatever damage type the user asserted (water_damage, dent, etc.).
- Assessment: Without vision analysis, the system has no defense against misleading claims. A user can claim "water damage" for a cracked screen and the system can neither confirm nor refute it.

### 5. OCR Attacks (8 claims)
- Claims tested: Images with text overlays, watermarks, stamps, annotations
- Results: 8/8 → `not_enough_information`
- Failures: The CV text detector (Tesseract-based) correctly flagged some images with `text_instruction_present` (e.g., adv_ocr_attack_040, adv_ocr_attack_046). However, without Gemini vision to analyze what the text says, the system cannot distinguish between "DAMAGE CONFIRMED" stamps and "FOR REFERENCE ONLY" disclaimers.
- Assessment: The deterministic text detector partially mitigates OCR attacks by flagging images with text, but cannot evaluate adversarial text content. Text overlays intended to confuse the VLM go undetected at the semantic level.

### 6. Wrong Objects (10 claims)
- Claims tested: Laptop claim with car images, car claim with laptop images, package claim with unrelated images
- Results: 10/10 → `not_enough_information`
- Failures: The `ObjectValidator` CV component detects wrong objects deterministically, but only for claims with real images (not `nonexistent/missing.jpg` paths). Claims referencing missing images all fall through to `damage_not_visible;manual_review_required`. The system cannot match images to claimed object type without Gemini.
- Assessment: The CV object validator provides weak wrong-object detection, but the primary defense (Gemini) is absent. Claims referencing missing images bypass object validation entirely.

### 7. Low Evidence (10 claims)
- Claims tested: No images, single blurry image, wrong angle, insufficient lighting, pixelated images
- Results: 10/10 → `not_enough_information`
- Failures: The evidence checker correctly rejects all claims because the vision result is empty (no damage type, no object part, no confidence). The deterministic blur detector flagged some with `blurry_image` (adv_low_evidence_062). However, the system cannot distinguish between "genuinely insufficient evidence" and "empty vision due to API failure."
- Assessment: The evidence checker is overly conservative in Safe Mode — it cannot evaluate any claim because every vision field is "unknown." This means legitimate low-evidence claims get the same treatment as API-failure claims.

### 8. Conflicting Images (8 claims)
- Claims tested: Different damage types across images, inconsistent backgrounds, photos taken at different times
- Results: 8/8 → `not_enough_information`
- Failures: The `conflicting_images` flag in the risk analyzer depends on `image_analysis.get("conflicting_images", False)` from Gemini's per-image assessment. Since Gemini returned empty, `conflicting_images` was never True. No claim got the `claim_mismatch` or additional risk flags from image inconsistency.
- Assessment: The system cannot detect conflicting image evidence without Gemini. A user submitting photos of different cars or different damage types would not be flagged.

### 9. History Fraud (10 claims)
- Claims tested: Users with high claim counts, suspicious patterns, multiple rejections
- Results: 10/10 → `not_enough_information`
- Failures: User history data (`user_history.csv`) was loaded but the history_fraud claims used adversarial user IDs (`user_hf_001` through `user_hf_010`) that likely have no entries in the history file, so no `user_history_risk` flag was raised. The `_get_user_history()` method returned `None` for unknown users.
- Assessment: The history fraud detection relies on the user_history.csv having entries for the user IDs. Unknown/fabricated user IDs get no history scrutiny. Even known users would only trigger basic checks (claim count > 3, rejections > 2), not behavioral pattern analysis.

### 10. Image Text Manipulation (8 claims)
- Claims tested: Photoshopped text, annotations, measurement markers, information overlays, stamps
- Results: 8/8 → `not_enough_information`
- Failures: The CV text detector flagged some manipulated images with `text_instruction_present`, but the `possible_manipulation` flag (which requires Gemini notes containing "photoshopped", "edited", "manipulated", or "altered") was never set. The system cannot detect image manipulation without VLM analysis.
- Assessment: The deterministic CV layer catches text presence but not manipulation. All 8 claims were processed as if nothing was wrong with the images beyond being "insufficient evidence."

### 11. Non-Original Images (8 claims)
- Claims tested: Screenshots, stock photos, rephotographed images, photos of photos, insurance report photos
- Results: 8/8 → `not_enough_information`
- Failures: The `non_original_image` risk flag requires Gemini notes containing "screenshot", "stock photo", "stock image", "template", or "non-original". Since Gemini returned empty, no claim received this flag. The output_validator and critic ensure `manual_review_required` is added, but no distinction is made between original and non-original images.
- Assessment: This is the most critical gap in Safe Mode. Non-original images (screenshots, stock photos, rephotographed images) are a major fraud vector, and the system has zero defense against them without Gemini.

## Aggregate Metrics

| Metric | Value |
|--------|-------|
| Total claims | 100 |
| Zero crashes | 100% |
| Graceful degradation rate | 100% |
| Claims with manual_review_required | 100 |
| Claims with damage_not_visible | 95 |
| Claims with blurry_image | 9 |
| Claims with text_instruction_present | 12 |

## Failures Found

### False Positives
- None in the traditional sense since all claims returned `not_enough_information`. However, `damage_not_visible` was incorrectly set on 95/100 claims even for claims where damage might actually be visible (the system can't tell without Gemini). This is a false positive for the `damage_not_visible` flag in degraded mode.
- Negation claims where the user explicitly says "no damage" still triggered `damage_not_visible` because the keyword matcher found words like "dent" or "crack" and concluded damage was claimed.

### False Negatives
- **Non-original images (8/8 missed):** None of the 8 non-original image claims received the `non_original_image` risk flag because it depends on Gemini vision notes.
- **Image manipulation (8/8 missed):** None of the 8 image text manipulation claims received the `possible_manipulation` flag for the same reason.
- **Conflicting images (8/8 missed):** No claim received `claim_mismatch` from conflicting images because Gemini never set `conflicting_images=True`.
- **Wrong objects (potentially missed):** The deterministic `ObjectValidator` runs, but only on valid images. Claims referencing missing/nonexistent image paths skip object validation entirely.
- **History fraud (missed):** Unknown adversarial user IDs bypass history checks entirely.

### Brittle Rules
- **Keyword-based damage detection** (`_user_claimed_damage` in `risk_analyzer.py:161-166`): The keyword list is incomplete. Words like "destroyed", "fell off", "shattered" (as standalone), "cracked" (as adjective), and "broken" all have gaps. Sarcastic claims without explicit keywords avoid the `damage_not_visible` flag.
- **evidence_standard_met** always returns `false` when vision is empty, making Safe Mode completely unable to evaluate any claim. There is no "last resort" check that says "even without Gemini, if images exist and are valid, consider reviewing manually."
- **`parts_conflict` logic** in `rule_engine.py:121-126`: When `visible_object_part` is "unknown" and `claimed_object_part` is not, the method returns `True` (conflict). But when both are "unknown", no conflict. This means empty vision always produces `parts_conflict=True` when the parser extracts a part — but the rule_engine never reaches that logic path because `evidence_standard_met=false` short-circuits at path 1.

### Confidence Weaknesses
- **Confidence is always 0.0** when Gemini is unavailable. The rule_engine (path 5, `confidence < low_confidence_threshold`) would catch this, but path 1 (`evidence_standard_met=False`) short-circuits before confidence is ever evaluated.
- **No uncertainty quantification:** The system does not distinguish between "no evidence because images are missing" and "no evidence because API is down." Both collapse to `evidence_standard_met=false; claim_status=not_enough_information`.
- **`manual_review_required` is universal (100/100)** in degraded mode, which makes it a meaningless signal. With full Gemini, it would be a useful triage flag.

## Robustness Score

**Overall robustness: 4.5/10**

Scoring:
- Crash resistance: **10/10** — Zero crashes across all 100 adversarial claims. Every component has try/except with fallback defaults. The Safe Mode implementation is production-grade.
- Graceful degradation: **9/10** — Every claim produces valid output conforming to the schema, with justifications, even when every upstream component fails. No unhandled exceptions, no malformed output.
- Adversarial detection: **0/10** — Without Gemini, the system detects zero adversarial patterns. Non-original images, manipulation, conflicting evidence, wrong objects, OCR attacks, sarcasm, negation, contradictory conversations, misleading claims — all produce the same `not_enough_information` verdict.
- Edge case handling: **5/10** — Missing images are handled consistently (image validation catches nonexistent paths, but downstream processing treats all images the same). The system never crashes on edge cases but also never distinguishes between different types of edge cases.
- Safe Mode effectiveness: **4/10** — Safe Mode prevents crashes (excellent) but produces no actionable output (poor). All 100 claims go to manual review with "insufficient evidence" justification, which is correct but not helpful for triage.

## Verdict

**The adversarial evaluation reveals a system with excellent crash-safety but zero adversarial robustness when operating without its VLM backbone.**

**What holds up well:**
- The deterministic engineering is solid — 100/100 claims processed without a single crash, valid schema output every time, per-component exception handling works as designed.
- Image validation (size, format, integrity checks) prevents corrupted/malformed files from crashing the pipeline.
- The CV text detector provides some signal (12 claims flagged with `text_instruction_present`) even without Gemini.
- Output consistency checks (validator + critic) ensure no contradictory status/flags pairs escape.

**What can be exploited:**
- **Non-original images are completely invisible** — an attacker submitting screenshots, stock photos, or rephotographed images will not be flagged.
- **Bad-faith conversation manipulation is undetectable** — the system cannot identify retractions, contradictions, or sarcasm in claim conversations.
- **Wrong objects go unchecked** when images are missing or the CV object validator cannot match them.
- **History fraud bypasses scrutiny** with fabricated user IDs not found in the history CSV.
- **Misleading claims cannot be refuted** without visual confirmation from the VLM.

**Critical recommendation:** With Gemini API key enabled, the system would likely score significantly higher on adversarial detection (potentially 6-7/10) because Gemini would provide the semantic layer needed to detect negation, sarcasm, manipulation, non-originality, and conflicting evidence. The current 4.5/10 robustness score reflects Safe Mode performance only. **Deterministic adversarial defenses should be added** as a second layer that operates independently of the VLM — including heuristic image origin checks, conversation coherence analysis, and user history pattern matching — so the system has baseline fraud detection even in degraded mode.
