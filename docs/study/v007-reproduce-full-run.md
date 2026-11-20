# Reproduce the v0.0.7 full run

The canonical analysis environment recorded in this run was **Python 3.14.7**. CI separately checks package compatibility on Python 3.10 and 3.12; those matrix jobs are not the environment used for this full-corpus run.

For a full scan, first check out the validation branch to obtain the captured environment lock, install it, then check out the original analysis commit `d1711f90b7ab45fe80f429927c310cf58a323f77` and run the scan:

```bash
git switch study/v007-human-validation
python3.14 -m venv .venv
.venv/bin/python -m pip install -r study/environments/v007-full-run-pip-freeze.txt
git checkout d1711f90b7ab45fe80f429927c310cf58a323f77
PYTHON=.venv/bin/python ./scripts/run_v007_full_repro.sh --clean
```

The tracked lock file is an exact copy of the run's `environment/pip-freeze.txt` (SHA256 `f5001985a76186a61daea0bc169675b096fefed0773fbd67b2b16ea8e964ddd5`). `requirements.txt` and `pyproject.toml` describe supported dependency ranges.

To regenerate only the corrected tables and reports from an already completed local run, check out `study/v007-human-validation` again and run `.venv/bin/python scripts/v007_full_repro.py --postprocess-only`. This mode uses the preserved snapshots and does not reacquire or rescan repositories.

The command runs the test suite before it downloads or analyzes a repository, acquires the 207 tracked frozen Git revisions, and runs exactly four repository jobs concurrently. It produces `study/runs/v007-full-repro-2026/` and `study/runs/v007-full-repro-2026-results.tar.gz` plus its SHA256 file.

The runner requires Git, network access to the frozen clone URLs, at least 40 GiB free disk for 207 shallow exact-SHA checkouts, raw outputs, and the final archive, and the Python dependencies in `requirements.txt`; Docker is optional. It does not promise a runtime because repository size and network conditions vary.

Interrupted downloads may be resumed by rerunning the same command without `--clean`: every existing checkout is verified at the frozen SHA again. A local clone is reused only if its SHA is exact and its working tree is clean; otherwise the runner fetches the frozen commit. Do not reuse a prior analytical output as a new result; use `--clean` to start a canonical analysis. Verify inputs with `inputs/input-checksums.sha256`, outputs with `checksums/outputs.sha256`, and reproducibility with `DETERMINISM_REPORT.md` and `determinism-comparison.csv`.

## Verified procedure and pitfalls (re-execution of 2026-10-16)

The run was re-executed from `d1711f90` in a separate worktree and gave
identical AnsibleGuard, GitLeaks and review occurrences. The procedure that
worked, and the traps that did not:

```bash
# 1. a worktree at the analysis commit, with its own interpreter
git worktree add --detach ../AnsibleChecklist-v007-repro d1711f90b7ab45fe80f429927c310cf58a323f77
cd ../AnsibleChecklist-v007-repro
python3.14 -m venv .venv-repro
# the lock file is not present at d1711f90: take it from the validation branch
git show study/v007-human-validation:study/environments/v007-full-run-pip-freeze.txt \
  | grep -v '^-e ' > /tmp/lock.txt
.venv-repro/bin/python -m pip install -r /tmp/lock.txt
.venv-repro/bin/python -m pip install --no-deps -e .       # AnsibleGuard from THIS worktree
# 2. link the large untracked benchmark input (ignored by a global *.gz rule)
ln -s <main-checkout>/study/threshold-benchmark-v007/observations.csv.gz study/threshold-benchmark-v007/
# 3. run (needs ~20-40 GiB free; --minimum-free-gib lowers the guard)
PYTHON=.venv-repro/bin/python ./scripts/run_v007_full_repro.sh --minimum-free-gib 20
```

- **Provenance.** The tool commit recorded in every repository result is read
  from the *installed* package. An environment whose editable install points
  at another checkout stamps that checkout's commit, and the validation gate
  then marks all 207 repositories `failed`. Always `pip install -e` the
  worktree you run from, and check `observed_tool_commits` in
  `status/validation-report.json`.
- **The gate fails for the known timeout repository** (`encapsulate-xyz/cosmos-ansible`,
  1,800 s): `run_all` stops before aggregation. The original package was
  produced by normalising that row and running `--postprocess-only` at the
  later packaging commit (`15ff61b9`), which is what to do after the scan.
- **Do not edit source while a run is in progress.** Each repository scan
  re-imports AnsibleGuard; changing `src/` in the same checkout changes the run.
  Develop in another worktree.
- **ansible-lint modifies checkouts** (before the 2026-10-15 workspace guard):
  five repositories were rewritten or polluted by the frozen run itself. Reset
  checkouts to a clean state (`git checkout -- . && git clean -fd .ansible`)
  before a rerun, and verify `git status --porcelain` is empty everywhere.
- **Shallow clones must stay shallow.** Fetching parents into a frozen checkout
  turns it into a partial clone and changes review-rule results; use the side
  repositories of `scripts/fetch_v007_review_history_parents.py`.
- **Disk.** The full package is ~11 GB plus ~1 GB archive; keep 25 GB free
  before starting and do not leave failed attempts behind.

## Full-run architecture

The canonical identity is `v007-full-repro-2026`; analysis uses exactly four concurrent repository jobs.

```text
tracked frozen 207-row manifest + classification manifests
    ↓ exact Git clone URL and detached frozen commit checkout
    ↓ per-repository file classification manifest
    ↓ AnsibleGuard internal analysis
    ↓ optional external providers (ansible-lint and GitLeaks)
    ↓ raw provider outputs and stdout/stderr logs
    ↓ canonical occurrence identity and normalized CSV/GZip evidence
    ↓ aggregation with explicit provider-completeness states
    ↓ machine-readable tables and chart source CSVs
    ↓ SVG charts (and PNG copies when CairoSVG is available)
    ↓ sanity checks, deterministic re-postprocessing comparison, checksums
    ↓ portable results archive
```

`study/manifests/github-v2-final-eligible.csv` is the authoritative frozen population. Local checkout paths are regenerated below `study/cache/v007-full-repro-2026/repositories`. A pre-existing clone under `study/repositories` is used only when the runner independently proves the exact frozen SHA and an entirely clean worktree; it is then linked into the new cache and rechecked during preflight. All other repositories use a depth-one fetch of their exact SHA. This download cache cannot supply analytical output.
