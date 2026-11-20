# large_playbook_loc labeling codebook

## Review question

Is this Ansible artifact excessively large and in need of decomposition?

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: The file contains separable concerns or is too large to maintain safely as one artifact.
- `negative`: The file is cohesive and its source size is justified by one clear responsibility.
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

The production implementation computes this metric for admitted Ansible documents, including task files; judge the actual artifact kind.

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
