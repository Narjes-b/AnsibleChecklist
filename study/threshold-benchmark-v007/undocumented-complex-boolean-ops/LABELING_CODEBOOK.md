# undocumented_complex_boolean_ops labeling codebook

## Review question

Is this task condition complex enough to require a preceding rationale comment?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The condition or surrounding task logic is difficult enough that an explanatory rationale is needed and is missing.
- `negative`: The task is understandable without an extra rationale comment, or an adequate preceding comment is present.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

This cutoff is one branch of an OR rule with Jinja-filter count and nesting depth. Candidate replay changes only the Boolean-operator cutoff while holding the other two at production defaults.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
