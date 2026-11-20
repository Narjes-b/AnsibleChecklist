# long_statement_chars labeling codebook

## Review question

Is this source line excessively long in a way that materially harms readability or maintainability?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The line combines too much logic/data or should be reformatted, decomposed, or moved to a clearer representation.
- `negative`: The line remains clear and cohesive, or its length is unavoidable and changing it would not improve the code.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Long URLs and base64-like blobs were excluded before sampling. Judge YAML/Jinja readability, not length alone.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
