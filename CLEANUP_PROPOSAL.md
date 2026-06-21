# Cleanup Proposal — VerifyIQ

Generated: 2026-06-20

> DO NOT DELETE without explicit approval. This document proposes removals.

---

## 1. Empty/Redundant Directories

| Path | Size | Proposal | Reason |
|------|------|----------|--------|
| `verifyiq/v2/recommender/` | 0 bytes | Delete | Empty leftover dir |
| `code/v2/localization/` | 1 file (research.md) | Already moved to `research/localization/` | Contents relocated |

## 2. Temporary/One-off Files (→ research/validation/)

Already moved. No deletion proposed.

## 3. Duplicate Reports

| Files | Proposal | Reason |
|-------|----------|--------|
| `reports/winning_report.md` ↔ `docs/WINNING_REVIEW.md` | Keep both? Check content | `docs/` version may be superseded |
| `docs/evaluation/JUDGE_INTERVIEW.md` ↔ `archive/judge_interview.md` | Check content | Archive may hold older version |

## 4. Generated Artifacts (Already in .gitignore)

| Pattern | Proposal |
|---------|----------|
| `dist/` | Keep in .gitignore |
| `verifyiq.egg-info/` | Keep in .gitignore |
| `__pycache__/` | Keep in .gitignore |
| `.pytest_cache/` | Keep in .gitignore |
| `.ruff_cache/` | Keep in .gitignore |

## 5. Stale/Dangling Files

| File | Proposal | Reason |
|------|----------|--------|
| `docs/superpowers/plans/2026-06-19-leaderboard-score-optimization.md` | Archive or delete | Superseded plan |

## 6. Frozen V1 Code

| Path | Proposal | Status |
|------|----------|--------|
| `code/` | Keep as-is | FROZEN — no modifications |
| `code/` → `archive/competition_v1/` | Move after approval | Awaiting user approval |

## 7. Code Duplication Risk

The following now exist in two locations:

| Source | Copy | Status |
|--------|------|--------|
| `code/v2/` | `verifyiq/v2/` | Original kept for test compatibility |
| `code/tests/` | `tests/v1/` | New canonical location |
| `code/v2/tests/` | `tests/v2/` | New canonical location |

**Proposal after validation:**
- Tests should run from `tests/` only
- `code/v2/` can be archived once `verifyiq/v2/` is verified in all paths
- `code/tests/` and `code/v2/tests/` can be removed once all CI and workflows point to `tests/`

## 8. Path Cleanup (pyproject.toml)

Currently includes both old and new test paths:

```toml
testpaths = [
    "tests/v1",
    "tests/v2",
    "code/tests",      # ← can be removed after migration
    "code/v2/tests",   # ← can be removed after migration
]
```

**Proposal:** Remove `code/tests` and `code/v2/tests` from testpaths after 1 week of stable CI runs.

---

## Summary

| Category | Items | Action |
|----------|-------|--------|
| Delete safe | 1 empty dir | Delete |
| Move pending | 1 archived plan | Archive |
| Remove after validation | 2 old test paths | Wait |
| Archive pending approval | `code/` → `archive/competition_v1/` | Wait |
| Monitor | Duplicate test locations | Resolve in next pass |
