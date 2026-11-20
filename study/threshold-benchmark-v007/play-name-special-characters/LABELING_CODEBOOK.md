# play_name_special_chars labeling codebook

## Review question

Does this task or its parent play have an inconsistent name that materially harms clarity?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The task or parent-play characters are decorative, confusing, or inconsistent with a readable naming convention.
- `negative`: The punctuation is ordinary technical notation or necessary to identify the operation.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Production propagates a play-name violation to each task in that play, so this study uses task units and holds the task-name cutoff fixed while varying the play-name cutoff.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
