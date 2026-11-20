# Threshold benchmark cleanup audit and corrected results

## Outcome

The threshold benchmark has been cleaned and regenerated. The corrected frozen dataset contains **2,986,459 unique observations**, covers **24 numerical metrics** across the **207-repository frozen corpus**, and has **zero scan failures**. The 24 primary samples contain **16,971 rows** and the independent agreement workload remains **1,800 rows per reviewer** (75 per metric).

No human precision, recall, F1, human–human agreement, or human–AI agreement is claimed yet. Those results require two genuinely independent human reviewers. The files remain ready for that work.

## Problems found and fixes applied

| Problem | Why it mattered | Correction |
|---|---|---|
| File manifests contained 7,676 repeated included paths | The same source unit could enter a metric more than once | De-duplicated admitted parsed files by repository-relative path; the validator now rejects duplicate observation IDs |
| Playbook metrics included vars and metadata files | These files became artificial zero-valued playbooks; the affected denominator was 31,804 instead of the detector-relevant population | Restricted large-playbook, complex-playbook, and coupling populations to playbook, task, and handler documents; active playbook population is now 21,455 observations from 197 repositories |
| Composite sensitivity changed one branch but ignored unchanged OR branches | Candidate counts did not represent the production detector | Replayed the complete large-play, active large-playbook, high-coupling, naming, expression, undocumented-task, and missing-abstraction decisions while changing only the candidate cutoff |
| Play-name special characters were studied once per play | Production propagates the parent play-name decision to task findings | Rebuilt this metric at task level; both naming studies now replay `task name OR parent play name` and have 128,220 observations |
| Repeated task names were mapped to the first matching name in source | Comment suppression and reported lines could belong to the wrong task | Production `_task_line` now uses the parser's source position, with name search only as a fallback; a regression test covers repeated names |
| Occurrence identities could collide for repeated structures | Distinct tasks or expressions could collapse into one observation | Added stable source ordinals/identity suffixes and regenerated every observation |
| Cohesion used upper-tail bands/candidates even though low scores are worse | Sampling and threshold candidates pointed in the wrong direction | Added lower-tail bands/percentiles and a `<` comparator path; clamped the Tukey lower fence to observed support so no impossible negative cutoff is tested |
| Samples were stratified only by repository and value band | Rare current positives could be missed or underrepresented | Added current-prediction state to every sampling stratum; current-positive populations of 1–200 are fully included in the primary sample |
| Agreement pilots ignored prediction state | A pilot could contain too few positive detector cases | Balanced pilots across available `metric band × current prediction` cells and recorded the prediction counts in each pilot manifest |
| Continuous candidates were rounded to two decimals | Nearby but meaningfully distinct budget thresholds could collapse | Increased stored candidate precision to four decimals |
| Source context was often limited to a short leading excerpt | Reviewers could lack the play or file context needed for a judgment | Small files are included in full; long files receive head/middle/tail plus local or play-level context, with completeness metadata |
| Cohen's kappa alone is unstable under strong class imbalance | High raw agreement can coexist with misleading kappa on rare findings | Kept kappa as the preregistered 0.80 gate and added Gwet's AC1, prevalence, and label-specific agreement |
| Threshold estimates had no uncertainty interval | Point estimates hid repository-to-repository variation | Added deterministic project-cluster bootstrap confidence intervals for precision, recall, F1, and F0.5 |
| One repository failed in the earlier v0.0.7 execution | Old and new production counts differed slightly | The benchmark parses all 207 repositories with zero failures. `encapsulate-xyz/cosmos-ansible` supplies the reconciled extra findings |

## Important before/after results

The old and corrected totals are not expected to differ by only the duplicate count: the correction simultaneously removes duplicated/file-role observations and adds the correct task-level parent-play observations.

| Quantity | Before cleanup | Corrected |
|---|---:|---:|
| All metric observations | 2,925,814 | 2,986,459 unique |
| Duplicate extra observations found by audit | 7,676 | 0 |
| Primary review rows | 14,463 | 16,971 |
| Playbook population used by large-playbook studies | 31,804 / 207 repos | 21,455 / 197 repos |
| `complex_playbook_budget` Q1 / median / Q3 | 0.1394 / 0.4076 / 0.9091 | 0.3 / 0.5894 / 1.1758 |
| Production complex-playbook predictions | 2,719 in mixed file population | 2,516 in detector-relevant population |
| Parent-play special-character population | 5,479 plays | 128,220 task decisions |
| Production naming predictions | 51 task branch; 1 play branch | 52 complete task-or-play decisions |
| Cohesion candidate set | included impossible −0.25 | 0.4, 0.5, 1.0 |
| Scan failures | 0 in benchmark, but one repo missing from old run | 0; all 207 processed |

At the current production settings, complete-rule replay now gives:

- large play: **1,451** findings for each component study at its current cutoff;
- active large playbook: **3,104** findings for each of its four component studies;
- high coupling: **480** findings for each component study;
- task/parent-play special characters: **52** findings for both component studies;
- undocumented complex task: **1,285** findings for each component study;
- complex expression: **11,124** findings for score and length-modifier studies.

`large_playbook_avg_task_size` remains a clearly marked counterfactual study because that accepted configuration value is not used by the production large-playbook OR. `similarityPlays` remains excluded because production never reads it. Neither was silently wired into detector behavior.

## Reconciliation with the earlier 207-repository run

The prior run analyzed 206 repositories and failed on `encapsulate-xyz/cosmos-ansible`; the corrected benchmark analyzes all 207. The count differences reconcile exactly where checked:

- large task: 12,202 = prior 12,179 + 23 from the recovered repository;
- large playbook: 3,104 = prior 3,100 + 4;
- complex playbook: 2,516 = prior 2,514 + 2.

This supports the corrected extraction and explains why those totals are slightly above the earlier published run.

## Sampling and agreement checks

The samples are now drawn from `repository × metric band × current prediction` strata. Examples of deliberately protected rare positives are:

- all **57** current-positive excessive-nesting observations are in its primary sample;
- all **52** current-positive task-naming observations are in its primary sample;
- all **52** current-positive parent-play-naming observations are in its primary sample.

Every metric has a 75-row agreement pilot. The cohesion pilot correctly contains no current positives because the detector produces none in this corpus; this is a detector-support finding, not a sampling failure.

## Verification performed

- Rebuilt the full 207-repository observation dataset from frozen sources.
- Confirmed zero scan failures and zero duplicate observation identities.
- Regenerated distributions, candidate sensitivity, box plot, all primary samples, all pilots, codebooks, and manifests.
- Added a repeated-task-name production regression test and threshold replay/sampling unit tests.
- Ran the focused detector and benchmark suite: **54 passed**.
- Ran the complete repository test suite: **1,030 passed, 2 skipped**.
- Ran the integrity validator: **24 metrics**, **24 study packets**, **2,986,459 population rows**, **16,971 primary rows**, **1,800 pilot rows**, and **158 immutable artifact hashes** all validated, with zero scan failures.

## What remains

The next valid step is independent human labeling, not another automatic threshold choice:

1. Two humans independently label each metric's 75-row `agreement-pilot-labels.csv`.
2. Compute kappa, AC1, prevalence, and label-specific agreement.
3. If kappa is below 0.80, revise the codebook from disagreements and label a new pilot.
4. Freeze the agreed codebook, label and adjudicate the primary sample, then calculate weighted threshold quality with project-cluster confidence intervals.
5. Only after human consensus is frozen, run the blinded Ansible-expert AI comparison.

The box plot and sensitivity analysis generate candidates; neither one is treated as proof that Q3 or any other cutoff is correct.
Each box-plot row uses its own logarithmic scale because the metrics have different units and ranges; horizontal positions must not be compared across different rows.
