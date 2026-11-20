# AnsibleGuard

AnsibleGuard is a static-analysis CLI for Ansible configuration code. It scans
a playbook or an entire repository, combines its internal rules with GitLeaks
and ansible-lint, and emits one normalized, deduplicated set of findings in
JSON, CSV, text, and SARIF. It also runs in pull-request mode, comparing a base
and head revision and reporting introduced, fixed, and moved findings.

<p align="center">
  <a href="docs/demo/ansibleguard-demo.mp4"><img src="docs/demo/demo-poster.jpg" alt="AnsibleGuard tool demonstration (4:38)" width="760"></a>
</p>

<p align="center">
  <a href="docs/demo/ansibleguard-demo.mp4"><b>▶ Demo video (4:38)</b></a> ·
  <a href="docs/demo/README.md">What the demo shows and how to reproduce it</a> ·
  <a href="docs/README.md">Documentation</a> ·
  <a href="CHANGELOG.md">Changelog</a>
</p>

**Version:** 0.0.7.1 — 76 catalog rules (see
[RULE_REFERENCE.generated.md](RULE_REFERENCE.generated.md)).

**Research status.** The v0.0.7 study scanned a frozen population of 207
GitHub repositories (run `v007-full-repro-2026`; 390,286 raw findings and
376,115 canonical occurrences; 171 complete, 35 ansible-lint-partial, 1
timeout). Those counts describe detector output, not confirmed defects. Human
validation is in the calibration-pilot stage on a 144/62 calibration/heldout
repository split; no v0.0.7 precision or recall estimate exists yet. Earlier
estimates (for example the v0.0.3 calibration corpus) belong to their own
versions and are recorded in [CHANGELOG.md](CHANGELOG.md).

Start with [docs/README.md](docs/README.md) for the documentation map.
The [ICPC 2027 readiness record](docs/study/icpc2027-tool-readiness-2026-11-10.md)
tracks development changes and reproduction commands. Local inference now works;
the [development results](study/icpc2027-development-2026-11-10/README.md) distinguish
backend decision checks from model explanation failures. Human review remains
pending. These changes do not establish new accuracy results.

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
- Materializes local, GitHub, and GitLab sources through one provider-neutral
  snapshot contract, resolves remote refs to immutable SHAs, and records a
  deterministic source-tree fingerprint.
- Supports GitHub base/head and fork pull-request comparison through the same
  canonical comparison/SARIF pipeline used by local diff mode.
- Provides secure filesystem caching by default and optional Redis metadata,
  locks, and job state without storing repository blobs in Redis.

The canonical rule inventory is [ALL_DETECTED_SMELLS.md](docs/rules/detected-smells.md).
The comparison with the 38-criterion research checklist is in
[docs/research/checklist-coverage.md](docs/research/checklist-coverage.md).
The PR annotation implementation and developer workflow are in
PR_ANNOTATIONS_IMPLEMENTATION_AND_USE.md.

For slow, beginner-friendly explanations and current implementation audits,
use:

- [ULTIMATE_SMELL_CATALOG.md](docs/rules/smell-catalog.md) for every rule's
  purpose, algorithm, mathematics, complexity, inspiration, and checklist
  status;
- REAL_REPOSITORY_TESTING_ZERO_TO_HERO.md
  for the complete real-repository workflow;
- [SANER24_PAPER_AND_ANSIBLEGUARD_APPROACH.md](docs/research/saner24-approach.md)
  for the Puppet-paper method and the exact relationship to this project;
- [ANSIBLE_LINT_GITLEAKS_OVERLAP.md](docs/rules/external-tool-overlap.md) for
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

Compare a working branch or exactly the staged commit with its base:

```bash
ansibleguard diff . --base origin/main
ansibleguard diff . --staged
```

Analyze GitHub repositories, immutable revisions, comparisons, and pull
requests:

```bash
ansibleguard github owner/repo
ansibleguard github owner/repo --ref develop
ansibleguard github owner/repo --commit abc123
ansibleguard github-diff owner/repo --base main --head feature/security
ansibleguard github-pr owner/repo 42
ansibleguard github-pr owner/repo 42 --comment
```

`technical-full` uses temporary Git acquisition because its review rules need
history. Source-only profiles use a bounded secure archive by default. Remote
refs, tags, and abbreviated commits are always resolved to a full SHA before
acquisition. Set `GITHUB_TOKEN` or `GH_TOKEN` for private repositories; the CLI
falls back to `gh auth token` and then anonymous access. GitHub Enterprise uses
`--github-host`.

Analyze GitLab or a self-managed GitLab instance through the same analyzer:

```bash
ansibleguard gitlab group/project --ref develop
ansibleguard gitlab group/project --commit abc123
ansibleguard gitlab group/project --gitlab-host gitlab.company.example
```

GitLab authentication checks `GITLAB_TOKEN`, then `GL_TOKEN`, then
`glab auth token`. Credentials are passed only in request/process environment
headers and are not written into URLs, Git configuration, findings, SARIF, or
run metadata.

Remote commands use the permission-restricted filesystem cache by default:

```bash
ansibleguard cache info
ansibleguard cache clean --older-than 30
ansibleguard github owner/repo --no-cache

ANSIBLEGUARD_REDIS_URL=redis://localhost:6379/0 \
  ansibleguard github owner/repo --cache-backend redis
```

Redis contains only cache metadata/locks and optional API job state. Repository
trees remain in the filesystem cache (or a future object-store adapter). See
[REMOTE_SOURCE_ARCHITECTURE.md](docs/remote-sources.md) for acquisition,
submodule/LFS, cache, API, provenance, and equivalence contracts.

Diff mode reports introduced/fixed findings, changed-line context, affected
playbooks, and introduced-only SARIF. See
[docs/commands-and-pr-guide.md](docs/commands-and-pr-guide.md).

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
ansibleguard /path/to/ansible-project --profile developer-fast
ansibleguard /path/to/ansible-project --profile security
ansibleguard /path/to/ansible-project --profile lint
ansibleguard /path/to/ansible-project --profile quality
ansibleguard /path/to/ansible-project --profile pr
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
ansibleguard . --fail-on analysis-error
ansibleguard . --fail-on never
```

Available options:

```text
usage: ansibleguard [-h] [--gitleaks-path PATH]
                    [--fail-on {never,error,warning,tool-error,parse-error,analysis-error}]
                    [-o OUTPUT] [--file-manifest FILE_MANIFEST]
                    [--profile {technical-full,developer-fast,security,lint,quality,pr,snapshot-source,research-core,extended-ansible,review-range}]
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

Every effective configuration is validated before analysis. Invalid YAML,
unknown keys/rule IDs, incorrect types, misspelled thresholds, and invalid
regular expressions stop the scan with exit code 2 instead of silently using
defaults.

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

The 76 rules are grouped into the following areas:

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
[docs/rules/detected-smells.md](docs/rules/detected-smells.md) and
[RULE_REFERENCE.generated.md](RULE_REFERENCE.generated.md).

## Output contract

Every scan writes collision-safe per-file directories and project-wide
rollups:

```text
ansibleguard-output/
├── summary/
│   ├── report.json
│   ├── run-summary.md
│   ├── summary.csv
│   └── diagnostics.json
├── raw/
│   ├── findings.json
│   ├── suppressed-external-findings.json
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
├── files/
│   └── <mirrored/path/including-file.yml>/
│       ├── report.json
│       ├── findings.json
│       ├── occurrences.json
│       ├── diagnostics.json
│       └── metrics.json
├── diff/                         # after `ansibleguard diff`
│   ├── comparison.json
│   ├── introduced.json
│   ├── introduced-actionable.json
│   ├── fixed.json
│   ├── playbooks.json
│   ├── introduced.sarif
│   ├── introduced-actionable.sarif
│   └── summary.md
├── <mirrored/path/without-extension>/
│   ├── Technical_Analysis.json
│   ├── IaC_Smells.csv
│   ├── Play_Level_Analysis.txt
│   ├── ansiblelint.txt
│   └── gitleaks.txt
├── summary.csv
├── findings.json
├── findings.raw.json
├── occurrences.json
├── findings.csv
├── findings.txt
├── findings.sarif
├── review_metrics.json
└── diagnostics.json
```

Use `files/` for new per-file integrations and `diff/` for PR/commit
integrations. The older mirrored CSV/text layout remains a 0.0.1 compatibility
surface.

The PR bundle deliberately keeps two views. `introduced.json` and
`introduced.sarif` retain all evidence, including optional style policy.
`introduced-actionable.json` and `introduced-actionable.sarif` contain the
risk-first developer view used for GitHub inline reporting. Optional findings
remain visible in the collapsed section of `diff/summary.md`.

Normalized findings share this schema:

```json
{
  "file": "roles/web/tasks/main.yml",
  "line": 12,
  "rule_id": "default-credentials",
  "severity": "error",
  "confidence": "medium",
  "message": "Credential 'password' uses the well-known default value 'admin'.",
  "remediation": "Replace the default credential, rotate it if deployed, and retrieve the replacement from a protected source."
}
```

- `Technical_Analysis.json` contains raw per-file measurements and details.
- `IaC_Smells.csv` preserves the legacy one-row per-file metric view.
- `Play_Level_Analysis.txt` contains the legacy play/task view plus every
  normalized finding for that file.
- `summary.csv` ranks analyzed files by severity and finding count.
- `summary/run-summary.md` presents scan completeness, provider status,
  versions, and raw/canonical/suppressed totals before findings.
- `findings.json` and `findings.raw.json` preserve every normalized provider
  result. `occurrences.json` groups overlapping detectors without deleting
  their evidence, and SARIF uses those canonical occurrences.
- `findings.csv` and `findings.txt` retain provider, native-rule, and shared
  concept identity.
- `review_metrics.json` retains raw project-level Git review counts/details.
- `diagnostics.json` records parse and external-tool failures separately from
  code findings.
- `raw/suppressed-external-findings.json` preserves redacted GitLeaks findings
  removed by built-in noise policy, including the exact suppression reason and
  policy version.

See [docs/output-formats.md](docs/output-formats.md) for the complete contract.

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
history, scans the exact pull-request head SHA, compares it with the base SHA,
publishes category-first annotations and a job summary, uploads actionable
SARIF to GitHub Code Scanning, and preserves the complete evidence bundle as an
artifact.

## Development and verification

Run the full suite:

```bash
.venv/bin/pytest -q
```

Current verified result: **498 passed**.

Run the reproducible detector-corpus baseline:

```bash
.venv/bin/python scripts/validate_detector_corpus.py TestData/projects
```

The current bundled corpus contains 56 discovered YAML files. Results and the
false-positive tuning performed from that run are recorded in
CORPUS_VALIDATION.md.

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

## Current limitations

- Git review-history rules (`missing-release-note`, `missing-test-update`,
  `untested-override-change`) need a real base revision. On a parentless
  (shallow) snapshot they must not treat the whole repository as the change;
  see [docs/study/v007-audit-2026-10-15.md](docs/study/v007-audit-2026-10-15.md).
- A repository symbol index resolves visible defaults/vars, inventory files,
  play/task vars, facts, registers, loop variables, and static vars includes.
  Dynamic inventory, external secret stores, runtime includes, CI, and
  command-line extra variables remain incomplete; `known_variables` is the
  explicit project escape hatch.
- Handler and role resolution is strongest for visible local files; dynamically
  loaded collections or runtime includes can require project-specific review.
- Fifteen of the paper's 38 checklist criteria are direct matches, eighteen are
  partially automated, and five need reviewer intent that static analysis
  cannot observe.
- ansible-lint loads repository plugins/modules while linting; scan untrusted
  repositories in an isolated environment (see `Dockerfile.research`).

## Documentation

The full map is [docs/README.md](docs/README.md). The most used entries:

| Document | Purpose |
|---|---|
| [docs/how-it-works.md](docs/how-it-works.md) | Pipeline walkthrough from discovery to reports |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Package boundaries, call flow, verification |
| [docs/pr-scan.md](docs/pr-scan.md) | How the pull-request scan works |
| [docs/commands-and-pr-guide.md](docs/commands-and-pr-guide.md) | Install, scan, profile, study, and PR commands |
| [docs/output-formats.md](docs/output-formats.md) | Output layers, schemas, SARIF, severities |
| [RULE_REFERENCE.generated.md](RULE_REFERENCE.generated.md) | Generated rule inventory (CI rejects drift) |
| [PROFILE_REFERENCE.generated.md](PROFILE_REFERENCE.generated.md) | Generated profile membership and thresholds |
| [docs/study/v007-reproduce-full-run.md](docs/study/v007-reproduce-full-run.md) | Reproduce the v0.0.7 207-repository run |
| [study/validation-v007-human/README.md](study/validation-v007-human/README.md) | Current human-validation materials |
| [CHANGELOG.md](CHANGELOG.md) | Release history, newest first |
| [docs/study/verified-claims-v82.md](docs/study/verified-claims-v82.md) | Source-bound verified explanations, CLI option and internal evaluation |
| [study/exploratory-labels/local-llm/SETUP.md](study/exploratory-labels/local-llm/SETUP.md) | Optional local-LLM explanations (`--explain`) |

## Contributors

- Aymen Jedidi
- Ahmed Amine Essid ([@Daehkcarc-sys](https://github.com/Daehkcarc-sys))
- Narjes Bessghaier ([@Narjes-b](https://github.com/Narjes-b))

## License

No license file is currently included in the repository. Add one before
redistributing the project outside the terms agreed by its contributors.
