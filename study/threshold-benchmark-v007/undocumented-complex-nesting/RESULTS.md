# undocumented_complex_nesting_depth threshold study

## Simple meaning

Is this task nested deeply enough to require a preceding rationale comment?

The corpus contains **132,295 task observations** across **194 repositories**.

## Distribution

- Q1: 0
- Median: 0
- Q3: 0
- Current threshold: 5 using `>`
- Tukey upper whisker: 0
- Maximum: 5

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1;q2_median;q3;tukey_upper_fence;p80 | 0 | 25,931 | 19.60% | 162/194 |
| p90;p95 | 1 | 3,812 | 2.88% | 117/194 |
| current | 5 | 1,285 | 0.97% | 98/194 |

At Q3, the detector would produce **25,931** predictions. At the current threshold it produces **1,285**. Q3 therefore represents **20.18 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **483 rows** from **194 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=287, B4_high=196.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
