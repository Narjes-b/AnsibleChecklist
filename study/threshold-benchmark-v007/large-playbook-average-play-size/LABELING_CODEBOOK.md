# large_playbook_avg_play_size labeling codebook

## Review question

Is this Ansible artifact excessively large and in need of decomposition?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The plays are generally too large and should be decomposed into roles, includes, or smaller plays.
- `negative`: The average play size is appropriate for the cohesive workflow.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Inspect the individual plays because averages can hide one extreme play or many empty/small plays.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
