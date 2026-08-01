# AnsibleGuard architecture and verification guide

This document describes the current package architecture. Historical debugging
and migration details are retained separately in `PROJECT_STATUS.md`,
`CLI_STATUS.md`, and `PARSING_GITHUB_IMPLEMENTATION.md`.

## Runtime architecture

```text
ansibleguard command
  │
  └── cli.main()
      └── cli.analyze_path(target, output_root)
          ├── profiles.profile_definition()
          ├── collect_yaml_files()
          │   └── optional file_manifest.included_files_from_manifest()
          ├── external.gitleaks.scan_with_gitleaks(target)
          ├── external.ansible_lint.scan_with_ansible_lint(target)
          ├── for each YAML file
          │   ├── document.inspect_document()
          │   ├── smells.execute_for_single_file()
          │   │   ├── parser.mainn()
          │   │   │   └── internal detector modules
          │   │   ├── smells.assess_code_smells()
          │   │   └── legacy per-file writers
          │   ├── safe source checks for structurally skipped documents
          │   ├── report.findings.build_findings_list()
          │   ├── detector_config.filter_findings()
          │   └── append normalized per-file text findings
          ├── detectors.review_metadata.detect_project_review_smells()
          ├── retain non-YAML GitLeaks findings
          └── write project rollups
              └── report.output_contract.write_rollups_v2()
                  ├── summary/report.json + summary.csv + diagnostics.json
                  ├── raw/findings.json + .csv + .txt
                  ├── canonical/occurrences.json + .csv + .txt + SARIF
                  ├── metadata/run.json + file-selection.json
                  └── one-release root compatibility aliases
```

External tools are executed once per scan target. Their findings are matched
back to individual YAML files for per-file output, while GitLeaks results for
non-YAML files remain in the project rollups.

## Package responsibilities

| Path | Responsibility |
|---|---|
| `src/ansibleguard/cli.py` | Discovery, external-tool orchestration, file/project aggregation, exit policy |
| `src/ansibleguard/document.py` | Safe loading and document classification |
| `src/ansibleguard/file_manifest.py` | Row-level repository classification, manifest validation, and selection provenance |
| `src/ansibleguard/profiles.py` | Complete rule-family partition, execution flags, filtering, and profile hashes |
| `src/ansibleguard/parser.py` | Calls internal detectors for one structurally analyzable document |
| `src/ansibleguard/smells.py` | Applies legacy thresholds and writes legacy per-file reports |
| `src/ansibleguard/detector_config.py` | `.ansibleguard.yml` lookup, merging, options, and normalized suppressions |
| `src/ansibleguard/detectors/` | Internal rule implementations |
| `src/ansibleguard/detectors/source_lines.py` | Shared ruamel loader and exact YAML coordinates |
| `src/ansibleguard/external/` | GitLeaks installation/execution and ansible-lint execution |
| `src/ansibleguard/report/findings.py` | Canonical 65-rule catalog and finding normalization |
| `src/ansibleguard/report/output_contract.py` | Versioned layout, report index, summaries, and compatibility aliases |
| `src/ansibleguard/report/occurrences.py` | Cross-provider canonical occurrence grouping |
| `src/ansibleguard/report/csv_writer.py` | Legacy metric CSV and normalized finding CSV |
| `src/ansibleguard/report/text_writer.py` | Legacy and normalized human-readable reports |
| `src/ansibleguard/report/sarif_writer.py` | SARIF 2.1.0 conversion and stable fingerprints |
| `scripts/validate_detector_corpus.py` | Reproducible source-detector corpus baseline |
| `scripts/classify_study_files.py` | Generate per-project classification manifests from frozen study rows |

## Document classification

`inspect_document()` separates parseability from structural applicability.
This prevents variable files and metadata from being treated as playbooks while
still allowing content-only and safe source detectors to contribute findings.

The run summary distinguishes:

- YAML files discovered;
- files structurally analyzed;
- parse/read failures;
- GitLeaks and ansible-lint tool failures;
- code findings by severity.

Tool failures are written to `diagnostics.json`; they are not converted into
code findings.

Repository population classification is a separate layer owned by
`file_manifest.py`. It assigns every YAML candidate one controlled file class
and a reason. The collector derives aggregate counts from those same rows, so
the counted and scanned population cannot drift because of duplicated
classification implementations. `--file-manifest` requires complete path
coverage and scans only explicit inclusions.

## Execution profiles

Profile selection controls both rule output and stage execution. Source
profiles never call the Git review detector. `review-range` does not send YAML
through source detectors. External tools run only for profiles that request
them, including `technical-full`, `security`, `lint`, and `pr`.
Filtering happens before per-file/project normalized rollups are written, so
JSON, CSV, text, and SARIF contain the same profile population.

`profiles.py` validates that all catalog IDs are assigned exactly once among
research-core, extended-Ansible, review-range, or external-tool families.
`technical-full` is their union; `snapshot-source` is core plus extended.

## Detector families

### Legacy structural metrics

The original detectors measure playbook, play, and task properties such as LOC,
task counts, imports, roles, cohesion, duplicates, naming, `set_fact`, boolean
filters, file extensions, and credential logging. Their raw output is retained
in `Technical_Analysis.json` and evaluated by `smells.py`.

### Paper-derived candidates

`paper_candidates.py` shares one safe traversal for complex expressions,
unfinished markers, long statements, role structure, empty/missing
abstractions, nesting, role dependencies, and unguarded variables.

### Review checklist rules

`review_checklist.py` covers permissions, default credentials, idempotency,
silent error suppression, redundant defaults, shell exports, and missing
documentation for complex tasks.

### Strengthened partial rules

`partial_checklist.py` detects unused registered variables, unscoped shell
variables, invalid task attribute types, and invalid numeric values.

### Formerly missing checklist rules

`missing_checklist.py` detects linear variable use before a later
`register`/`set_fact`, objectively misplaced role content, and deprecated
module options from installed Ansible metadata plus project overrides.

### Legacy candidate modules with exact locations

Missing tags, deprecated modules, disabled certificate validation,
shell/module alternatives, and handler issues use the shared ruamel coordinate
helper. Missing and unused handlers report the notify or handler definition
line, respectively.

### Git review metadata

`review_metadata.py` finds the repository root and evaluates seven project
rules. When `ANSIBLEGUARD_BASE_SHA` and `ANSIBLEGUARD_HEAD_SHA` are valid:

- changed files come from `base...head`;
- every commit message in `base..head` is checked;
- copyright headers are compared at the committed base and head revisions;
- test, override-test, and release-note coverage use the complete changed set.

Local runs fall back to the head commit and its parent.

## Configuration flow

The nearest `.ansibleguard.yml` is merged over built-in defaults. New detector
thresholds read directly from this configuration. Legacy thresholds start with
`src/ansibleguard/thresholds.csv` and accept same-name overrides from the YAML
file. The configuration also controls default credential values, additional
mutating-command patterns, known runtime variables, deprecated module-option
overrides, and disabled rule IDs.

Finding suppressions happen after normalization and before project formats are
written. This keeps JSON, CSV, text, and SARIF aligned without deleting raw
measurement evidence.

## Output architecture

There are three views of the same analysis:

1. Raw and legacy per-file metrics for detector debugging and compatibility.
2. `summary.csv` for project triage.
3. A normalized finding list rendered as JSON, CSV, text, and SARIF.

Every normalized record contains `file`, `line`, `rule_id`, `severity`, and
`message`. `RULE_CATALOG` is the authority for stable IDs and severity.
Project-only Git review rules enter the same normalized list and also retain
their full raw detail in `review_metrics.json`.

## Source locations

Task-level detectors use ruamel's round-trip node coordinates where exact YAML
locations are required. External findings retain the location reported by
GitLeaks or ansible-lint. Genuinely file-wide rules use line 1 because no single
task is the correct location.

SARIF paths are converted relative to the scan root so GitHub can associate
results with pull-request files.

## Failure and exit behavior

`--fail-on` supports:

- `never` — always return success;
- `error` — fail when an error-severity finding exists;
- `warning` — fail on warning or error findings;
- `tool-error` — fail when an external tool does not complete;
- `parse-error` — fail when YAML parsing or reading fails.

Invalid/non-playbook documents do not crash the scan. Ansible-lint resolves its
executable next to the running virtual-environment Python before checking PATH
and uses a writable temporary Ansible directory.

## Verification matrix

| Concern | Primary tests |
|---|---|
| Package/import smoke | `test_00_smoke.py` |
| Discovery and output paths | `test_cli.py` |
| Parse/tool status separation | `test_cli_statuses.py`, `test_document_classification.py` |
| Output parity | `test_output_contract.py`, `test_sarif_writer.py` |
| Configuration and suppressions | `test_detector_config.py` |
| Exact legacy source lines | `test_legacy_detector_lines.py` |
| Complete PR range | `test_review_metadata.py` |
| External wrappers | `test_ansible_lint.py`, `test_gitleaks_hardcoded_credentials.py` |
| Rule normalization/catalog | `test_findings.py` |
| Internal detectors | Remaining detector-specific test modules |
| Formerly missing checklist criteria | `test_missing_checklist.py` |
| OpenStack study pipeline | `test_study_scripts.py` |

Current complete suite:

```text
153 passed
```

## Reproducible verification

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m spacy download en_core_web_lg
python -c "import nltk; nltk.download('wordnet')"
ansibleguard install-tools
pytest -q
python scripts/validate_detector_corpus.py TestData/projects
```

The most recent clean temporary-environment check installed the package,
resolved ansible-lint 26.6.0 beside the environment's Python, displayed the CLI
help, and returned three structured findings for the issue fixture.

## Current engineering priorities

The implementation is stable enough for review and CI. The next quality step is
a labeled external corpus, followed by precision/recall measurement and
threshold/severity calibration. Cross-file resolution for dynamic inventory,
external collections, and runtime includes remains necessarily partial.
