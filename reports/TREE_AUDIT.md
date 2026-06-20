# Project Tree Audit

## Overview

Complete recursive file inventory and classification of the VerifyIQ repository. Generated 2026-06-20.

## Classification Legend

| Class | Description |
|-------|-------------|
| **Active Source** | Core pipeline code, actively used |
| **Active Test** | Test files for active source |
| **Documentation** | Project documentation, READMEs, guides |
| **Report** | Evaluation reports, analysis, reviews |
| **Configuration** | Config files, gitignores, agent prompts |
| **Dataset** | Input data (CSV, images) |
| **Generated Output** | Files produced by running the pipeline |
| **Generated Artifact** | Files produced by utility scripts |
| **Temporary** | Cache directories, temp files |
| **Design/Plan** | Superpowers specs and plans |
| **Obsolete** | Files no longer relevant |
| **Duplicate** | Files that duplicate content |

## File Inventory

### Root Level

| File | Class | Notes |
|------|-------|-------|
| `AGENTS.md` | Configuration | Agent instructions for AI tools |
| `ARCHITECTURE.md` | Documentation | Pre-hardening architecture doc |
| `CLAUDE.md` | Configuration | Claude-specific instructions |
| `PROJECT_FLOW_REPORT.md` | Report | Pre-hardening project flow |
| `README.md` | Documentation | Current README (needs rewrite) |
| `problem_statement.md` | Documentation | Original challenge description |
| `challenge_instructions_extracted.txt` | Documentation | Extracted instructions |
| `output.csv` | Generated Output | Pipeline output (gitignored) |
| `executive_scorecard.md` | Report | Executive scoring (Task 18) |
| `judge_interview.md` | Report | Judge interview prep (Task 11) |
| `architecture_review.md` | Report | Architecture challenge (Task 12) |
| `competitor_report.md` | Report | Competitor analysis (Task 16) |
| `winning_report.md` | Report | First place review (Task 17) |
| `reproducibility_report.md` | Report | Reproducibility report (Task 13) |
| `scalability_report.md` | Report | Throughput report (Task 14) |
| `security_report.md` | Report | Security review (Task 15) |
| `.gitignore` | Configuration | Git ignore rules |
| `TREE_AUDIT.md` | Report | This file |
| `PROJECT_IDENTITY.md` | Documentation | Project philosophy (new) |
| `ATTRIBUTIONS.md` | Documentation | License audit (new) |
| `AGENT_HISTORY.log` | Documentation | Development history (new) |

### code/ Directory

| File | Class | Notes |
|------|-------|-------|
| `code/main.py` | Active Source | Entry point, orchestrates processing |
| `code/claim_processor.py` | Active Source | Per-claim pipeline orchestrator |
| `code/claim_parser.py` | Active Source | Deterministic claim text parser |
| `code/vision_analyzer.py` | Active Source | Gemini vision client |
| `code/evidence_checker.py` | Active Source | Evidence requirement evaluation |
| `code/rule_engine.py` | Active Source | Decision rule engine |
| `code/risk_analyzer.py` | Active Source | Risk flag computation |
| `code/severity_engine.py` | Active Source | Severity mapping |
| `code/decision_agent.py` | Active Source | Final output builder |
| `code/output_validator.py` | Active Source | Schema + consistency validation |
| `code/submission_critic.py` | Active Source | Post-processing critic (v2) |
| `code/image_preprocessor.py` | Active Source | Image normalization (v2) |
| `code/image_validator.py` | Active Source | Image validation (v2) |
| `code/config.py` | Active Source | Configuration dataclass |
| `code/prompts.py` | Active Source | Gemini prompt templates |
| `code/utils.py` | Active Source | Utility functions |
| `code/README.md` | Documentation | Code directory README |

### code/cv/ Directory

| File | Class | Notes |
|------|-------|-------|
| `code/cv/__init__.py` | Active Source | Package init |
| `code/cv/blur_detector.py` | Active Source | OpenCV blur detection |
| `code/cv/crop_detector.py` | Active Source | OpenCV crop detection |
| `code/cv/text_detector.py` | Active Source | OCR text detection (v2, safe mode) |
| `code/cv/object_validator.py` | Active Source | Wrong object detection |

### code/tests/ Directory

| File | Class | Notes |
|------|-------|-------|
| `code/tests/__init__.py` | Active Test | Package init |
| `code/tests/test_utils.py` | Active Test | Utils tests (original) |
| `code/tests/test_parser.py` | Active Test | Parser tests (original) |
| `code/tests/test_rule_engine.py` | Active Test | Rule engine tests (original) |
| `code/tests/test_risk_flags.py` | Active Test | Risk flag tests (original) |
| `code/tests/test_cv.py` | Active Test | CV module tests (original) |
| `code/tests/test_validator.py` | Active Test | Validator tests (v2) |
| `code/tests/test_critic.py` | Active Test | Critic tests (v2) |
| `code/tests/test_image_validator.py` | Active Test | Image validator tests (v2) |

### code/evaluation/ Directory

| File | Class | Notes |
|------|-------|-------|
| `code/evaluation/__init__.py` | Active Source | Package init |
| `code/evaluation/main.py` | Active Source | Compatibility entry point |
| `code/evaluation/evaluate.py` | Active Source | Full evaluation pipeline |
| `code/evaluation/static_evaluate.py` | Active Source | Static (ideal vision) evaluation |
| `code/evaluation/error_analysis.py` | Active Source | Error analysis utilities |
| `code/evaluation/evaluation_report.md` | Report | Generated evaluation report |
| `code/evaluation/error_report.md` | Report | Generated error analysis report |
| `code/evaluation/WINNING_REVIEW.md` | Report | Winning solution review (v2) |

### dataset/ Directory

| File | Class | Notes |
|------|-------|-------|
| `dataset/claims.csv` | Dataset | Production input (44 claims) |
| `dataset/sample_claims.csv` | Dataset | Evaluation input (20 claims) |
| `dataset/user_history.csv` | Dataset | User history for risk analysis |
| `dataset/evidence_requirements.csv` | Dataset | Evidence rules |
| `dataset/images/sample/*.jpg` | Dataset | Sample images (20 images) |
| `dataset/images/test/*.jpg` | Dataset | Test images (82 images) |

### adversarial_evaluation/ Directory

| File | Class | Notes |
|------|-------|-------|
| `adversarial_evaluation/adversarial_claims.csv` | Dataset | 100 synthetic adversarial claims |
| `adversarial_evaluation/adversarial_report.md` | Report | Adversarial testing report |
| `adversarial_evaluation/generate_claims.py` | Active Source | Claim generator script |
| `adversarial_evaluation/run_adversarial.py` | Active Source | Adversarial runner script |

### docs/superpowers/ Directory

| File | Class | Notes |
|------|-------|-------|
| `docs/superpowers/plans/2026-06-19-leaderboard-score-optimization.md` | Design/Plan | Previous optimization plan |
| `docs/superpowers/plans/2026-06-20-professionalization.md` | Design/Plan | Professionalization plan (this work) |

## Unused / Obsolete Files

| File | Reason | Risk of Removal |
|------|--------|-----------------|
| `CLAUDE.md` | Agent-specific config for Claude Code. No longer the primary agent. | Low — other agents don't use it |
| `AGENTS.md` | HackerRank project instructions. Contains onboarding flow, log format, project contract. Still provides useful project context. | Medium — other agents may rely on it |
| `challenge_instructions_extracted.txt` | Extracted from the original problem statement. Redundant with `problem_statement.md`. | Low |
| `docs/superpowers/plans/2026-06-19-leaderboard-score-optimization.md` | Previous plan from earlier development phase. Historical record. | Low |

## Generated Artifacts (Should Be .gitignored but Are Committed)

| File | Reason |
|------|--------|
| `output.csv` | Pipeline output; already in .gitignore |
| `dataset/output.csv` | Another output; same generated nature |
| `code/evaluation/evaluation_report.md` | Generated by evaluation run |
| `code/evaluation/error_report.md` | Generated by error analysis |

## Recommendations

### Ready for Removal (with approval)
1. `CLAUDE.md` — Claude-specific config; framework-agnostic project shouldn't include it
2. `challenge_instructions_extracted.txt` — Redundant with `problem_statement.md`

### Should Remain
1. `AGENTS.md` — Still provides valuable project context for any agent
2. `problem_statement.md` — Core problem definition
3. All historical plans and reports — Development record

### Should Be .gitignored (not committed in future)
1. `code/evaluation/evaluation_report.md` — Generated artifact
2. `code/evaluation/error_report.md` — Generated artifact
3. `dataset/output.csv` — Generated output
