# undocumented_complex_jinja_filters labeling codebook

## Review question

Is this task's Jinja filtering complex enough to require a preceding rationale comment?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The transformations or surrounding task logic are difficult enough that an explanatory rationale is needed and is missing.
- `negative`: The task is understandable without an extra rationale comment, or an adequate preceding comment is present.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

This cutoff is one branch of an OR rule with Boolean-operator count and nesting depth. Candidate replay changes only the filter cutoff while holding the other two at production defaults.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
