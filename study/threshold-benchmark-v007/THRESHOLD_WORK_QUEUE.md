# Threshold evaluation work queue

Automated benchmarking, primary sampling, codebooks, and agreement pilots are complete for all 24 study metrics. The remaining work is genuinely human: two independent reviewers must label each 75-row pilot before agreement and threshold quality can be calculated.

| Order | Metric | Primary sample | Agreement pilot | Current state |
|---:|---|---:|---:|---|
| 1 | `large_task_loc` | 944 / 193 projects | 75 | awaiting two humans |
| 2 | `missing_abstraction_leaf_tasks` | 1,077 / 197 | 75 | awaiting two humans |
| 3 | `long_statement_chars` | 977 / 207 | 75 | awaiting two humans |
| 4 | `complex_expression_score` | 878 / 197 | 75 | awaiting two humans |
| 5 | `complex_expression_length_chars` | 1,209 / 197 | 75 | awaiting two humans |
| 6 | `excessive_nesting_depth` | 405 / 194 | 75 | awaiting two humans; all 57 current positives included in primary sample |
| 7 | `long_task_name_chars` | 881 / 193 | 75 | awaiting two humans |
| 8 | `task_name_special_chars` | 364 / 193 | 75 | awaiting two humans; all 52 current positives included in primary sample |
| 9 | `play_name_special_chars` | 251 / 193 | 75 | awaiting two humans; all 52 current positives included in primary sample |
| 10 | `large_play_loc` | 662 / 169 | 75 | awaiting two humans |
| 11 | `large_play_task_count` | 647 / 169 | 75 | awaiting two humans |
| 12 | `large_play_avg_task_size` | 642 / 169 | 75 | awaiting two humans |
| 13 | `large_playbook_loc` | 1,107 / 197 | 75 | awaiting two humans |
| 14 | `large_playbook_play_count` | 662 / 197 | 75 | awaiting two humans |
| 15 | `large_playbook_avg_play_size` | 665 / 197 | 75 | awaiting two humans |
| 16 | `large_playbook_task_count` | 1,194 / 197 | 75 | awaiting two humans |
| 17 | `large_playbook_avg_task_size` | 873 / 197 | 75 | awaiting two humans; configured cutoff is currently unused |
| 18 | `high_coupling_import_count` | 386 / 195 | 75 | awaiting two humans |
| 19 | `high_coupling_role_count` | 425 / 195 | 75 | awaiting two humans |
| 20 | `undocumented_complex_boolean_ops` | 561 / 194 | 75 | awaiting two humans |
| 21 | `undocumented_complex_jinja_filters` | 550 / 194 | 75 | awaiting two humans |
| 22 | `undocumented_complex_nesting_depth` | 483 / 194 | 75 | awaiting two humans |
| 23 | `cohesion_playbook_score` | 208 / 131 | 75 | awaiting two humans; current cutoff makes zero predictions |
| 24 | `complex_playbook_budget` | 920 / 197 | 75 | awaiting two humans |

Totals: **16,971 primary rows** and **1,800 pilot rows per reviewer**.

After pilot agreement reaches 0.80 for a metric, label its full `review-labels.csv`, adjudicate disagreements without deleting either original judgment, and run `score_threshold_candidates.py`. Composite rules must also be evaluated end-to-end after their component studies; component precision cannot be added or averaged to obtain composite-rule precision.

`similarityPlays` is not in this queue because its configured threshold is unused by production code. It must first be removed as dead configuration or connected to a defined detector decision and tested before threshold benchmarking is meaningful.
