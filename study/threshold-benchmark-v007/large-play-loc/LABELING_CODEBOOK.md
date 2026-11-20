# large_play_loc labeling codebook

## Review question

Is this Ansible play excessively large and in need of decomposition?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The play combines separable responsibilities or is too large to understand and test as one unit.
- `negative`: The play is cohesive and its size is justified by one clear orchestration responsibility.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Review source size together with task count and task content; LOC alone is not a defect.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
