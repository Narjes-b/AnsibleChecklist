# complex_expression_length_chars threshold study

## Simple meaning

Is this Jinja or conditional expression too complex and in need of simplification?

The corpus contains **199,913 expression observations** across **197 repositories**.

## Distribution

- Q1: 22
- Median: 33
- Q3: 49
- Current threshold: 100 using `>`
- Tukey upper whisker: 89
- Maximum: 4987

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 22 | 19,852 | 9.93% | 178/197 |
| q2_median | 33 | 19,798 | 9.90% | 178/197 |
| q3 | 49 | 18,517 | 9.26% | 178/197 |
| p80 | 55 | 17,626 | 8.82% | 176/197 |
| p90 | 78 | 13,722 | 6.86% | 173/197 |
| tukey_upper_fence | 89.5 | 12,073 | 6.04% | 169/197 |
| current | 100 | 11,124 | 5.56% | 166/197 |
| p95 | 108 | 10,585 | 5.29% | 165/197 |

At Q3, the detector would produce **18,517** predictions. At the current threshold it produces **11,124**. Q3 therefore represents **1.66 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **1,209 rows** from **197 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=195, B2_lower_middle=193, B3_upper_middle=213, B4_high=332, B5_current_positive_tail=276.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
