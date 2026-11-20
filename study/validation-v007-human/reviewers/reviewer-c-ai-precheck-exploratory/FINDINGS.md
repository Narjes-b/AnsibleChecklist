# Reviewer C AI precheck: findings

This summarizes the separate AI-only precheck in this folder. It is not human gold, adjudication, an agreement result, or a detector precision/recall estimate. No Reviewer A/B decisions or AI-shadow decision values were used or compared. Keep this file and CSV out of official agreement/performance statistics.

## Overall labels

All 350 rows were labeled (50 from each of the seven families), covering 112 distinct repository/commit pairs.

| Semantic label | Count | Meaning in this pass |
| --- | ---: | --- |
| `positive` | 127 | The documented condition is present in the frozen evidence. |
| `negative` | 139 | The documented condition is absent or contradicted by the frozen evidence. |
| `uncertain` | 80 | Evidence exists, but context or policy is materially ambiguous. |
| `unreviewable` | 4 | Required evidence is missing or insufficient for a defensible decision. |

Actionability is a separate field: 4 blocking, 39 actionable, 78 advisory, 140 not-applicable, and 89 uncertain. These counts need not match the semantic labels.

## By family

| Family | Positive | Negative | Uncertain | Unreviewable |
| --- | ---: | ---: | ---: | ---: |
| Objective correctness | 18 | 16 | 16 | 0 |
| Variable/reference reasoning | 13 | 31 | 6 | 0 |
| Security | 34 | 11 | 5 | 0 |
| Style/policy | 28 | 12 | 10 | 0 |
| Maintainability/complexity | 8 | 28 | 13 | 1 |
| Structure/reuse | 18 | 30 | 0 | 2 |
| Review/history | 8 | 11 | 30 | 1 |

## Main patterns and limits

- Security had the highest positive count (34/50). Within the sampled security rules, positive labels included insecure permissions (7/8), missing certificate validation (7/8), default credentials (6/8), and plaintext sensitive variables (6/7). These are sample-specific judgments against the frozen contexts, not claims about the repositories as a whole.
- Review/history had 30 uncertain rows. All 25 `commit-message-format` rows are uncertain because the exact messages were available but each repository's configured subject/body limits and formatting policy were not in the frozen bundles. The thresholds were not guessed. The remaining review/history uncertainty is about release-note convention or whether test changes were relevant. Of 17 missing-bug-reference rows, 6 were positive and 11 negative based on the exact message.
- Style/policy uncertainty is concentrated in missing-tag policy (5 rows) and whether a Molecule test is required (5 rows); repository conventions and test policy were not established by the supplied contexts.
- Variable/reference reasoning had 31 negative rows, 13 positive, and 6 uncertain. The uncertain cases depend on caller/runtime/module facts that could not be settled from the frozen evidence.
- The 4 unreviewable rows identify concrete evidence gaps:
  - `V007PILOT-MAINTAINABILITY_COMPLEXITY-020` (`large-playbook`): only lines 1–36 of a 4,812-line task file were supplied.
  - `V007PILOT-STRUCTURE_REUSE-046` (`role-readme-absent`): the supplied tracked-path tree was truncated before the cited role.
  - `V007PILOT-STRUCTURE_REUSE-049` (`insufficient-modularization`): only lines 1–36 of a 654-line playbook were supplied.
  - `V007PILOT-REVIEW_HISTORY-015` (`missing-release-note`): the changed-path list showed `CHANGELOG.md`, but its first-parent diff content was omitted.

The row-level rationale, evidence sufficiency, external-context field, and confidence are in the CSV. These results are an independent AI estimate for later comparison only; no human comparison has been performed.
