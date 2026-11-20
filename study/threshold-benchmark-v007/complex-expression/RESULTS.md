# complex_expression_score threshold study

## Simple meaning

Is this Jinja or conditional expression too complex and in need of simplification?

The corpus contains **199,913 expression observations** across **197 repositories**.

## Distribution

- Q1: 0
- Median: 0
- Q3: 2
- Current threshold: 6 using `>=`
- Tukey upper whisker: 5
- Maximum: 360

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1;q2_median | 0 | 199,913 | 100.00% | 197/197 |
| q3;p80 | 2 | 61,930 | 30.98% | 189/197 |
| p90 | 4 | 22,055 | 11.03% | 179/197 |
| tukey_upper_fence | 5 | 15,433 | 7.72% | 171/197 |
| p95;current | 6 | 11,124 | 5.56% | 166/197 |

At Q3, the detector would produce **61,930** predictions. At the current threshold it produces **11,124**. Q3 therefore represents **5.57 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **878 rows** from **197 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=197, B3_upper_middle=192, B4_high=328, B5_current_positive_tail=161.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
