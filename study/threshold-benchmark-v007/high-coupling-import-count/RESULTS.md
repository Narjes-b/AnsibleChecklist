# high_coupling_import_count threshold study

## Simple meaning

Does this playbook have harmful dependency coupling?

The corpus contains **21,115 file observations** across **195 repositories**.

## Distribution

- Q1: 0
- Median: 0
- Q3: 0
- Current threshold: 4 using `>`
- Tukey upper whisker: 0
- Maximum: 110

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1;q2_median;q3;tukey_upper_fence;p80;p90;p95 | 0 | 844 | 4.00% | 130/195 |
| current | 4 | 480 | 2.27% | 100/195 |

At Q3, the detector would produce **844** predictions. At the current threshold it produces **480**. Q3 therefore represents **1.76 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **386 rows** from **195 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=269, B4_high=87, B5_current_positive_tail=30.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
