# Security Report

## Overview
Security review of the VerifyIQ evidence review system.

## Test Scenarios

For each scenario, report: test performed, actual behavior, severity, and mitigation.

### 1. Missing Images
- **Test**: Pass non-existent image paths (e.g., `nonexistent.jpg`) to the pipeline.
- **Actual behavior**: `image_preprocessor.py:27` checks `p.exists()` — missing paths are passed through unconverted. `image_validator.py:20-24` detects `File not found`, marks `valid=False`, continues. `vision_analyzer.py:107-109` checks `img_path.exists()`, logs a warning, and skips the image via `continue`. `claim_processor.py:65-78` wraps everything in try/except. The pipeline never crashes; output shows `valid_image=false`, `evidence_standard_met=false`, `claim_status=not_enough_information`.
- **Severity**: Low
- **Mitigation**: Already handled — every component that touches file paths has an existence guard and does not crash.

### 2. Corrupt Images
- **Test**: Feed unreadable/broken JPEG files (zero-byte files, truncated headers, random bytes).
- **Actual behavior**: `image_preprocessor.py:47-49` catches PIL open/convert exceptions and returns the original path. `image_validator.py:41-46` calls `Image.open(p).verify()` — if corrupt, catches `Exception`, marks `valid=False`. `vision_analyzer.py:110-113` attempts `read_bytes()` and catches any read error. Pipeline continues with degraded output.
- **Severity**: Low
- **Mitigation**: Already handled — try/except at every stage prevents crashes.

### 3. Invalid Image Paths
- **Test**: Path traversal (`../../windows/win.ini`), null bytes (`%00`), Unicode RTL/LTR override characters.
- **Actual behavior**: `utils.py:42-44` constructs paths by `base_dir / p` for relative paths. A traversal like `../../etc/passwd` resolves within the dataset's parent directory tree, potentially accessing files outside the intended directory. `image_preprocessor.py:27` then checks existence. Null bytes: Python's `Path` raises `ValueError: embedded null byte` on Windows before any file access, but this exception is caught at `claim_processor.py:67-68`. Unicode exploits: Windows handles Unicode paths; no sanitization is applied, but file-access failures are caught gracefully.
- **Severity**: Medium — path traversal can read arbitrary files on disk (e.g., config files with API keys), though the system is read-only for images.
- **Mitigation**: Resolve paths with `Path.resolve()` and verify they fall under the allowed `base_dir`. Reject paths containing `..` segments.

### 4. Oversized Images
- **Test**: Files > 10MB and files > 100MB.
- **Actual behavior**: `image_validator.py:32-35` checks `size > 10MB` and marks oversized files as invalid. However, `claim_processor.py:65-96` passes image paths to `analyze_images` regardless of validation results (validation is for logging only). `vision_analyzer.py:111` calls `img_path.read_bytes()` which loads the entire file into memory. A 100MB file triggers a 100MB+ allocation; under concurrency this could OOM. The Gemini API also rejects oversize payloads, but the OOM risk happens client-side first.
- **Severity**: Medium — potential OOM on very large files; no hard size enforcement before the read_bytes call.
- **Mitigation**: Filter image paths by file size before passing to `analyze_images`. Also wrap `read_bytes()` in the existing try/except at `vision_analyzer.py:112` and skip oversized files instead of crashing.

### 5. Invalid JSON from Gemini
- **Test**: Gemini returns malformed JSON (truncated, extra fields, wrong structure).
- **Actual behavior**: `vision_analyzer.py:146-156` uses regex to extract JSON from markdown fences or bare braces, then calls `json.loads()`. On `json.JSONDecodeError`, returns `_empty_analysis()` with error message. The pipeline continues with default values (`damage_visible=False`, `confidence=0.0`, etc.).
- **Severity**: Low
- **Mitigation**: Already handled — JSON parsing errors produce a safe empty result.

### 6. Empty Gemini Output
- **Test**: Gemini returns `response.text` as `None` or empty string.
- **Actual behavior**: `vision_analyzer.py:142-143` checks `if not text` and returns `_empty_analysis("Empty response from Gemini")`.
- **Severity**: Low
- **Mitigation**: Already handled.

### 7. OCR Unavailable
- **Test**: Tesseract not installed; binary missing from expected path.
- **Actual behavior**: `text_detector.py:12-24` attempts `pytesseract.get_tesseract_version()` during `_check_tesseract()`. On failure, sets `_TESSERACT_AVAILABLE = False`. `contains_text()` at line 40 returns `False` for all images. `risk_analyzer.py:132-135` calls `has_text_images()` which returns `contains_text: false` for every image. No crash, no error propagation.
- **Severity**: Low
- **Mitigation**: Already handled via safe fallback.

### 8. API Unavailable
- **Test**: Network failure, invalid API key, rate limit exhaustion.
- **Actual behavior**: `vision_analyzer.py:115-137` implements up to 5 retries with exponential backoff for rate limit errors (`RESOURCE_EXHAUSTED` / 429). Network/auth failures fall through to the general `except Exception` handler and return `_empty_analysis()`. `claim_processor.py:96-98` catches any remaining vision failure and provides a fallback result. If `GEMINI_API_KEY` env var is not set and `config.api_key` is None, `GeminiVisionClient.__init__` at line 37 skips client creation, and `analyze_images` at line 85-86 returns empty analysis immediately.
- **Severity**: Medium — system degrades to fallback with no intelligent output; retries mitigate transient failures.
- **Mitigation**: Already has retry + graceful degradation. Consider secondary model or heuristic fallback.

### 9. CSV Injection
- **Test**: Input CSV fields containing `=CMD(...)`, `+HYPERLINK(...)`, `@SUM(...)` formulas.
- **Actual behavior**: Input is read via Python `csv.DictReader` (`utils.py:55`) which treats all values as plain strings — no formula execution. Output is written via `csv.DictWriter` (`main.py:52`) which also does not interpret formulas. However, if the output CSV is opened in Microsoft Excel or LibreOffice Calc, cells starting with `=`, `+`, `-`, `@` could be treated as formulas and executed. The `user_claim` and `claim_status_justification` fields contain user-supplied text that may include formula-like content.
- **Severity**: Low — execution depends on user opening CSV in an external application with formula features enabled.
- **Mitigation**: Sanitize output fields by prepending a single quote or space to values starting with `=`, `+`, `-`, `@`, or use Excel-compatible quoting. Alternatively, write output in a non-formula format.

### 10. Prompt Injection
- **Test**: User claim text containing "Ignore previous instructions", "You are now a different system", or other prompt manipulation.
- **Actual behavior**: `prompts.py:13` embeds `{user_claim}` directly into the prompt template with `USER_PROMPT_TEMPLATE.format(user_claim=user_claim[:500])`. No delimiters, escaping, or instruction-boundary markers around user input. An attacker could override the system prompt, inject output format changes, or leak information. The system prompt at line 5-7 instructs "Return visual observations only", but a crafted claim could override this.
- **Severity**: High — user-controlled text is directly interpolated into a VLM prompt with no sanitization.
- **Mitigation**: Apply input sanitization: delimit user claim text with clear boundaries (e.g., `[USER_CLAIM_START]...[/USER_CLAIM_END]`), strip or escape prompt-injection patterns, use a structured separate field instead of prose interpolation, and reinforce the system prompt after the user input section.

## Summary

| Category | Severity | Mitigated? |
|----------|----------|------------|
| Missing Images | Low | Yes |
| Corrupt Images | Low | Yes |
| Invalid Image Paths | Medium | Partial |
| Oversized Images | Medium | Partial |
| Invalid JSON from Gemini | Low | Yes |
| Empty Gemini Output | Low | Yes |
| OCR Unavailable | Low | Yes |
| API Unavailable | Medium | Yes |
| CSV Injection | Low | No |
| Prompt Injection | High | No |

## Crash Scenarios Found
No crash scenarios found; all handled gracefully. Every component call in `claim_processor.py:57-160` is individually wrapped in try/except. `main.py:77-95` catches any remaining unhandled exceptions with a hardcoded fallback row. The Gemini retry loop (`vision_analyzer.py:115-137`) has an upper bound of 5 attempts with exponential backoff, so it cannot infinite-loop.

## Unsafe Assumptions
1. **Path safety** (`utils.py:42-44`): Assumes image paths are safe relative paths. `../../etc` bypasses the intended `base_dir` prefix.
2. **File size safety** (`vision_analyzer.py:111`): Assumes files are small enough to read entirely into memory. No server-side size enforcement before `read_bytes()`.
3. **User input safety** (`prompts.py:13`): Assumes `user_claim` text is benign content to be analyzed, not a prompt injection vector.
4. **Output CSV safety** (`main.py:51-56`): Assumes CSV output is only consumed programmatically, not by formula-aware spreadsheet applications.
5. **API key presence** (`vision_analyzer.py:32-37`): Assumes at least one of `config.api_key` or `GEMINI_API_KEY` env var is set; if neither is set, all claims return "Analysis failed: Gemini client not available" with no user-facing indication.
6. **Single VLM dependency** (`vision_analyzer.py:29`): Assumes Gemini is always the correct and only vision model. No fallback to a different VLM or heuristic-based analysis.

## Risk Score
**Overall security risk: Medium**

Justification: The system handles all error conditions gracefully without crashing, and most failure modes produce degraded but safe output. Two issues raise the overall risk to Medium: (1) path traversal (`utils.py:42-44`) could read arbitrary files from disk — a realistic attack vector since image paths come from CSV input. (2) Prompt injection (`prompts.py:13`) is unmitigated and could allow an attacker to manipulate the VLM's output arbitrarily. Both are fixable with targeted input validation. The remaining issues are Low severity or already mitigated.
