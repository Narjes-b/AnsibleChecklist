# large_playbook_task_count labeling codebook

## Review question

Is this Ansible artifact excessively large and in need of decomposition?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The task population covers separable responsibilities and should be decomposed.
- `negative`: The tasks implement one cohesive workflow and are appropriately grouped.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Judge task cohesion as well as count; task-only files are included by the production metric.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
