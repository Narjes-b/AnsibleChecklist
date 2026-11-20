# complex_playbook_budget threshold study

## Simple meaning

Is this Ansible artifact overly complex because several size and dependency dimensions compound?

The corpus contains **21,455 file observations** across **197 repositories**.

## Distribution

- Q1: 0.3
- Median: 0.5894
- Q3: 1.1758
- Current threshold: 2 using `>`
- Tukey upper whisker: 2.4894
- Maximum: 64.3576

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 0.3 | 16,046 | 74.79% | 197/197 |
| q2_median | 0.5894 | 10,726 | 49.99% | 196/197 |
| q3 | 1.1758 | 5,359 | 24.98% | 192/197 |
| p80 | 1.3851 | 4,291 | 20.00% | 190/197 |
| current | 2 | 2,516 | 11.73% | 177/197 |
| p90 | 2.2152 | 2,142 | 9.98% | 174/197 |
| tukey_upper_fence | 2.4895 | 1,726 | 8.04% | 168/197 |
| p95 | 3.197 | 1,072 | 5.00% | 139/197 |

At Q3, the detector would produce **5,359** predictions. At the current threshold it produces **2,516**. Q3 therefore represents **2.13 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **920 rows** from **197 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=183, B2_lower_middle=187, B3_upper_middle=191, B4_high=182, B5_current_positive_tail=177.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
