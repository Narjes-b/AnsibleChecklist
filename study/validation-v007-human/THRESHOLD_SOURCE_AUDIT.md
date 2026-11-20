# V0.0.7 threshold source audit

Audit time: `2026-10-06T02:46:13.609682Z`
Result: **PASS**

source identity/schema audit only; metric values and predictions are not analyzed and historical reviewer-label files are not opened

## Verified population identity

- Threshold source rows: 2,986,459.
- Metrics mapped to human-condition families: 24 metrics / 13 families.
- Project identities in source: 207; frozen split: 206 repositories (144 calibration / 62 heldout).
- Commit mismatches: 0; missing run-status joins: 0; multi-commit projects: 0.
- Projects outside the frozen split: encapsulate-xyz/cosmos-ansible (the known timed-out repository is excluded).

## Use boundary

This verifies that threshold observations can be joined to the frozen repository split and run commits. It does not generate any threshold sample, inspect metric values/predictions, or consume historical reviewer labels. The exact execution order still requires agreement-pilot closeout and codebook freeze before generating calibration threshold batches; heldout observations remain unopened for human review until final freeze.
