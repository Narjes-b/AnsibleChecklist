# v0.0.7 numerical-threshold benchmark results

## What is complete

The frozen 207-repository corpus was scanned without network access. All unique files admitted by the repository-specific v0.0.7 classification manifests were used. The corrected audit produced **2,986,459 unique scalar observations** across **24 numerical study metrics** and reported **zero scan failures**.

The completed automated stages are:

- raw metric extraction from frozen source;
- pooled and repository-median distribution summaries;
- Tukey box plots on a logarithmic display scale;
- Q1, median, Q3, tail-appropriate Tukey/percentile, and current-threshold candidates;
- deterministic occurrence-level and repository-level candidate-rate sensitivity;
- frozen weighted primary samples for all 24 metrics, totaling 16,971 rows;
- a balanced 75-row agreement pilot for every metric, totaling 1,800 rows per reviewer;
- a versioned labeling codebook and blinded AI prompt;
- human–human and human–AI agreement tooling with Cohen's kappa, Gwet's AC1, prevalence, and label-specific agreement;
- weighted precision, recall, F1, and F0.5 scoring with project-cluster bootstrap confidence intervals.

The manual labels are intentionally not fabricated. At present there are zero independently double-labeled rows, so Cohen's kappa, precision, recall, F1, and F0.5 are correctly reported as unavailable. Two independent humans must populate each metric's `agreement-pilot-labels.csv` before those inferential results exist.

## Distribution and current production behavior

| Metric | Units | Q1 | Median | Q3 | Current | Current predictions | Repositories |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cohesion_playbook_score` | 2,369 | 0.5 | 1 | 1 | 0.4 (`<`) | 0 (0.00%) | 0/131 |
| `complex_expression_length_chars` | 199,913 | 22 | 33 | 49 | 100 | 11,124 (5.56%) | 166/197 |
| `complex_expression_score` | 199,913 | 0 | 0 | 2 | 6 | 11,124 (5.56%) | 166/197 |
| `complex_playbook_budget` | 21,455 | 0.3 | 0.5894 | 1.1758 | 2 | 2,516 (11.73%) | 177/197 |
| `excessive_nesting_depth` | 132,295 | 0 | 0 | 0 | 3 | 57 (0.04%) | 5/194 |
| `high_coupling_import_count` | 21,115 | 0 | 0 | 0 | 4 | 480 (2.27%) | 100/195 |
| `high_coupling_role_count` | 21,115 | 0 | 0 | 0 | 5 | 480 (2.27%) | 100/195 |
| `large_play_avg_task_size` | 5,479 | 0 | 6.4 | 11 | 15 | 1,451 (26.48%) | 122/169 |
| `large_play_loc` | 5,479 | 9 | 17 | 37 | 50 | 1,451 (26.48%) | 122/169 |
| `large_play_task_count` | 5,479 | 0 | 1 | 3 | 7 | 1,451 (26.48%) | 122/169 |
| `large_playbook_avg_play_size` | 21,455 | 0 | 0 | 0 | 50 | 3,104 (14.47%) | 184/197 |
| `large_playbook_avg_task_size` | 21,455 | 4.4444 | 6.6 | 9.3333 | 15 | 1,488 (6.94%) | 141/197 |
| `large_playbook_loc` | 21,455 | 12 | 28 | 60 | 110 | 3,104 (14.47%) | 184/197 |
| `large_playbook_play_count` | 21,455 | 0 | 0 | 0 | 4 | 3,104 (14.47%) | 184/197 |
| `large_playbook_task_count` | 21,455 | 1 | 3 | 7 | 15 | 3,104 (14.47%) | 184/197 |
| `large_task_loc` | 128,220 | 4 | 6 | 10 | 15 | 12,202 (9.52%) | 185/193 |
| `long_statement_chars` | 1,333,350 | 17 | 28 | 46 | 160 | 8,093 (0.61%) | 151/207 |
| `long_task_name_chars` | 128,220 | 21 | 31 | 44 | 75 | 5,236 (4.08%) | 134/193 |
| `missing_abstraction_leaf_tasks` | 21,457 | 1 | 3 | 7 | 10 | 1,648 (7.68%) | 163/197 |
| `play_name_special_chars` | 128,220 | 0 | 0 | 0 | 3 | 52 (0.04%) | 21/193 |
| `task_name_special_chars` | 128,220 | 0 | 0 | 0 | 3 | 52 (0.04%) | 21/193 |
| `undocumented_complex_boolean_ops` | 132,295 | 0 | 0 | 0 | 4 | 1,285 (0.97%) | 98/194 |
| `undocumented_complex_jinja_filters` | 132,295 | 0 | 0 | 0 | 4 | 1,285 (0.97%) | 98/194 |
| `undocumented_complex_nesting_depth` | 132,295 | 0 | 0 | 0 | 5 | 1,285 (0.97%) | 98/194 |

Different denominators are intentional: a task metric is defined only where executable tasks exist, while line and file metrics can apply more broadly. Playbook-level detector populations now include only playbooks, task files, and handler files; vars and metadata files are not treated as empty playbooks. Fourteen corpus repositories contain no executable task observation in the included file cohort, so the large-task distribution covers all **193 eligible repositories**, not an invented zero-valued task for those projects. The complete configuration-to-study audit and the two ineffective legacy keys are documented in `COMPLETE_THRESHOLD_INVENTORY.md`.

## Large-task sensitivity result

The measured `LOC_task` distribution is Q1 = 4, median = 6, Q3 = 10, with a Tukey upper fence of 19. The current threshold 15 coincides with the measured P90.

| Candidate source | Threshold | Predicted tasks | Task rate | Repositories with predictions |
|---|---:|---:|---:|---:|
| Q1 | 4 | 93,321 | 72.78% | 193/193 |
| Median | 6 | 63,313 | 49.38% | 192/193 |
| Q3 | 10 | 27,158 | 21.18% | 192/193 |
| P80 | 11 | 22,566 | 17.60% | 191/193 |
| P90 / current | 15 | 12,202 | 9.52% | 185/193 |
| Tukey upper fence | 19 | 7,738 | 6.03% | 180/193 |
| P95 | 21 | 6,378 | 4.97% | 174/193 |

Therefore, Q3 is a useful candidate but not a justified final choice. It would create approximately **2.23 times** as many findings as the current threshold. Only the frozen manual labels can show whether those additional 14,956 findings improve recall enough to justify their precision and review cost.

## Manual sample construction

Every one of the 128,220 task observations was assigned to one of five bands formed from Q1, median, Q3, and the current threshold. Within every eligible repository × band × current-prediction stratum, one task was selected by SHA-256 ranking under the fixed seed `v007-threshold-benchmark-20260917`. This produced 944 rows. Metric packets use the same design, and fully include rare current-positive populations of at most 200 observations.

Each selected row records:

- project, commit, file, source line, and task name;
- metric value and current prediction;
- project-size quartile and numerical band;
- stratum population, inclusion probability, and inverse-probability weight;
- a numbered source window;
- independent reviewer, adjudication, and blinded-AI fields.

This design represents all eligible projects without allowing prolific repositories to dominate. It also provides the weights needed to recover corpus-level estimates from the deliberately balanced sample.

## Agreement and evaluation workflow

1. Reviewers independently label a pilot with `positive`, `negative`, or `uncertain` using `LABELING_CODEBOOK.md`.
2. `compare_threshold_reviewers.py` calculates raw agreement, Cohen's kappa, Gwet's AC1, label prevalence, label-specific agreement, and the confusion matrix.
3. If kappa is below 0.80, disagreements are used to improve the codebook and a **new pilot** is labeled. The primary or held-out labels are not repeatedly tuned.
4. After reaching the target, the codebook is frozen, primary labels are completed, and disagreements are adjudicated while original labels remain preserved.
5. `score_threshold_candidates.py` replays every threshold over the same adjudicated labels using the recorded sampling weights and calculates precision, recall, F1, and F0.5 with project-cluster bootstrap confidence intervals.
6. The AI prompt is run only after the human labels are frozen. The same agreement tool compares `adjudicated_label` with `ai_label`.

Claude or another language model is **not required for threshold arithmetic**. Python performs the deterministic threshold sweep. The AI is an evaluated blinded reviewer, not the gold standard and not a substitute for either human annotator.

## Reproduction commands

Build the complete corpus benchmark from frozen source:

```bash
.venv/bin/python scripts/build_threshold_benchmark.py
```

Rebuild plots, summaries, hashes, and the frozen sample without rescanning source:

```bash
.venv/bin/python scripts/build_threshold_benchmark.py --reuse-observations
```

After two independent reviewers enter labels in the working label file, calculate human–human agreement and materialize disagreements:

```bash
.venv/bin/python scripts/compare_threshold_reviewers.py \
  study/threshold-benchmark-v007/large-task-review-labels.csv \
  --target 0.80 \
  --output study/threshold-benchmark-v007/agreement-status.json \
  --disagreements study/threshold-benchmark-v007/reviewer-disagreements.csv
```

After adjudication, calculate the weighted threshold metrics:

```bash
.venv/bin/python scripts/score_threshold_candidates.py \
  study/threshold-benchmark-v007/large-task-review-labels.csv \
  study/threshold-benchmark-v007/candidate-sensitivity.csv \
  --output study/threshold-benchmark-v007/threshold-scores.csv
```

After blinded AI review, calculate human-consensus versus AI agreement with the same implementation:

```bash
.venv/bin/python scripts/compare_threshold_reviewers.py \
  study/threshold-benchmark-v007/large-task-review-labels.csv \
  --first-column adjudicated_label \
  --second-column ai_label \
  --output study/threshold-benchmark-v007/human-ai-agreement.json
```

## Current stopping point

`agreement-status.json` reports `insufficient-independent-labels`, with 0 paired items. `threshold-scores.csv` contains only its header because there are no adjudicated labels. This is a real external evidence boundary, not a computation failure. Reporting numerical precision or human agreement before the labels exist would be fabricated.
