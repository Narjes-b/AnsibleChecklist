# excessive_nesting_depth labeling codebook

## Review question

Is this task nested too deeply for clear and safe maintenance?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The block/rescue/always nesting obscures control flow or should be flattened/extracted.
- `negative`: The nesting is shallow, purposeful, and makes error handling or grouping clearer.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Depth zero is ordinary top-level task structure. Judge the surrounding block and recovery logic.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
