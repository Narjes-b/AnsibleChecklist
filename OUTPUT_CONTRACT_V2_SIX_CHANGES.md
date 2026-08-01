# Output contract v2: the six organization changes

## Purpose

This document explains the six output improvements implemented before the new
five-repository test. The old root filenames remain available for one
compatibility release, but new integrations should use the organized v2 paths.

## New layout

```text
ansibleguard-output/
├── summary/
│   ├── report.json
│   ├── summary.csv
│   └── diagnostics.json
├── raw/
│   ├── findings.json
│   ├── findings.csv
│   └── findings.txt
├── canonical/
│   ├── occurrences.json
│   ├── occurrences.csv
│   ├── occurrences.txt
│   └── findings.sarif
├── metadata/
│   ├── run.json
│   ├── file-selection.json
│   └── review-metrics.json
├── legacy/
│   └── layout.json
├── <mirrored per-file legacy directories>/
└── <compatibility root aliases>
```

Start with `summary/report.json`. It tells a developer or script what happened,
how many results exist, which tools ran, and where every artifact is.

## Change 1 — one report index

### Why

Previously, a user needed to know whether to start with `summary.csv`,
`findings.json`, `run_metadata.json`, or `diagnostics.json`.

### How

`summary/report.json` now contains:

- schema and contract version;
- completion status, profile, target, and tool statuses;
- raw and canonical totals;
- counts by severity, provider, and concept;
- PR-comparison status;
- relative paths to every primary artifact;
- compatibility/deprecation information.

Example:

```bash
python - <<'PY'
import json
report = json.load(open("ansibleguard-output/summary/report.json"))
print(report["status"])
print(report["counts"]["raw_findings"])
print(report["counts"]["canonical_occurrences"])
PY
```

## Change 2 — canonical CSV and text

### Why

Deduplicated occurrences existed in JSON and SARIF, but spreadsheet and text
users still saw only raw provider results.

### How

The scanner now writes:

- `canonical/occurrences.csv`;
- `canonical/occurrences.txt`.

They include the shared concept, location, scan mode, severity, canonical
provider, detector count, native rules, fingerprints, and occurrence identity.

Use canonical output for normal review. Use `raw/findings.*` to audit exactly
what every detector reported.

## Change 3 — explicit schemas and versions

### Why

The old JSON shapes were implicit, so consumers could not reliably identify
the contract they received.

### How

Organized JSON documents now contain:

```json
{
  "schema_version": 2,
  "contract": "ansibleguard://schemas/output-v2.json",
  "kind": "canonical-occurrences"
}
```

The bundled schema is:

```text
src/ansibleguard/report/schemas/output-v2.json
```

It validates raw findings, occurrences, diagnostics, metadata, the report
index, legacy metadata, and PR comparisons. Collection documents use an
`items` array. Automated tests validate every primary v2 JSON document.

Manual validation:

```bash
python - <<'PY'
import json
from jsonschema import validate
schema = json.load(open("src/ansibleguard/report/schemas/output-v2.json"))
data = json.load(open("ansibleguard-output/canonical/occurrences.json"))
validate(data, schema)
print("valid output contract v2")
PY
```

## Change 4 — richer per-file summary

### Why

The old summary did not explain overlap or provider contribution.

### How

`summary/summary.csv` and its compatibility alias contain one row per file and
add:

| Column | Meaning |
|---|---|
| `raw_findings` | Results before overlap grouping |
| `canonical_occurrences` | Developer-visible problems |
| `ansibleguard_findings` | Raw internal-provider results |
| `ansible_lint_findings` | Raw ansible-lint results |
| `gitleaks_findings` | Raw GitLeaks results |
| `new_pr_findings` | Introduced occurrences after comparison |
| `pr_comparison_status` | `not-compared` or `compared` |

If a row has 12 raw findings and 8 canonical occurrences, four results were
grouped with other evidence. They remain available in the raw files.

Immediately after a standalone scan, PR columns say `not-compared`. The PR
comparison script updates them after it has both base and head evidence.

## Change 5 — clear output areas

Each directory now has one responsibility:

| Directory | Responsibility |
|---|---|
| `summary/` | Start page, triage, and failures |
| `raw/` | Lossless provider evidence |
| `canonical/` | Grouped problems and SARIF |
| `metadata/` | Reproducibility and file-selection evidence |
| `legacy/` | Compatibility explanation |

Recommended reading order:

1. `summary/report.json`
2. `summary/summary.csv`
3. `canonical/occurrences.txt` or `.csv`
4. `summary/diagnostics.json`
5. `raw/findings.json` for evidence auditing
6. `metadata/run.json` for reproducibility

Per-file legacy reports remain at their mirrored root paths during the
compatibility release. `legacy/layout.json` explains those paths instead of
copying thousands of reports and doubling artifact size.

## Change 6 — one-release compatibility

The existing root files are still written:

```text
summary.csv
findings.json
findings.raw.json
occurrences.json
findings.csv
findings.txt
findings.sarif
review_metrics.json
diagnostics.json
file_selection.json
run_metadata.json
```

The root findings/occurrences keep their list shape. Organized JSON uses v2
envelopes. Root and organized SARIF contain the same canonical results.

New code should discover paths through `summary/report.json`. Root aliases
should be removed only after study scripts, PR automation, and external
consumers migrate and a release note announces the removal.

## PR integration

The comparator consumes organized base/head occurrences:

```bash
python scripts/compare_pr_results.py \
  base-output/canonical/occurrences.json \
  head-output/canonical/occurrences.json \
  --policy observe \
  --head-output head-output \
  --output pr-decision.json
```

`--head-output` updates:

- `head-output/summary/summary.csv`;
- `head-output/summary.csv`;
- `head-output/summary/report.json`.

The decision JSON uses the v2 `pr-comparison` contract. The comparator still
accepts old occurrence lists during migration.

## Implementation files

| File | Responsibility |
|---|---|
| `src/ansibleguard/report/output_contract.py` | Layout, summaries, envelopes, report index, aliases |
| `src/ansibleguard/report/schemas/output-v2.json` | JSON Schema |
| `src/ansibleguard/report/csv_writer.py` | Versioned raw CSV |
| `src/ansibleguard/cli.py` | Calls the v2 writer |
| `scripts/compare_pr_results.py` | Reads v1/v2 and enriches PR summaries |
| `.github/workflows/ansibleguard.yml` | Uses organized canonical paths |

## Tests

The tests prove:

- every organized path exists;
- all primary v2 JSON validates;
- old raw/canonical aliases contain the same items as v2;
- root and organized SARIF match;
- the summary has unique files and correct counts;
- report totals match detailed files;
- the comparator accepts v2 envelopes;
- PR comparison updates the head report and summary.

Run:

```bash
.venv/bin/pytest -q tests/test_output_contract.py tests/test_pr_comparison.py
```

The five-repository scan must start only after the complete software suite
passes with this contract.
