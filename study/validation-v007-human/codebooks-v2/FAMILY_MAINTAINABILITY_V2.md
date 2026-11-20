# Family v2: maintainability and complexity
Question: is the metric the rule reports **correctly measured on the right unit**, and does the construct genuinely show the condition? The threshold itself is validated separately by the threshold panels (plan v2 mode B); do not label a finding negative merely because you dislike the threshold.

Operational definitions:
- Right unit: `large-task` = one task; `large-play` = one play; `large-playbook`/`complex-playbook` = a playbook file (not a role task file or data file). A mismatched unit is `negative`, reason `wrong-analysis-unit`.
- Measured values (lines, tasks, depth, imports): see COMMON_V2 C11. `large-task` uses LOC_task > 15 where LOC is the normalised YAML re-serialisation of the task (not source lines); `large-play`: measured against LOC_play 50, 7 tasks per play and average task size 15; `large-playbook`/`complex-playbook`: measured against LOC_playbook 110, 4 plays and the coupling limits (the exact combination is the oracle's job, see C11); comments are not part of the metric. You judge the unit and the visible size order, not the exact count.
- `excessive-nesting`: depth counted as the rule counts it (block/include nesting), threshold 3.
- `complex-expression`: a Jinja or `when`/`changed_when`/`failed_when`/`until` expression whose complexity score (logical words and/or/not/in/is, comparison operators, pipes, parentheses, brackets, `?`, +2 when longer than 100 characters) is at least 6. Count the score and list the contributors.
- `undocumented-complex-task`: a task whose `when` has at least the configured number of boolean operators or Jinja filters, or nesting depth above the configured limit, and no comment immediately above it. Positive = the complexity holds and no preceding comment. Report the operator/filter count.
- `incomplete-task`: a whole-word marker TODO, FIXME, HACK or XXX (any case) inside a task name or a module argument string (comments are not scanned). A marker inside a path (`hack/`) or identifier (`containerd-hack`) is negative.
- `unused-handler`: no `notify` or `listen` anywhere in the visible tasks, included/imported files, or role handler files refers to the handler. A notify set through `include_role`/`import_role` with `apply:` counts as a reference. If the notifying files are not in the bundle: `uncertain` + bundle_issue `missing-file`.
- `high-coupling`: imports > 4 or roles > 5 in the unit (strictly greater). A file that only dispatches imports (no functional tasks) counts 0 imports by the rule.
- `deprecated-modules`: see objective family (2.21 metadata).
- `unused-registered-variable`/`shell-instead-of-module`: positive only with a stated equivalent module (name it in notes).

Positive semantic reasons: `metric-reproduced-condition-present`, `repetition-supported`, `confirmed-equivalent-module`.
Negative: `wrong-analysis-unit`, `cohesive-or-manageable`, `metric-not-reproduced`.
Uncertain: `architecture-context-needed`, `dynamic-reference`.
