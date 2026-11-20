# large_playbook_play_count labeling codebook

## Review question

Is this Ansible artifact excessively large and in need of decomposition?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The plays represent separable workflows that should be split or imported.
- `negative`: The plays form one understandable orchestration workflow.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Many admitted documents contain zero plays because they are task/variable artifacts; those are valid negative units for this metric.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
