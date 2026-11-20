# complex_expression_length_chars labeling codebook

## Review question

Is this Jinja or conditional expression too complex and in need of simplification?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The complete expression is difficult to reason about and should be split, named, precomputed, or simplified.
- `negative`: The complete expression remains understandable and expresses one cohesive condition or transformation.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

In production, crossing this cutoff adds two points to the expression score; it is not an independent finding. Judge the whole expression, not character count alone.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
