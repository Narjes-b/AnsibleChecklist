# long_statement_chars threshold study

## Simple meaning

Is this source line excessively long in a way that materially harms readability or maintainability?

The corpus contains **1,333,350 line observations** across **207 repositories**.

## Distribution

- Q1: 17
- Median: 28
- Q3: 46
- Current threshold: 160 using `>`
- Tukey upper whisker: 89
- Maximum: 3408

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 17 | 996,559 | 74.74% | 207/207 |
| q2_median | 28 | 651,945 | 48.90% | 206/207 |
| q3 | 46 | 323,411 | 24.26% | 206/207 |
| p80 | 51 | 266,141 | 19.96% | 206/207 |
| p90 | 69 | 132,678 | 9.95% | 204/207 |
| p95 | 87 | 66,356 | 4.98% | 202/207 |
| tukey_upper_fence | 89.5 | 61,613 | 4.62% | 202/207 |
| current | 160 | 8,093 | 0.61% | 151/207 |

At Q3, the detector would produce **323,411** predictions. At the current threshold it produces **8,093**. Q3 therefore represents **39.96 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **977 rows** from **207 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=207, B2_lower_middle=207, B3_upper_middle=206, B4_high=206, B5_current_positive_tail=151.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
