# V0.0.7 source-first recall protocol

## Purpose and estimand

Precision validation samples emitted detector findings. Recall requires a candidate universe independent of detector positives so that missed findings can enter human review. Do not calculate recall from emitted AnsibleGuard findings alone, and do not combine incompatible source universes into a global recall value.

For an eligible source-first universe, compare the detector's frozen firing state to adjudicated human truth at the same source-unit identity. Estimate recall as weighted human-positive units where the detector fired divided by all weighted human-positive units (detected positives plus false negatives). Preserve uncertain/unreviewable rates and the candidate-universe definition; do not force them into binary truth.

## Candidate panels

Prepare calibration panels only after the agreement pilot is closed and codebooks are frozen. Candidate extraction is performed from the frozen source commits without conditioning on whether the detector fired. Keep each family in a separate panel with its own population, sample, seed, identity, and inclusion probability.

- Variable resolution: enumerate variable references from frozen source, including references not emitted by AnsibleGuard. Reviewer labels are `valid/resolved`, `missing-internal`, `external-input`, `runtime-input`, or `uncertain`; compare those to detector outputs using stable source-reference identities. A global repository search is limited to the frozen evidence rules documented for the panel.
- Handler references: enumerate `notify`/`listen`/handler relationships from source, including non-firing candidates. Preserve reference/handler identities and distinguish missing internal handlers from externally defined or runtime-dependent behavior.
- Objective structural/correctness rules: include only rule families for which a complete source-unit candidate universe can be enumerated independently of detector output. Freeze each universe definition and exclusion logic before labeling.

## Eligibility and output

Create `results/recall-eligibility.csv` with `rule_id`, `recall_estimable`, `candidate_universe_definition`, `sampling_method`, and `reason_if_not_estimable`. Mark a rule `recall_estimable=false` when no defensible candidate universe exists; explain why rather than provide a proxy/global number.

Within calibration, sample only from the 144 frozen calibration repositories. Use deterministic SHA ranking, preserve population sizes and exact selection probabilities/weights, and keep repository-cluster uncertainty. Source-first labels remain separate from positive-finding precision labels even when the same source object overlaps; a shared review item may carry multiple memberships but is counted once per estimand.

Do not build or open heldout source-first contexts before the final detector/codebook/mapping/calibration freeze. After that gate, construct heldout universes from only the 62 heldout repositories, apply the frozen candidate-universe and sampling rules, and never use heldout labels to tune rules or thresholds.
