# Calibration diagnostics after the eligibility repair

This is a new diagnostic snapshot generated from the original pilot master,
manifest and Reviewer A/B comparison. Its provenance is in
`report-status.json`. There are still 119 pending semantic disagreements.

The repository owner attested that Aymen Jedidi and Ahmed Amine Essid
provided the two manual pilot reviews. Some historical records describe
those passes as automated. The attestation concerns this pilot only.

The sample is explicitly excluded from performance scoring. Completing
adjudication cannot change that exclusion. The precision tables describe
settled pilot labels and do not estimate population precision.

The CSVs here are diagnostic snapshots. Continue adjudication in the original
`study/rq1-agreement-pilot/adjudication-sheet.csv`; these generated copies do
not establish another labeling track. Reproduction requires the archived consolidated Reviewer A/B comparison as input.

Reproduce this snapshot from the project root:

```sh
.venv/bin/python scripts/rq1_precision.py --labels /path/to/consolidated-comparison.csv \
  --output-dir /tmp/rq1-calibration-diagnostics
```
