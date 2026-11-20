# large_play_loc threshold study

## Simple meaning

Is this Ansible play excessively large and in need of decomposition?

The corpus contains **5,479 play observations** across **169 repositories**.

## Distribution

- Q1: 9
- Median: 17
- Q3: 37
- Current threshold: 50 using `>`
- Tukey upper whisker: 79
- Maximum: 2042

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 9 | 3,877 | 70.76% | 157/169 |
| q2_median | 17 | 2,734 | 49.90% | 143/169 |
| q3 | 37 | 1,699 | 31.01% | 133/169 |
| p80 | 46 | 1,509 | 27.54% | 124/169 |
| current | 50 | 1,451 | 26.48% | 122/169 |
| tukey_upper_fence | 79 | 1,255 | 22.91% | 118/169 |
| p90 | 82 | 1,246 | 22.74% | 117/169 |
| p95 | 125 | 1,204 | 21.97% | 115/169 |

At Q3, the detector would produce **1,699** predictions. At the current threshold it produces **1,451**. Q3 therefore represents **1.17 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **662 rows** from **169 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=115, B2_lower_middle=153, B3_upper_middle=173, B4_high=111, B5_current_positive_tail=110.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
