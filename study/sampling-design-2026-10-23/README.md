# Sampling frame inventory — 2026-10-23

These tables describe the existing `v0071-rerun-2026-10-22` canonical-provider
allocation. They are **planning evidence**, not new samples or performance
estimates. No source contexts or reviewer/model labels were generated.

| Artifact | Purpose |
|---|---|
| `repository-frame.csv` | 207 repositories: split, exact SHA, source/provider health, listed-example exposure, source counts |
| `sampling-cells.csv` | 121 nonempty split/rule/policy/certainty/resolution cells |
| `partition-margins.csv` | Counts by split, listed exposure, repository-size quartile, provider completeness and decision state |
| `rule-feasibility.csv` | Required-rule counts and repository support; availability screen and possible small-population censuses |
| `frame-manifest.json` | Input, output and script hashes; population view and interpretation limits |

Totals: 264,704 internally assigned static-source occurrences, including
82,767 required and 181,937 optional. Calibration contains 59,891 required
occurrences; the old heldout partition contains 22,876. The failed repository
has an unavailable count, not a measured zero.

The exposure join uses only the two explicitly supplied exploratory samples.
It identifies 55 old-heldout repositories with listed examples. Absence from
those two files does not establish an untouched repository. None of this
development population is certified as eligible final evaluation data.

Reproduce after extracting the frozen run's internal-source occurrence CSV:

```sh
.venv/bin/python scripts/audit_sampling_partitions.py \
  --occurrences /path/to/extracted-run/aggregate/all-internal-source-occurrences.csv \
  --repository-status study/analysis-v0071-rerun-2026-10-22/run/tables/repository-execution-status.csv \
  --exposure-samples \
    study/exploratory-labels/stratified-sample/stratified-sample.csv \
    study/exploratory-labels/stratified-sample-v0071/stratified-sample.csv \
  --output-dir /tmp/sampling-frame
```

The [sampling methodology](../../docs/study/sampling-methodology-2026-10-23.md)
uses these results to define repository/decision partitions, probability
selection, complete evidence retrieval, missingness and final validation.
