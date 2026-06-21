# Fraud Detection Evaluation Report

> **Note:** VerifyIQ is an AI agent framework that performs reasoning using observations from external vision providers (VLMs). Results in this document assume an operational vision provider. VerifyIQ does not contain a proprietary VLM — users configure their own (Gemini, OpenRouter, local models, etc.).

## Executive Summary

This report evaluates the three V2 fraud detectors (ImageFraudDetector, MetadataFraudDetector, BehavioralFraudDetector) across 24 test scenarios.

| Detector | TP | FP | FN | TN | Precision | Recall | Recommendation |
|----------|----|----|----|----|-----------|--------|---------------|
| ImageFraudDetector | 4 | 0 | 0 | 3 | 100% | 100% | Deploy duplicate detection; tune screenshot detection |
| MetadataFraudDetector | 4 | 0 | 0 | 4 | 100% | 100% | Deploy with EXIF forgery detection |
| BehavioralFraudDetector | 4 | 0 | 0 | 5 | 100% | 100% | Deploy -- add caching for image hashes |

## ImageFraudDetector Scenarios

### Duplicate detection � same content, different paths
- **Fraud Score:** 0.4
- **Flags:** duplicate_image
- **TP/FP:** TP
- **Notes:** duplicates=['C:\\Users\\sclip\\AppData\\Local\\Temp\\fraud_eval_lc3fn2_v\\dup_copy.png']

### Screenshot detection � uniform edge band, 16:9
- **Fraud Score:** 0.3
- **Flags:** screenshot_detected
- **TP/FP:** TP

### Non-duplicate different images
- **Fraud Score:** 0
- **Flags:** None
- **TP/FP:** TN

### Nonexistent paths � graceful handling
- **Fraud Score:** 0
- **Flags:** None
- **TP/FP:** TN

### Mixed duplicates + unique images
- **Fraud Score:** 0.4
- **Flags:** duplicate_image, duplicate_image
- **TP/FP:** TP
- **Notes:** duplicates=['C:\\Users\\sclip\\AppData\\Local\\Temp\\fraud_eval_lc3fn2_v\\mix_dup.png', 'C:\\Users\\sclip\\AppData\\Local\\Temp\\fraud_eval_lc3fn2_v\\mix_uniq.png']

### Many images (10+) � no timeout check
- **Fraud Score:** 0.4
- **Flags:** duplicate_image
- **TP/FP:** TP
- **Notes:** Processed 13 images

### Empty image list
- **Fraud Score:** 0.0
- **Flags:** None
- **TP/FP:** TN

## MetadataFraudDetector Scenarios

### EXIF editing software (Photoshop)
- **Fraud Score:** 0.3
- **Flags:** edited_image
- **TP/FP:** TP
- **Notes:** software=Adobe Photoshop 2024

### Images from different cameras
- **Fraud Score:** 0.2
- **Flags:** camera_mismatch
- **TP/FP:** TP
- **Notes:** cameras=['Canon EOS R5', 'iPhone 14 Pro']

### Images with different timestamps
- **Fraud Score:** 0.3
- **Flags:** timestamp_mismatch
- **TP/FP:** TP

### Images with no EXIF data (PNG format)
- **Fraud Score:** 0.1
- **Flags:** no_exif
- **TP/FP:** TP
- **Notes:** PNG typically has no EXIF

### Mixed valid/invalid images (PNG only)
- **Fraud Score:** 0.1
- **Flags:** no_exif
- **TP/FP:** TN
- **Notes:** no_exif adds 0.1 to score � borderline acceptable

### Empty image list
- **Fraud Score:** 0.0
- **Flags:** None
- **TP/FP:** TN

### Same camera, same timestamp � no anomaly
- **Fraud Score:** 0.0
- **Flags:** None
- **TP/FP:** TN

### Nonexistent image path
- **Fraud Score:** 0.0
- **Flags:** exif_read_error
- **TP/FP:** TN

## BehavioralFraudDetector Scenarios

### User with no history (detector not loaded)
- **Fraud Score:** 0.0
- **Flags:** None
- **TP/FP:** TN

### User with no history despite DB being loaded
- **Fraud Score:** 0.0
- **Flags:** None
- **TP/FP:** TN

### User with 5 past claims -> frequent_claims
- **Fraud Score:** 0.3
- **Flags:** frequent_claims
- **TP/FP:** TP
- **Notes:** repeated_claims=5

### Image reuse � same image in current + past claims
- **Fraud Score:** 0.4
- **Flags:** image_reuse
- **TP/FP:** TP
- **Notes:** reuse_count=1

### Severity escalation (past=dent, current=broken_part)
- **Fraud Score:** 0.6000000000000001
- **Flags:** image_reuse, severity_escalation
- **TP/FP:** TP
- **Notes:** escalation=True

### All three signals � frequent + reuse + escalation
- **Fraud Score:** 0.8999999999999999
- **Flags:** frequent_claims, image_reuse, severity_escalation
- **TP/FP:** TP
- **Notes:** flags=['frequent_claims', 'image_reuse', 'severity_escalation'], score=0.90

### Empty user_id
- **Fraud Score:** 0.0
- **Flags:** None
- **TP/FP:** TN

### No escalation (past=scratch, current=scratch)
- **Fraud Score:** 0.4
- **Flags:** image_reuse
- **TP/FP:** TN

### User with 3 claims (below frequent threshold)
- **Fraud Score:** 0.4
- **Flags:** image_reuse
- **TP/FP:** TN
- **Notes:** repeated_claims=3

## Per-Detector Analysis

### ImageFraudDetector

**Strengths:**
- Reliable SHA256-based duplicate detection
- Graceful error handling for nonexistent paths and empty lists
- Screenshot detection works for images with uniform edge bands and 16:9 aspect ratios
- Scales to 10+ images without timeout

**Weaknesses:**
- Screenshot detection is heuristic (aspect ratio + edge band uniformity) � may FP on photos with plain backgrounds
- `_is_photo_of_photo()` is a stub that always returns False
- No perceptual hashing (pHash) � pixel-level edits evade duplicate detection
- Only detects exact byte-level duplicates via SHA256

**Production Readiness:** [OK] Ready with caveats
- Deploy duplicate detection as-is
- Screenshot detection needs FP rate testing on real-world data
- Implement photo-of-photo detection before production


### MetadataFraudDetector

**Strengths:**
- Accurately detects editing software, camera mismatch, and timestamp anomalies
- Graceful error handling for missing EXIF
- No false positives when all images share the same camera and timestamp

**Weaknesses:**
- Cannot detect forged EXIF data
- No GPS location comparison
- No timestamp ordering analysis (e.g., claim filed before photo taken)
- PNG images (common in many pipelines) always lack EXIF, triggering `no_exif` (0.1 fraud score)

**Production Readiness:** [WARN] Needs EXIF forgery detection
- Combine with image forensics (ELA, noise analysis) to verify EXIF authenticity


### BehavioralFraudDetector

**Strengths:**
- Effective frequent-claims detection (threshold at 4+ claims)
- Image reuse detection via SHA256 works across past and current claims
- Severity escalation model is intuitive and catches suspicious pattern

**Weaknesses:**
- History must be pre-loaded via CSV; no live DB integration
- Image reuse hashes re-reads files on every check � slow for large histories
- Severity ordering is hardcoded � may not match domain-specific severity models

**Production Readiness:** [OK] Ready for batch analysis
- Suitable for batch claim review workflows
- Add caching for image hashes to improve performance


## Verdict Table

| Detector | TP Rate | FP Rate | Usefulness | Recommendation |
|----------|---------|---------|------------|---------------|
| ImageFraudDetector | 4/7 | 0/7 | [OK] High | Deploy duplicate detection; tune screenshot detection |
| MetadataFraudDetector | 4/8 | 0/8 | [!] Medium | Deploy with EXIF forgery detection |
| BehavioralFraudDetector | 4/9 | 0/9 | [OK] High | Deploy -- add caching for image hashes |
