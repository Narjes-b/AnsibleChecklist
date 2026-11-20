# long_task_name_chars threshold study

## Simple meaning

Is this task name unnecessarily long or difficult to scan?

The corpus contains **128,220 task observations** across **193 repositories**.

## Distribution

- Q1: 21
- Median: 31
- Q3: 44
- Current threshold: 75 using `>`
- Tukey upper whisker: 78
- Maximum: 1999

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 21 | 94,157 | 73.43% | 188/193 |
| q2_median | 31 | 63,034 | 49.16% | 185/193 |
| q3 | 44 | 31,185 | 24.32% | 182/193 |
| p80 | 48 | 24,533 | 19.13% | 180/193 |
| p90 | 59 | 12,695 | 9.90% | 172/193 |
| p95 | 72 | 6,071 | 4.73% | 144/193 |
| current | 75 | 5,236 | 4.08% | 134/193 |
| tukey_upper_fence | 78.5 | 4,534 | 3.54% | 125/193 |

At Q3, the detector would produce **31,185** predictions. At the current threshold it produces **5,236**. Q3 therefore represents **5.96 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **881 rows** from **193 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=193, B2_lower_middle=188, B3_upper_middle=185, B4_high=181, B5_current_positive_tail=134.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
