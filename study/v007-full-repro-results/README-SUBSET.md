# v0.0.7 full-reproduction results — 127-repo clean subset

This is **not** the canonical 207-repo `v007-full-repro-2026` package. It is a derived,
internally-consistent subset produced after the full run, to get a gate-passing,
analyzable result set quickly.

## What was excluded, and why

Starting from the full 207-repo corpus:

1. **41 repos** failed to complete even with a 90-minute per-repo timeout (raised from
   the original 30 minutes). Confirmed as genuine I/O-bound timeouts under this
   Windows/WSL/drvfs setup (low CPU time relative to huge wall-clock time), not
   analysis bugs. Listed in `status/validation.csv` with error `missing:*` (never
   produced output files).

2. **39 repos** were analyzed earlier in the session under an older tool commit
   (`21ada9649ef2360891b21c58872b8938f502a6eb`) than the other 127, which were analyzed
   under a later commit (`c5a703096a50a86670cee6f9e8584e6e53f9fc30`). The *only* code
   difference between those two commits is a `repository_timeout` config value
   (1800s → 5400s) in `study/configs/v007-207.yaml` — **not** any AnsibleGuard detector
   logic. Confirmed via `git diff --stat` (one line changed) and via the validation
   report's `observed_profile_rule_hashes` (identical single hash across all 166
   candidate repos regardless of which commit analyzed them).

   The validation gate requires every repo in a run to share one recorded tool commit.
   Since no single value can satisfy both groups simultaneously, the 39 repos run under
   the newer (minority) commit were excluded to keep the final 127 repos on one fully
   consistent, gate-passing identity (`21ada964...`).

Remaining: **127 of 207** repositories (61%), zero validation failures, one tool
commit, one rule-catalog hash.

## What's here

- `aggregate/` — rule, category, severity, provider, concept, resolution, certainty,
  and per-repository summary CSVs (the `__ALL__` aggregate row is excluded from
  `repository-summary.csv` by the pipeline's own `report()` step — do not re-aggregate
  it in). The pipeline's `all-*-occurrences.csv` raw dumps (every individual occurrence,
  ~320MB combined) are intentionally **not** included here — regenerate them locally
  with `study_pipeline.aggregate()` from the frozen run if you need row-level data;
  only the aggregated summaries are checked in.
- `charts/` — SVG charts generated from the above.
- `status/validation-report.json` + `validation.csv` — the passing gate result and
  per-repo status (`complete`/`partial`, none `failed`).
- `run-manifest.json` — records the single tool commit and config hash this subset
  was validated against.

## What's NOT here

The canonical `.tar.gz` archive, checksums, and `DETERMINISM_REPORT.md` that
`v007_full_repro.py --postprocess-only` would normally produce. That script's
`_sanity()` step hardcodes an expectation of exactly 207 repositories for this run ID
and correctly refuses to package a reduced corpus under the same canonical name. If a
packaged archive is needed later, it should be built as a clearly-labeled, separate
"127-repo subset" package rather than forcing the canonical packaging script to accept
a different repository count.

## Known limitation

`publication_ready` is `false` in the validation report — not because of failures
(there are none), but because 62 of the 127 repos are `partial` (an `ansible-lint`
warning only; `ansible-lint` is not a required provider in this run's config, so a
warning doesn't fail the gate, but it does keep `publication_ready` from being `true`,
which requires every repo to be fully `complete`).
