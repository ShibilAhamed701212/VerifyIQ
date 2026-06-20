# VerifyIQ V2 — Security Posture

## Known Vulnerabilities in V1

### Path Traversal in `utils.py`
The V1 `utils.py` module handles user-supplied image paths without proper sanitization. Paths are used directly in file I/O operations, making the system susceptible to directory traversal attacks. An attacker could supply paths like `../../etc/passwd` to read arbitrary files from the server filesystem. V1 does not canonicalize paths with `Path.resolve()` and does not validate that resolved paths remain within an allowed base directory.

### Additional V1 Concerns
- No input-length limits on claim text, leaving the system open to resource exhaustion via large payloads.
- No prompt-injection filtering on user-provided claim text before it reaches the LLM.
- No CSV-injection protection on fields written to output CSVs.
- Filename sanitization is minimal and does not strip control characters.

## V2 InputSanitizer Protections

The `code/v2/security/sanitizer.py` `InputSanitizer` class provides four sanitization methods:

### `sanitize_claim_text(text)`
- **1000-character hard limit** prevents resource exhaustion.
- **Prompt injection redaction**: Scans for known injection patterns (e.g., "ignore previous instructions", "system prompt", "override", "disregard all previous", "you must now", "redefine your purpose") and replaces them with `[REDACTED]`.

### `sanitize_image_path(path, base_dir)`
- **Null byte detection**: Rejects paths containing `\x00`.
- **Path traversal pattern detection**: Explicit regex check for `../` and `..\` sequences (cross-platform: Windows and POSIX). Detects both inline and trailing `..` patterns.
- **Canonicalization + prefix check**: Resolves the full path via `Path.resolve()` and verifies the resolved target starts with the resolved base directory. This catches symlink-relative attacks and indirect traversal.

### `sanitize_csv_field(value)`
- **Dangerous leading characters**: Detects `=`, `+`, `-`, `@`, `|`, and tab (`\t` or `\x09`).
- **Double-quote wrapping**: Wraps dangerous fields in double quotes for Excel compatibility, prefixed with `'` for defense-in-depth.
- **Tab-hijacking detection**: Detects tab characters anywhere in the field value.

### `sanitize_filename(name)`
- Strips `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, `*`, and ASCII control characters (`\x00`–`\x1f`) from filenames.

## Security Posture Overview

| Threat | V1 | V2 |
|---|---|---|
| Path traversal | Not protected | Resolve + prefix check + pattern detection + null byte check |
| Prompt injection | Not protected | 12 regex patterns + hard length limit |
| CSV injection | Not protected | Leading-char detection + double-quote wrapping + tab detection |
| Filename injection | Minimal | Full control-char stripping |
| Input-length DoS | Not protected | 1000-char hard limit |
