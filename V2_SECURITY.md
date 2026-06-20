# VerifyIQ V2 — Security Evaluation

## Overview

V2 introduces a dedicated `InputSanitizer` class that addresses the three critical security gaps identified in V1: prompt injection, path traversal, and CSV injection. No API authentication or rate limiting layer exists yet — these are planned for the production API server (Phase 20).

---

## Gaps Resolved vs V1

### 1. Prompt Injection

**V1 status:** Fully vulnerable. User claim text was interpolated directly into the Gemini prompt without delimiters. A claim text containing `ignore previous instructions` would bypass the system prompt entirely.

**V2 mitigation:** `InputSanitizer.sanitize_claim_text()` (`code/v2/security/sanitizer.py:8-24`)

- Strips known injection patterns via regex: `ignore all previous instructions`, `forget all prior prompts`, `you are now`, `system prompt`, `new instructions`, `override`
- Enforces 1000-character hard length limit
- Replaces matched patterns with `[REDACTED]`

**Limitation:** Regex-based pattern matching is brittle. An attacker who varies capitalization, adds whitespace, or uses encoded characters may bypass the pattern list. A proper solution would wrap claim text in instruction boundary tokens and use a dedicated safety classifier.

### 2. Path Traversal

**V1 status:** Known gap. Image paths were resolved via `pathlib` composition without a `Path.resolve()` call, making `../../etc/passwd` traversal theoretically possible.

**V2 mitigation:** `InputSanitizer.sanitize_image_path()` (`code/v2/security/sanitizer.py:27-36`)

- Resolves the base directory with `Path.resolve()`
- Resolves the target path relative to the base
- Returns empty string if the resolved target does not start with the base directory
- Catches all exceptions and returns empty string on error

**Coverage:** All image paths pass through this check in `V2Pipeline.process()` (`pipeline.py:90`). Paths that fail are filtered out.

### 3. CSV Injection

**V1 status:** Low risk. Formula-starting characters (`=`, `+`, `-`, `@`) in output fields could execute commands when opened in Excel or LibreOffice Calc.

**V2 mitigation:** `InputSanitizer.sanitize_csv_field()` (`code/v2/security/sanitizer.py:39-45`)

- Prefixes values starting with `=`, `+`, `-`, `@`, or `|` with a leading single quote
- Applied to claim text before pipeline processing

### 4. Malicious Filenames

**V1 status:** No filename sanitization existed.

**V2 mitigation:** `InputSanitizer.sanitize_filename()` (`code/v2/security/sanitizer.py:48-50`)

- Removes dangerous characters: `<`, `>`, `:`, `"`, `/`, `\`, `|`, `?`, `*`, and control characters (0x00-0x1F)

---

## Remaining Gaps

| Gap | Severity | Status | Details |
|-----|----------|--------|---------|
| No output encoding for HTML contexts | Medium | Unmitigated | Decision justification text is not HTML-encoded. If rendered in a web dashboard, stored XSS is possible. |
| No API authentication | High | Unmitigated | V2 has no API layer. When the API server is built (Phase 20), `X-API-Key` auth must be added. |
| No rate limiting | Medium | Unmitigated | No protection against abuse or DDoS. Planned for Phase 20. |
| Prompt injection bypass via variant patterns | Medium | Partial | Regex patterns cover common cases but not all variants. Consider switching to instruction boundary wrapping + LLM-based safety filter. |
| No input size limits for batch | Low | Unmitigated | Batch endpoint (planned) has no upper bound on claim count. Must add limit enforcement. |

---

## Risk Assessment

| Category | V1 Score | V2 Score | Delta |
|----------|----------|----------|-------|
| Prompt injection | High | Medium | +1 |
| Path traversal | Medium | Low | +1 |
| CSV injection | Low | Low | 0 |
| API security | High | High | 0 |
| **Overall** | **Medium** | **Low** | **+1** |

**Overall risk score: LOW** (down from MEDIUM in V1)

The improvement is driven by prompt injection mitigation and path traversal resolution. Both were the highest-severity gaps in V1. The remaining gaps (auth, rate limiting, output encoding) are standard for pre-production systems and are scoped to the planned API server phase.

---

## Mitigation Timeline

| Gap | Planned Phase | Target Date |
|-----|---------------|-------------|
| API authentication | Phase 20 | Production server |
| Rate limiting | Phase 20 | Production server |
| Output encoding | Phase 20 | Production server |
| Prompt injection hardening | Phase 20 | Production server |
