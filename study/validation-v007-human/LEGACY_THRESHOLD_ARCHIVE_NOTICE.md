# Notice: historical threshold-benchmark artifacts

`study/threshold-benchmark-v007/` is preserved as a prior full-corpus threshold study. It contains threshold samples, earlier human/AI labels, adjudication, codebooks, and results created before the current 144/62 repository split.

These files are historical evidence only. They are not Reviewer A/B labels, adjudicated gold, calibration labels, or heldout labels for the current split-safe V0.0.7 human-validation study. Do not copy any historical label into the current blank reviewer files, and do not use the old full-corpus threshold labels to select thresholds or claim heldout performance.

The current study has no returned human labels and has not generated calibration or heldout performance samples. The retained `observations.csv.gz` is a machine-readable source population whose repository/commit join was audited in `THRESHOLD_SOURCE_AUDIT.md`; use it only under `THRESHOLD_VALIDATION_PROTOCOL.md`. Heldout human-review items/contexts remain gated on final freeze.
