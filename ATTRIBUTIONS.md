# Attributions

## Overview

VerifyIQ is an original work built for the HackerRank Orchestrate (June 2026) challenge. The system performs multi-modal evidence review for damage claims using computer vision and a Gemini-based vision language model. All pipeline architecture, orchestration logic, rule-based decision engines, prompt engineering, evaluation framework, and CV heuristics were developed independently by the VerifyIQ team.

## Third-Party Dependencies

| Package | License | Usage | Attribution Required |
|---------|---------|-------|---------------------|
| google-genai | Apache 2.0 | Gemini API client for visual observation extraction | Yes |
| Pillow | Historical Permission Notice and Disclaimer (BSD-like) | Image loading, format conversion, validation | Yes |
| opencv-python | MIT | Computer vision (blur detection, crop detection, object validation) | Yes |
| pytesseract | Apache 2.0 | OCR text detection in images | Yes |
| pytest | MIT | Unit testing framework | Yes |

### Dependency Details

- **google-genai** (`vision_analyzer.py:16-17`) — Provides the Gemini client used for vision-based fact extraction from claim images. Licensed under Apache 2.0.
- **Pillow / PIL** (`image_preprocessor.py:14`, `image_validator.py:7`, `tests/test_cv.py:7`) — Used for image format normalization (AVIF, PNG, WebP, BMP → JPEG) and image corruption/validity checks. Licensed under the Historical Permission Notice and Disclaimer (BSD-like).
- **opencv-python (cv2)** (`cv/blur_detector.py:5`, `cv/crop_detector.py:5`, `cv/object_validator.py:6`) — Enables deterministic Laplacian variance blur detection, edge-based crop/obstruction analysis, and dimension-based object validation. Licensed under MIT.
- **pytesseract** (`cv/text_detector.py:17,36-37`) — Wraps Tesseract OCR engine to detect instructional text present in images. Licensed under Apache 2.0.
- **pytest** (`tests/`) — Test runner for all unit tests across CV modules, parsers, rule engine, risk analysis, and output validation. Licensed under MIT.

## License Compatibility

All third-party dependencies use permissive licenses (MIT, Apache 2.0, BSD-like). No GPL, AGPL, LGPL, or other copyleft dependencies are present. VerifyIQ can be distributed under MIT, Apache 2.0, or any permissive license without conflict.

## Original Work Statement

The following components are original works of the VerifyIQ team and are not copied from third-party sources:

- **Pipeline architecture and orchestration** — End-to-end data flow connecting claim parsing, image preprocessing, CV analysis, Gemini vision, rule evaluation, risk analysis, and output validation.
- **Rule engine** — Deterministic decision logic that combines parser results, vision observations, and evidence requirements to produce claim_status, severity, and supporting evidence.
- **Risk analysis and severity mapping** — Heuristic-based risk flag generation and severity assignment based on image quality, mismatches, user history, and confidence levels.
- **Prompt engineering for Gemini** — Custom system and user prompt templates in `code/prompts.py` designed to extract structured visual observations from claim images.
- **Evaluation framework** — Static (deterministic CV + rules) and live (Gemini API) evaluation pipeline with metrics comparison, strategy comparison, and operational cost analysis.
- **CV modules** — BlurDetector (Laplacian variance), CropDetector (edge density + aspect ratio), ObjectValidator (dimension profiles), TextDetector (OCR wrapper) — all independently implemented.
- **Configuration and constants** — Allowed values, thresholds, and path configuration in `code/config.py`.
- **All documentation and reports** — README, evaluation reports, and operational analyses.

## Copied Text Audit

| File | Status | Notes |
|------|--------|-------|
| `problem_statement.md` | Copied from competition repository | Original HackerRank problem specification. Retained verbatim as the authoritative task reference. This is the canonical competition problem statement and must remain unmodified. |
| `README.md` | Original with minor template-derived structure | The repository layout diagram, quickstart instructions, and submission checklist are based on the competition starter template but have been rewritten and extended with project-specific content (chat transcript logging, judge interview prep, evaluation guidance). No verbatim copying from external sources. |
| `code/prompts.py` | Original | Custom-engineered prompts for the Gemini vision model. No copying from external sources. |
| `code/config.py` | Original | Configuration dataclass with allowed-value sets derived from the competition schema. The allowed-value lists (issue types, object parts, risk flags) are factual enumerations from the problem specification, not creative works. |
| `code/vision_analyzer.py` | Original | Gemini vision client implementation, caching layer, response parsing, normalization, and aggregation logic. |
| `code/image_preprocessor.py` | Original | Image normalization pipeline using PIL. |
| `code/image_validator.py` | Original | Image validation checks (size, format, corruption). |
| `code/cv/` | Original | All CV detector modules (blur, crop, text, object validation). |
| `code/tests/` | Original | All test suites. |

## Acknowledgments

- **Google Gemini SDK** (`google-genai`) — Apache 2.0 — https://github.com/googleapis/python-genai
- **Pillow** — Historical Permission Notice and Disclaimer (BSD-like) — https://python-pillow.org
- **OpenCV** — MIT — https://opencv.org
- **Tesseract OCR / pytesseract** — Apache 2.0 — https://github.com/madmaze/pytesseract
- **pytest** — MIT — https://pytest.org
- **HackerRank Orchestrate** — For organizing the challenge and providing the competition problem, starter dataset, and evaluation framework.
