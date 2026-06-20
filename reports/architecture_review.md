# Architecture Review

## Decision 1: Gemini as the single vision model

**Strengths:**
- Single model eliminates cross-model inconsistency — you always get one opinion. (`vision_analyzer.py:117-124`)
- `gemini-3.1-flash-lite-preview` is cost-effective; it's Google's cheapest multimodal tier. (`config.py:24`)
- The model is called with `temperature=0.0` which makes outputs as deterministic as Gemini gets. (`config.py:27`)
- The Gemini SDK supports JSON mode via `response_mime_type="application/json"`, which is exactly what the structured extraction needs. (`vision_analyzer.py:122`)

**Weaknesses:**
- **Single point of failure.** If Gemini is down, rate-limited, or returns empty, the entire pipeline falls back to "unknown" defaults — nothing else can produce vision output. (`vision_analyzer.py:85-86`, `claim_processor.py:96-98`)
- The model name is hardcoded at `config.py:24`. A model deprecation or rename breaks the system silently (the fallback is just "client not available").
- No cross-validation. One model call per claim, one chance to get it right. No ensemble, no second-opinion check.
- The retry logic only handles `RESOURCE_EXHAUSTED` / 429 errors — any other API error immediately returns `_empty_analysis`. (`vision_analyzer.py:131-137`)

**Alternatives:**
1. **GPT-4o** — Stronger at fine-grained visual detail (text in images, small object defects). Cons: ~5-10x cost per call, OpenAI's JSON mode is less reliable than Gemini's native `response_mime_type`.
2. **Open-source VLM (Llava-NeXT / Qwen-VL)** — Can run locally, zero API cost, no rate limits. Cons: significantly lower accuracy on nuanced damage assessment, requires GPU hardware.
3. **Hybrid (OpenCV + small VLM + Gemini enhancement)** — CV handles basic checks (blur, crop), a small model (e.g., CLIP + classifier) handles object/damage classification, Gemini only for ambiguous cases. Cons: more moving parts, higher maintenance surface, 2-3x development time.

**Would we still choose it?** Yes — for a 24-hour hackathon, shipping with one well-integrated VLM is correct. The cost-to-accuracy ratio of Gemini Flash Lite is hard to beat. Post-hackathon, the team should add at least a GPT-4o fallback when Gemini returns errors.

---

## Decision 2: Rule engine instead of end-to-end VLM

**Strengths:**
- Fully deterministic, testable, and explainable. Every decision has a 6-path if/elif chain. (`rule_engine.py:33-88`)
- `COMPATIBLE_DAMAGE_TYPES` maps real-world ambiguity (crack ≈ glass_shatter, stain ≈ water_damage). (`rule_engine.py:103-108`)
- Review candidate detection at `0.50 ≤ confidence < 0.80` creates a sensible triage band. (`rule_engine.py:14-16, 98`)
- The engine never calls external models — zero latency, zero cost, zero API dependency.

**Weaknesses:**
- **The hardcoded compatible types are fragile.** `("stain", "water_damage")` is a one-way door — the system treats stain-as-water-damage as compatible, but those are genuinely different damage modes requiring different remediation. (`rule_engine.py:106-107`)
- `_parts_conflict` treats any unknown vision part as a conflict when a part is claimed. (`rule_engine.py:124-125`) This means `claimed_part="door" + vision_part="unknown"` → contradicted, even when the VLM just couldn't identify the part.
- No fuzzy matching on damage types. A tiny string difference between what the parser extracts and what the VLM detects results in a mismatch. Only exact string matches or the hardcoded compatibility table work.
- The `review_candidate` band (0.50-0.80) doesn't differentiate by claim object or damage type — a 0.55 on glass shatter and a 0.55 on a scratch get treated identically.

**Alternatives:**
1. **End-to-end VLM prompting** — "Given this claim and these images, what's the status?" One call, simpler code. Cons: non-deterministic, harder to debug, expensive, no explainability.
2. **Learned classifier** — Train a damage-type classifier on the VLM embeddings. Cons: needs labeled training data the team doesn't have.
3. **Fuzzy rule engine** — Use string similarity (Levenshtein, embedding cosine similarity) for damage type matching instead of exact equality. Cons: introduces nondeterminism and threshold tuning.

**Would we still choose it?** Yes — the rule engine is the right architectural call. The determinism is essential for an evaluable submission. However, the `_parts_conflict` logic needs softening: "unknown" from the VLM should not automatically contradict a claimed part.

---

## Decision 3: Static + Live dual evaluation

**Strengths:**
- **Live evaluation** (`evaluate.py`) runs the full pipeline end-to-end including Gemini calls and measures real accuracy. Per-field comparison, precision/recall/F1, confusion matrices. (`evaluate.py:41-76, 139-170`)
- **Static evaluation** (`static_evaluate.py`) substitutes ideal vision from expected output and runs only deterministic components. This isolates parser/rule/risk errors from VLM quality. (`static_evaluate.py:56-88`)
- Compatible issue types at `evaluate.py:33-38` mirror the rule engine's, keeping eval consistent with prod.
- Risk flag accuracy is measured independently of claim status accuracy. (`evaluate.py:112-113, 168`)

**Weaknesses:**
- Static evaluation always sets confidence=0.85 for ideal vision (`static_evaluate.py:71`). This means it never hits the `low_confidence` path in the rule engine, masking confidence-threshold bugs.
- The expected outputs are loaded from `sample_claims.csv` itself (`evaluate.py:24-30`), which means the "expected" values are whatever was in that CSV — there's no independent ground truth.
- No evaluation of severity or object_part accuracy as separate metrics — only the full row match. (`evaluate.py:48-56` lists both fields in `compare_fields` but the summary only reports overall match + per-status metrics).
- No cross-validation split — same file is used for both development and evaluation.

**Alternatives:**
1. **Single live evaluation pipeline** — Simpler, one script to run. Cons: can't isolate whether failures are from vision or downstream logic.
2. **Hold-out validation** — Split sample claims into dev/test sets to measure generalization. Cons: reduces training data, which matters when you have ~44 claims.

**Would we still choose it?** Yes — dual evaluation is genuinely best-in-class for this kind of challenge. The static eval is invaluable for debugging rule+risk logic without burning Gemini API calls. The only change: use a held-out test set for the live evaluation.

---

## Decision 4: Risk analyzer + manual review flags

**Strengths:**
- Aggregates signals from image quality (blurry, cropped, wrong angle), CV modules (blur detection, OCR, object validation), user history (claim count > 3 in 90 days, rejected claims > 2), and VLM notes. (`risk_analyzer.py:46-147`)
- Lazy initialization of CV modules avoids importing cv2 unless needed. (`risk_analyzer.py:20-30`)
- `_user_claimed_damage` at line 157-166 provides a crude sanity check — if the user clearly described damage but the VLM sees none, that's suspicious.
- Internal flags (`evidence_insufficient`, `low_confidence`, `object_part_mismatch`) are stripped from the final output at line 149-150, keeping the surface clean for external consumers.

**Weaknesses:**
- **The `manual_review_required` flag is overproliferated.** At least 6 independent code paths can add it (confidence < 0.5 at line 58, line 106; evidence_insufficient without wrong_angle at line 69-71; conflicting_images at line 76-78; wrong_object at line 142; claim_mismatch + user_history_risk at line 144; user_history_risk alone at line 147). This makes it a near-default flag rather than a meaningful escalation.
- `confidence < 0.50` is checked twice (lines 58, 106) with identical logic. Dead code or intentional redundancy? Either way, it's a maintenance trap.
- Notes-based risk detection at lines 84-89 uses simple keyword matching: `"photoshopped"` in notes → manipulation flag. The VLM could easily use the word "photoshopped" in context like "no evidence of photoshopping."
- The `_user_claimed_damage` function at line 157-166 would match "water" in "water bottle" as a damage claim, because the keyword list includes "water" as a sign of water_damage.
- User history has no cache invalidation — once loaded at `claim_processor.py:48-52`, it's static for the process lifetime.

**Alternatives:**
1. **Weighted risk scoring** — Each signal contributes a numeric score; a threshold determines whether manual review is needed. Cons: more parameters to tune, less explainable.
2. **ML-based risk classifier** — Train on historical claims. Cons: needs labeled data, introduces black-box behavior.
3. **Reduced flag taxonomy** — Remove over-specific flags (`wrong_angle`, `low_light_or_glare`) that are just image quality dimensions, not risk indicators. Cons: loses granularity.

**Would we still choose it?** Yes — the signal aggregation approach is sound. But deprecate `manual_review_required` as a derived flag (compute it at the end based on other flags) and eliminate the redundant confidence checks. The keyword note-matching should use substring-checking only on VLM-enumerated categories, not free-text scanning.

---

## Decision 5: Severity engine (static mapping + boost words)

**Strengths:**
- Deterministic, testable, zero external dependencies. (`severity_engine.py:8-75`)
- Object-type overrides: `laptop + dent = low` (down from medium). This is sensible — a dent on a laptop is cosmetic. (`severity_engine.py:27-29`)
- Boost words like "severe", "smashed", "extensive" escalate severity by one level. (`severity_engine.py:31-34`)
- Negation detection attempts to avoid "no severe damage" being treated as a boost. (`severity_engine.py:61-74`)

**Weaknesses:**
- **Only 8 boost words.** "catastrophic", "totaled", "destroyed", "massive" are absent. The hardcoded set means many legitimate severity escalations are missed. (`severity_engine.py:31-34`)
- Negation detection uses a 50-char lookback window from the keyword position (`severity_engine.py:66`) with the last 5 words checked (`severity_engine.py:69`). This is both arbitrary and fragile — "I don't think there's severe damage, it's minor" would still match "severe" because the negation-preceding words check doesn't see "don't" in the right window.
- No severity for `"unknown"` damage types — returns "unknown" directly, which propagates to output where it may not trigger `manual_review_required` properly.
- The `BASE_OVERRIDE` dict only has one entry (laptop + dent). No other object-type overrides exist despite the config defining three object types with different risk profiles. (`severity_engine.py:27-29`)

**Alternatives:**
1. **VLM-based severity assessment** — "Given the images and claim, rate severity low/medium/high." Cons: non-deterministic, costs money per call, hard to test.
2. **Decision tree with more factors** — Incorporate number of images showing damage, confidence level, image quality. Cons: more complex, more tuning.
3. **Extended static mapping** — Add 20+ boost words, more object overrides (package crushing → high by default), and relative damage-type severity (glass_shatter on a laptop screen → high, not medium).

**Would we still choose it?** Yes — a deterministic severity engine is the right call. But expand the boost word list to 25+ terms, increase the negation window to 80 characters, and add overrides for all three object types. Validate with static evaluation.

---

## Decision 6: CV modules (blur, crop, OCR, object validation)

**Strengths:**
- Laplacian variance is a textbook blur detection method. Fast, deterministic, zero training data needed. (`blur_detector.py:13,22`)
- Crop detector uses edge density analysis with Canny + border bands, not just aspect ratio. Reasonably clever approach. (`crop_detector.py:31-47`)
- Lazy initialization at `risk_analyzer.py:20-30` avoids importing OpenCV unless actually needed (i.e., image paths exist).
- Each CV module produces per-image results that can be traced back for debugging.

**Weaknesses:**
- **Blur threshold of 15.0 (`blur_detector.py:13`) is arbitrary and untuned.** Different image content produces vastly different Laplacian variance. A photo of a textured surface (asphalt, gravel) will have high variance even if blurry. A clean white wall will have low variance even if perfectly sharp.
- Crop detector's aspect ratio check at `crop_detector.py:13,28` with `max_aspect_ratio=3.0` is very coarse. A 16:9 image (aspect 1.78) passes, but a panorama (3:1) is flagged as cropped.
- **Object validator does zero actual object recognition.** It checks image dimensions (`min_dim >= 100`, aspect ratio range) — that's it. (`object_validator.py:40-63`) Any small image of a shoe would pass the "car" check. The "validation" name is misleading.
- OCR path is hardcoded to Windows at `text_detector.py:18` — `r"C:\Program Files\Tesseract-OCR\tesseract.exe"`. Cross-platform users must edit the source.
- The CV results are only additive — `risk_analyzer.py:123` explicitly says "Do NOT remove vision-based flags." This means Gemini's inaccurate "is_clear=False" cannot be corrected by CV's blur detector finding it sharp.

**Alternatives:**
1. **ML-based blur detection** — A tiny CNN trained on blurry/sharp classification. Cons: needs labeled data, introduces dependency on ML frameworks.
2. **YOLO / object detection** — Actual trained model that identifies objects in the frame and verifies the claimed object is present. Cons: heavyweight dependency, slow per-image.
3. **No CV modules at all** — Rely entirely on the VLM for blur/crop/object assessment. Most VLMs can detect these reliably. Cons: more API cost, less deterministic.

**Would we still choose it?** Maybe. The CV modules add complexity but the actual object validator is a placebo — it doesn't validate objects at all. Drop the object validator or replace it with a CLIP-based zero-shot classifier. Keep blur and crop detection as Gemini overrides (CV can add blur flag even when Gemini says clear), which is the opposite of the current "add-only" approach.

---

## Decision 7: Per-component try/catch Safe Mode

**Strengths:**
- Every component call in the pipeline is individually wrapped. (`claim_processor.py:65-146`)
- Each catch produces sensible fallback defaults — empty vision result, evidence failure with reason, risk as manual_review_required.
- The fallback values preserve the pipeline shape so downstream components still receive the right data types.
- Error messages are truncated to 100 characters to prevent bloating the output. (`claim_processor.py:98, 109, 119`)

**Weaknesses:**
- **Silent degradation.** A component failure is logged as `logger.warning` or `logger.error`, but the pipeline continues producing output that looks structurally valid but may be completely wrong. There's no escalation mechanism.
- 100-character truncation on error messages (`claim_processor.py:98, 109, 119`) loses stack trace information that would be essential for debugging.
- Evidence checker, rule engine, and risk analyzer are all pure Python (no network calls) yet still wrapped. Their exceptions indicate programming bugs, not transient failures — catching them masks bugs.
- The `_empty_vision_result` at `claim_processor.py:152-160` claims `damage_visible=False`, `confidence=0.0`, but `damage_type="unknown"`. The downstream rule engine sees "unknown" damage, which triggers the `_damage_conflict` path differently depending on whether claimed_damage_type is also "unknown".

**Alternatives:**
1. **Circuit breaker with fallback** — Allow N failures in a time window, then fail-fast for the rest. Prevents silent incorrectness at scale.
2. **Fail-fast with retry** — If a pure-Python component throws an exception, that's a bug — don't catch it, fix the code. Only catch network errors.
3. **Component-level health checks** — Periodic synthetic test inputs to verify each component produces sane output before running real claims.

**Would we still choose it?** Maybe. The try/catch strategy is exactly right for the VLM and file I/O, but it's wrong for the pure-Python components (parser, rule engine, evidence checker). Those should propagate exceptions. Also increase truncation to 500 chars or include a reference to log file for full error.

---

## Decision 8: Hash-based Gemini response cache

**Strengths:**
- SHA-256 hash over canonical inputs guarantees determinism for identical inputs. (`vision_analyzer.py:46-53`)
- Cache key includes image paths (resolved absolute), user_claim (truncated 200 chars), claim_object, and model name. Reasonable scope.
- Cache is on local disk as JSON — zero infrastructure, works in any environment. (`vision_analyzer.py:42-44, 69-76`)
- Logs cache HIT/MISS, enabling operational observability. (`vision_analyzer.py:63`)

**Weaknesses:**
- **200-char truncation on user_claim at `vision_analyzer.py:49` could cause hash collisions.** Two different claims with the same first 200 characters would produce the same cache key, incorrectly returning cached results. User claims can be long conversation transcripts.
- No cache eviction policy. The `.gemini_cache/` directory grows unboundedly. For 44 claims it's fine, but for 1000+ it's a problem.
- Cache directory is at `config.base_dir.parent / ".gemini_cache"` (`vision_analyzer.py:42`). This is outside the code directory and could be accidentally lost in CI/deployment.
- No TTL — cached results from yesterday's Gemini API behavior are returned forever, even if Gemini's model behavior changes (which it does, frequently for preview models).
- The `_init_cache` check at line 40 says `if self.cache_dir is not None: return`, but `self.cache_dir` starts as `None` (line 31) and is only set after the first call to `analyze_images`. This means the first call always misses cache — that's fine but the init-on-first-use pattern is a minor code smell.

**Alternatives:**
1. **Database-backed cache** — SQLite or similar for production-grade persistence with TTL. Cons: adds dependency.
2. **No cache** — Simpler, but then every evaluation run costs API calls and produces different results due to model nondeterminism even at temperature=0.
3. **Content-addressable storage** — Store the raw image bytes hash + prompt into a content-addressed store (IPFS or similar). Overkill for this scale.
4. **Full-text cache key** (no truncation) — Hash the full string. SHA-256 handles arbitrarily long inputs. The truncation provides no benefit and only introduces collision risk.

**Would we still choose it?** Yes — caching is essential for reproducible evaluation. But remove the 200-char truncation (hash the entire string), add a `CACHE_TTL_DAYS` config option, and move the cache dir into the code directory with `.gitignore`.

---

## Decision 9: Output validator + submission critic dual-layer

**Strengths:**
- **OutputValidator** at `output_validator.py:67-100` catches per-row contradictions: "supported + none issue_type" → contradicted, "contradicted + evidence_standard_met=false" → not_enough_information.
- **SubmissionCritic** at `submission_critic.py:20-38` does post-processing across all rows: unknown issue_type without review flag adds it, critical flags ensure manual_review_required.
- Two layers catch different error patterns. The critic is a safety net for things the per-row validator misses — particularly cross-field interactions.
- Allowed enums are centrally defined in `config.py:37-62` and enforced by the validator, preventing invalid output.

**Weaknesses:**
- **Duplicated logic between validator and critic.** Both check "supported + damage=none" (validator line 73-78, critic line 69-72). Both ensure critical flags trigger manual_review_required (validator line 92-96, critic line 98-106). This duplication means behavior can diverge.
- The order of operations matters: the validator runs per-row in `decision_agent.py:58`, then the critic runs on all rows in the output pipeline. If the critic changes a row, the validator has already validated the pre-critic version.
- The critic's `_fix_unknown_without_review_flag` at line 50 adds `manual_review_required` if issue_type, severity, or object_part is "unknown" — but this is overly broad. Many legitimate claims have unknown parts after correct processing.
- The critic modifies rows in-place and tracks a "fixed" counter, but doesn't re-validate after fixes. No convergence check — potentially infinite cascading fixes (though unlikely in practice).

**Alternatives:**
1. **Single validation layer** — One component that handles all consistency checks. Simpler, no duplication, single responsibility.
2. **Validation-first, then post-processing** — Run the critic's changes back through the validator to ensure consistency. Prevents divergence.
3. **Schema-only validation** (no business logic) — Just validate enums and types. Remove the consistency heuristics entirely. Cons: loses the safety net for contradictory output.

**Would we still choose it?** Maybe. Two layers is belt-and-suspenders, and for a hackathon that's fine. But for production, unify them: the output validator should run all consistency checks, and the critic should only do cross-row validation (which the per-row validator can't do). Remove the duplicated logic.

---

## Decision 10: Image validation pre-processing

**Strengths:**
- Checks three concrete failure modes: file existence, extension whitelist, file size (<10MB). (`image_validator.py:20-38`)
- Uses `PIL.Image.open().verify()` for corruption detection — catches truncated/partial files. (`image_validator.py:41-46`)
- Returns per-image results with error messages, enabling targeted debugging.
- `any_valid_images` and `all_images_valid` provide flexible filtering. (`image_validator.py:53-58`)

**Weaknesses:**
- **The 10MB limit at `image_validator.py:11` is arbitrary.** Gemini supports images up to 20MB. A legitimate high-res phone photo (12MP) can easily be 8-15MB. The limit will reject valid submissions.
- `PIL.Image.verify()` only does a lazy check — it doesn't fully decode the image. Some corruption types pass verify() but fail on actual decode.
- No EXIF validation. An image with valid pixels but GPS metadata stripped or incorrect orientation tags passes validation.
- No MIME type verification beyond extension — a `.jpg` file containing a PNG bitstream passes the extension check and PIL's verify (since PIL auto-detects format).
- The validation runs before image normalization in `claim_processor.py:65-68`, and errors from either are only logged — the pipeline continues with potentially invalid images. (`claim_processor.py:66-78`)

**Alternatives:**
1. **No validation** (let Gemini/VLM reject bad images) — Simpler, fewer false positives. Cons: wastes API calls on invalid images.
2. **Full decode validation** — `img.load()` after `img.verify()` to force full decompression. Slower but catches more corruption.
3. **Content-type sniffing** — Read magic bytes (file signatures) to verify the declared extension matches actual content.

**Would we still choose it?** Yes — image validation is table stakes for a production system. But increase the limit to 20MB (matching Gemini's limit), add magic byte checking, and do a partial decode for PNGs (where corruption often hides in later chunks). Also wire validation failures to short-circuit the claim rather than silently continuing.

---

## Decision 11: OCR safe mode (lazy Tesseract check)

**Strengths:**
- Lazy import — Tesseract is probed once at class init, not at module import. (`text_detector.py:12-24`)
- Graceful fallback: if Tesseract is missing, `contains_text` returns False for every image. (`text_detector.py:40-41`)
- `min_text_length=3` filters out single characters that are noise. (`text_detector.py:30`)
- `confidence_threshold=30` filters low-confidence OCR output. (`text_detector.py:30`)

**Weaknesses:**
- **Hardcoded Windows path at `text_detector.py:18` — `C:\Program Files\Tesseract-OCR\tesseract.exe`.** This is system-specific and will fail on any non-standard install, Linux, or macOS. The correct approach is `shutil.which("tesseract")` or relying on `pytesseract`'s own discovery.
- Returns False for all images when Tesseract is unavailable — this is a false negative risk. A claim with text instructions in images (a known risk flag) would not be flagged.
- Only checks for text presence, not content. Even when OCR works, there's no analysis of what the text says. `text_instruction_present` is flagged but the actual instructions remain unexamined.
- No test coverage for the fallback path — the `_TESSERACT_AVAILABLE = None` flag is a module-level global, making it hard to test without resetting module state.
- The confidence threshold of 30 (`text_detector.py:30`) comes from Tesseract's 0-100 scale, but Tesseract's confidence calibration is notoriously unreliable. 30 is a very low bar.

**Alternatives:**
1. **Cross-platform Tesseract discovery** — Use `shutil.which()` or rely entirely on pytesseract's `tesseract_cmd` default (which searches PATH).
2. **Alternative OCR engine** — Use `easyocr` or `paddleocr` which are pip-installable and don't require a system binary. Cons: larger dependencies, slower.
3. **No local OCR** — Rely on Gemini's built-in text detection. Modern VLMs are excellent at reading text in images. Cons: API cost per call.

**Would we still choose it?** Maybe. OCR adds little value when Gemini already reads text well. The main justification is determinism (CV text detection is the same every run, Gemini is not). But the hardcoded Windows path is a bug, not a design choice. Fix Tesseract discovery to be cross-platform, or switch to easyocr.

---

## Decision 12: Claim parser (deterministic keyword + negation)

**Strengths:**
- Full deterministic parsing: no model calls, no randomness, pure string operations. (`claim_parser.py:56-72`)
- Customer text filtering at `claim_parser.py:34-54` strips out Support/Agent lines, focusing on the customer's actual description. This is smart for conversation transcripts.
- Negation detection at `claim_parser.py:75-82` prevents "not cracked" from being classified as crack damage. Reasonable 25-char lookback window.
- Object-specific part keyword maps for car, laptop, and package at `claim_parser.py:85-119` with prioritized matching order.

**Weaknesses:**
- **The keyword list is simplistic and produces false positives.** "water" at line 59 matches "water_damage" — but also "water bottle" (someone describing a drink near their laptop), "watermark", "waterproof case". There's no context awareness.
- "damage" as a keyword at line 163 in `risk_analyzer.py` but not in `claim_parser.py`'s damage keywords — inconsistency between the two components that both parse claim text.
- 25-character negation window at `claim_parser.py:75` is small. "The glass appeared to have a crack, though I'm not entirely certain" — the word "not" is more than 25 characters before "crack" after skip-connective text.
- Object part matching has no ambiguity handling. "mirror" matches `side_mirror` for "car", but what if the user says "rear view mirror"? The keyword "mirror" matches, mapping to `side_mirror` instead of something more specific — there's no `rear_view_mirror` entry.
- The `_filter_customer_text` function splits on `" | "` (line 36-43) but also on `\n` (line 44-54) — two different code paths for the two separator styles. If a conversation uses mix of both, the filtering may produce inconsistent results.

**Alternatives:**
1. **LLM-based parsing** — "Extract the claimed damage type and object part from this text." More accurate, handles ambiguity. Cons: costs per call, non-deterministic, introduces latency.
2. **Regex grammar** — More precise patterns with word boundaries: `r'\b(shatter(ed)?|broken glass)\b'` instead of substring matching. Cons: more development time, still misses edge cases.
3. **NLP dependency tree** — Parse sentence structure to find the actual subject and object of damage verbs. Overkill for a 24-hour hackathon.

**Would we still choose it?** Yes — deterministic parsing is the right call. But fix the false positives: use word-boundary regex instead of `in` operator, add a stopword filter ("water" should not match "water bottle"), expand the object part maps with more synonyms, and increase the negation window to 50 characters. Also, align the keyword sets between `claim_parser.py` and `risk_analyzer.py`.
