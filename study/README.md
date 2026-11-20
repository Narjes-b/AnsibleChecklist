# Study workspace

This directory holds the empirical-study inputs and evidence. Tracked files
are frozen definitions and published evidence; local generated data is
ignored by Git. Never edit frozen evidence to match later code.

## Current study: v0.0.7 (207 repositories)

| Path | Contents |
|---|---|
| `manifests/github-v2-final-eligible.csv` | Authoritative frozen 207-repository population (exact clone URL and SHA) |
| `manifests/file-classification-v007-207/` | Per-repository file-classification manifests |
| `configs/v007-207.yaml` | Run configuration for `v007-full-repro-2026` |
| `environments/v007-full-run-pip-freeze.txt` | Exact Python environment lock of the run |
| `threshold-benchmark-v007/` | Threshold benchmark manifest and samples (`observations.csv.gz` is a large local input; see the audit) |
| `validation-v007-human/` | Split, identities, codebooks, agreement pilot, reviewer forms, protocols |
| `validation-v007-variable-resolution/` | Variable-resolution sample and results |

Generated, ignored by Git:

| Path | Contents |
|---|---|
| `runs/v007-full-repro-2026/` | Full run output: raw provider outputs, normalized evidence, tables, charts, reports |
| `cache/v007-full-repro-2026/repositories/` | Exact-SHA checkouts used by the run (many are links into `repositories/`) |
| `repositories/` | Reusable local clones; used only after exact-SHA and clean-worktree verification |

How to reproduce the run: [docs/study/v007-reproduce-full-run.md](../docs/study/v007-reproduce-full-run.md).
Current status and known problems: [docs/study/v007-audit-2026-10-15.md](../docs/study/v007-audit-2026-10-15.md).
Selection method: [docs/study/selection-protocol-v2.md](../docs/study/selection-protocol-v2.md).

## Earlier studies (historical evidence)

These directories are frozen evidence for earlier versions and corpora. Their
numbers are valid only for the version they name.

| Path | Study |
|---|---|
| `releases/v004/`, `freeze-v004/`, `archives/` | v0.0.4 149-repository freeze, calibration and release evidence |
| `pr-validation-v1/`, `recall-v1/` | v0.0.4 controlled PR-mode precision and synthetic recall |
| `validation/`, `validation-v5` … `validation-v8` | Earlier labeling ledgers and validation rounds |
| `analysis/`, `comparisons/`, `results/`, `labels/`, `history/` | Earlier analysis outputs and comparisons |
| `repositories-retired-149-2026-09-17/`, `repositories-207/` | Retired or auxiliary clone sets |
