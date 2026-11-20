# high_coupling_import_count labeling codebook

## Review question

Does this playbook have harmful dependency coupling?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The dependencies make behavior difficult to trace or bind unrelated components together.
- `negative`: The imports are a clear modularization/dispatch mechanism and do not create harmful coupling.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

Import-only dispatchers are normalized to zero by the detector and should not be called coupled merely for being modular.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
