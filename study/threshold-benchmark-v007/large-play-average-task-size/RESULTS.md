# large_play_avg_task_size threshold study

## Simple meaning

Is this Ansible play excessively large and in need of decomposition?

The corpus contains **5,479 play observations** across **169 repositories**.

## Distribution

- Q1: 0
- Median: 6.4
- Q3: 11
- Current threshold: 15 using `>`
- Tukey upper whisker: 27.3333
- Maximum: 202

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 0 | 3,420 | 62.42% | 143/169 |
| q2_median | 6.4 | 3,070 | 56.03% | 142/169 |
| q3 | 11 | 1,890 | 34.50% | 131/169 |
| p80 | 12 | 1,725 | 31.48% | 129/169 |
| current | 15 | 1,451 | 26.48% | 122/169 |
| p90 | 17 | 1,347 | 24.58% | 122/169 |
| p95 | 22.8875 | 1,200 | 21.90% | 117/169 |
| tukey_upper_fence | 27.5 | 1,135 | 20.72% | 115/169 |

At Q3, the detector would produce **1,890** predictions. At the current threshold it produces **1,451**. Q3 therefore represents **1.30 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **642 rows** from **169 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=167, B2_lower_middle=111, B3_upper_middle=173, B4_high=115, B5_current_positive_tail=76.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
