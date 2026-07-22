# AnsibleGuard

New contributors and project reviewers should begin with
[START_HERE.md](START_HERE.md). It gives the required reading order, current
research status, reproduction commands, and next implementation tickets.

AnsibleGuard is a static-analysis CLI for Ansible configuration code. It scans
a playbook or an entire repository, combines 58 internal rules with GitLeaks
and ansible-lint, and emits one normalized set of findings in JSON, CSV, text,
and SARIF.

The current implementation contains **60 active finding rules**, preserves
findings from invalid or non-playbook YAML where applicable, reports precise
source lines for task-level rules, and includes Git-aware checks for complete
pull-request ranges.

## Capabilities

- Recursively discovers `.yml` and `.yaml` files while excluding generated,
  virtual-environment, Molecule, and Git metadata directories.
- Generates auditable row-level file classifications and can restrict research
  scans to a complete, validated `included=true` manifest population.
- Classifies playbooks, task files, variable/default files, metadata, empty
  documents, inline Vault values, encrypted Vault files, and invalid YAML.
- Detects structural, maintainability, security, idempotency, variable,
  handler, role-layout, type/value, documentation, and review-process smells.
- Runs GitLeaks once for the complete target and retains non-YAML secret
  findings.
- Runs ansible-lint and distinguishes a clean result from a missing or failed
  tool.
- Produces GitHub-compatible SARIF with repository-relative paths and stable
  fingerprints.
- Evaluates Git review checks across `base...head`, including every commit in a
  pull request.
- Supports project-level threshold overrides, detector options, known runtime
  variables, and rule suppressions through `.ansibleguard.yml`.

The canonical rule inventory is [ALL_DETECTED_SMELLS.md](ALL_DETECTED_SMELLS.md).
The comparison with the 38-criterion research checklist is in
[CODE_REVIEW_CHECKLIST_COVERAGE.md](CODE_REVIEW_CHECKLIST_COVERAGE.md).

For slow, beginner-friendly explanations and current implementation audits,
use:

- [ULTIMATE_SMELL_CATALOG.md](ULTIMATE_SMELL_CATALOG.md) for every rule's
  purpose, algorithm, mathematics, complexity, inspiration, and checklist
  status;
- [REAL_REPOSITORY_TESTING_ZERO_TO_HERO.md](REAL_REPOSITORY_TESTING_ZERO_TO_HERO.md)
  for the complete real-repository workflow;
- [SANER24_PAPER_AND_ANSIBLEGUARD_APPROACH.md](SANER24_PAPER_AND_ANSIBLEGUARD_APPROACH.md)
  for the Puppet-paper method and the exact relationship to this project;
- [ANSIBLE_LINT_GITLEAKS_OVERLAP.md](ANSIBLE_LINT_GITLEAKS_OVERLAP.md) for
  external-tool capabilities, overlap, and remaining integration gaps.

## Requirements

- Python 3.10 or newer
- Git, for review-range checks
- Internet access during the initial dependency/model/tool installation
- A supported Linux, macOS, or Windows Python environment

The semantic-cohesion detectors use spaCy's `en_core_web_lg` model and NLTK
WordNet data. GitLeaks is installed separately by the CLI. ansible-lint is a
normal Python package dependency.

## Installation

```bash
git clone https://github.com/Narjes-b/AnsibleChecklist.git
cd AnsibleChecklist
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m spacy download en_core_web_lg
python -c "import nltk; nltk.download('wordnet')"
ansibleguard install-tools
```

The package installs an `ansibleguard` command that can be run from any
directory. Tool installation is explicit; importing the package does not
download binaries.

## Usage

Scan a repository recursively:

```bash
ansibleguard /path/to/ansible-project
```

Scan one file and choose the output directory:

```bash
ansibleguard playbook.yml --output ./analysis-results
```

Scan only the explicitly included files in a complete classification manifest:

```bash
ansibleguard /path/to/ansible-project \
  --file-manifest /path/to/project-files.csv \
  --output ./classified-results
```

Manifest mode rejects missing/stale rows, unsafe paths, duplicate paths,
unknown classes, and unexplained exclusions before analysis starts. The output
records the exact manifest hash in `file_selection.json`.

Separate technical, snapshot, core, extended, and review questions:

```bash
ansibleguard /path/to/ansible-project --profile technical-full
ansibleguard /path/to/ansible-project --profile review-range

ansibleguard /path/to/ansible-project \
  --file-manifest /path/to/project-files.csv \
  --profile snapshot-source
```

Research profiles do not run aggregate external tools. Snapshot profiles do
not run Git review rules. The exact allowlist and hash are written to
`run_metadata.json`; `research-core` remains provisional pending calibration.
The three source research profiles require `--file-manifest`; the CLI rejects
recursive source selection for those profiles.

Control the exit policy:

```bash
ansibleguard . --fail-on error
ansibleguard . --fail-on warning
ansibleguard . --fail-on tool-error
ansibleguard . --fail-on parse-error
ansibleguard . --fail-on never
```

Available options:

```text
usage: ansibleguard [-h] [--gitleaks-path PATH]
                    [--fail-on {never,error,warning,tool-error,parse-error}]
                    [-o OUTPUT] [--file-manifest FILE_MANIFEST]
                    [--profile {technical-full,snapshot-source,research-core,extended-ansible,review-range}]
                    target
```

The default output directory is `./ansibleguard-output` and the default failure
policy is `error`.

## Configuration

Copy the example file into the root of the project being scanned:

```bash
cp .ansibleguard.example.yml .ansibleguard.yml
```

AnsibleGuard searches from each analyzed path toward the filesystem root and
uses the nearest `.ansibleguard.yml`. The configuration can:

- override any legacy `thresholds.csv` value;
- adjust complex-expression, long-line, nesting, and abstraction thresholds;
- define project-specific default credential values;
- add regular expressions for mutating commands;
- declare variables supplied by inventory plugins, CI, or `--extra-vars`;
- supplement installed Ansible metadata with project option deprecations;
- disable findings by stable rule ID.

Example:

```yaml
thresholds:
  LOC_playbook: 150
  long_statement_length: 140

rules:
  default_credentials: [admin, changeme, company-default]
  additional_mutating_command_patterns:
    - '\bcustomctl\s+apply\b'
  known_variables:
    - deployment_environment
  deprecated_module_options:
    ansible.builtin.example:
      old_option:
        replacement: new_option
        removed_in: "3.0"

suppressions:
  disabled_rules:
    - long-statement
```

Suppressions are applied to the normalized finding list before JSON, CSV,
text, and SARIF are written, keeping those formats consistent. Raw technical
metrics remain available for auditability.

## Detection coverage

The 60 rules are grouped into the following areas:

| Area | Examples |
|---|---|
| Size and complexity | large playbook/play/task, complex expressions, excessive nesting, long statements |
| Modularity and structure | high coupling, missing/empty abstractions, unstructured roles, broken dependencies |
| Naming and cohesion | unnamed plays/tasks, duplicated names, naming punctuation, NLP cohesion |
| Variables and defaults | unguarded variables, unused registered variables, redundant defaults, overriding facts |
| Security | hardcoded/default credentials, credential logging, insecure permissions, disabled TLS validation |
| Reliability | missing handlers, unused handlers, invalid task types, invalid numeric values, silent error suppression |
| Idempotency and modules | non-idempotent commands, shell alternatives, deprecated modules, file extensions |
| Ordering and compatibility | use-before-definition, misplaced role content, deprecated module options |
| Documentation and review | missing tags, unfinished markers, complex-task comments, release notes, bug references |
| External analysis | GitLeaks findings and ansible-lint issues |

For exact algorithms, severity, limitations, and stable IDs, use
[ALL_DETECTED_SMELLS.md](ALL_DETECTED_SMELLS.md) and
[inventory.md](inventory.md).

## Output contract

Every scan writes collision-safe per-file directories and project-wide
rollups:

```text
ansibleguard-output/
├── <mirrored/path/without-extension>/
│   ├── Technical_Analysis.json
│   ├── IaC_Smells.csv
│   ├── Play_Level_Analysis.txt
│   ├── ansiblelint.txt
│   └── gitleaks.txt
├── summary.csv
├── findings.json
├── findings.csv
├── findings.txt
├── findings.sarif
├── review_metrics.json
└── diagnostics.json
```

Normalized findings share this schema:

```json
{
  "file": "roles/web/tasks/main.yml",
  "line": 12,
  "rule_id": "default-credentials",
  "severity": "error",
  "message": "Credential 'password' uses the well-known default value 'admin'."
}
```

- `Technical_Analysis.json` contains raw per-file measurements and details.
- `IaC_Smells.csv` preserves the legacy one-row per-file metric view.
- `Play_Level_Analysis.txt` contains the legacy play/task view plus every
  normalized finding for that file.
- `summary.csv` ranks analyzed files by severity and finding count.
- `findings.json`, `findings.csv`, `findings.txt`, and `findings.sarif` represent
  the same normalized finding set.
- `review_metrics.json` retains raw project-level Git review counts/details.
- `diagnostics.json` records parse and external-tool failures separately from
  code findings.

See [OUTPUT_FORMATS.md](OUTPUT_FORMATS.md) for the complete contract.

## Pull-request analysis

Git-aware rules use these optional environment variables:

```bash
export ANSIBLEGUARD_BASE_SHA=<base-commit>
export ANSIBLEGUARD_HEAD_SHA=<head-commit>
ansibleguard . --output ansibleguard-output
```

When both revisions are valid, changed-file checks use `base...head` and commit
message checks inspect every commit in `base..head`. Without explicit values,
local analysis falls back to `HEAD^..HEAD` when a parent exists.

The included workflow at `.github/workflows/ansibleguard.yml` fetches complete
history, supplies pull-request SHAs, uploads SARIF to GitHub Code Scanning, and
publishes the reports as an artifact.

## Development and verification

Run the full suite:

```bash
.venv/bin/pytest -q
```

Current verified result: **153 passed**.

Run the reproducible detector-corpus baseline:

```bash
.venv/bin/python scripts/validate_detector_corpus.py TestData/projects
```

The current bundled corpus contains 56 discovered YAML files. Results and the
false-positive tuning performed from that run are recorded in
[CORPUS_VALIDATION.md](CORPUS_VALIDATION.md).

## Project structure

```text
.
├── .ansibleguard.example.yml
├── .github/workflows/ansibleguard.yml
├── pyproject.toml
├── scripts/validate_detector_corpus.py
├── src/ansibleguard/
│   ├── cli.py
│   ├── config.py
│   ├── detector_config.py
│   ├── document.py
│   ├── parser.py
│   ├── smells.py
│   ├── thresholds.csv
│   ├── detectors/
│   ├── external/
│   └── report/
└── tests/
```

## Current limitations and next work

- The bundled corpus is not labeled with ground truth, so its results support
  candidate-rate and manual-sample validation but not an honest precision or
  recall percentage.
- Fifteen of the paper's 38 checklist criteria are direct matches, eighteen are
  partially automated, and five still require information or reviewer intent
  that is not reliably observable by static analysis.
- Cross-file and runtime variable resolution is necessarily incomplete when
  values arrive through dynamic inventory, external secret stores, CI, or
  command-line extra variables. `known_variables` provides an explicit project
  escape hatch.
- Handler and role resolution is strongest for visible local files; dynamically
  loaded collections or runtime includes can require project-specific review.
- Threshold and severity calibration still needs a larger labeled corpus.
- Some older internal identifiers retain historical spelling, although public
  rule IDs and output schemas are stable.

## Documentation

| Document | Purpose |
|---|---|
| [START_HERE.md](START_HERE.md) | Required first read: ordered documentation map, current state, reproduction, and continuation |
| [ALL_DETECTED_SMELLS.md](ALL_DETECTED_SMELLS.md) | Canonical live rule catalog |
| [inventory.md](inventory.md) | Detailed detection strategies and false-positive risks |
| [CODE_REVIEW_CHECKLIST_COVERAGE.md](CODE_REVIEW_CHECKLIST_COVERAGE.md) | Mapping to all 38 research criteria |
| [HOW_IT_WORKS.md](HOW_IT_WORKS.md) | Detector and pipeline walkthrough |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Package architecture and verification guide |
| [OUTPUT_FORMATS.md](OUTPUT_FORMATS.md) | Report schemas and intended consumers |
| [CORPUS_VALIDATION.md](CORPUS_VALIDATION.md) | Reproducible corpus baseline and tuning results |
| [SEVEN_PRIORITY_IMPLEMENTATION.md](SEVEN_PRIORITY_IMPLEMENTATION.md) | Latest hardening implementation record |
| [SESSION_IMPLEMENTATION_REPORT.md](SESSION_IMPLEMENTATION_REPORT.md) | First-person professional session summary |
| [PAPER_SMELLS_IMPLEMENTATION.md](PAPER_SMELLS_IMPLEMENTATION.md) | Paper-derived detector implementation |
| [REVIEW_CHECKLIST_IMPLEMENTATION.md](REVIEW_CHECKLIST_IMPLEMENTATION.md) | Review-checklist detector implementation |
| [PARTIAL_AND_REVIEW_METADATA_IMPLEMENTATION.md](PARTIAL_AND_REVIEW_METADATA_IMPLEMENTATION.md) | Partial and Git-aware checks |
| [MISSING_CHECKLIST_IMPLEMENTATION.md](MISSING_CHECKLIST_IMPLEMENTATION.md) | Three formerly missing checklist checks |
| [CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md](CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md) | Auditable file classification, manifest validation, CLI selection, and real Nova evidence |
| [WHAT_IS_A_SNAPSHOT_STUDY.md](WHAT_IS_A_SNAPSHOT_STUDY.md) | Boundary between a frozen source state and review/history evidence |
| [RESEARCH_PROFILES_IMPLEMENTATION.md](RESEARCH_PROFILES_IMPLEMENTATION.md) | Explicit profile allowlists, execution separation, metadata, and Nova results |
| [OPENSTACK_ANSIBLE_REAL_PROJECT_TESTING_PLAN.md](OPENSTACK_ANSIBLE_REAL_PROJECT_TESTING_PLAN.md) | Full empirical-study methodology |
| [LOCAL_OPENSTACK_STUDY_WORKFLOW.md](LOCAL_OPENSTACK_STUDY_WORKFLOW.md) | Exact local discovery, collection, pilot, and pre-PR commands |
| [RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md](RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md) | Why scaling is gated and how files/rules/findings become research evidence |
| [STUDY_SCRIPTS_REFERENCE.md](STUDY_SCRIPTS_REFERENCE.md) | Complete behavior, rationale, schemas, commands, and limits for study scripts |
| [PARSING_GITHUB_IMPLEMENTATION.md](PARSING_GITHUB_IMPLEMENTATION.md) | Historical parsing/GitHub implementation log |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Historical detector debugging log plus current status |
| [CLI_STATUS.md](CLI_STATUS.md) | Historical CLI implementation log plus current status |

## License

No license file is currently included in the repository. Add one before
redistributing the project outside the terms agreed by its contributors.
