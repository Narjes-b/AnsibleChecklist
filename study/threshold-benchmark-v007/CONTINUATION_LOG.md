# Threshold-study continuation log

## 2026-09-18 — complete threshold audit and rescan (superseded counts)

I audited the configuration keys and the actual detector comparisons, rather than assuming the first 17 scalar distributions represented every production threshold.

Added seven missing production-sensitive studies:

- complex-expression length, replayed as the real two-point score modifier;
- undocumented-complex-task Boolean operators;
- undocumented-complex-task Jinja filters;
- undocumented-complex-task nesting depth;
- play-name special characters;
- playbook cohesion score with its `<` comparator;
- the fixed normalized complex-playbook budget.

The undocumented-task studies preserve the two unchanged OR branches and the preceding-comment suppression. The expression-length study preserves the final score gate. Missing-abstraction preserves its file-role multiplier and existing-abstraction gate.

A final equivalence audit aligned the undocumented-task comment check with production's name-based task locator, including its behavior for duplicate task names. The corpus was rescanned after that correction; totals remained stable and the affected sensitivity counts were regenerated.

The first complete pass reported **2,925,814 observations, 24 metrics, 0 failures**. These counts were later superseded by the cleanup audit below.

The first pass created **14,463 frozen primary review rows** and **1,800 frozen pilot rows** across the 24 metrics. The primary count was later superseded; the 1,800-row pilot workload remains current. Mutable human-label files were preserved. Human labels, agreement, precision, recall, F1, F0.5, and human–AI agreement remain pending; no values were invented.

The configuration audit also found two ineffective legacy keys: `avg_task_playbook` is not used in the large-playbook OR decision, and `similarityPlays` is never compared to its configured threshold. These are recorded for an explicit remove-or-wire decision.

Added `BLINDED_AI_REVIEW_PROTOCOL.md` so every metric uses the same post-consensus Ansible-expert evaluation format while keeping human answers and threshold outcomes hidden.

## 2026-09-18 — population, replay, and sampling cleanup

Audited the benchmark for unusual patterns before beginning human labeling. Corrected 7,676 duplicate extra observations, removed vars/metadata from playbook detector populations, changed parent-play naming to the production task-level unit, and made every composite sensitivity row replay its complete production decision.

Fixed production source-line lookup for duplicate task names so comment suppression and reported locations use each parsed task's own line. Added stable occurrence identities, four-decimal continuous candidates, lower-tail cohesion bands with valid-domain clamping, prediction-aware sample strata, rare-positive censuses, expanded context, prediction-balanced pilots, Gwet's AC1, label-specific agreement, and project-cluster bootstrap confidence intervals.

Regenerated the corpus and all review artifacts: **2,986,459 unique observations**, **24 metrics**, **207 repositories**, **0 failures**, **16,971 primary rows**, and **1,800 pilot rows**. The complete explanation and before/after values are in `CLEANUP_AUDIT_AND_CORRECTED_RESULTS.md`.
