# Evaluation Report

## Summary

- **Total Claims:** 20
- **Correct:** 0
- **Accuracy:** 0.00%

- **Precision:** 5.00%
- **Recall:** 5.00%

- **F1 Score:** 5.00%
- **Risk Flag Accuracy:** 0.00%

## Claim Status Metrics

| Status | Accuracy | Precision | Recall | Support |
|--------|----------|-----------|--------|---------|
| supported | 0.00% | 0.00% | 0.00% | 10 |
| contradicted | 0.00% | 0.00% | 0.00% | 9 |
| not_enough_information | 100.00% | 5.00% | 100.00% | 1 |

## Detailed Results

| Claim | Status | Match | Differences |
|-------|--------|-------|-------------|
| user_001 | car | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_002 | car | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_004 | car | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_007 | car | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_005 | car | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_006 | car | NO | risk_flags, issue_type, valid_image, severity |
| user_003 | car | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_008 | car | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_009 | laptop | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_010 | laptop | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_011 | laptop | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_012 | laptop | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_018 | laptop | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_020 | laptop | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_015 | package | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_030 | package | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_031 | package | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_032 | package | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_033 | package | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_034 | package | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |

## Operational Analysis

### Model Calls
- Sample processing: ~20 claims x 1 vision call = ~20 calls
- Test processing: ~20 claims x 1 vision call = ~20 calls

### Token Usage (Estimated)
- Input per call: ~500-800 tokens (text + images)
- Output per call: ~300-500 tokens
- Total input: ~13000 tokens
- Total output: ~8000 tokens

### Cost Estimation
- Model used by implementation: Gemini via google-genai
- Cost depends on the active Gemini pricing tier and image token accounting

### Latency
- Average per claim: ~3-8 seconds (including API calls)
- Total for test set: ~100 seconds

### Rate Limiting Strategy
- Retry with exponential backoff (3 attempts, 2s-30s)
- Sequential processing to respect TPM limits
- Configurable max images per claim (default: 5)
- Image caching via base64 encoding
