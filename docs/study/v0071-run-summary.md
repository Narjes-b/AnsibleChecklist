# v0.0.7.1 full run (207 repositories): summary

2026-10-16. Run id `v0071-full-2026`, tool version 0.0.7.1, tool commit `91c6438e7f83e1760d97dcbc0d976eb4bc9c0488`
(branch `fix/v007-audit-2026-10-15`), pinned environment of the v0.0.7 reproduction (ansible-core 2.21.0, ansible-lint 26.4.0).
Config: `study/configs/v0071-207.yaml`. Archive: `study/runs/v0071-full-2026-results.tar.gz`,
sha256 `152a6c957e58cb48f09953462a255a9a7683d7b070d18cd7d78ce2589b503605` (file `study/runs/v0071-full-2026-results.tar.gz.sha256`).

## Health
- 171 complete, 35 partial, 1 failed (the same single timeout repository as v0.0.7). The validation gate reports `failed` and
  `publication_ready: false` because of that one repository; post-processing was run with `--postprocess-only`, as for v0.0.7.
- Sanity checks passed. Determinism: 46 of 46 artifacts identical on re-aggregation.
- Provenance deviation to state in any write-up: the runner's own pytest step was skipped (`--skip-tests`). The suite had been run
  separately on the same commit: 1,169 passed and 2 skipped with `PYTHONPATH=src`, and the wheel-install test (which fails only when
  `PYTHONPATH` leaks into its clean environment) passed without it.
- `study/threshold-benchmark-v007/observations.csv.gz` (git-ignored) was copied into the run worktree for the benchmark integrity check, which reported valid.

## Counts
| | v0.0.7 | v0.0.7.1 |
|---|---:|---:|
| Canonical occurrences (all providers) | 376,115 | 373,924 |
| Raw findings | 390,286 | 389,924 |
| AnsibleGuard source occurrences | 265,434 | 264,704 |
| Required / optional | 83,497 / 181,937 | 82,767 / 181,937 |
| Rules with at least one occurrence | 60 | 59 |

The differences come from all audit fixes since v0.0.7 (see CHANGELOG 0.0.7.1), not only the latest ones. Largest required changes
(`study/analysis-v0071-2026-10-16/rule-delta-vs-v007.csv`): non-idempotent-command −768, read-only-command-change +118,
insecure-permissions −28, unused-handler −21, missing-file-extension −12, incomplete-task −8, missing-handler −7;
broken-role-dependency 1 → 0. Optional counts are unchanged. A decrease is not evidence of higher precision: it only shows that
the audited false-positive mechanisms no longer fire. The read-only increase is a transfer between two overlapping rules and
needs the pilot labels before any claim.

These are detector counts, not validated defects (no precision estimate exists yet).
