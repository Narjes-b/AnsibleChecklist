# large_playbook_task_count threshold study

## Simple meaning

Is this Ansible artifact excessively large and in need of decomposition?

The corpus contains **21,455 file observations** across **197 repositories**.

## Distribution

- Q1: 1
- Median: 3
- Q3: 7
- Current threshold: 15 using `>`
- Tukey upper whisker: 16
- Maximum: 340

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 1 | 15,954 | 74.36% | 196/197 |
| q2_median | 3 | 10,965 | 51.11% | 195/197 |
| q3 | 7 | 5,772 | 26.90% | 192/197 |
| p80 | 9 | 4,574 | 21.32% | 190/197 |
| p90 | 14 | 3,213 | 14.98% | 185/197 |
| current | 15 | 3,104 | 14.47% | 184/197 |
| tukey_upper_fence | 16 | 3,017 | 14.06% | 182/197 |
| p95 | 20 | 2,865 | 13.35% | 181/197 |

At Q3, the detector would produce **5,772** predictions. At the current threshold it produces **3,104**. Q3 therefore represents **1.86 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **1,194 rows** from **197 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=253, B2_lower_middle=221, B3_upper_middle=253, B4_high=309, B5_current_positive_tail=158.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
