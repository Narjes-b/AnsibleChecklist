# large_playbook_loc threshold study

## Simple meaning

Is this Ansible artifact excessively large and in need of decomposition?

The corpus contains **21,455 file observations** across **197 repositories**.

## Distribution

- Q1: 12
- Median: 28
- Q3: 60
- Current threshold: 110 using `>`
- Tukey upper whisker: 132
- Maximum: 4586

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 12 | 15,991 | 74.53% | 197/197 |
| q2_median | 28 | 10,552 | 49.18% | 196/197 |
| q3 | 60 | 5,459 | 25.44% | 194/197 |
| p80 | 71 | 4,581 | 21.35% | 191/197 |
| current | 110 | 3,104 | 14.47% | 184/197 |
| p90 | 115 | 3,001 | 13.99% | 184/197 |
| tukey_upper_fence | 132 | 2,768 | 12.90% | 180/197 |
| p95 | 167 | 2,576 | 12.01% | 176/197 |

At Q3, the detector would produce **5,459** predictions. At the current threshold it produces **3,104**. Q3 therefore represents **1.76 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **1,107 rows** from **197 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=177, B2_lower_middle=193, B3_upper_middle=245, B4_high=314, B5_current_positive_tail=178.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
