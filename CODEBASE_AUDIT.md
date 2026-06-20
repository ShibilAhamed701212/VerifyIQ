# Codebase Audit

## Repository Overview

| Metric | Value |
|--------|-------|
| Python files | 105 (406,746 bytes total) |
| Markdown files | 99 (909,008 bytes total) |
| Python avg size | 3,873 bytes |
| Python median | 2,264 bytes |
| Empty .py files | 4 (cv/__init__, evaluation/__init__, tests/__init__, v2/tests/__init__) |
| Largest .py file | validate_v1_vs_v2.py (35,302 bytes) |
| Memory (loaded) | 24.6 MB RSS |

## Module Inventory

### V1 Core (code/)
| File | Lines | Role |
|------|-------|------|
| main.py | 3,415 | Primary orchestrator |
| config.py | 2,264 | Configuration and constants |
| claim_parser.py | 5,231 | Deterministic claim parsing |
| claim_processor.py | 7,314 | Claim processing orchestrator |
| vision_analyzer.py | 14,039 | Gemini vision extraction |
| evidence_checker.py | 6,085 | Semantic evidence checking |
| rule_engine.py | 6,017 | Deterministic rule engine |
| risk_analyzer.py | 6,997 | Risk flag and severity analysis |
| severity_engine.py | 2,189 | Severity mapping |
| decision_agent.py | 5,118 | Final decision assembly |
| output_validator.py | 4,186 | Output schema validation |
| submission_critic.py | 4,835 | Post-processing validation |
| image_validator.py | 1,781 | Pre-processing validation |
| image_preprocessor.py | 1,414 | Format normalization |
| prompts.py | 1,336 | Gemini prompt templates |
| utils.py | 2,704 | Shared utilities |

### V1 CV (code/cv/)
| File | Lines | Role |
|------|-------|------|
| blur_detector.py | 889 | Laplacian blur detection |
| crop_detector.py | 1,886 | Crop/obstruction detection |
| text_detector.py | 2,320 | OCR via pytesseract |
| object_validator.py | 2,422 | Wrong-object heuristics |

### V2 Core (code/v2/)
| File | Lines | Role |
|------|-------|------|
| pipeline.py | 13,817 | 10-layer orchestrator |
| v1_adapter.py | 5,936 | V1 bridge adapters |
| risk_merger.py | 4,122 | Mode-aware flag classification |

### V2 Models (code/v2/models/)
| File | Lines | Role |
|------|-------|------|
| __init__.py | 851 | Re-exports |
| observation.py | 895 | Observation dataclasses |
| consensus.py | 503 | Consensus dataclasses |
| fraud.py | 1,412 | Fraud dataclasses |
| evidence.py | 436 | Evidence dataclasses |
| conversation.py | 554 | Conversation dataclasses |
| confidence.py | 482 | Confidence dataclasses |
| decision.py | 950 | Decision dataclasses |

### V2 Modules
| Module | Files | Role |
|--------|-------|------|
| confidence/ | 1 | ConfidenceCalibrator |
| consensus/ | 1 | ConsensusEngine |
| conversation/ | 1 | ConversationAnalyzer |
| critic/ | 1 | V2Critic cross-layer review |
| evidence/ | 1 | EvidenceRecommender |
| explainability/ | 1 | DecisionTracer |
| fraud/ | 3 | Image, Metadata, Behavioral |
| observability/ | 2 | MetricsCollector, TraceLogger |
| providers/ | 4 | Vision providers (base, gemini, openrouter, local) |
| security/ | 1 | InputSanitizer |
| decision/ | 0 | Placeholder only |

### Root Validators
| File | Lines | Role |
|------|-------|------|
| validate_v1_vs_v2.py | 35,302 | 3-mode comparison harness |
| validate_confidence.py | 21,909 | Confidence analysis |
| validate_fraud.py | 22,666 | Fraud validation |
| validate_conversation.py | 22,227 | Conversation validation |
| validate_hidden_tests.py | 32,282 | Hidden test simulation |
| validate_performance.py | 4,569 | Performance benchmark |
| validate_reliability.py | 5,274 | Reliability validation |

### Distribution Package (verifyiq/)
| File | Lines | Role |
|------|-------|------|
| __init__.py | 474 | Package metadata |
| __main__.py | 2,060 | CLI entry point |
| v1/__init__.py | 1,153 | V1 wrapper |
| v2/__init__.py | 2,483 | V2 wrapper |

### Supporting
| File | Lines | Role |
|------|-------|------|
| adversarial_evaluation/ | 2 | Adversarial test generation |
| examples/ | 4 | Quickstart, V1, V2, security demos |

## Import Graph Summary

```
code/ (V1) ──────────────────────────────┐
    ├── config.py (standalone)            │
    ├── utils.py (used by all V1)         │
    ├── claim_parser.py (standalone)      │
    ├── rule_engine.py (claim_parser)     │
    ├── evidence_checker.py (config)      │
    ├── risk_analyzer.py (config, rule)   │
    ├── decision_agent.py (many deps)     │
    ├── output_validator.py (config)      │
    └── submission_critic.py (standalone) │
                                          │
code/v2/ (V2) ────────────────────────────┤
    ├── v1_adapter.py → ALL V1 modules    │
    ├── pipeline.py → v1_adapter, models  │
    ├── risk_merger.py (standalone)       │
    └── models/ → dataclasses only        │
                                          │
verifyiq/ (distribution) ────────────────┤
    ├── v1/__init__ → wraps code/         │
    └── v2/__init__ → wraps code/v2/      │
```

## File Count by Category

| Category | Count |
|----------|-------|
| Production Python | 35 |
| Test Python | 18 |
| Validation/Harness Python | 9 |
| Adversarial Python | 2 |
| Examples Python | 4 |
| Distribution Python | 4 |
| Empty __init__.py | 6 |
| Markdown reports | 55 |
| Markdown docs | 20 |
| Markdown submissions | 10 |
| Markdown archive | 2 |
| Other (.yml, .toml, Dockerfile) | 8 |

## Documentation Inventory

55 Markdown files at root level. These span:
- 10 phase reports (FINAL_ACCURACY_*.md, CONFIDENCE_AUDIT.md, etc.)
- 10 competition analysis reports
- 7 operational docs (CHANGELOG, GOVERNANCE, CONTRIBUTING, etc.)
- 8 competitive/scoring docs
- 5 V2 design docs (V2_ARCHITECTURE, V2_ROADMAP, etc.)
- 3 risk analysis docs (RISK_GAP, RISK_FLAG, RISK_MODE)
- 1 from each validation script (CONFIDENCE_ANALYSIS, FRAUD_EVALUATION, etc.)
- Various others
