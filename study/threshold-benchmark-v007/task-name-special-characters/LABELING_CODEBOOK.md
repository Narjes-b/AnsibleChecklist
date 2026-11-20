# task_name_special_chars labeling codebook

## Review question

Does this task or its parent play have an inconsistent name that materially harms clarity?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The task or parent-play characters are decorative, confusing, or inconsistent with a readable naming convention.
- `negative`: The punctuation is ordinary technical notation or is necessary to identify the operation.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Jinja expressions and common technical punctuation are already excluded. Candidate replay varies the task-name cutoff while holding the parent play-name cutoff fixed.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
