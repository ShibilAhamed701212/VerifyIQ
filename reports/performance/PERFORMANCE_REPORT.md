# Performance Report — VerifyIQ V1 vs V2

**Environment:** Windows, Python 3.12, no VLM API calls (degraded mode)

**Sample:** "There is a dent on the rear bumper of my car"

## Overall Comparison

| Metric | V1 (10) | V2 (1) | V2 (10) | V2 (50) |
|---|---|---|---|---|
| Total (ms) | 3471.7 | 2144.37 | 7495.77 | 35736.11 |
| Per-claim (ms) | 347.1723 | 2144.3739 | 749.5773 | 714.7221 |
| Claims/sec | 2.9 | 0.5 | 1.3 | 1.4 |
| Failures | N/A | 1 | 10 | 50 |

## V2 Module Breakdown (10 claims)

| Module | Total (ms) | Avg (ms) | Share |
|---|---|---|---|
| confidence | 0.00 | 0.0000 | 0.0% |
| consensus | 0.00 | 0.0000 | 0.0% |
| conversation | 0.00 | 0.0000 | 0.0% |
| evidence | 14.41 | 1.4411 | 0.2% |
| fraud | 0.00 | 0.0000 | 0.0% |
| observation | 7481.36 | 748.1362 | 99.8% |
| v1_rule_adapter | 0.00 | 0.0000 | 0.0% |

## Module Scaling

| Module | 1 claim (ms) | 10 claims | 50 claims |
|---|---|---|---|
| confidence | 0.0000 | 0.0000 | 0.0000 |
| consensus | 0.0000 | 0.0000 | 0.0000 |
| conversation | 0.0000 | 0.0000 | 0.0000 |
| evidence | 0.0000 | 1.4411 | 0.0311 |
| fraud | 0.0000 | 0.0000 | 0.0000 |
| observation | 2144.3739 | 748.1362 | 714.3625 |
| v1_rule_adapter | 0.0000 | 0.0000 | 0.3083 |

## Scalability

- V2 (50 claims): 35.7361s = 714.7221ms/claim
- Scale factor 1->10: 3.5x (linear = ~10x)
- Scale factor 10->50: 4.8x (linear = 5x)
- Observation layer skipped (no API key); real VLM adds ~2-5s/claim

## Projected Cost

| Scenario | Cost/1000 claims |
|---|---|
| V2 without VLM | $0.00 |
| V2 with Gemini Flash | ~$0.16-$0.40 |
| V2 with 3 models | ~$0.50-$1.20 |