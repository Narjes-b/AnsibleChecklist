# cohesion_playbook_score threshold study

## Simple meaning

Does this playbook combine unrelated responsibility domains so strongly that it should be decomposed?

The corpus contains **2,369 file observations** across **131 repositories**.

## Distribution

- Q1: 0.5
- Median: 1
- Q3: 1
- Current threshold: 0.4 using `<`
- Tukey lower whisker: 0.5
- Minimum: 0.5

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| current | 0.4 | 0 | 0.00% | 0/131 |
| tukey_lower_fence;p05;p10;p20;q1 | 0.5 | 0 | 0.00% | 0/131 |
| q2_median;q3 | 1 | 616 | 26.00% | 90/131 |

At Q3, the detector would produce **616** predictions. At the current threshold it produces **0**. Q3 therefore represents **undefined because the current threshold produces zero predictions**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **208 rows** from **131 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B2_current_to_q1=90, B3_q1_to_median=118.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
