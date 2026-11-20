# play_name_special_chars threshold study

## Simple meaning

Does this task or its parent play have an inconsistent name that materially harms clarity?

The corpus contains **128,220 task observations** across **193 repositories**.

## Distribution

- Q1: 0
- Median: 0
- Q3: 0
- Current threshold: 3 using `>`
- Tukey upper whisker: 0
- Maximum: 4

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1;q2_median;q3;tukey_upper_fence;p80;p90;p95 | 0 | 254 | 0.20% | 26/193 |
| current | 3 | 52 | 0.04% | 21/193 |

At Q3, the detector would produce **254** predictions. At the current threshold it produces **52**. Q3 therefore represents **4.88 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **251 rows** from **193 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=244, B4_high=6, B5_current_positive_tail=1.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
