# large_play_task_count labeling codebook

## Review question

Is this Ansible play excessively large and in need of decomposition?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The tasks form separable stages that should be roles/includes or separate plays.
- `negative`: The task sequence is cohesive and splitting it would create unnecessary indirection.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Imported task files and block containers must not be confused with executable task count.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
