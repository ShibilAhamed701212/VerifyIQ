# Architecture

## Pipeline Diagram

```
Input CSV --> ImagePreprocessor --> ImageValidator --> ClaimParser
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
                                              +----------+----------+
                                              |                     |
                                              v                     v
                                        RiskAnalyzer        SeverityEngine
                                              |                     |
                                              +----------+----------+
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

## 11 Components

1. **ImagePreprocessor** — Normalizes AVIF/WebP/PNG/BMP/GIF to standard JPEG (quality=95) so downstream modules receive a uniform format. RGBA/LA/P modes converted to RGB.

2. **ImageValidator** — Pre-processing checks: file existence, format whitelist (`.jpg`, `.png`, `.gif`, `.webp`, `.bmp`), 10MB size limit, PIL decode integrity via `img.verify()`. Per-image error isolation.

3. **ClaimParser** — Extracts `claimed_damage_type` and `claimed_object_part` from customer utterances using keyword matching with 25-char negation detection. Filters out Support/Agent lines.

4. **GeminiVisionClient** — The only non-deterministic component. Extracts visual observations only (damage type, visible parts, quality, confidence) — never outputs claim status. Hash-based response cache eliminates API variance on cache hits.

5. **EvidenceChecker** — Evaluates whether images meet semantic evidence requirements from CSV. Checks clarity, angle, obstruction, and non-original markers. Prefers vision-detected part over claimed part.

6. **RuleEngine** — Six-path deterministic decision tree: evidence insufficient → not_enough_information, damage not visible → contradicted, damage type conflict → contradicted, object part conflict → contradicted, low confidence → not_enough_information, otherwise → supported.

7. **RiskAnalyzer** — Computes risk flags from vision quality, rule mismatches, user history (claims >3 in 90 days, >2 rejected), and CV module overrides (blur, crop, OCR, object validation). CV modules only add flags, never remove.

8. **SeverityEngine** — Static lookup table: glass_shatter/water_damage → high, crack/broken_part/dent → medium, scratch/torn_packaging → low. Boost words ("severe", "major") increase one level. Non-original images force high.

9. **DecisionAgent** — Assembles final output row from all prior components. Builds human-readable `claim_status_justification` trace. `fallback_output` method ensures every failure produces a valid row.

10. **OutputValidator** — Schema enforcement, enum whitelist validation, boolean normalization, consistency checks (e.g., supported status cannot have unknown issue_type).

11. **SubmissionCritic** — Post-processing across all rows. Four fix functions catch contradictions per-row validation missed: unknown-without-review, supported-with-no-damage, supported-with-conflict, missing-manual-review.

## Data Flow

The pipeline processes one claim at a time. Each CSV row enters with `user_id`, `image_paths`, `user_claim`, `claim_object`. Images are normalized → validated → parsed alongside claim text → sent to Gemini for observations → evidence checked against requirements → rule engine decides status → risk flags computed → severity assigned → all fields assembled → validated → post-processed → written to CSV. Every stage produces valid output even on complete failure.
