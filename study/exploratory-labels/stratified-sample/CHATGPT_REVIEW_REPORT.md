# ChatGPT reviewer C comparison

This compares a fresh ChatGPT AI pass with the existing Claude Sonnet 5 labels on the same 400-row impact-weighted sample. It is an AI-versus-AI consistency check, not a human gold standard, adjudication, or precision/recall estimate.

## Scope and method

- Sample branch commit: `598f43fa2fcba001ddfef70bc034d08abb626d31` (`feat/v005-empirical-study`).
- Sample: all 400 rows from `stratified-sample/stratified-sample.csv`; the four 100-row segments were reviewed, with the last segment split into two 50-row batches against the source files at each row's pinned commit SHA. Missing exact source objects were fetched into existing local repository clones; repositories were not recloned.
- Guidance: V007 reviewer instructions and family codebooks from workspace commit `15ff61b9859592a847b3dd49dc232d9d2f6e71cf`.
- The new CSV keeps all original source columns and adds a per-row GitHub URL, then the same 10 label columns used by the existing completed file. Existing Claude labels were not used as evidence during review.
- This covers the latest 400-row branch sample, not the historical 3,425-row V0.0.5 packet.
- Codebook QC reclassified 14 `loop-legacy-syntax` rows as uncertain because no supported Ansible version was present in the frozen evidence, as required by the rule override.
- New reviewer identity: ChatGPT AI precheck (not human); protocol: `stratified-v2-400-chatgpt-v1`.

## Overall agreement

- Semantic labels exactly matched: **235/400 (58.8%)**.
- Actionability labels exactly matched: **204/400 (51.0%)**.
- Both semantic and actionability labels matched: **201/400 (50.3%)**.
- Context-sufficiency flags matched: **287/400 (71.8%)**.
- External-context flags matched: **333/400 (83.3%)**.
- ChatGPT semantic distribution: positive 181, uncertain 68, negative 131, unreviewable 20.
- Claude semantic distribution: positive 195, uncertain 115, negative 79, unreviewable 11.
- Semantic label transitions (ChatGPT → Claude): negative → negative: 58; negative → positive: 22; negative → uncertain: 49; negative → unreviewable: 2; positive → negative: 17; positive → positive: 139; positive → uncertain: 25; uncertain → negative: 4; uncertain → positive: 33; uncertain → uncertain: 30; uncertain → unreviewable: 1; unreviewable → positive: 1; unreviewable → uncertain: 11; unreviewable → unreviewable: 8.

- ChatGPT actionability distribution: blocking 14, actionable 51, advisory 113, not-actionable 2, uncertain 69, not-applicable 151.
- Claude actionability distribution: blocking 9, actionable 73, advisory 99, not-actionable 7, uncertain 122, not-applicable 90.

## Agreement by family

| Family | Rows | Semantic match | Actionability match | Both match |
|---|---:|---:|---:|---:|
| Maintainability/complexity | 92 | 32 (34.8%) | 31 (33.7%) | 30 (32.6%) |
| Objective correctness | 48 | 21 (43.8%) | 20 (41.7%) | 20 (41.7%) |
| Review/history | 8 | 8 (100.0%) | 8 (100.0%) | 8 (100.0%) |
| Security | 38 | 27 (71.1%) | 22 (57.9%) | 22 (57.9%) |
| Structure/reuse | 31 | 2 (6.5%) | 3 (9.7%) | 2 (6.5%) |
| Style/policy | 133 | 106 (79.7%) | 80 (60.2%) | 80 (60.2%) |
| Variable/reference reasoning | 50 | 39 (78.0%) | 40 (80.0%) | 39 (78.0%) |

## Main findings

- Exact semantic agreement is 58.8%; exact agreement on both semantic and actionability labels is 50.3%. ChatGPT used fewer uncertain labels (68 vs. Claude's 115) and more negatives (131 vs. 79), showing a calibration difference as well as row-level disagreement.
- Agreement varies sharply by family: style/policy 79.7%, variable/reference 78.0%, security 71.1%, maintainability/complexity 34.8%, objective correctness 43.8%, and structure/reuse 6.5%. Spot checks of whole-file rules show Claude notes limited to short context windows, while this pass reviewed available pinned source-file blobs; repository-tree predicates still lacked tree evidence. These are evidence-scope and judgment differences, not proof either reviewer is right.
- Review/history has 8/8 label agreement, but all eight are unreviewable: five missing-release-note and three missing-test-update rows lack the required first-parent diff/changed-file evidence. The three missing-test-update predecessor commit objects were also unavailable locally. This is shared missing evidence, not successful validation.
- The largest residual semantic splits are loop-legacy-syntax (13/14), large-playbook (12/12), role-readme-absent (11/11), complex-playbook (10/10), and large-play (10/10). The loop-legacy labels remain a human review target because the supported Ansible version was absent.

## Rules with the most semantic disagreement

| Rule | Family | Rows | Disagreements | Rate |
|---|---|---:|---:|---:|
| ansibleguard/loop-legacy-syntax | Objective correctness | 14 | 13 | 92.9% |
| ansibleguard/large-playbook | Maintainability/complexity | 12 | 12 | 100.0% |
| ansibleguard/role-readme-absent | Structure/reuse | 11 | 11 | 100.0% |
| ansibleguard/variable-naming-convention | Style/policy | 22 | 11 | 50.0% |
| ansibleguard/complex-playbook | Maintainability/complexity | 10 | 10 | 100.0% |
| ansibleguard/large-play | Maintainability/complexity | 10 | 10 | 100.0% |
| ansibleguard/large-task | Maintainability/complexity | 22 | 9 | 40.9% |
| ansibleguard/missing-abstraction | Structure/reuse | 8 | 8 | 100.0% |
| ansibleguard/complex-expression | Maintainability/complexity | 17 | 6 | 35.3% |
| ansibleguard/molecule-test-absent | Style/policy | 6 | 6 | 100.0% |

## Example disagreements

At most three examples are listed per family; all labels and row IDs are available in the two CSVs.

| Sample ID | Family | Rule | ChatGPT semantic / actionability | Claude semantic / actionability |
|---|---|---|---|---|
| V007STRAT-UNGUARDED-VARIABLE-008 | Variable/reference reasoning | ansibleguard/unguarded-variable | negative / not-applicable | uncertain / uncertain |
| V007STRAT-UNGUARDED-VARIABLE-015 | Variable/reference reasoning | ansibleguard/unguarded-variable | uncertain / uncertain | negative / not-applicable |
| V007STRAT-UNGUARDED-VARIABLE-021 | Variable/reference reasoning | ansibleguard/unguarded-variable | uncertain / uncertain | negative / not-applicable |
| V007STRAT-VARIABLE-NAMING-CONVENTION-001 | Style/policy | ansibleguard/variable-naming-convention | positive / advisory | negative / not-applicable |
| V007STRAT-VARIABLE-NAMING-CONVENTION-003 | Style/policy | ansibleguard/variable-naming-convention | positive / advisory | negative / not-applicable |
| V007STRAT-VARIABLE-NAMING-CONVENTION-004 | Style/policy | ansibleguard/variable-naming-convention | positive / advisory | negative / not-applicable |
| V007STRAT-LARGE-TASK-003 | Maintainability/complexity | ansibleguard/large-task | negative / not-applicable | positive / actionable |
| V007STRAT-LARGE-TASK-005 | Maintainability/complexity | ansibleguard/large-task | positive / actionable | uncertain / uncertain |
| V007STRAT-LARGE-TASK-006 | Maintainability/complexity | ansibleguard/large-task | negative / not-applicable | positive / actionable |
| V007STRAT-CREDENTIALS-LEAKING-IN-LOG-004 | Security | ansibleguard/credentials-leaking-in-log | positive / blocking | negative / not-applicable |
| V007STRAT-CREDENTIALS-LEAKING-IN-LOG-013 | Security | ansibleguard/credentials-leaking-in-log | uncertain / uncertain | negative / not-applicable |
| V007STRAT-LOOP-LEGACY-SYNTAX-001 | Objective correctness | ansibleguard/loop-legacy-syntax | uncertain / uncertain | positive / actionable |
| V007STRAT-LOOP-LEGACY-SYNTAX-002 | Objective correctness | ansibleguard/loop-legacy-syntax | uncertain / uncertain | positive / actionable |
| V007STRAT-LOOP-LEGACY-SYNTAX-003 | Objective correctness | ansibleguard/loop-legacy-syntax | uncertain / uncertain | positive / actionable |
| V007STRAT-ROLE-README-ABSENT-001 | Structure/reuse | ansibleguard/role-readme-absent | unreviewable / not-applicable | uncertain / uncertain |
| V007STRAT-ROLE-README-ABSENT-002 | Structure/reuse | ansibleguard/role-readme-absent | unreviewable / not-applicable | uncertain / uncertain |
| V007STRAT-ROLE-README-ABSENT-003 | Structure/reuse | ansibleguard/role-readme-absent | unreviewable / not-applicable | uncertain / uncertain |
| V007STRAT-INSECURE-PERMISSIONS-001 | Security | ansibleguard/insecure-permissions | uncertain / uncertain | positive / actionable |

## Interpretation limits

Exact agreement measures consistency only. Disagreements can reflect different judgments, the limited source context available in a row, or codebook interpretation; neither AI pass is treated as correct by default. A human reviewer should adjudicate disagreements before either file is used as ground truth. The branch's design document already characterizes this sample as exploratory rather than a precision/recall measurement.
