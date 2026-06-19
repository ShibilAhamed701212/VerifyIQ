# Error Analysis Report

- **Total wrong predictions:** 17

## Other

| Claim ID | Expected | Predicted | Reason |
|----------|----------|-----------|--------|
| user_001 | supported | supported | severity |
| user_003 | supported | supported | severity |

## Damage Type Mismatch

| Claim ID | Expected | Predicted | Reason |
|----------|----------|-----------|--------|
| user_002 | supported | not_enough_information | risk_flags, issue_type, claim_status |
| user_007 | supported | supported | issue_type, severity |
| user_005 | contradicted | supported | risk_flags, issue_type, claim_status |
| user_006 | not_enough_information | contradicted | risk_flags, issue_type, object_part, claim_status, severity |
| user_009 | supported | not_enough_information | risk_flags, issue_type, claim_status, severity |
| user_011 | supported | contradicted | evidence_standard_met, risk_flags, issue_type, claim_status, severity |
| user_018 | supported | supported | issue_type, severity |
| user_020 | contradicted | supported | risk_flags, issue_type, claim_status, severity |
| user_032 | not_enough_information | contradicted | risk_flags, issue_type, claim_status, valid_image, severity |
| user_033 | contradicted | not_enough_information | risk_flags, issue_type, object_part, claim_status |
| user_034 | contradicted | contradicted | evidence_standard_met, risk_flags, issue_type, severity |

## Object Part Mismatch

| Claim ID | Expected | Predicted | Reason |
|----------|----------|-----------|--------|
| user_008 | contradicted | not_enough_information | risk_flags, object_part, claim_status, valid_image, severity |

## Evidence Issue

| Claim ID | Expected | Predicted | Reason |
|----------|----------|-----------|--------|
| user_010 | supported | contradicted | evidence_standard_met, risk_flags, claim_status |
| user_030 | supported | contradicted | evidence_standard_met, risk_flags, claim_status, severity |

## Risk Flag Issue

| Claim ID | Expected | Predicted | Reason |
|----------|----------|-----------|--------|
| user_031 | supported | supported | risk_flags, severity |

