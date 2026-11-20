# Start here: threshold study, file map, and next plan

## The short version

We studied **24 numerical threshold effects** in the frozen Ansible corpus. The corpus contains **207 repositories**, **2,986,459 unique measured observations**, and **zero scan failures**.

The automatic measurement work is complete. We have **not** selected a new production threshold yet, because that needs independent human judgment of whether the reported code is genuinely a maintainability problem. The next step is human labeling, then precision/recall/F1 comparison of the candidate thresholds.

## Exactly what was done

1. Used the frozen 207-repository corpus and its existing file-classification manifests.
2. Extracted every numerical value that can affect an active detector decision, plus the fixed complex-playbook budget and one explicitly marked inactive configuration value.
3. Calculated the distribution for each metric: Q1, median, Q3, percentiles, Tukey values, current threshold, current detector volume, and candidate-threshold volume.
4. Replayed the real detector logic for every candidate. For a rule such as `A OR B OR C`, changing A's threshold still keeps B and C at their real production settings.
5. Created immutable review samples, stratified by project, value band, and whether the current detector fires. Rare current-positive populations of 200 observations or fewer were fully included.
6. Created a separate 75-row human-agreement pilot for every metric.
7. Fixed data and logic problems found during the audit: duplicate admitted paths, wrong playbook file population, duplicate-name source-line mapping, parent-play naming unit, lower-tail cohesion logic, continuous-value rounding, incomplete source context, and composite-rule replay.
8. Added statistical safeguards: Cohen's kappa plus Gwet's AC1 and label-specific agreement; weighted precision/recall/F1/F0.5 with project-cluster confidence intervals.
9. Verified the result: **1,030 tests passed, 2 skipped**; the benchmark integrity validator passed 24 metrics, 24 study packets, 158 immutable hashes, 16,971 primary rows, 1,800 pilot rows, and all 2,986,459 population rows.

The detailed audit is in [CLEANUP_AUDIT_AND_CORRECTED_RESULTS.md](CLEANUP_AUDIT_AND_CORRECTED_RESULTS.md).

## Thresholds studied

“Active” means the current detector really uses the value. “Counterfactual” means we measured it, but production currently does not use that cutoff to make a decision.

| Metric studied | Configuration key / fixed value | Current cutoff | Direction | Status |
|---|---|---:|---|---|
| `large_task_loc` | `LOC_task` | 15 | `>` | active |
| `long_task_name_chars` | `task_name_len` | 75 | `>` | active |
| `task_name_special_chars` | `special_chars` | 3 | `>` | active task-or-parent-play rule |
| `play_name_special_chars` | `special_chars` | 3 | `>` | active task-or-parent-play rule |
| `long_statement_chars` | `long_statement_length` | 160 | `>` | active |
| `complex_expression_score` | `complex_expression_score` | 6 | `>=` | active |
| `complex_expression_length_chars` | `complex_expression_length` | 100 | `>` | active modifier; final expression rule replayed |
| `excessive_nesting_depth` | `excessive_nesting_depth` | 3 | `>` | active |
| `missing_abstraction_leaf_tasks` | `missing_abstraction_tasks` | 10 | `>` | active; role multiplier and abstraction gate preserved |
| `undocumented_complex_boolean_ops` | `undocumented_complex_boolean_ops` | 4 | `>=` | active OR branch; comment gate preserved |
| `undocumented_complex_jinja_filters` | `undocumented_complex_jinja_filters` | 4 | `>=` | active OR branch; comment gate preserved |
| `undocumented_complex_nesting_depth` | `undocumented_complex_nesting_depth` | 5 | `>` | active OR branch; comment gate preserved |
| `large_play_loc` | `LOC_play` | 50 | `>` | active large-play OR branch |
| `large_play_task_count` | `num_tasks_play` | 7 | `>` | active large-play OR branch |
| `large_play_avg_task_size` | `avg_task_play` | 15 | `>` | active large-play OR branch |
| `large_playbook_loc` | `LOC_playbook` | 110 | `>` | active large-playbook OR branch |
| `large_playbook_play_count` | `num_plays` | 4 | `>` | active large-playbook OR branch |
| `large_playbook_avg_play_size` | `avg_play_size` | 50 | `>` | active large-playbook OR branch |
| `large_playbook_task_count` | `num_tasks_playbook` | 15 | `>` | active large-playbook OR branch |
| `large_playbook_avg_task_size` | `avg_task_playbook` | 15 | `>` | **counterfactual**; accepted config, not used by production large-playbook decision |
| `high_coupling_import_count` | `Num_Imports` | 4 | `>` | active high-coupling OR branch |
| `high_coupling_role_count` | `Num_Roles` | 5 | `>` | active high-coupling OR branch |
| `cohesion_playbook_score` | `similarity` | 0.4 | `<` | active; low values are worse |
| `complex_playbook_budget` | fixed normalized budget | 2.0 | `>` | active fixed detector cutoff |

For every active composite rule, the study preserves all other branches. Therefore the current-count value is identical for each active component of the same composite detector; that is expected and correct.

## Values not currently eligible for a production threshold study

| Value | Why it is not an active threshold study | What must happen next |
|---|---|---|
| `similarityPlays` (0.5) | Production accepts the configuration but never compares code against it. There is no detector decision to benchmark. | Decide whether to remove it or define and implement a play-level detector that uses it; then benchmark that real decision. |
| `avg_task_playbook` (15) | It is measured above as a counterfactual, but production does not include it in the large-playbook OR rule. | Decide whether to remove it from configuration or intentionally wire it into production; only then can it be called an active threshold. |

The cohesion rule is active but currently produces zero findings at `< 0.4` in this corpus. That is not missing data: it is a detector-support finding. Human labels and later logic review are needed before changing its gate or cutoff.

## What we will do next

1. Two independent humans label the 75-row `agreement-pilot-labels.csv` for each metric using its `LABELING_CODEBOOK.md`.
2. Run the agreement calculation. The main target is Cohen's kappa >= 0.80; also inspect Gwet's AC1, label prevalence, and per-label agreement.
3. If agreement is below the target, revise the codebook from the disagreements and label a **new** pilot. Do not repeatedly tune the primary sample.
4. When a metric reaches agreement, independently label its primary `review-labels.csv`, then adjudicate disagreements while preserving both original labels.
5. Run the threshold scorer. It calculates weighted precision, recall, F1, F0.5, and project-cluster confidence intervals for every candidate cutoff.
6. Compare candidates by the complete production rule, not by a single OR component alone. Select a threshold only when human evidence, uncertainty, and review cost support it.
7. After human consensus is frozen, run the blinded AI/Ansible-expert comparison. AI output is compared with humans; it is never renamed as a human label.

## Exact file locations

Everything below is inside this directory:

`/home/aymmzn/Documents/AnsibleChecklist/study/threshold-benchmark-v007/`

### Read these first

| File | What it tells you |
|---|---|
| [SIMPLE_EXPLANATION.md](SIMPLE_EXPLANATION.md) | Plain-language explanation, beginning with the large-task example |
| [ALL_THRESHOLDS_STUDY.md](ALL_THRESHOLDS_STUDY.md) | Main table for all 24 metrics and threshold candidates |
| [CLEANUP_AUDIT_AND_CORRECTED_RESULTS.md](CLEANUP_AUDIT_AND_CORRECTED_RESULTS.md) | What was found wrong, what was fixed, before/after numbers, verification |
| [COMPLETE_THRESHOLD_INVENTORY.md](COMPLETE_THRESHOLD_INVENTORY.md) | Maps every configuration value to production use and study status |
| [THRESHOLD_WORK_QUEUE.md](THRESHOLD_WORK_QUEUE.md) | The exact human-labeling workload and order |
| [PROTOCOL.md](PROTOCOL.md) | Formal method: sampling, agreement, scoring, AI comparison |

### Main CSV data

| Exact path | Contents | Read this when |
|---|---|---|
| `distribution-summary.csv` | One row per metric: population, Q1, median, Q3, whiskers, current cutoff, comparator | You want to understand the distributions |
| `candidate-sensitivity.csv` | One row per candidate cutoff: number/rate of predicted findings and affected repositories | You want to compare Q1, median, Q3, percentiles, Tukey, and current cutoff |
| `observations.csv.gz` | All 2,986,459 raw measurement rows | You need reproducibility or a deep custom analysis; do not start here |
| `large-task-review-sample.csv` | Frozen large-task primary sample | You want to inspect the large-task cases selected for review |
| `large-task-review-labels.csv` | Mutable large-task human-label worksheet | Two humans enter their independent judgments here |
| `large-task-agreement-pilot.csv` | Frozen 75-row large-task agreement pilot | Start human agreement for large tasks here |
| `large-task-agreement-pilot-labels.csv` | Mutable large-task pilot worksheet | Two humans enter pilot labels here |
| `all-study-samples.json` | Index of all metric sample folders, row counts, and projects | You need a quick map of the 23 metric packets |

### Per-metric folders

The large-task study stays at the root directory. Every other metric has its own folder below. Each folder contains at least:

- `RESULTS.md`: simple explanation for that metric;
- `LABELING_CODEBOOK.md`: definitions of positive, negative, and uncertain;
- `candidate-sensitivity.csv`: candidate cutoffs for that metric;
- `review-sample.csv`: frozen primary sample;
- `review-labels.csv`: mutable human-label worksheet;
- `agreement-pilot.csv`: frozen 75-row pilot;
- `agreement-pilot-labels.csv`: mutable pilot worksheet;
- `sample-manifest.json` and `agreement-pilot-manifest.json`: counts and integrity hashes.

| Metric | Exact folder |
|---|---|
| Missing abstraction | `missing-abstraction/` |
| Long statement | `long-statement/` |
| Expression score | `complex-expression/` |
| Expression length | `complex-expression-length/` |
| Nesting | `excessive-nesting/` |
| Long task name | `long-task-name/` |
| Task special characters | `task-name-special-characters/` |
| Parent-play special characters | `play-name-special-characters/` |
| Large play LOC | `large-play-loc/` |
| Large play task count | `large-play-task-count/` |
| Large play average task size | `large-play-average-task-size/` |
| Large playbook LOC | `large-playbook-loc/` |
| Large playbook play count | `large-playbook-play-count/` |
| Large playbook average play size | `large-playbook-average-play-size/` |
| Large playbook task count | `large-playbook-task-count/` |
| Large playbook average task size | `large-playbook-average-task-size/` |
| Import coupling | `high-coupling-import-count/` |
| Role coupling | `high-coupling-role-count/` |
| Undocumented Boolean complexity | `undocumented-complex-boolean-ops/` |
| Undocumented Jinja-filter complexity | `undocumented-complex-jinja-filters/` |
| Undocumented nesting complexity | `undocumented-complex-nesting/` |
| Cohesion | `incohesive-playbook-score/` |
| Complex playbook budget | `complex-playbook-budget/` |

## How to read a review-sample CSV row

Focus on these columns first:

| Column | Meaning |
|---|---|
| `metric_id` | Which threshold study this row belongs to |
| `project`, `commit`, `path`, `line` | Exact frozen source location |
| `value` | Measured numerical value for the source unit |
| `threshold`, `comparator` | Current cutoff and whether larger (`>`, `>=`) or smaller (`<`) is problematic |
| `current_prediction` | Whether the complete current detector decision flags the item |
| `metric_band` | Its region relative to Q1, median, Q3, and the current cutoff |
| `source_context` | The source code the human should judge |
| `sampling_weight` | How many similar population observations this row represents |
| `reviewer_1_label`, `reviewer_2_label` | Independent human labels |
| `adjudicated_label` | Final consensus label after disagreement review |
| `ai_label` | Later blinded AI label; leave blank until human consensus is frozen |

## The simplest reading order

1. Read this file.
2. Read `SIMPLE_EXPLANATION.md`.
3. Read `ALL_THRESHOLDS_STUDY.md`.
4. Choose one metric and read its `RESULTS.md` and `LABELING_CODEBOOK.md`.
5. Open that metric's `agreement-pilot.csv`, not the full raw observations file.
6. Only use `observations.csv.gz` if you need to independently reproduce a statistic or build a new analysis.
