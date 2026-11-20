# cohesion_playbook_score labeling codebook

## Review question

Does this playbook combine unrelated responsibility domains so strongly that it should be decomposed?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: Multiple plays show conservatively gated domain fragmentation that makes the playbook difficult to understand or reuse.
- `negative`: The playbook remains cohesive, or ordinary module diversity is justified by one orchestration goal.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Lower scores are more suspicious. The detector currently emits 0 only after a conservative gate and otherwise at least 0.5, so many numerical candidates may be behaviorally equivalent.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
