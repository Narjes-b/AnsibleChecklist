# Complete production threshold inventory

## Audit result

The configuration accepts **23 numerical threshold keys**: 8 current checklist keys and 15 legacy keys. The benchmark now covers every active numerical effect, the shared task/play effect, one measured-but-unused key, and the fixed complex-playbook budget.

| Configuration key or fixed cutoff | Default | Production use | Study metric(s) | Status |
|---|---:|---|---|---|
| `complex_expression_score` | 6 | final expression score `>=` cutoff | `complex_expression_score` | active, studied |
| `complex_expression_length` | 100 | adds 2 to expression score when length is greater | `complex_expression_length_chars` | active modifier, studied with final rule replay |
| `long_statement_length` | 160 | source-line length `>` cutoff | `long_statement_chars` | active, studied |
| `excessive_nesting_depth` | 3 | task nesting `>` cutoff | `excessive_nesting_depth` | active, studied |
| `missing_abstraction_tasks` | 10 | leaf tasks `>` role-adjusted cutoff plus abstraction gate | `missing_abstraction_leaf_tasks` | active composite, studied with gates |
| `undocumented_complex_boolean_ops` | 4 | Boolean ops `>=`, OR with two other branches | `undocumented_complex_boolean_ops` | active composite branch, studied |
| `undocumented_complex_jinja_filters` | 4 | filters `>=`, OR with two other branches | `undocumented_complex_jinja_filters` | active composite branch, studied |
| `undocumented_complex_nesting_depth` | 5 | depth `>`, OR with two other branches | `undocumented_complex_nesting_depth` | active composite branch, studied |
| `LOC_playbook` | 110 | large-playbook OR, insufficient-modularization AND, complex budget denominator | `large_playbook_loc`, `complex_playbook_budget` | active, studied |
| `num_plays` | 4 | large-playbook OR, insufficient-modularization AND, complex budget denominator | `large_playbook_play_count`, `complex_playbook_budget` | active, studied |
| `avg_play_size` | 50 | large-playbook OR | `large_playbook_avg_play_size` | active, studied |
| `num_tasks_playbook` | 15 | large-playbook OR and complex budget denominator | `large_playbook_task_count`, `complex_playbook_budget` | active, studied |
| `avg_task_playbook` | 15 | metric is computed but cutoff is never used in the large-playbook decision | `large_playbook_avg_task_size` | accepted but ineffective; measured for evidence |
| `Num_Imports` | 4 | high-coupling OR and complex budget denominator | `high_coupling_import_count`, `complex_playbook_budget` | active, studied |
| `Num_Roles` | 5 | high-coupling OR and complex budget denominator | `high_coupling_role_count`, `complex_playbook_budget` | active, studied |
| `similarity` | 0.4 | playbook cohesion score `<` cutoff | `cohesion_playbook_score` | active, studied; zero current predictions |
| `similarityPlays` | 0.5 | configuration is accepted, but the value is never compared in production | none | dead/ineffective configuration |
| `LOC_play` | 50 | large-play OR | `large_play_loc` | active, studied |
| `num_tasks_play` | 7 | large-play OR | `large_play_task_count` | active, studied |
| `avg_task_play` | 15 | large-play OR | `large_play_avg_task_size` | active, studied |
| `special_chars` | 3 | task-name OR parent-play-name comparison propagated to task findings | `task_name_special_chars`, `play_name_special_chars` | active shared cutoff, both task-level effects studied |
| `LOC_task` | 15 | task LOC `>` cutoff | `large_task_loc` | active, studied |
| `task_name_len` | 75 | task-name length `>` cutoff | `long_task_name_chars` | active, studied |
| fixed complex-playbook budget | 2.0 | normalized sum of LOC, plays, tasks, imports, and roles `>` 2.0 | `complex_playbook_budget` | active fixed cutoff, studied |

## Composite decisions that still need end-to-end labels

- `large-play`: OR of LOC, task count, and average task size.
- `large-playbook`: OR of LOC, play count, average play size, and task count. The configured average-task-size cutoff is omitted by current code.
- `high-coupling`: OR of import and role counts.
- `insufficient-modularization`: playbook LOC AND play count.
- `inconsistent-naming-convention`: task-name OR parent play-name special characters.
- `complex-expression`: base expression score plus a two-point length modifier.
- `undocumented-complex-task`: Boolean ops OR filters OR nesting, suppressed by a preceding comment.
- `missing-abstraction`: role-adjusted task cutoff plus an existing-abstraction suppression.
- `complex-playbook`: normalized five-dimension sum above 2.0.

The component samples isolate which numerical cutoff causes errors while replaying every unchanged branch and gate. Consequently, active components of an OR rule agree at their current threshold. Final detector claims must additionally score the combined production decision on adjudicated rule-level labels.

## Implementation findings

1. Decide whether `avg_task_playbook` should be wired into `large-playbook` or removed from user-facing threshold configuration.
2. Decide whether `similarityPlays` should control a play-level finding or be removed. Benchmarking a value that production ignores would be misleading.
3. Treat the cohesion cutoff and its upstream conservative gate separately: the present score support makes `< 0.4` produce no findings in this corpus.
4. Do not use zero-valued quartiles as cutoffs for sparse OR branches; the undocumented-task sensitivity shows that this can activate nearly all uncommented tasks.
5. Restrict file-level playbook populations to file roles the detector actually analyzes (`playbook`, `tasks`, and `handlers`); vars and metadata must not enter as artificial zero-valued playbooks.
6. Keep source identities occurrence-based. Duplicate task names cannot safely be mapped back to source by searching for the first matching name.
