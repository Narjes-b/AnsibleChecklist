# Calibration diagnostics after the eligibility repair

This is a new diagnostic snapshot generated from the original pilot master,
manifest and Reviewer A/B comparison. Its provenance is in
`report-status.json`. There are still 119 pending semantic disagreements.

The sample is explicitly excluded from performance scoring. Completing
adjudication cannot change that exclusion. The precision tables describe
settled pilot labels and do not estimate population precision.

The CSVs here are diagnostic snapshots. Continue adjudication in the original
`study/rq1-agreement-pilot/adjudication-sheet.csv`; these generated copies do
not establish another labeling track. Original reports and reviewer evidence
remain available as historical artifacts.

Reproduce this snapshot from the project root:

```sh
.venv/bin/python scripts/rq1_precision.py \
  --output-dir /tmp/rq1-calibration-diagnostics
```
