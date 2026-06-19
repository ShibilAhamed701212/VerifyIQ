# Evaluation Report

## Summary

- **Total Claims:** 10
- **Correct:** 2
- **Accuracy:** 20.00%

## Detailed Results

| Claim | Status | Match | Differences |
|-------|--------|-------|-------------|
| user_001 | car | NO | severity |
| user_002 | car | NO | evidence_standard_met, risk_flags, issue_type, object_part, claim_status, valid_image, severity |
| user_004 | car | NO | issue_type, severity |
| user_007 | car | YES | None |
| user_005 | car | NO | risk_flags, issue_type, object_part, claim_status |
| user_006 | car | NO | risk_flags, object_part, severity |
| user_003 | car | NO | severity |
| user_008 | car | NO | risk_flags, object_part, claim_status, valid_image, severity |
| user_009 | laptop | NO | issue_type, severity |
| user_010 | laptop | YES | None |

## Operational Analysis

### Model Calls
- Sample processing: ~10 claims x 1 vision call = ~10 calls
- Test processing: ~10 claims x 1 vision call = ~10 calls

### Token Usage (Estimated)
- Input per call: ~500-800 tokens (text + images)
- Output per call: ~300-500 tokens
- Total input: ~6500 tokens
- Total output: ~4000 tokens

### Cost Estimation
- GPT-4o: ~$2.50/1M input tokens, ~$10.00/1M output tokens
- Estimated cost: ~$0.06

### Latency
- Average per claim: ~3-8 seconds (including API calls)
- Total for test set: ~50 seconds

### Rate Limiting Strategy
- Retry with exponential backoff (3 attempts, 2s-30s)
- Sequential processing to respect TPM limits
- Configurable max images per claim (default: 5)
- Image caching via base64 encoding
