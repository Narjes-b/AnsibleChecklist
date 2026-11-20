# undocumented_complex_jinja_filters threshold study

## Simple meaning

Is this task's Jinja filtering complex enough to require a preceding rationale comment?

The corpus contains **132,295 task observations** across **194 repositories**.

## Distribution

- Q1: 0
- Median: 0
- Q3: 0
- Current threshold: 4 using `>=`
- Tukey upper whisker: 0
- Maximum: 30

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1;q2_median;q3;tukey_upper_fence;p80 | 0 | 120,068 | 90.76% | 194/194 |
| p90;p95 | 1 | 13,803 | 10.43% | 168/194 |
| current | 4 | 1,285 | 0.97% | 98/194 |

At Q3, the detector would produce **120,068** predictions. At the current threshold it produces **1,285**. Q3 therefore represents **93.44 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **550 rows** from **194 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=243, B4_high=242, B5_current_positive_tail=65.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
