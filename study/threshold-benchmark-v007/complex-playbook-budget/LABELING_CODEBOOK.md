# complex_playbook_budget labeling codebook

## Review question

Is this Ansible artifact overly complex because several size and dependency dimensions compound?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The combined source size, plays, tasks, imports, and roles create an artifact that should be decomposed.
- `negative`: The combined dimensions remain maintainable and support one cohesive orchestration responsibility.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

The value is LOC/110 + plays/4 + tasks/15 + imports/4 + roles/5. Production uses a fixed budget cutoff of 2.0; this study tests its distribution and alternatives.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
