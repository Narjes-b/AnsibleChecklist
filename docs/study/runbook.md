# Running an AnsibleGuard study for 5, 149, or any N repositories

This is the operational companion to `docs/study/pipeline-design.md`. Commands are
run from the repository root.

## 1. Prepare the environment

```bash
cd /home/aymmzn/Documents/AnsibleChecklist
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

Install/verify GitLeaks according to `README.md`. Verify provider availability:

```bash
.venv/bin/python -m ansibleguard.cli --help
.venv/bin/ansible-lint --version
./gitleaks-bin/gitleaks version
```

## 2. Choose the population

The pipeline uses rows whose frozen manifest `status` is `collected`. Every row
must include at least:

```text
project,repository_path,commit_sha,status
```

For each row, the configured classification directory must contain:

```text
<project-with-slash-replaced-by-__>__<commit_sha>.csv
```

Existing examples:

| Population | Manifest |
|---|---|
| Five-repository OpenStack smoke set | `study/manifests/pilot-five-frozen.csv` |
| Frozen 149-repository set | `study/manifests/github-v2-final-frozen.csv` |

For another population, create/freeze a manifest using the existing discovery,
selection, clone, and classification scripts. Do not edit frozen SHAs after a
study begins.

## 3. Create a configuration

Copy an example to a new run-specific file:

```bash
cp study/configs/v0061-smoke-5.yaml study/configs/my-run.yaml
```

Change at least:

```yaml
run:
  id: unique-run-id

repositories:
  manifest: path/to/frozen.csv
  file_manifests_dir: path/to/file-classification
  expected_count: 27
```

The `expected_count` prevents accidental partial populations. It must equal the
selected collected-row count. Remove it only for exploratory development.

Validate configuration syntax without scanning:

```bash
.venv/bin/python scripts/study_pipeline.py prepare \
  --config study/configs/my-run.yaml
```

Official preparation rejects a dirty AnsibleGuard worktree. Commit the exact
implementation first. For a disposable development run only, set
`tool.allow_dirty: true` and use a run ID that clearly contains `dev`.

## 4. Preflight

```bash
.venv/bin/python scripts/study_pipeline.py preflight \
  --config study/configs/my-run.yaml
```

Inspect:

```text
study/runs/<run-id>/status/preflight.csv
study/runs/<run-id>/status/preflight.json
study/runs/<run-id>/run-manifest.json
study/runs/<run-id>/input/repositories.csv
```

All repositories must pass before scanning.

## 5. Run the complete pipeline

### Five-repository smoke run

```bash
.venv/bin/python scripts/study_pipeline.py all \
  --config study/configs/v0061-smoke-5.yaml
```

### Official 149-repository run

Do this only after the five-repository acceptance gate passes:

```bash
.venv/bin/python scripts/study_pipeline.py all \
  --config study/configs/v0061-149.yaml
```

### Any other number

```bash
.venv/bin/python scripts/study_pipeline.py all \
  --config study/configs/my-run.yaml
```

The manifest determines N; no code change is required.

## 6. Run stages separately

```bash
.venv/bin/python scripts/study_pipeline.py prepare --config study/configs/my-run.yaml
.venv/bin/python scripts/study_pipeline.py preflight --config study/configs/my-run.yaml
.venv/bin/python scripts/study_pipeline.py scan --config study/configs/my-run.yaml
.venv/bin/python scripts/study_pipeline.py validate --config study/configs/my-run.yaml
.venv/bin/python scripts/study_pipeline.py aggregate --config study/configs/my-run.yaml
.venv/bin/python scripts/study_pipeline.py report --config study/configs/my-run.yaml
```

Separate stages are recommended during the first five-repository execution so
each gate can be inspected before continuing.

## 7. Resume an interrupted run

Keep the same configuration and run ID with:

```yaml
run:
  resume: true
```

Then rerun:

```bash
.venv/bin/python scripts/study_pipeline.py scan \
  --config study/configs/my-run.yaml
```

Compatible completed repositories are reused. Failed/missing repositories are
attempted again. Do not change the manifest/configuration under the same run
ID; create a new run when experimental inputs change.

## 8. Understand validation failure

Inspect:

```text
status/repository-status.csv
status/validation.csv
status/validation-report.json
logs/*.log
```

Common states:

| State | Meaning | Action |
|---|---|---|
| `complete` | Required output and providers completed. | May enter aggregate reporting. |
| `partial` | Internal scan exists but an optional provider is incomplete. | Keep separate; do not call provider-clean. |
| `failed` | Required output/provenance/provider invariant failed. | Repair and resume or exclude through a documented new population. |

For an official complete-provider comparison, ansible-lint and Gitleaks must
both be required. The committed v0.0.6.1 corpus configurations instead model
the known partial ansible-lint repositories explicitly: internal findings
remain eligible, while incomplete ansible-lint-owned occurrences are excluded
from provider-comparison datasets. GitLeaks remains required.

An exploratory run can pass its structural validation with optional providers
while `publication_ready` remains false. Official results require
`publication_ready: true`.

## 9. Read the results

Start with:

```text
report/FULL_STUDY_REPORT.md
status/validation-report.json
aggregate/aggregate-summary.json
```

Then use:

- `aggregate/repository-summary.csv` for every repository and `__ALL__`;
- `aggregate/category-summary.csv` for category statistics;
- `aggregate/rule-summary.csv` for rule statistics;
- `aggregate/all-canonical-occurrences.csv` for problem-level analysis;
- `aggregate/all-internal-occurrences.csv` for AnsibleGuard-only analysis;
- `aggregate/all-provider-comparable-occurrences.csv` for fair provider comparisons;
- `aggregate/all-raw-findings.csv` for provider evidence;
- `aggregate/provider-health.csv` before interpreting absence;
- `aggregate/repository-category-matrix.csv` for heatmaps/statistics;
- `charts/` for publication-ready SVG figures.

The report tables contain all repositories and rules. Charts may show only the
configured top N for readability.

## 10. Generate PNG charts

SVG requires no extra dependency. For PNG, install CairoSVG in the study
environment and request it:

```bash
.venv/bin/python -m pip install cairosvg
```

```yaml
report:
  formats: [svg, png]
```

Rerun only the report stage. SVG and source CSV remain canonical.

## 11. Scan a different AnsibleGuard version

Create a dedicated environment for that version. Do not change the current
working tree during a frozen run.

Example configuration:

```yaml
tool:
  mode: installed
  version: 0.0.5
  python: /absolute/path/to/ansibleguard-v005/bin/python
  commit_sha: FULL_V005_COMMIT_SHA
```

Give the run a different ID/output directory. The pipeline verifies the
package version reported by that Python interpreter.

## 12. Compare two versions

Both runs must contain the same projects at the same SHAs and must already be
aggregated:

```bash
.venv/bin/python scripts/study_pipeline.py compare \
  --base study/runs/v006-149 \
  --candidate study/runs/v0061-149 \
  --output study/comparisons/v006-to-v0061-149
```

Read:

```text
COMPARISON_REPORT.md
comparison-report.json
comparison-summary.csv
occurrence-comparison.csv
```

Before publishing, also confirm identical profile, file-manifest population,
provider scope, dependencies, and configuration—not only repository SHA.

## 13. Custom N-repository development run

For an intentionally limited development run, add:

```yaml
repositories:
  manifest: study/manifests/github-v2-final-frozen.csv
  file_manifests_dir: study/manifests/file-classification
  limit: 2
  expected_count: 2
```

Use a run ID containing `dev` or `smoke`. Never present this as the complete
149-repository result.

## 14. Five-repository v0.0.6.1 acceptance checklist

After the smoke run:

- [ ] five repositories complete;
- [ ] both providers complete, or every exception explained;
- [ ] zero duplicate raw finding IDs;
- [ ] zero duplicate occurrence IDs;
- [ ] no nested findings regress to line 1;
- [ ] expected 93 historical location false positives are absent;
- [ ] metadata and vars-only rules are visible;
- [ ] facts, `include_vars`, and role-prefix behavior matches the audit;
- [ ] tables sum to canonical totals;
- [ ] category and rule matrices contain five repositories;
- [ ] every chart has a source CSV;
- [ ] Markdown links render correctly;
- [ ] tool commit, repository SHAs, manifest hashes, profile, and provider scope are frozen.

Only after this checklist passes should v0.0.6.1 be tagged and the 149 run
launched.

## 15. Labeling and threshold work after scanning

Use `all-canonical-occurrences.csv` as the finding-first sampling population.
Build a separate source-first sample from selected files to estimate missed
findings. Preserve:

- deterministic seed;
- selection probability;
- rule/category/certainty/repository strata;
- two independent reviewer labels;
- original disagreement;
- adjudicated label and reason;
- calibration versus held-out repository split.

Thresholds are selected only on calibration repositories. Held-out results are
evaluated once after thresholds and code are frozen. See
[threshold-calibration-plan.md](threshold-calibration-plan.md) and
[the v0.0.7 validation README](../../study/validation-v007-human/README.md).

## 16. Commands before committing a pipeline change

```bash
.venv/bin/python -m py_compile \
  scripts/study_pipeline.py \
  scripts/study_reporting.py \
  scripts/run_study_pilot.py

.venv/bin/python -m pytest -q tests/test_study_pipeline.py tests/test_study_scripts.py
.venv/bin/python -m pytest -q
git diff --check
```
