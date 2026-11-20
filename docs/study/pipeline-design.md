# Generic N-repository study and analysis pipeline

**Status:** implemented design, ready for focused validation
**Pipeline schema:** 1
**Supported population:** any positive number of frozen repositories
**Primary command:** `scripts/study_pipeline.py`

## 1. Purpose

The pipeline turns a frozen repository manifest into one reproducible study
run containing individual AnsibleGuard outputs, completeness evidence,
cross-repository datasets, statistical tables, charts, and a Markdown report.
It is not coupled to 149 repositories or to one AnsibleGuard release.

The core invariant is:

> One configuration + one frozen repository population + one immutable tool
> identity = one isolated run directory.

The pipeline organizes detector output. It does not automatically turn an
unlabeled finding into a confirmed software defect.

## 2. Stages

```text
configuration
  -> prepare immutable identity
  -> preflight repositories and manifests
  -> scan N repositories, with resume
  -> validate outputs and provider health
  -> aggregate raw and canonical data
  -> generate tables and charts
  -> generate complete Markdown report
  -> optionally compare with another compatible run
  -> later sample, label, adjudicate, calibrate, and evaluate
```

The CLI exposes `prepare`, `preflight`, `scan`, `validate`, `aggregate`,
`report`, `compare`, and `all`. Each stage can be rerun independently.

## 3. Components

| Component | Responsibility |
|---|---|
| `scripts/study_pipeline.py` | Configuration, identity, orchestration, resume, validation, aggregation, reporting, and comparison. |
| `scripts/study_reporting.py` | CSV/Markdown tables and dependency-light SVG bar, pie, and heatmap charts. |
| `scripts/run_study_pilot.py` | Existing frozen-SHA repository execution primitive, now accepting an explicit Python environment. |
| `scripts/scan_and_summarize_repositories.py` | Existing per-repository summary logic reused by the aggregate stage. |
| `scripts/compare_validation_versions.py` | Existing semantic occurrence matching reused by run comparison. |
| `study/schemas/study-pipeline-config.schema.json` | Configuration contract. |
| `study/schemas/study-run-manifest.schema.json` | Immutable run-provenance contract. |

## 4. Configuration contract

The YAML configuration has six logical sections:

| Section | Meaning |
|---|---|
| `run` | ID, profile, provider scope, workers, timeout, resume, and failure policy. |
| `tool` | Python environment, expected package version, execution mode, and exact commit provenance. |
| `repositories` | Frozen manifest, classification directory, optional expected count, and optional development limit. |
| `output` | Parent directory for isolated runs. |
| `providers` | Whether incomplete ansible-lint or Gitleaks makes validation fail. |
| `report` | Chart formats and visual top-N limits. Tables always retain the full population. |

Two examples are committed:

- `study/configs/v0061-smoke-5.yaml`;
- `study/configs/v0061-149.yaml`.

`repositories.expected_count` is an assertion, not a population selector. The
manifest controls the population. `repositories.limit` exists only for
development and smoke checks and must not be used silently for an official
study.

## 5. Tool-version independence

### Current-worktree mode

The configured Git reference must resolve to the current `HEAD`, because the
pipeline executes the configured Python environment rather than checking out
code behind the user's back. It verifies that the environment reports the
configured package version. A dirty worktree is rejected by default because
its executed content cannot be reconstructed from the recorded commit.
`tool.allow_dirty: true` is available only for explicitly named development
runs.

### Installed mode

Use a dedicated virtual environment, wheel, or container for another release.
Set:

```yaml
tool:
  mode: installed
  version: 0.0.5
  python: /absolute/path/to/v005-venv/bin/python
  commit_sha: FULL_40_CHARACTER_SHA
```

This keeps comparisons honest: every version has its own environment and full
commit identity. An official study should prefer a tagged wheel or immutable
container over a mutable working tree.

## 6. Run-directory contract

```text
study/runs/<run-id>/
├── run-config.yaml
├── run-manifest.json
├── input/
│   └── repositories.csv
├── status/
│   ├── preflight.csv
│   ├── preflight.json
│   ├── repository-status.csv
│   ├── validation.csv
│   └── validation-report.json
├── repositories/
│   └── <owner>__<repository>/<sha>/<profile-if-not-technical-full>/...
├── logs/
├── aggregate/
├── tables/
├── charts/
├── report/
├── labels/
└── comparison/
```

The copied configuration, resolved population, configuration hash, source
manifest hash, package version, commit SHA, profile, and provider scope make
the run identifiable. An existing run ID rejects a changed configuration or
manifest, or a different tool commit instead of silently mixing results.

## 7. Preflight guarantees

For each selected manifest row, preflight checks:

- nonempty, unique project identity;
- complete 40-character repository SHA;
- existing repository checkout;
- no duplicate checkout path;
- checkout `HEAD` equals the frozen SHA;
- matching per-project classification manifest.

Preparation also records the SHA-256 of every classification manifest in the
resolved repository population.

The scan refuses to start when any repository fails preflight.

## 8. Scan and resume behavior

Repositories may run concurrently. Results are written beneath the run,
preserving repository and SHA identity. Every repository records status,
duration, snapshot path, and an error when applicable.

With `resume: true`, an existing result is reused only when its profile,
classification hash, ansible-lint population, and configured build/container
provenance remain compatible with the existing runner checks. Failed units can
therefore be retried without rescanning successful ones.

The status vocabulary is:

- `completed` — executed successfully;
- `skipped` — compatible completed output reused;
- `failed` — repository execution failed;
- provider-level `completed`, `partial`, `failed`, or `missing` remains
  separately visible.

## 9. Validation gate

Validation checks every expected repository for:

- `run_metadata.json`;
- `raw/findings.json`;
- `canonical/occurrences.json`;
- requested profile;
- matching source SHA when recorded;
- matching classification-manifest hash;
- consistent rule/profile hash and tool commit across repositories;
- required provider completion;
- unique raw finding IDs;
- unique canonical occurrence IDs;
- positive line numbers.

Results are `complete`, `partial`, or `failed`. A missing or failed provider is
never converted to a clean result. Provider requirements can be relaxed for an
exploratory run, but the status remains recorded and `publication_ready`
remains false until every repository is complete.

## 10. Aggregate datasets

The aggregate stage creates:

| File | Unit |
|---|---|
| `repository-summary.csv` | One row per repository plus `__ALL__`. |
| `all-raw-findings.csv` | One row per native/provider finding. |
| `all-canonical-occurrences.csv` | One row per overlap-aware occurrence. |
| `all-internal-occurrences.csv` | Internal AnsibleGuard occurrences, independent of provider completeness. |
| `all-provider-comparable-occurrences.csv` | Canonical occurrences excluding evidence owned by an incomplete provider. |
| `category-summary.csv` | Category counts, shares, prevalence, distribution, and normalized rate. |
| `rule-summary.csv` | Rule counts, shares, prevalence, distribution, and normalized rate. |
| `severity-summary.csv` | Severity statistics. |
| `certainty-summary.csv` | Confirmed/uncertain/not-applicable statistics. |
| `provider-summary.csv` | Canonical provider contribution. |
| `provider-health.csv` | Completed/partial/failed/missing repositories per provider. |
| `diagnostics-summary.csv` | Diagnostics and scan errors per repository. |
| `repository-category-matrix.csv` | Wide repository × category table. |
| `repository-rule-matrix.csv` | Wide repository × rule table. |
| `aggregate-summary.json` | Small machine-readable index. |

Raw findings and canonical occurrences are deliberately separate. Provider
overlap must not be confused with distinct problems.

The internal, all-provider, and provider-comparable populations are also kept
separate. A partial ansible-lint repository remains in internal analyses, but
its ansible-lint-owned occurrences are excluded from provider comparisons.
This is missing-data modeling, not an assertion that ansible-lint was clean.

## 11. Statistics

For categories, rules, severity, certainty, and providers, the pipeline reports:

- findings;
- percentage of all canonical findings;
- affected repository count;
- repository prevalence percentage;
- median findings per repository;
- first and third quartiles per repository;
- findings per 1,000 selected lines.

Repository rows contain totals, selected files/LOC, diagnostics, findings per
100 files, and findings per 1,000 selected lines.

Totals answer “how much output exists?” Normalized rates and repository
distributions answer “is this merely a large-repository effect?” Neither is a
precision estimate until findings are independently labeled.

## 12. Tables and charts

The full Markdown report contains all repositories and rules. Visuals use a
top-N limit only for readability.

Generated SVG charts:

- category pie chart;
- severity pie chart;
- certainty pie chart;
- provider-contribution pie chart;
- top-rule horizontal bar chart;
- normalized repository bar chart;
- repository/category heatmap;
- provider-completeness chart.

SVG is generated using the Python standard library so the evidence pipeline
does not depend on a plotting stack. If `cairosvg` is installed and `png` is
requested, matching PNG copies are produced. Every chart has a source CSV;
charts are presentation, never the sole evidence.

Pie charts are restricted to part-to-whole composition. Repository and rule
comparisons use bars or heatmaps because pie slices are poor comparison tools.

## 13. Markdown report

`report/FULL_STUDY_REPORT.md` includes:

- run/tool/population overview;
- interpretation boundary;
- complete category and rule tables;
- complete repository table;
- certainty and provider tables;
- provider-health and diagnostics sections;
- charts with relative links;
- reproducibility pointers.

`report/report-data.json` preserves the same report inputs for another
presentation layer later.

## 14. Compatible run comparison

Comparison first requires identical project → SHA mappings. Classification
manifest hashes, profile, and ansible-lint scope must also match. The pipeline
then reuses the existing occurrence matcher to distinguish:

- introduced;
- fixed;
- unchanged;
- moved/semantic matches;
- location matches;
- uncertain detector-shape matches.

It writes row-level comparison evidence, category/rule summaries, JSON, and a
Markdown report. A mismatched repository population fails instead of producing
an invalid before/after claim. File-manifest/profile/provider compatibility
should also be reviewed before publishing the comparison.

## 15. Labeling extension

The run contains a reserved `labels/` directory. The next connection should
wrap the existing sampling and review tools into pipeline subcommands:

```text
sample-findings
sample-source
label
adjudicate
calibrate
evaluate-heldout
```

Finding-first samples estimate precision. Source-first samples expose false
negatives and support recall. Repositories—not individual findings—must be
split between calibration and held-out evaluation. Two independent labels,
pre-reconciliation agreement, adjudication, and selection probabilities must
be preserved.

## 16. Failure and safety rules

- Never overwrite a different run through the same run ID.
- Never scan a moved checkout in a frozen study.
- Never report provider failure as clean.
- Never merge raw and canonical totals.
- Never call unlabeled counts defects or precision.
- Never compare different repository SHAs as a tool-only change.
- Never tune thresholds on the final held-out repositories.
- Never remove historical run outputs when preparing a later version.

## 17. Remaining validation before the official 149 run

The pipeline implementation itself must pass:

1. unit tests with synthetic snapshots;
2. a two-fixture end-to-end scan;
3. the frozen five-repository v0.0.6.1 smoke run;
4. inspection of every validation, aggregate, chart, and report artifact;
5. version-comparison testing against a compatible earlier five-repository run;
6. resource tuning for the selected worker count.

Only then should `study/configs/v0061-149.yaml` launch the official run.
