# large_playbook_avg_task_size labeling codebook

## Review question

Would an average-task-size cutoff be a useful additional signal that this artifact needs decomposition?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: Multiple tasks are overly large or complex and should be decomposed.
- `negative`: The average reflects cohesive declarative detail rather than poor abstraction.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

This accepted legacy cutoff is currently unused by production. Treat this as a counterfactual design study, not current detector performance.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
