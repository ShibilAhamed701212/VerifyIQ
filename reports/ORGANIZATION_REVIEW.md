# Repository Organization Review

## Current Structure

```
verifyiq/
├── .gitignore
├── AGENTS.md
├── ARCHITECTURE.md              # Pre-hardening architecture (now outdated)
├── CLAUDE.md
├── PROJECT_FLOW_REPORT.md
├── README.md                    # Now rewritten
├── problem_statement.md
├── challenge_instructions_extracted.txt
├── TREE_AUDIT.md                # This audit
├── PROJECT_IDENTITY.md          # New
├── ATTRIBUTIONS.md              # New
├── AGENT_HISTORY.log            # New
├── executive_scorecard.md       # Root-level report
├── judge_interview.md           # Root-level report
├── architecture_review.md       # Root-level report
├── competitor_report.md         # Root-level report
├── winning_report.md            # Root-level report
├── reproducibility_report.md    # Root-level report
├── scalability_report.md        # Root-level report
├── security_report.md           # Root-level report
├── output.csv                   # Generated output
│
├── code/                        # Core pipeline
│   ├── main.py, claim_processor.py, ...
│   ├── cv/
│   ├── tests/
│   └── evaluation/
│       ├── evaluate.py
│       ├── static_evaluate.py
│       ├── evaluation_report.md    # Generated artifact
│       ├── error_report.md         # Generated artifact
│       └── WINNING_REVIEW.md       # Report
│
├── docs/                        # Documentation (new)
│   ├── ARCHITECTURE.md
│   ├── EVALUATION.md
│   ├── RELIABILITY.md
│   ├── SECURITY.md
│   ├── REPRODUCIBILITY.md
│   ├── ADVERSARIAL_TESTING.md
│   ├── JUDGE_INTERVIEW.md
│   └── WINNING_REVIEW.md
│
├── adversarial_evaluation/
│   ├── adversarial_claims.csv
│   ├── adversarial_report.md
│   ├── generate_claims.py
│   └── run_adversarial.py
│
├── submission/                  # (to be created)
│
└── docs/superpowers/
    └── plans/
```

## Observations

### Strengths of Current Layout
1. Core pipeline is well-organized in `code/` with clear separation
2. Tests are co-located with code in `code/tests/`
3. CV modules have their own subdirectory `code/cv/`
4. Images are properly separated into `sample/` and `test/`

### Issues with Current Layout

| Issue | Location | Description |
|-------|----------|-------------|
| Root clutter | Root directory | 11 reports + 4 config files + 3 generated files at root level |
| Redundant docs | `ARCHITECTURE.md` at root | Pre-hardening version; `docs/ARCHITECTURE.md` is the new canonical version |
| Generated artifacts committed | `code/evaluation/evaluation_report.md`, `error_report.md` | These are regenerated on every evaluation run |
| Agent configs at root | `AGENTS.md`, `CLAUDE.md` | Not relevant to the project itself |
| Competition artifacts at root | `problem_statement.md`, `challenge_instructions_extracted.txt` | Original problem definition |

## Proposed Structure

```
verifyiq/
├── README.md
├── LICENSE
├── ATTRIBUTIONS.md
├── AGENT_HISTORY.log
├── PROJECT_IDENTITY.md
│
├── code/                        # Core pipeline (unchanged)
│
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md
│   ├── EVALUATION.md
│   ├── RELIABILITY.md
│   ├── SECURITY.md
│   ├── REPRODUCIBILITY.md
│   ├── ADVERSARIAL_TESTING.md
│   ├── JUDGE_INTERVIEW.md
│   └── WINNING_REVIEW.md
│
├── reports/                     # Analysis reports (moved from root)
│   ├── TREE_AUDIT.md
│   ├── ORGANIZATION_REVIEW.md
│   ├── ARCHITECTURE_REVIEW.md
│   ├── COMPETITOR_ANALYSIS.md
│   ├── SCALABILITY.md
│   ├── REPRODUCIBILITY.md
│   └── SECURITY.md
│
├── dataset/                     # Dataset (unchanged)
│
├── adversarial_evaluation/      # Adversarial testing (unchanged)
│
├── submission/                  # Judge submission package
│
└── .gitignore
```

## Benefits of Proposed Structure

1. **Clean root**: Only README, LICENSE, and identity documents at root
2. **Reports organized**: All analysis in `reports/` for easy reference
3. **Canonical docs**: `docs/` is the single source of truth for documentation
4. **Generated artifacts**: Kept in place; `.gitignore` prevents re-committing
5. **Backward compatible**: Existing code references to `code/` don't break

## Recommended Actions

### Move (requires approval)
1. `ARCHITECTURE.md` → `reports/ARCHITECTURE_REVIEW.md` (or keep as historical artifact)
2. `executive_scorecard.md` → `reports/`
3. `judge_interview.md` → `docs/` (or `reports/`)
4. `architecture_review.md` → `reports/`
5. `competitor_report.md` → `reports/`
6. `winning_report.md` → `reports/`
7. `reproducibility_report.md` → `reports/`
8. `scalability_report.md` → `reports/`
9. `security_report.md` → `reports/`

### Delete (requires approval)
1. `CLAUDE.md` — Agent-specific config, not needed for project identity
2. `challenge_instructions_extracted.txt` — Redundant with `problem_statement.md`
3. `code/evaluation/evaluation_report.md` — Generated artifact (regenerated on run)
4. `code/evaluation/error_report.md` — Generated artifact (regenerated on run)

### Keep
1. `AGENTS.md` — Provides useful project context for agents
2. `problem_statement.md` — Core problem definition
3. `PROJECT_FLOW_REPORT.md` — Historical record

## Decision Table

| Change | Benefit | Risk | Requires Approval |
|--------|---------|------|-------------------|
| Move reports to `reports/` | Cleaner root | Breaks any external links to current paths | **Yes** |
| Delete `CLAUDE.md` | Less clutter | None | **Yes** |
| Delete `challenge_instructions_extracted.txt` | Less clutter | Low (content in `problem_statement.md`) | **Yes** |
| Delete generated evaluation reports | Cleaner evaluation dir | Low (regenerated on next run) | **Yes** |
| Keep `AGENTS.md` | Agent compatibility | Medium (contains competition-specific instructions) | **Yes** |
