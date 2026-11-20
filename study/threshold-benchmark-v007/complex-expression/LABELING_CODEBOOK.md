# complex_expression_score labeling codebook

## Review question

Is this Jinja or conditional expression too complex and in need of simplification?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The expression is difficult to reason about and should be split, named, precomputed, or simplified.
- `negative`: The expression is understandable and expresses one cohesive condition or transformation.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Inspect operators, filters, indexing, nesting, and length together. The numerical score is only a proxy.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
