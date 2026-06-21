# Security

## Overview

Security posture of the VerifyIQ evidence review system, covering image handling, API security, adversarial input processing, and dependency management. The architecture prioritizes graceful degradation over hard failure — every component wraps external calls in try/except blocks (`claim_processor.py:57-160`) so a single compromised input cannot crash the pipeline.

## Image Security

- **Size validation:** `image_validator.py:11` defines `MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024`. Files exceeding this threshold are marked invalid at line 33-35 before any decode attempt.
- **Format whitelist:** Only `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp` are accepted (`image_validator.py:12`). Any extension outside this set is rejected at line 27-29.
- **Integrity verification:** Every image passes through `PIL.Image.open().verify()` (`image_validator.py:42-43`) which checks header and decode integrity without loading pixel data. Corrupt images are caught here, logged, and the pipeline continues with degraded output.
- **Path traversal prevention:** Image paths are resolved via `utils.py:42-44` using `base_dir / Path(p)`, relying on `pathlib` for safe path composition rather than string concatenation. Relative paths resolve within the dataset directory tree. Note: `Path.resolve()` is not called before file access, meaning traversal via `../../etc/passwd` can reach outside `base_dir` — this is a known gap (see below).
- **Normalization:** `image_preprocessor.py:32-43` converts non-JPEG formats (AVIF, WebP, PNG, BMP) to standardized JPEG (quality=95) before downstream processing, reducing format-based attack surface.

## API Security

- **Key management:** The Gemini API key is read exclusively from the `GEMINI_API_KEY` environment variable or `config.api_key` (`vision_analyzer.py:32`). No hardcoded credentials exist anywhere in the codebase.
- **Client initialization failure:** If both sources are absent, `GeminiVisionClient.__init__` skips client creation (line 37). Subsequent `analyze_images()` calls return an empty analysis immediately (line 85-86), avoiding confusing API error propagation.
- **Rate limit handling:** The retry loop at `vision_analyzer.py:115-137` implements exponential backoff (`2^attempt * 5` seconds) specifically for `RESOURCE_EXHAUSTED` / 429 responses, with a maximum of 5 retries.

## Input Validation

- **CSV field validation:** `output_validator.py:36-65` processes every output row through enum whitelists — `ALLOWED_ISSUE_TYPES`, `ALLOWED_OBJECT_PARTS`, `ALLOWED_CLAIM_STATUS`, `ALLOWED_SEVERITY` — all defined in `config.py:37-61`. Invalid values are coerced to safe defaults (`"unknown"`, `"not_enough_information"`).
- **Risk flag filtering:** Only flags present in `config.ALLOWED_RISK_FLAGS` survive the filter at `output_validator.py:59`. Unknown flags are silently dropped.
- **Boolean normalization:** Fields like `evidence_standard_met` and `valid_image` are normalized to `"true"` or `"false"` at `output_validator.py:55-56`, preventing arbitrary string injection in boolean fields.
- **User history:** Loaded via `safe_csv_read()` in `claim_processor.py:48`, which wraps `csv.DictReader` in exception handling. Missing history files are logged as warnings (line 44-46), not crashes.

## Adversarial Inputs

- **Corrupt images:** Caught by `PIL.Image.verify()` at `image_validator.py:43`. Any `Exception` during decode marks the file invalid but does not halt processing. The pipeline continues with empty vision results and `claim_status=not_enough_information`.
- **Missing images:** Every component that touches file paths has an existence guard: `image_preprocessor.py:27` (`p.exists()`), `image_validator.py:20-24` (marks `valid=False`, continues), `vision_analyzer.py:107-109` (logs warning, skips via `continue`). The pipeline never crashes on missing files.
- **Invalid paths:** `pathlib.Path` raises `ValueError` on embedded null bytes, caught by the outer try/except at `claim_processor.py:67-68`. Unicode RTL/LTR override characters are handled safely — Windows accepts them in paths but they resolve the same way.
- **Oversized images (>10MB):** Rejected at `image_validator.py:33-35` before loading. However, validation results are not used to filter which paths reach `vision_analyzer.py:111` (`read_bytes()`) — oversized files can still trigger large memory allocation. Mitigation: current try/except at `vision_analyzer.py:112` catches read errors, but pre-filtering by size would be stronger.
- **OCR attacks:** `cv/text_detector.py:39-56` runs Tesseract OCR on images independently of the Gemini pipeline. Images containing text (watermarks, stamps, overlays) are flagged with `text_instruction_present` in the risk flags. The text detector does not evaluate semantic content — it only detects presence of readable text.
- **Prompt injection:** User claim text is interpolated into the Gemini prompt via `USER_PROMPT_TEMPLATE.format(user_claim=user_claim[:500])`. No instruction-boundary delimiters are placed around the user input. A crafted claim could override system instructions. The only mitigation is the structured prompt template itself — the claim text is passed as a field to be analyzed, not executed. This is a known gap (see below).
- **CSV injection in output:** Output is written via `csv.DictWriter` (`main.py:52`), which does not interpret formulas. However, if the output CSV is opened in Excel or LibreOffice, cells starting with `=`, `+`, `-`, `@` could execute as formulas. This affects the `user_claim` and `claim_status_justification` fields.

## Known Gaps

| Gap | Location | Impact | Mitigation |
|-----|----------|--------|------------|
| Prompt injection | `prompts.py:13` — user claim text directly interpolated | High — attacker can override VLM instructions | Delimit input with `[USER_CLAIM_START]...[/USER_CLAIM_END]`, strip injection patterns |
| Path traversal | `utils.py:42-44` — no `resolve()` check | Medium — `../../etc` can read arbitrary files | Call `Path.resolve()`, verify prefix matches `base_dir` |
| No size pre-filter before API | `vision_analyzer.py:111` — `read_bytes()` on all paths | Medium — potential OOM on very large files | Filter `image_paths` by size before passing to `analyze_images` |
| CSV injection | `main.py:51-56` — no quoting of formula chars | Low — depends on external spreadsheet app | Prepend `'` to values starting with `=`, `+`, `-`, `@` |
| Single VLM dependency | `vision_analyzer.py:29` — no fallback model | Medium — no intelligent output without Gemini | Add secondary VLM or heuristic fallback |

## Risk Score

**Overall security risk: Medium**

Justification: The system handles all error conditions gracefully without crashing. Most failure modes produce degraded but safe output. Two issues raise the score to Medium: (1) path traversal could read arbitrary files — a realistic attack vector since image paths come from CSV input. (2) Prompt injection is unmitigated and allows VLM output manipulation. Both are fixable with targeted input validation.
