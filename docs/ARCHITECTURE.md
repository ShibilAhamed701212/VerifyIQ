# Architecture

## Overview

VerifyIQ is a modular, deterministic AI system for automated damage claim verification. The architecture follows a pipeline pattern: each component processes the output of the previous one, with per-component error boundaries ensuring graceful degradation. The vision model is the only non-deterministic component; every downstream module applies hardcoded rules, static mappings, or logic trees that produce identical output for identical input.

```
Input CSV --> Image Preprocessor --> Image Validator --> ClaimParser
                                                           |
                                                           v
                                              GeminiVisionClient
                                                           |
                                                           v
                                                 EvidenceChecker
                                                           |
                                                           v
                                                     RuleEngine
                                                           |
                                               +-----------+-----------+
                                               |                       |
                                               v                       v
                                         RiskAnalyzer          SeverityEngine
                                               |                       |
                                               +-----------+-----------+
                                                           |
                                                           v
                                                     DecisionAgent
                                                           |
                                                           v
                                                  OutputValidator
                                                           |
                                                           v
                                                 SubmissionCritic
                                                           |
                                                           v
                                                    Output CSV
```

## Component Details

### 1. ClaimParser (`claim_parser.py:15-125`)

**Purpose:** Extract the claimed damage type and object part from the user's natural-language claim text using deterministic keyword matching with negation detection.

**Input:** `user_claim` (raw text, possibly multi-turn conversation with Customer/Support labels), `claim_object` (e.g., "car", "laptop", "package").

**Output:** `{"claimed_damage_type": str, "claimed_object_part": str, "claim_text": str}`

**Key design decisions:**
- Filters out non-customer utterances (Support:, Agent: lines) via `_filter_customer_text` before parsing, so agent descriptions of damage do not influence the parsed claim.
- Uses substring matching against a curated keyword list per damage type (e.g., "shatter" -> `glass_shatter`, "water damage" -> `water_damage`). The first matching type wins, making the parser fast and predictable.
- `_is_negated` checks for "no"/"not" within a 25-character window before each keyword match, preventing false positives like "there is no crack" from producing `crack`.
- Object part extraction is scoped per `claim_object` — car parts are only searched when `claim_object` is "car". Unknown claim objects return `"unknown"` for both fields.

**Error handling:** No exception path in the parser itself. If input is empty, both fields default to `"unknown"`. The orchestrator wraps the call at `claim_processor.py:81-84` to catch any unexpected failures.

**Dependencies:** `config.py`, `utils.py` (normalize_text).

---

### 2. ImagePreprocessor (`image_preprocessor.py:21-51`)

**Purpose:** Normalize all input images to standard JPEG format so downstream modules (Pillow-based CV detectors, Gemini API) receive a uniform format.

**Input:** `List[Path]` — image file paths in any format (AVIF, WebP, PNG, BMP, GIF, JPEG).

**Output:** `List[Path]` — paths to JPEG files (original files if already JPEG, converted copies otherwise).

**Key design decisions:**
- Uses `PIL.Image.open` and checks `img.format` — only converts non-JPEG inputs. JPEGs pass through without copying.
- Converts RGBA/LA/P modes to RGB before saving to eliminate alpha channel complications in downstream analysis.
- Converted files are written to a temporary directory with quality=95, balancing file size against visual fidelity.
- The temp directory is tracked in `_cleanup_dirs` for optional cleanup. Failures during conversion log a warning and return the original path unchanged.

**Error handling:** Per-image try/except. A single corrupt image does not block other conversions. Unreadable images are passed through as-is; the ImageValidator catches them later.

**Dependencies:** PIL (Pillow), `tempfile`.

---

### 3. ImageValidator (`image_validator.py:15-50`)

**Purpose:** Pre-processing checks for file existence, format support, file size, and image integrity.

**Input:** `List[Path]` — image file paths (post-normalization).

**Output:** `List[Dict]` — per-image results with `valid` (bool), `errors` (list of strings).

**Key design decisions:**
- Enforces a 10 MB per-file limit (`MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024`). Larger files are flagged invalid before any decode attempt.
- Allowed extensions are `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`. Unsupported extensions trigger an error.
- Calls `Image.open` then `img.verify()` to detect corrupt or truncated image data without fully decoding.
- The helper functions `any_valid_images` and `all_images_valid` let callers decide whether to proceed with partial results.

**Error handling:** Each image is validated independently — one corrupt file does not invalidate the rest. File-not-found and OSError are caught per file.

**Dependencies:** PIL (Pillow).

---

### 4. GeminiVisionClient (`vision_analyzer.py:25-326`)

**Purpose:** Extract visual observations from claim images using a vision language model. This is the only non-deterministic component in the pipeline.

**Input:** `List[Path]` (image paths), `user_claim` (str), `claim_object` (str).

**Output:** Structured dict with `damage_visible`, `damage_type`, `object_part`, `image_quality`, `supporting_images`, `confidence`, `per_image_assessments`, `conflicting_images`.

**Key design decisions:**
- The VLM is used **only for factual observation extraction**. It is explicitly instructed via `SYSTEM_PROMPT` to "Return visual observations only. Never output claim_status, approval, rejection, or policy decisions." This boundary prevents the model from making judgment calls that belong to downstream deterministic modules.
- A hash-based response cache (`_cache_key` using SHA-256 of image paths + claim text + model name) eliminates API variance on cache hits. The cache is stored on disk under `.gemini_cache/`, making it persistent across runs.
- Retry with exponential backoff handles rate limiting: 5 attempts with wait times of 5s, 10s, 20s, 40s, 80s. Rate-limit exhaustion returns an empty analysis rather than crashing.
- Each image gets a per-image assessment; an aggregation step (`_aggregate`) computes majority-vote damage type and object part across clear, well-angled images. Conflicting assessments (different damage types or parts across images) are flagged via `conflicting_images`.
- Prompt enforces the exact output JSON shape with a restricted enum of damage types and object parts, reducing parsing failures.

**Error handling:**
- No API key: returns empty analysis (`_empty_analysis`).
- Empty response or parse failure: returns empty analysis with descriptive error in `notes`.
- Individual image read failure: logged, image skipped, remaining images processed.
- The orchestrator wraps the call at `claim_processor.py:89-98` to catch any unexpected exceptions.

**Dependencies:** `google.genai` (Gemini SDK), `config.py`, `prompts.py`, `utils.py`.

---

### 5. EvidenceChecker (`evidence_checker.py:14-148`)

**Purpose:** Validate that submitted images meet the semantic evidence requirements defined in `evidence_requirements.csv`.

**Input:** `claim_object`, `parser_result`, `vision_result`, `total_images` (int).

**Output:** `{"evidence_standard_met": bool, "evidence_standard_met_reason": str, "requirement_text": str, "valid_image": bool}`

**Key design decisions:**
- Requirements are natural-language descriptions loaded from CSV and matched by `claim_object` and `applies_to` (damage type or part name). A fallback default requirement exists for unmatched objects.
- Rather than parsing the requirement text with NLP, the checker evaluates image quality signals from the vision analysis: clarity, angle, obstruction, and non-original markers. A requirement is met when clear, unobstructed images of the relevant part are available.
- The "relevant part" check prefers the vision-detected part over the claimed part, since the vision model directly observes the images. This avoids rejecting valid claims where the user described the part imprecisely.
- `valid_image` tracks whether images exist and are non-original (screenshots, stock photos).

**Error handling:** The orchestrator wraps the call at `claim_processor.py:100-109`, providing a default `evidence_standard_met: False` result.

**Dependencies:** `utils.py` (safe_csv_read).

---

### 6. RuleEngine (`rule_engine.py:11-147`)

**Purpose:** Apply a deterministic decision tree to compare parsed claim facts against visual observations.

**Input:** `parser_result`, `vision_result`, `evidence_result`.

**Output:** `{"claim_status": str, "justification": str, "claimed_damage_type": str, "claimed_object_part": str, "visible_damage_type": str, "visible_object_part": str, "confidence": float, "review_candidate": bool, "mismatch_type": str, "risk_flags": list}`

**Key design decisions:**
- Six mutually exclusive decision paths evaluated in order:
  1. **Evidence insufficient** — `evidence_standard_met` is False.
  2. **Damage not visible** — `damage_visible` is False despite sufficient evidence.
  3. **Damage type mismatch** — claimed and visible damage types differ (with compatible-type handling).
  4. **Object part mismatch** — claimed and visible parts differ.
  5. **Low confidence** — below 0.50 threshold, cannot automate.
  6. **Supported** — all checks pass.
- Compatible damage types (`COMPATIBLE_DAMAGE_TYPES`) treat `crack`/`glass_shatter` and `stain`/`water_damage` as non-conflicting, reflecting real-world ambiguity in visual assessment.
- `review_candidate` is set when confidence falls between 0.50 and 0.80, flagging borderline cases for human review without blocking automation.

**Error handling:** The orchestrator wraps the call at `claim_processor.py:111-119`, defaulting to `"not_enough_information"` status with an empty risk flag list.

**Dependencies:** None (pure logic on dict inputs).

---

### 7. RiskAnalyzer (`risk_analyzer.py:11-172`)

**Purpose:** Compute risk flags from multiple sources: vision quality, rule engine result, user claim text, user history, and deterministic CV module overrides.

**Input:** `image_analysis`, `user_history`, `claim_object`, `user_claim`, `evidence_result`, `rule_result`, `image_paths`.

**Output:** `List[str]` — sorted risk flags (e.g., `["blurry_image", "manual_review_required"]`, or `["none"]`).

**Key design decisions:**
- Aggregates risk from four independent sources:
  - **Vision quality flags:** blurry, cropped, low light, wrong angle extracted from per-image assessments.
  - **Rule engine flags:** mismatch types and confidence thresholds propagate to output flags like `claim_mismatch`, `damage_not_visible`, `wrong_object_part`.
  - **User history flags:** claims >3 in 90 days or >2 rejected claims add `user_history_risk`.
  - **CV module overrides:** BlurDetector, CropDetector, TextDetector, and ObjectValidator run per-image and add flags independently. CV only adds signals — it never removes vision-based flags.
- Internal flags (`evidence_insufficient`, `low_confidence`, `object_part_mismatch`) are filtered from the final output set since they describe root causes, not actionable flags.
- `manual_review_required` is added automatically when confidence <0.50, conflicting images exist, certain critical flags are present, or the claim mismatches with user history risk.

**Error handling:** The orchestrator wraps the call at `claim_processor.py:121-133`, defaulting to `["manual_review_required"]`.

**Dependencies:** `config.py`, `cv/blur_detector.py`, `cv/crop_detector.py`, `cv/text_detector.py`, `cv/object_validator.py`.

---

### 8. SeverityEngine (`severity_engine.py:8-75`)

**Purpose:** Map detected damage type to a static severity level, with optional boost from claim wording.

**Input:** `damage_type`, `user_claim`, `claim_object`, `risk_flags`.

**Output:** `str` — one of `"none"`, `"low"`, `"medium"`, `"high"`, `"unknown"`.

**Key design decisions:**
- Severity is a static lookup table (`BASE` mapping) — `glass_shatter` always maps to `"high"`, `scratch` always to `"low"`, `dent` to `"medium"`. This eliminates model-driven severity estimation.
- Per-object overrides (`BASE_OVERRIDE`) allow fine-tuning: e.g., `dent` on a laptop is `"low"` instead of `"medium"`.
- Boost words (`"severe"`, `"major"`, `"extensive"`, etc.) in the user claim text increase severity by one level. Negation checking prevents false boosts from phrases like "no major damage".
- `non_original_image` risk flag forces `"high"` severity regardless of damage type, reflecting the elevated scrutiny required for potentially inauthentic images.

**Error handling:** Unknown damage types return `"unknown"`. The orchestrator's error boundary covers any unexpected failure.

**Dependencies:** `utils.py` (normalize_text).

---

### 9. DecisionAgent (`decision_agent.py:14-115`)

**Purpose:** Assemble the final output row by combining parser, vision, evidence, rule, risk, and severity results into a single structured dict ready for CSV output.

**Input:** `claim_row`, `parser_result`, `vision_result`, `evidence_result`, `rule_result`, `risk_result`.

**Output:** `Dict[str, str]` — 14-field output row.

**Key design decisions:**
- This is the only component that produces the final output schema. All other components pass intermediate data through it.
- `_merge_flags` deduplicates risk flags, removes internal flags, and adds `manual_review_required` for review candidates or conflicting images.
- `_reasoning_trace` builds a human-readable justification string that concatenates the claimed and visible damage, supporting image IDs, evidence status, confidence, rule justification, and risk flags. This provides full explainability for every decision.
- `fallback_output` produces a valid row (with `manual_review_required` and `not_enough_information`) when any part of the pipeline fails, ensuring the orchestrator always produces output.

**Error handling:** The orchestrator calls `fallback_output` at `claim_processor.py:144-146` if `build_output_row` raises.

**Dependencies:** `output_validator.py`, `severity_engine.py`.

---

### 10. OutputValidator (`output_validator.py:13-103`)

**Purpose:** Validate and clean the output row before it reaches the CSV file.

**Input:** `Dict[str, Any]` — raw output row from DecisionAgent.

**Output:** `Dict[str, str]` — cleaned row with enum validation and consistency fixes.

**Key design decisions:**
- **Schema enforcement:** Every output field is cast to `str` via `FIELDNAMES` ordering.
- **Enum validation:** `issue_type`, `object_part`, `claim_status`, `severity`, `risk_flags` are checked against `Config.ALLOWED_*` sets. Invalid values are replaced with safe defaults (`unknown`, `not_enough_information`, etc.).
- **Boolean normalization:** `evidence_standard_met` and `valid_image` are converted from any truthy variant to `"true"` or `"false"`.
- **Consistency checks** (`_consistency_check`):
  - If `claim_status` = `supported` but `issue_type` is `none` or `unknown`, status is downgraded to `contradicted` or `not_enough_information`.
  - If `claim_status` = `contradicted` but evidence was not met, status becomes `not_enough_information`.
  - Critical flags (`possible_manipulation`, `non_original_image`, `user_history_risk`) automatically add `manual_review_required`.

**Error handling:** All validation failures are handled internally — no exceptions propagate. The caller always gets a valid output dict.

**Dependencies:** `config.py`.

---

### 11. SubmissionCritic (`submission_critic.py:20-119`)

**Purpose:** Post-processing pass over all output rows to catch contradictions that individual row processing could not detect.

**Input:** `List[Dict[str, str]]` — all output rows.

**Output:** `List[Dict[str, str]]` — corrected rows.

**Key design decisions:**
- Four independent fix functions run on each row:
  - `_fix_unknown_without_review_flag`: If `issue_type` or `severity` is `unknown` but the status is not `not_enough_information`, adds `manual_review_required`.
  - `_fix_contradiction_detected_supported_with_no_damage`: If status is `supported` but `issue_type` is `none` or `unknown`, corrects the status.
  - `_fix_contradiction_supported_with_conflict`: If status is `supported` but `claim_mismatch` flag is set, corrects to `contradicted`.
  - `_fix_missing_manual_review`: Ensures critical flags always carry `manual_review_required`.
- Each fix logs the diff, making corrections auditable.

**Error handling:** Runs over rows in a loop; a failure in one row does not affect others. The critic is invoked as a post-processing step after all rows are generated.

**Dependencies:** None (pure logic on dict inputs).

---

## Data Flow

The pipeline processes one claim at a time. Here is the exact field flow through each stage:

1. **CSV row** enters with `user_id`, `image_paths`, `user_claim`, `claim_object`.
2. **ImagePreprocessor** converts non-JPEG images to JPEG; passes paths to ImageValidator and GeminiVisionClient.
3. **ImageValidator** produces `per-image valid/errors` — consumed only as a warning log (processing continues regardless).
4. **ClaimParser** extracts `claimed_damage_type`, `claimed_object_part` from `user_claim`.
5. **GeminiVisionClient** produces `damage_visible`, `damage_type`, `object_part`, `confidence`, `supporting_images`, `per_image_assessments`, `conflicting_images`, `notes`.
6. **EvidenceChecker** takes `claim_object`, `parser_result`, `vision_result` and produces `evidence_standard_met`, `reason`, `valid_image`.
7. **RuleEngine** takes `parser_result`, `vision_result`, `evidence_result` and produces `claim_status`, `mismatch_type`, `justification`, `review_candidate`, `risk_flags`.
8. **RiskAnalyzer** takes all prior results plus `user_history` and `image_paths` and produces a sorted `List[str]` of risk flags.
9. **SeverityEngine** takes `damage_type`, `user_claim`, `claim_object`, `risk_flags` and produces a severity level.
10. **DecisionAgent** assembles everything into a 14-field dict and passes it through OutputValidator.
11. **OutputValidator** normalizes enums, booleans, and applies consistency rules.
12. **SubmissionCritic** runs across all completed rows for cross-row consistency fixes.
13. **Output CSV** is written with the 14 validated fields.

## Error Boundaries

Every pipeline stage in `claim_processor.py:57-146` is wrapped in its own try/except block. When a component fails:

| Component | Fallback | Location |
|---|---|---|
| Image normalization | Original paths passed through | `claim_processor.py:66-68` |
| Image validation | Warning logged, processing continues | `claim_processor.py:70-78` |
| ClaimParser | `{claimed_damage_type: "unknown", claimed_object_part: "unknown"}` | `claim_processor.py:81-84` |
| Vision analysis | Empty result with error note | `claim_processor.py:89-98` |
| EvidenceChecker | `{evidence_standard_met: False, valid_image: False}` | `claim_processor.py:100-109` |
| RuleEngine | `{claim_status: "not_enough_information", risk_flags: []}` | `claim_processor.py:111-119` |
| RiskAnalyzer | `["manual_review_required"]` | `claim_processor.py:121-133` |
| DecisionAgent | Fallback output with error message | `claim_processor.py:135-146` |

This architecture guarantees that every input row produces an output row — zero crashes is the non-negotiable standard.
