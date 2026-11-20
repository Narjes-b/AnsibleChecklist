# How AnsibleGuard works

This is the plain-language guide to the current analysis pipeline. For stable
rule IDs and exact limitations, see [detected-smells.md](rules/detected-smells.md) and
[RULE_REFERENCE.generated.md](../RULE_REFERENCE.generated.md).

## The analysis model

AnsibleGuard separates four questions that are easy to mix together:

1. Can the file be read and parsed as Ansible-aware YAML?
2. Is its document shape a playbook/task file that structural detectors can
   analyze?
3. What raw properties and source-level problems are present?
4. Which normalized findings should be reported after configuration and
   suppressions?

Keeping those questions separate is why variable files, Vault content, invalid
YAML, and external-tool failures no longer crash or silently erase unrelated
findings.

## Step 1: discover the target

The CLI accepts a file or directory. By default, directory scans recursively
collect `.yml` and `.yaml` files while skipping `.git`, `.github`, `.ansible`,
virtual environments, Molecule scenarios, and prior `ansibleguard-output`
directories.

Research scans may instead provide `--file-manifest`. The row-level classifier
first records every repository YAML candidate, its class, parse/document type,
LOC, inclusion decision, and reason. Before scanning, the CLI checks that the
manifest and current target contain exactly the same YAML paths and rejects
unsafe, duplicate, unexplained, missing, or stale rows. Only `included=true`
rows enter the YAML analysis loop.

Both modes write `file_selection.json`. Manifest mode includes the exact CSV's
SHA-256, class counts, included count, project, and commit identity.

## Step 1A: select the execution profile

Profiles answer different questions before findings are aggregated:

- `technical-full` runs all 66 rules, GitLeaks, ansible-lint, and Git review;
- `snapshot-source` runs 57 internal source rules and no review/external stage;
- `research-core` runs the provisional eight-rule primary allowlist;
- `extended-ansible` runs the 49 disjoint non-core source rules;
- `review-range` processes no source files and evaluates seven Git rules.

The three source research profiles require a complete classification manifest.
This makes it impossible to calculate findings over recursively discovered
YAML while dividing by a classified production-file denominator.

Every catalog rule belongs to one scientific family. Adding a rule without a
family fails profile validation. `run_metadata.json` records the exact allowed
IDs and a deterministic rule-list hash.

Per-file output mirrors the source path without the extension. This prevents
files such as `roles/web/tasks/main.yml` and `roles/db/tasks/main.yml` from
overwriting one another.

## Step 2: run content and lint tools

GitLeaks and ansible-lint run once against the requested target.

- GitLeaks scans content independently of YAML parsing. Results for YAML files
  are matched back to those files; results for `.env`, scripts, and other
  non-YAML files remain in project rollups.
- ansible-lint findings are matched by their reported path and preserve the
  tool's source line.
- A missing, crashing, or malformed tool result becomes a diagnostic, not a
  code smell.

In manifest-enabled `technical-full` mode, ansible-lint messages are retained
only when they match an included YAML path. GitLeaks continues its
repository-wide security scan so non-YAML secrets are not lost, but findings
attached to excluded YAML are not added to the rollup. Research profiles mark
external tools `not-requested`; source snapshot profiles leave
`review_metrics.json` empty.

The ansible-lint wrapper can find the console script beside the active virtual
environment's Python even when that directory is absent from PATH.

## Step 3: classify each YAML document

`document.inspect_document()` returns parse status, document type, structural
applicability, parsed content, and diagnostics. Important cases include:

- ordinary playbooks;
- task-only role files;
- variable/default mappings;
- metadata and other mappings;
- empty documents;
- inline Ansible Vault tags;
- fully encrypted Vault files;
- syntactically invalid YAML;
- read errors.

Only playbooks and task lists enter the complete structural parser. Safe
source, variable, and role-layout checks can still run for skipped document
types.

## Step 4: measure internal properties

`parser.mainn()` calls the detector modules and assembles one raw metrics
dictionary. The original detector family measures playbook/play/task LOC,
counts, names, imports, roles, duplicated structures, facts, conditions,
cohesion, file references, includes, and credential logging.

Newer detector bundles add source, security, reliability, type/value, and
variable checks. Most return both a count and a list of detail dictionaries.
Details carry the source line and evidence used to build the final message.

Task traversal consistently descends into `block`, `rescue`, and `always`.
Wrappers are containers; leaf tasks are the executable units being measured.

Before source analysis, a repository symbol index records definitions from
visible vars/defaults/inventory files, play/task vars, `set_fact`, registers,
loop variables, static includes, and configured runtime variables. Its
provenance hash is written to run metadata and used by the unguarded-variable
detector.

## Step 5: preserve exact YAML lines

PyYAML is suitable for ordinary semantic traversal but does not preserve exact
source coordinates and silently collapses duplicate keys. Detectors needing
locations use ruamel's round-trip parser.

That coordinate path currently covers duplicate keys, play/task naming and
size details, credential logging, missing tags, deprecated modules, disabled
TLS validation, shell/module alternatives, and handler definitions/notifies.

File-wide findings such as high coupling or missing release notes intentionally
use line 1 because the evidence describes the entire file or review range.

## Step 6: apply thresholds and detector configuration

Legacy size/cohesion rules start with `src/ansibleguard/thresholds.csv`. The
nearest `.ansibleguard.yml` may override those keys and the newer thresholds:

- complex-expression score and length;
- maximum statement length;
- maximum block nesting depth;
- task count requiring abstraction.

The same configuration supplies project-specific default credentials,
additional mutating-command regular expressions, and variables known to arrive
from outside visible YAML.

Most thresholds use strict greater-than comparison: a value equal to the limit
does not fire. Cohesion is the exception in direction: similarity below its
minimum is suspicious. When semantic similarity cannot be measured, the value
is `None`; it is not converted to a fake zero or perfect score.

## Step 7: analyze the Git review range

For Git repositories, seven checks inspect review metadata. In CI, the workflow
provides `ANSIBLEGUARD_BASE_SHA` and `ANSIBLEGUARD_HEAD_SHA`.

- Changed files are calculated over `base...head`.
- Commit formatting, bug references, and `Depends-On` trailers are evaluated
  for every commit in `base..head`.
- Test, override-test, and release-note checks use the complete changed-file
  set.
- Copyright headers compare file content committed at base and head.

Without explicit SHAs, a local run uses the current head and parent where
available.

## Step 8: normalize findings

`report.findings.build_findings_list()` converts detector details, thresholded
metrics, GitLeaks, ansible-lint, and project review metrics into one schema:

```json
{
  "file": "roles/web/tasks/main.yml",
  "line": 12,
  "rule_id": "missing-tags",
  "severity": "note",
  "message": "Task 'Configure web': Task has no tags."
}
```

`RULE_CATALOG` defines the 57 stable IDs, descriptions, categories, and default
severity. Project suppressions are applied by rule ID after normalization.

## Step 9: write every view

Per-file reports preserve backward compatibility:

- `Technical_Analysis.json` — raw metrics/details;
- `IaC_Smells.csv` — legacy metric summary;
- `Play_Level_Analysis.txt` — legacy play/task view plus normalized findings;
- `ansiblelint.txt` and `gitleaks.txt` — external-tool detail.

New per-file consumers should use
`files/<repository-relative-file.yml>/{report,findings,occurrences,diagnostics,metrics}.json`.
The legacy files above remain available during the 0.0.1 migration.

Project reports provide the consistent integration contract:

- `summary/report.json` — versioned entry point and artifact index;
- `summary/summary.csv` — triage with raw/canonical/provider counts;
- `raw/findings.json|csv|txt` — lossless provider evidence;
- `canonical/occurrences.json|csv|txt` — grouped developer-visible problems;
- `canonical/findings.sarif` — grouped GitHub Code Scanning results;
- `metadata/` — run, selection, and review provenance;
- `summary/diagnostics.json` — parse and tool failures.

Compatibility root aliases remain for one release. The organized documents
are produced from the same in-memory raw and canonical populations, and
end-to-end tests assert parity.

`ansibleguard diff` scans complete base and head snapshots, then combines
canonical comparison with the zero-context Git diff. It writes introduced,
fixed, moved, unchanged, and uncertain populations under `diff/`, groups their
effect by playbook and static role/include dependencies, and emits only
introduced occurrences to `diff/introduced.sarif`.

## Rule families

### Size, complexity, and cohesion

Large playbooks, plays, and tasks compare LOC/count metrics with configurable
limits. Complex playbooks combine size and coupling. Complex expressions score
operators and syntax. NLP cohesion compares task/play names when the configured
spaCy model has usable vectors.

### Structure and modularity

These rules detect imports/role coupling, insufficient or unnecessary
abstraction, empty nested sections, excessive nesting, unconventional role
entry points, and missing/cyclic/self-referential role dependencies.

### Naming and duplication

Rules cover unnamed plays/tasks, long names, punctuation-heavy names,
duplicated task names, duplicated task bodies, and duplicate YAML keys.

### Variables and defaults

Rules detect unused `set_fact` and registered variables, conflicting facts,
unused `include_vars`, redundant role-default assignments, unguarded variables,
shell variables that do not persist across tasks, and registered/fact values
used before a later task defines them.

The unguarded-variable rule loads visible play/task/role definitions plus
repository `group_vars` and `host_vars`, accepts `default`, `d`, and
`is defined` guards, and recognizes `ansible_*` facts. Dynamic inventory and
extra-vars remain outside static visibility and can be declared as known.

### Security and transport

Internal rules detect credentials exposed to logs, well-known default
credentials, insecure modes, and `validate_certs: false`. GitLeaks supplies
content-based hardcoded-secret detection across YAML and non-YAML files.

### Reliability and idempotency

Rules cover mutating commands without repeat-safe guards, shell commands with
native module alternatives, silent failure suppression, missing/unused
handlers, invalid attribute types, invalid numeric ranges, and deprecated or
short-name modules. Installed Ansible option metadata and project overrides
also identify deprecated module parameters.

### Role placement

Role files are checked for objective placement errors: task lists under
defaults/vars/meta, mappings under tasks/handlers, plays inside role
directories, and handler-only `listen` attributes under tasks.

### Documentation and review

Rules cover missing tags, unresolved TODO/FIXME/HACK/XXX markers, undocumented
complex tasks, release-note and test co-changes, bug references, dependency
trailers, commit formatting, copyright removal, and untested variable/default
overrides.

## Configuration versus suppression

Prefer configuring evidence the analyzer cannot see (known runtime variables,
project command patterns, project credential defaults) before suppressing a
rule. Suppression is appropriate when a stable rule is intentionally out of
scope for the whole project. Raw metrics are never deleted by suppression.

## Known boundaries

- Static analysis cannot prove developer intent or runtime behavior.
- Dynamic includes, external collections, secret stores, and inventory plugins
  can hide definitions and handlers.
- A co-changed test file does not prove meaningful semantic coverage.
- NLP cohesion is a soft maintainability signal, not a correctness result.
- Thresholds and severity need calibration against a larger labeled corpus.
- The 56-file bundled corpus is reproducible but not ground-truth labeled.

## Verification

The current full-suite count is recorded in `README.md`.
`test_output_contract.py`
locks JSON/CSV/text/SARIF parity, `test_review_metadata.py` locks multi-commit
PR behavior, `test_legacy_detector_lines.py` locks exact locations, and
`test_detector_config.py` locks thresholds/options/suppressions, and
`test_missing_checklist.py` covers the three newly automated criteria.

Run:

```bash
.venv/bin/pytest -q
.venv/bin/python scripts/validate_detector_corpus.py TestData/projects
```
