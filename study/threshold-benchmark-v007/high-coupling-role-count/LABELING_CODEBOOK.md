# high_coupling_role_count labeling codebook

## Review question

Does this playbook have harmful dependency coupling?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The role dependencies combine unrelated responsibilities or make the play difficult to reuse and reason about.
- `negative`: The roles form one clear orchestration composition and their number is justified.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Role count is a proxy; architectural cohesion and dependency direction are the real judgment.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
