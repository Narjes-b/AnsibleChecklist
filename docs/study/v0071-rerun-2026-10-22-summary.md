# v0.0.7.1 full rerun on the consolidated branch (2026-10-22)

Run id `v0071-rerun-2026-10-22`, tool version 0.0.7.1, tool commit `ad1d60023d237b6e1cfa53466e81407e3f329229`
(branch `chore/consolidate-and-cleanup-2026-10-22`), ansible-core 2.21.0, ansible-lint 26.4.0.
Config: `study/configs/v0071-207-rerun-2026-10-22.yaml` (same population, profile and providers as `v0071-full-2026`).
Archive: `v0071-rerun-2026-10-22-results.tar.gz`, sha256
`b89d10f7c37f7093a66162323b68f6e34ae5c76599360d759607003347fc8c66` (file `study/runs/v0071-rerun-2026-10-22-results.tar.gz.sha256`).
Tables and charts: `study/analysis-v0071-rerun-2026-10-22/`. Full results report: [v0071-rerun-2026-10-22-full-report.md](v0071-rerun-2026-10-22-full-report.md).
The raw run archive is kept outside Git in `~/Documents/AnsibleChecklist-results-2026-10-22/`.

## Health
- 171 complete, 35 partial, 1 failed: `encapsulate-xyz/cosmos-ansible` timed out (1,800 s), the same repository as in
  v0.0.7 and v0.0.7.1. The validation gate therefore reports `failed` / `publication_ready: false`; post-processing ran with
  `--postprocess-only`, as for the earlier runs.
- The runner's own test step ran this time: 1,227 passed, 2 skipped.
- Sanity checks passed. Determinism: 46 of 46 artifacts identical on re-aggregation. `scripts/v007_charts_check.py`: all checks pass.

## Deviations to state in any write-up
- `--skip-benchmark-validation`: `study/threshold-benchmark-v007/LABELING_CODEBOOK.md` was revised on 2026-09-30 (commit
  `09428bd7`) without updating its frozen hash in `benchmark-manifest.json`, so the threshold-benchmark integrity check fails.
  That check covers the separate threshold-labelling pilot, not scan output. The manifest was not edited.
- `UtrechtUniversity/yoda`: the shallow fetch of its frozen commit timed out on a slow connection. The run-cache checkout was
  prepared by a manual fetch of the same commit (`a9175010…`) and verified by the runner (exact SHA, clean worktree).

## Comparison with `v0071-full-2026` (2026-10-16)
All AnsibleGuard results are identical: 264,704 source occurrences, 82,767 required / 181,937 optional, 59 rules, and every
row of `rule-profile.csv`, `category-overview.csv`, `family-overview.csv`, `repository-profile.csv` and the crosstab.
The only differences:

| | 2026-10-16 | 2026-10-22 |
|---|---:|---:|
| Canonical occurrences (all providers) | 373,924 | 373,923 |
| ansible-lint findings | 107,627 | 107,626 |
| Runtime distribution chart | machine timing | machine timing |

The one-finding difference comes from the external ansible-lint provider, not from AnsibleGuard. The detector changes merged
since 2026-10-16 (the `include_vars` PermissionError fix, `--explain` and output-format additions) do not change any
AnsibleGuard count on this population.

These are detector counts, not validated defects.
