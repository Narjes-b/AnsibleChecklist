# All numerical-threshold studies — consolidated report

For a simple reading order, exact CSV paths, and the full next-step plan, see [START_HERE_FILE_MAP_AND_PLAN.md](START_HERE_FILE_MAP_AND_PLAN.md).

## What is complete

The frozen 207-repository corpus was rescanned for every numerical value that can change a current detector decision. After a population and replay-logic audit, the corrected benchmark contains **2,986,459 unique observations across 24 study metrics**, with **zero scan failures**.

The 24 metrics consist of 23 measured configured-threshold effects plus the fixed `complex-playbook` budget. The shared `special_chars` cutoff is evaluated separately for task names and play names. `avg_task_playbook` is measured even though the current large-playbook decision does not use it. `similarityPlays` cannot be given a production threshold study because the configured value is never consulted; this is documented in `COMPLETE_THRESHOLD_INVENTORY.md`.

For every study metric, the saved package contains the distribution, tail-appropriate quartiles/percentiles/Tukey/current sensitivity, a deterministic weighted review sample stratified by repository, value band, and current prediction, expanded source context, a labeling codebook, separate frozen and mutable files, a 75-row agreement pilot, and hashes for immutable artifacts. Composite detectors replay their complete production OR/gating logic while changing only the candidate component.

The frozen primary samples contain **16,971 review rows**. The initial human-agreement workload is **1,800 pilot rows per reviewer**: 75 rows for each of 24 metrics. Rare current-positive populations of at most 200 observations are fully included in their primary sample.

## Main comparison

“Q3/current volume” is descriptive. It compares how many candidate findings Q3 would produce with the current production cutoff while preserving each rule's real comparator and gates.

| Metric | Q1 | Median | Q3 | Current | Q3 predictions | Current predictions | Q3/current volume | Sample rows / projects |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `cohesion_playbook_score` | 0.5 | 1 | 1 | 0.4 | 616 | 0 | undefined | 208 / 131 |
| `complex_expression_length_chars` | 22 | 33 | 49 | 100 | 18,517 | 11,124 | 1.66× | 1,209 / 197 |
| `complex_expression_score` | 0 | 0 | 2 | 6 | 61,930 | 11,124 | 5.57× | 878 / 197 |
| `complex_playbook_budget` | 0.3 | 0.5894 | 1.1758 | 2 | 5,359 | 2,516 | 2.13× | 920 / 197 |
| `excessive_nesting_depth` | 0 | 0 | 0 | 3 | 26,352 | 57 | 462.32× | 405 / 194 |
| `high_coupling_import_count` | 0 | 0 | 0 | 4 | 844 | 480 | 1.76× | 386 / 195 |
| `high_coupling_role_count` | 0 | 0 | 0 | 5 | 1,726 | 480 | 3.60× | 425 / 195 |
| `large_play_avg_task_size` | 0 | 6.4 | 11 | 15 | 1,890 | 1,451 | 1.30× | 642 / 169 |
| `large_play_loc` | 9 | 17 | 37 | 50 | 1,699 | 1,451 | 1.17× | 662 / 169 |
| `large_play_task_count` | 0 | 1 | 3 | 7 | 1,866 | 1,451 | 1.29× | 647 / 169 |
| `large_playbook_avg_play_size` | 0 | 0 | 0 | 50 | 5,904 | 3,104 | 1.90× | 665 / 197 |
| `large_playbook_avg_task_size` | 4.4444 | 6.6 | 9.3333 | 15 | 5,318 | 1,488 | 3.57× | 873 / 197 |
| `large_playbook_loc` | 12 | 28 | 60 | 110 | 5,459 | 3,104 | 1.76× | 1,107 / 197 |
| `large_playbook_play_count` | 0 | 0 | 0 | 4 | 5,904 | 3,104 | 1.90× | 662 / 197 |
| `large_playbook_task_count` | 1 | 3 | 7 | 15 | 5,772 | 3,104 | 1.86× | 1,194 / 197 |
| `large_task_loc` | 4 | 6 | 10 | 15 | 27,158 | 12,202 | 2.23× | 944 / 193 |
| `long_statement_chars` | 17 | 28 | 46 | 160 | 323,411 | 8,093 | 39.96× | 977 / 207 |
| `long_task_name_chars` | 21 | 31 | 44 | 75 | 31,185 | 5,236 | 5.96× | 881 / 193 |
| `missing_abstraction_leaf_tasks` | 1 | 3 | 7 | 10 | 2,911 | 1,648 | 1.77× | 1,077 / 197 |
| `play_name_special_chars` | 0 | 0 | 0 | 3 | 254 | 52 | 4.88× | 251 / 193 |
| `task_name_special_chars` | 0 | 0 | 0 | 3 | 2,955 | 52 | 56.83× | 364 / 193 |
| `undocumented_complex_boolean_ops` | 0 | 0 | 0 | 4 | 120,068 | 1,285 | 93.44× | 561 / 194 |
| `undocumented_complex_jinja_filters` | 0 | 0 | 0 | 4 | 120,068 | 1,285 | 93.44× | 550 / 194 |
| `undocumented_complex_nesting_depth` | 0 | 0 | 0 | 5 | 25,931 | 1,285 | 20.18× | 483 / 194 |

For expression length, the prediction count is the final expression rule after adding the two-point length modifier. For every composite component, only that component's cutoff changes; all unchanged OR branches and suppression gates remain at production defaults. This is why each active component of the same rule has the same current-production count. `large_playbook_avg_task_size` is explicitly counterfactual because production currently ignores that configured cutoff. For cohesion, lower values are worse, so candidates come from the lower tail and are clamped to observed support. The current detector returns no score below 0.4 in this corpus, hence zero current predictions and no finite Q3/current ratio.

## Interpretation

There is no defensible rule saying “always use Q3.” Q3 ranges from a modest 1.17× current volume for play LOC to 462.32× for nesting. Sparse count metrics frequently have Q1, median, and Q3 all equal to zero. That zero is a corpus description, not a sensible production threshold.

The most striking new result concerns undocumented complex tasks. Setting any sparse component cutoff to its Q3 of zero effectively makes nearly every uncommented task eligible through that OR branch. This confirms that quartiles alone are unsafe for composite rules.

The cohesion result exposes a different issue: the conservative detector returns either 0 after a strict gate or at least 0.5. No observed file crossed the current `< 0.4` cutoff, so changing the numeric cutoff may be less useful than reviewing the upstream gate itself.

## Human evaluation boundary

The automated benchmark and all review packets are complete. Human precision, recall, F1, F0.5, human–human agreement, and human–AI agreement are not yet available because no two independent humans have entered labels.

Review starts in each metric's `agreement-pilot-labels.csv`. Two people label independently. The codebook is revised on a new pilot until Cohen's kappa is at least 0.80, then frozen. Only afterward is the full weighted sample labeled and adjudicated. Python replays every candidate against the same adjudicated labels.

No detector threshold or logic was changed from distribution results alone. A detector correction requires a repeated, adjudicated error pattern and evaluation on untouched data. An AI reviewer is introduced only after human consensus is frozen and is never described as a human annotator or gold standard.
