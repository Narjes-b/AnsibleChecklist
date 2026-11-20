# large_playbook_avg_task_size threshold study

## Simple meaning

Would an average-task-size cutoff be a useful additional signal that this artifact needs decomposition?

The corpus contains **21,455 file observations** across **197 repositories**.

## Distribution

- Q1: 4.4444
- Median: 6.6
- Q3: 9.3333
- Current threshold: 15 using `>`
- Tukey upper whisker: 16.625
- Maximum: 252

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
| q1 | 4.4444 | 16,088 | 74.98% | 192/197 |
| q2_median | 6.6 | 10,721 | 49.97% | 190/197 |
| q3 | 9.3333 | 5,318 | 24.79% | 185/197 |
| p80 | 10.2 | 4,277 | 19.93% | 182/197 |
| p90 | 13.3333 | 2,126 | 9.91% | 151/197 |
| current | 15 | 1,488 | 6.94% | 141/197 |
| tukey_upper_fence | 16.6666 | 1,142 | 5.32% | 130/197 |
| p95 | 17 | 1,046 | 4.88% | 125/197 |

At Q3, the detector would produce **5,318** predictions. At the current threshold it produces **1,488**. Q3 therefore represents **3.57 times the current volume**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **873 rows** from **197 repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: B1_low=184, B2_lower_middle=183, B3_upper_middle=184, B4_high=181, B5_current_positive_tail=141.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
