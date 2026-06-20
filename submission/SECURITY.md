# Security — VerifyIQ

## Image Validation

- **Size limit:** `MAX_FILE_SIZE_BYTES = 10MB` enforced before any decode
- **Format whitelist:** Only `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp` accepted
- **Integrity:** `PIL.Image.open().verify()` checks header and decode integrity without loading pixel data
- **Path handling:** Paths resolved via `pathlib` safe composition (not string concatenation). Known gap: no `Path.resolve()` call before file access — `../../etc` traversal possible

## API Security

- API key read exclusively from `GEMINI_API_KEY` environment variable — no hardcoded credentials
- Missing key: `GeminiVisionClient` skips client creation; returns empty analysis immediately
- Rate limiting: Exponential backoff (`2^attempt * 5s`, max 5 retries) for 429/RESOURCE_EXHAUSTED

## Input Validation

- Output rows pass through enum whitelists for issue_type, object_part, claim_status, severity — invalid values coerced to safe defaults
- Risk flags filtered against `ALLOWED_RISK_FLAGS` — unknown flags silently dropped
- Boolean fields normalized to `"true"`/`"false"`
- User history loaded via `safe_csv_read()` with exception handling

## Adversarial Robustness

- Corrupt images: caught by PIL verify, processing continues with degraded output
- Missing images: every file-touching component has existence guards — pipeline never crashes
- Invalid paths: `pathlib.Path` catches null bytes; outer try/except catches all
- OCR attacks: TextDetector flags readable text presence but doesn't evaluate semantics
- Prompt injection: User claim text interpolated into Gemini prompt without delimiters — fully vulnerable. Known gap.

## Known Gaps

| Gap | Severity | Status |
|-----|----------|--------|
| Prompt injection via claim text | High | Unmitigated — no input sanitization or instruction delimiters |
| Path traversal (no resolve check) | Medium | `../../etc` can read arbitrary files from CSV paths |
| No size pre-filter before API call | Medium | Oversized files (>10MB) still reach `read_bytes()` |
| CSV injection in output | Low | Formula chars in output fields could execute in Excel |
| Single VLM dependency | Medium | No fallback model; Gemini outage = all claims degraded |

**Overall risk score: Medium**
