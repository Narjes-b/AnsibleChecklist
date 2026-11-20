# large_play_avg_task_size labeling codebook

## Review question

Is this Ansible play excessively large and in need of decomposition?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: Several tasks contain overly large operations and the play would benefit from decomposition.
- `negative`: The average is driven by cohesive declarative tasks or otherwise appropriate detail.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Inspect multiple tasks in the play; one unusual task can distort an average.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
