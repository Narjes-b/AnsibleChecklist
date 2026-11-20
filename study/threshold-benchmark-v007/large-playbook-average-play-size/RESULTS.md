# large_playbook_avg_play_size threshold study

## Simple meaning

Is this Ansible artifact excessively large and in need of decomposition?

The corpus contains **21,455 file observations** across **197 repositories**.

## Distribution

- Q1: 0
- Median: 0
- Q3: 0
- Current threshold: 50 using `>`
- Tukey upper whisker: 0
- Maximum: 2042

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1;q2_median;q3;tukey_upper_fence;p80 | 0 | 5,904 | 27.52% | 190/197 |
| p90 | 16 | 4,355 | 20.30% | 187/197 |
| p95 | 38 | 3,340 | 15.57% | 185/197 |
| current | 50 | 3,104 | 14.47% | 184/197 |

At Q3, the detector would produce **5,904** predictions. At the current threshold it produces **3,104**. Q3 therefore represents **1.90 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **665 rows** from **197 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=357, B4_high=207, B5_current_positive_tail=101.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
