# large_play_task_count threshold study

## Simple meaning

Is this Ansible play excessively large and in need of decomposition?

The corpus contains **5,479 play observations** across **169 repositories**.

## Distribution

- Q1: 0
- Median: 1
- Q3: 3
- Current threshold: 7 using `>`
- Tukey upper whisker: 7
- Maximum: 130

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 0 | 3,420 | 62.42% | 143/169 |
| q2_median | 1 | 2,541 | 46.38% | 139/169 |
| q3 | 3 | 1,866 | 34.06% | 132/169 |
| p80 | 4 | 1,656 | 30.22% | 128/169 |
| p90;current | 7 | 1,451 | 26.48% | 122/169 |
| tukey_upper_fence | 7.5 | 1,451 | 26.48% | 122/169 |
| p95 | 12 | 1,397 | 25.50% | 120/169 |

At Q3, the detector would produce **1,866** predictions. At the current threshold it produces **1,451**. Q3 therefore represents **1.29 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **647 rows** from **169 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=167, B2_lower_middle=137, B3_upper_middle=131, B4_high=129, B5_current_positive_tail=83.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
