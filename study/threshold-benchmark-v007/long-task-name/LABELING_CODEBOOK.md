# long_task_name_chars labeling codebook

## Review question

Is this task name unnecessarily long or difficult to scan?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The name contains excessive detail, duplicated context, or prose that should be shortened without losing intent.
- `negative`: The name is long because the operational distinction is necessary and remains clear.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Do not reward short but vague names. A useful task name should say what the task accomplishes.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
