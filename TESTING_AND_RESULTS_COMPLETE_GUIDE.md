# Complete guide to AnsibleGuard testing, profiles, manifests, snapshots, and results

This document explains:

- how AnsibleGuard repository testing is run;
- how to choose an execution profile;
- how the five-repository OpenStack pilot was created;
- where manifests, repositories, snapshots, logs, findings, and validation
  results are stored;
- where `ansiblelint.txt` and `gitleaks.txt` appear;
- how to read project-wide and individual-file results;
- how unit tests differ from repository-analysis tests.

All paths in this guide are relative to:

```text
/home/aymmzn/Documents/AnsibleChecklist
```

## 1. The complete testing evidence chain

The reproducible repository-testing workflow is:

```text
candidate repositories
        ↓
reviewed pilot selection
        ↓
repositories cloned at exact commit SHAs
        ↓
frozen repository manifest
        ↓
one file-classification manifest per repository
        ↓
one selected AnsibleGuard profile
        ↓
project-wide and per-file findings
        ↓
logs, summaries, labels, and validation
```

A valid snapshot result is not just an output directory. It is the
combination:

```text
repository + exact commit SHA + file manifest + profile + configuration
```

This is what makes a run reproducible.

## 2. The five execution profiles

The profile definitions are implemented in:

[`src/ansibleguard/profiles.py`](src/ansibleguard/profiles.py)

| Profile | What it runs | External tools | Manifest required | Recommended use |
|---|---|---:|---:|---|
| `technical-full` | All internal rules, Git review rules, GitLeaks, and ansible-lint | Yes | No, but one can be supplied | Full technical inspection and external-tool comparison |
| `snapshot-source` | All internal source rules at one frozen repository state | No | Yes | Complete internal snapshot analysis |
| `research-core` | Conservative paper-derived internal rules | No | Yes | Primary empirical/research analysis |
| `extended-ansible` | Remaining Ansible-specific internal source rules | No | Yes | Secondary analysis outside the research core |
| `review-range` | Git/base-to-head review-process rules | No | No | Review-change analysis, not snapshot prevalence |

The relationship between the three source profiles is:

```text
snapshot-source = research-core + extended-ansible
```

`research-core` and `extended-ansible` are disjoint. A finding should not
belong to both.

### How to choose a profile

Use this decision guide:

```text
Do you need GitLeaks or ansible-lint findings?
├── Yes → technical-full
└── No
    ├── Do you need all internal source rules?
    │   └── Yes → snapshot-source
    ├── Do you need the conservative primary research rule set?
    │   └── Yes → research-core
    ├── Do you need the remaining Ansible-specific source rules?
    │   └── Yes → extended-ansible
    └── Are you studying commit/review changes?
        └── Yes → review-range
```

### Recommended choice by question

| Research or testing question | Profile |
|---|---|
| “What do all AnsibleGuard internal source detectors find at this commit?” | `snapshot-source` |
| “What findings belong in the conservative primary study?” | `research-core` |
| “What additional Ansible-specific findings exist?” | `extended-ansible` |
| “What problems are introduced across a Git change range?” | `review-range` |
| “What do AnsibleGuard, GitLeaks, and ansible-lint find together?” | `technical-full` |

Do not use `technical-full` findings as if every result were independently
detected by AnsibleGuard. Its `hardcoded-credentials` findings come from
GitLeaks, and its `ansible-lint-issue` findings come from ansible-lint.

For the detailed overlap explanation, see:

[`ANSIBLEGUARD_EXTERNAL_TOOL_OVERLAP.md`](ANSIBLEGUARD_EXTERNAL_TOOL_OVERLAP.md)

## 3. The principal storage map

```text
study/
├── manifests/                         # repository and file-selection manifests
│   └── file-classification/           # one complete YAML manifest per repository
├── repositories/openstack/            # cloned source repositories at frozen SHAs
├── analysis/
│   └── five-project-pilot/            # current five-project results
├── snapshots/                         # older/default snapshot-run output
├── logs/
│   └── five-project-pilot/            # execution logs for current pilot
├── labels/                             # manual labels and aggregate study summaries
└── cache/                              # discovery cache

validation/
├── ansible-role-apache/                # validation corpus
└── results/
    ├── baseline/                       # original corpus results
    └── mutated/                        # deliberately mutated corpus results

tests/                                  # automated Python test suite
results/                                # older/local CLI analysis output
test-output/                            # end-to-end test output
TestData/Results/                       # legacy test fixtures/results
```

## 4. Manifests

All study manifests are stored under:

[`study/manifests`](study/manifests)

### `candidates.csv`

Path:

[`study/manifests/candidates.csv`](study/manifests/candidates.csv)

Purpose:

- records repositories discovered as possible study candidates;
- supports human review before repositories enter the pilot;
- is not itself the frozen execution manifest.

### `pilot.csv`

Path:

[`study/manifests/pilot.csv`](study/manifests/pilot.csv)

Purpose:

- records the reviewed pilot selection;
- identifies repositories selected for collection;
- acts as input to the cloning/freezing script.

### `pilot-five-frozen.csv`

Path:

[`study/manifests/pilot-five-frozen.csv`](study/manifests/pilot-five-frozen.csv)

This is the principal frozen manifest for the current five-project pilot.

It records, for each repository:

- project name;
- OpenDev clone URL;
- local repository path;
- default branch;
- exact full commit SHA;
- commit date;
- collection timestamp;
- total commits;
- contributor count;
- YAML-file counts;
- production/test/other classifications;
- production Ansible lines of code;
- collection status and errors.

The five frozen repositories are:

| Project | Frozen commit |
|---|---|
| `openstack/openstack-ansible-os_nova` | `e06c7bceef3f7c365828116b7aadea6fc2d3e22b` |
| `openstack/openstack-ansible` | `b7c10cbcc04a06207c2344a312d4f612a0810939` |
| `openstack/kolla-ansible` | `9c41bdca79d4c7267beeece141909e679f70dea8` |
| `openstack/kayobe` | `9a6e4333b2aa2fbe8dc80a93cd5aa3e2f1872970` |
| `openstack/ansible-collection-kolla` | `785982d7c09dda3d8e46f6c9b09597ca14820497` |

### `pilot-frozen.csv`

Path:

[`study/manifests/pilot-frozen.csv`](study/manifests/pilot-frozen.csv)

This is an earlier frozen pilot manifest, primarily associated with the Nova
pilot work. For the current five-project analysis, use
`pilot-five-frozen.csv`.

### File-classification manifests

Directory:

[`study/manifests/file-classification`](study/manifests/file-classification)

There is one CSV for each repository and exact commit:

```text
<namespace>__<repository>__<full-commit-sha>.csv
```

For example:

```text
openstack__openstack-ansible-os_nova__
e06c7bceef3f7c365828116b7aadea6fc2d3e22b.csv
```

Each classification manifest inventories every YAML candidate in the
repository and records whether it is included in the production snapshot.

It distinguishes:

- production Ansible;
- tests;
- examples;
- CI/configuration YAML;
- release notes;
- invalid YAML;
- other excluded YAML.

The source research profiles process only rows whose `included` value is
`true`. Before scanning, AnsibleGuard validates that the manifest covers the
repository’s complete YAML population.

### Generate classification manifests

```bash
cd /home/aymmzn/Documents/AnsibleChecklist

.venv/bin/python scripts/classify_study_files.py \
  study/manifests/pilot-five-frozen.csv \
  --output-dir study/manifests/file-classification
```

The script verifies that each local repository’s current `HEAD` equals the
commit recorded in the frozen manifest.

## 5. Frozen repository source

The locally cloned repositories are stored under:

[`study/repositories/openstack`](study/repositories/openstack)

```text
study/repositories/openstack/
├── ansible-collection-kolla/
├── kayobe/
├── kolla-ansible/
├── openstack-ansible/
└── openstack-ansible-os_nova/
```

These directories contain the source code that was scanned.

The study runner refuses to scan a repository if:

```text
repository HEAD != commit SHA in pilot-five-frozen.csv
```

This prevents a later checkout or branch update from silently changing the
snapshot.

### Clone and freeze selected repositories

The collection command is:

```bash
cd /home/aymmzn/Documents/AnsibleChecklist

.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/pilot.csv \
  --repos-dir study/repositories \
  --output study/manifests/pilot-five-frozen.csv
```

This command changes local repository state and should only be rerun when a
new frozen study population is intentionally being created.

## 6. Current five-project results

The current principal repository-test results are stored in:

[`study/analysis/five-project-pilot`](study/analysis/five-project-pilot)

The organization is:

```text
study/analysis/five-project-pilot/
└── <project-with-/-replaced-by-__>/
    └── <full-commit-sha>/
        ├── snapshot-source/
        ├── research-core/
        ├── extended-ansible/
        └── review-range/
```

Example:

```text
study/analysis/five-project-pilot/
└── openstack__openstack-ansible-os_nova/
    └── e06c7bceef3f7c365828116b7aadea6fc2d3e22b/
        ├── snapshot-source/
        ├── research-core/
        ├── extended-ansible/
        └── review-range/
```

The four research/review profiles deliberately disable external tools. The
completed `technical-full` results are kept in the separate directory:

[`study/analysis/five-project-technical-full`](study/analysis/five-project-technical-full)

## 7. How the five-project profile tests are run

The reproducible runner is:

[`scripts/run_study_pilot.py`](scripts/run_study_pilot.py)

It:

1. reads repositories with `status=collected` from the frozen manifest;
2. verifies each repository’s exact `HEAD`;
3. finds the matching file-classification manifest;
4. creates a project/SHA/profile output directory;
5. runs AnsibleGuard with `--fail-on never`, ensuring reports are written;
6. writes stdout and stderr to a profile-specific log;
7. records profile and manifest provenance in the output.

### Run `snapshot-source`

```bash
cd /home/aymmzn/Documents/AnsibleChecklist

.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-five-frozen.csv \
  --file-manifests-dir study/manifests/file-classification \
  --profile snapshot-source \
  --output-root study/analysis/five-project-pilot \
  --logs-dir study/logs/five-project-pilot
```

### Run `research-core`

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-five-frozen.csv \
  --file-manifests-dir study/manifests/file-classification \
  --profile research-core \
  --output-root study/analysis/five-project-pilot \
  --logs-dir study/logs/five-project-pilot
```

### Run `extended-ansible`

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-five-frozen.csv \
  --file-manifests-dir study/manifests/file-classification \
  --profile extended-ansible \
  --output-root study/analysis/five-project-pilot \
  --logs-dir study/logs/five-project-pilot
```

### Run `review-range`

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-five-frozen.csv \
  --profile review-range \
  --output-root study/analysis/five-project-pilot \
  --logs-dir study/logs/five-project-pilot
```

### Resume without rerunning completed results

Add:

```text
--skip-existing
```

The runner checks the existing output’s manifest hash and profile identity
before skipping it. This prevents a result produced from one manifest/profile
from being mistaken for another.

## 8. Running `technical-full` with ansible-lint and GitLeaks

Use `technical-full` when the purpose is to include external-tool results.

To keep external-tool output separate from the research outputs:

```bash
cd /home/aymmzn/Documents/AnsibleChecklist

.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-five-frozen.csv \
  --file-manifests-dir study/manifests/file-classification \
  --profile technical-full \
  --output-root study/analysis/five-project-technical-full \
  --logs-dir study/logs/five-project-technical-full
```

Important runner behavior:

- nontechnical profiles are stored under `<SHA>/<profile>/`;
- `technical-full` is stored directly under `<SHA>/`, because it is the
  runner’s default/full output contract.

Its structure is therefore:

```text
study/analysis/five-project-technical-full/
└── <project>/
    └── <full-commit-sha>/
        ├── findings.json
        ├── summary.csv
        ├── run_metadata.json
        └── mirrored per-file directories
```

### Current completed `technical-full` run

The five-repository `technical-full` run completed on 2026-07-27. All five
`run_metadata.json` files report:

```text
profile.name = technical-full
tools.gitleaks = completed
tools.ansible_lint = completed
diagnostics = 0
```

| Repository | Included files | All findings | `ansible-lint-issue` | `hardcoded-credentials` |
|---|---:|---:|---:|---:|
| `openstack/ansible-collection-kolla` | 42 | 453 | 77 | 0 |
| `openstack/kayobe` | 342 | 6,339 | 2,626 | 0 |
| `openstack/kolla-ansible` | 1,228 | 8,222 | 425 | 1 |
| `openstack/openstack-ansible-os_nova` | 28 | 797 | 17 | 0 |
| `openstack/openstack-ansible` | 216 | 946 | 213 | 1 |

The corresponding logs are under:

[`study/logs/five-project-technical-full`](study/logs/five-project-technical-full)

## 9. Running AnsibleGuard directly

To analyze one file or repository without the study runner:

```bash
.venv/bin/ansibleguard <target> \
  --profile technical-full \
  --output <output-directory> \
  --fail-on never
```

For a manifest-locked source profile:

```bash
.venv/bin/ansibleguard <repository> \
  --file-manifest <classification-manifest.csv> \
  --profile research-core \
  --output <output-directory> \
  --fail-on never
```

The available command-line profiles are:

```text
technical-full
snapshot-source
research-core
extended-ansible
review-range
```

The default profile is `technical-full`. The default output directory for a
direct invocation is:

```text
ansibleguard-output/
```

## 10. Project-wide result files

At the root of every project/profile result, AnsibleGuard writes:

| File | Purpose | When to read it |
|---|---|---|
| `summary.csv` | One row per analyzed file, statuses and finding counts | Start here for file triage |
| `findings.csv` | All normalized findings in spreadsheet form | Best for filtering and manual review |
| `findings.json` | Canonical normalized finding list | Best for scripts and exact data |
| `findings.txt` | Human-readable normalized findings | Best for quick reading |
| `findings.sarif` | SARIF representation | GitHub Code Scanning or SARIF tools |
| `diagnostics.json` | Parse failures and external-tool failures | Check whether the run was healthy |
| `file_selection.json` | Manifest identity, hash, and selected-file counts | Verify the exact scanned population |
| `run_metadata.json` | Profile, rule hash, commit, config, tool statuses | Verify provenance |
| `review_metrics.json` | Git review-range metrics | Read for `review-range`; empty for source profiles |

### Recommended reading order

For each project/profile:

1. Open `run_metadata.json`.
2. Confirm the intended profile name.
3. Confirm the exact commit SHA.
4. Confirm the rule-list hash.
5. Confirm external-tool statuses.
6. Open `file_selection.json`.
7. Confirm the manifest path and SHA-256.
8. Confirm included and processed file counts.
9. Open `diagnostics.json`.
10. Ensure unexpected parse/tool failures are absent.
11. Open `summary.csv`.
12. Sort or filter by `total`, `errors`, or `warnings`.
13. Open `findings.csv` for detailed filtering.
14. Open an individual per-file directory for raw metrics.

### `summary.csv`

Its principal columns are:

| Column | Meaning |
|---|---|
| `file` | Repository-relative YAML path |
| `parse_status` | Whether YAML parsing succeeded |
| `document_type` | Tasks, playbook, variables, metadata, etc. |
| `structural_status` | Whether full structural analysis ran |
| `gitleaks_status` | `completed`, `not-requested`, or tool error |
| `ansible_lint_status` | `completed`, `not-requested`, or tool error |
| `errors` | Error-severity findings for the file |
| `warnings` | Warning-severity findings for the file |
| `notes` | Note-severity findings for the file |
| `total` | Total normalized findings for the file |

In `five-project-pilot`, the research-profile outputs record
`gitleaks_status=not-requested` and `ansible_lint_status=not-requested`. In
`five-project-technical-full`, both statuses are `completed`.

### `findings.csv` and `findings.json`

Each normalized finding contains at least:

```text
file
line
rule_id
severity
message
```

Example conceptual record:

```json
{
  "file": "tasks/main.yml",
  "line": 14,
  "rule_id": "long-statement",
  "severity": "note",
  "message": "Line has 132 characters (threshold 120)."
}
```

Use `findings.csv` for spreadsheet review and `findings.json` for scripts.

## 11. Individual file-result storage

AnsibleGuard mirrors each source file’s repository-relative path underneath
the profile result.

The source extension is removed and replaced by a directory.

Example:

```text
Source:
roles/kolla_user/tasks/main.yml

Result directory:
roles/kolla_user/tasks/main/
```

That result directory contains:

```text
Technical_Analysis.json
IaC_Smells.csv
Play_Level_Analysis.txt
ansiblelint.txt
gitleaks.txt
```

### Per-file result meanings

| File | Meaning |
|---|---|
| `Technical_Analysis.json` | Raw AnsibleGuard metrics and detector detail structures |
| `IaC_Smells.csv` | Legacy per-file metric/smell summary |
| `Play_Level_Analysis.txt` | Human-readable play/task analysis plus file findings |
| `ansiblelint.txt` | ansible-lint output assigned to this source file |
| `gitleaks.txt` | GitLeaks output assigned to this source file |

### File-by-file reading example

For:

```text
openstack/ansible-collection-kolla
roles/kolla_user/tasks/main.yml
research-core
```

read:

```text
study/analysis/five-project-pilot/
openstack__ansible-collection-kolla/
785982d7c09dda3d8e46f6c9b09597ca14820497/
research-core/
roles/kolla_user/tasks/main/
```

Then:

1. Open `Play_Level_Analysis.txt` for the readable explanation.
2. Open `Technical_Analysis.json` for raw detector metrics.
3. Open `IaC_Smells.csv` for the legacy summary.
4. Check `ansiblelint.txt`.
5. Check `gitleaks.txt`.
6. Cross-reference normalized findings in the profile-root `findings.csv`.

## 12. Where ansible-lint findings are stored

### Raw per-file output

Raw formatted ansible-lint output is written to:

```text
<project-output>/<mirrored-source-path>/ansiblelint.txt
```

Example:

[`study/analysis/five-project-pilot/openstack__ansible-collection-kolla/785982d7c09dda3d8e46f6c9b09597ca14820497/research-core/roles/kolla_user/tasks/main/ansiblelint.txt`](study/analysis/five-project-pilot/openstack__ansible-collection-kolla/785982d7c09dda3d8e46f6c9b09597ca14820497/research-core/roles/kolla_user/tasks/main/ansiblelint.txt)

### Normalized output

When ansible-lint runs, every ansible-lint finding is also converted into:

```text
rule_id = ansible-lint-issue
```

These normalized records appear in the project/profile:

- `findings.json`
- `findings.csv`
- `findings.txt`
- `findings.sarif`

The original ansible-lint rule, such as `name[missing]` or
`yaml[key-duplicates]`, is collapsed under the common
`ansible-lint-issue` rule in normalized results.

### Current research-profile status

The current five-project pilot has 5,568 `ansiblelint.txt` files because
per-file report files are created for the three source profiles:

```text
1,856 included files × 3 source profiles = 5,568 files
```

However, they contain only headings. They do not contain actual ansible-lint
findings because:

```text
snapshot-source  → external_tools=false
research-core    → external_tools=false
extended-ansible → external_tools=false
```

This is recorded in:

- `summary.csv`: `ansible_lint_status=not-requested`;
- `run_metadata.json`: `external_tools=false`;
- `run_metadata.json`: `ansible_lint=not-requested`.

### Existing examples with actual ansible-lint findings

Actual findings can currently be inspected in:

[`validation/results/mutated/handlers/main/ansiblelint.txt`](validation/results/mutated/handlers/main/ansiblelint.txt)

and older local output such as:

[`results/large-ansible/deploy/ansiblelint.txt`](results/large-ansible/deploy/ansiblelint.txt)

The validation example contains native findings such as:

```text
fqcn[action-core]
name[casing]
```

### Current five-project `technical-full` status

Actual ansible-lint findings for all five frozen repositories are now stored
under:

[`study/analysis/five-project-technical-full`](study/analysis/five-project-technical-full)

There are 3,358 normalized `ansible-lint-issue` findings across the five
completed runs. The raw findings are mirrored into each analyzed source
file’s `ansiblelint.txt`, while normalized versions appear in each project’s
`findings.json`, `findings.csv`, `findings.txt`, and `findings.sarif`.

For example:

[`study/analysis/five-project-technical-full/openstack__openstack-ansible-os_nova/e06c7bceef3f7c365828116b7aadea6fc2d3e22b/tasks/main/ansiblelint.txt`](study/analysis/five-project-technical-full/openstack__openstack-ansible-os_nova/e06c7bceef3f7c365828116b7aadea6fc2d3e22b/tasks/main/ansiblelint.txt)

## 13. Where GitLeaks findings are stored

GitLeaks follows the same two-level storage model.

Raw per-file formatted output:

```text
<project-output>/<mirrored-source-path>/gitleaks.txt
```

Normalized output:

```text
rule_id = hardcoded-credentials
```

in:

- `findings.json`
- `findings.csv`
- `findings.txt`
- `findings.sarif`

Repository-wide GitLeaks findings from non-YAML files are retained in the
project-wide normalized output even though those files do not enter the
Ansible YAML structural-analysis loop.

Like ansible-lint, GitLeaks is not requested by the research profiles. It
completed for all five current `technical-full` runs. Two normalized
`hardcoded-credentials` findings were produced: one in `kolla-ansible` and one
in `openstack-ansible`.

## 14. Logs

Current five-project logs are stored in:

[`study/logs/five-project-pilot`](study/logs/five-project-pilot)

The completed `technical-full` logs are stored separately in:

[`study/logs/five-project-technical-full`](study/logs/five-project-technical-full)

Naming structure:

```text
<project>__<first-12-SHA-characters>__<profile>.log
```

Example:

```text
openstack__openstack-ansible-os_nova__
e06c7bceef3f__research-core.log
```

Logs contain the scanner’s stdout and stderr. Use them to determine:

- which repository was processed;
- how many YAML files were selected;
- which files were processed;
- where output was written;
- whether parsing or a tool failed;
- where a failed study-run command stopped.

Project result files are the evidence; logs are the execution trace.

## 15. Snapshot storage

### Meaning of a snapshot

In this project, a snapshot means:

```text
one repository at one immutable commit
+ one complete file manifest
+ one profile and rule hash
+ one result set
```

It does not mean only a copied directory.

### Current five-project snapshots

For the current five-project study:

- frozen source is under `study/repositories/openstack/`;
- exact SHAs are in `study/manifests/pilot-five-frozen.csv`;
- exact file populations are in `study/manifests/file-classification/`;
- scan results are under `study/analysis/five-project-pilot/`.

Together, those locations form the snapshot evidence.

### Older `study/snapshots`

Directory:

[`study/snapshots`](study/snapshots)

This contains output from the earlier/default snapshot workflow, primarily
the Nova pilot. It is not the principal output root for the current
five-project run.

The current results should be read from:

```text
study/analysis/five-project-pilot/
```

## 16. Aggregate summaries and manual labels

Study summaries and human-review labels are under:

[`study/labels`](study/labels)

The fastest overall five-project summary is:

[`study/labels/five_project_pilot_summary.csv`](study/labels/five_project_pilot_summary.csv)

It reports per repository:

- commit SHA;
- manifest rows;
- included-file count;
- manifest SHA-256;
- `snapshot-source` finding count;
- `research-core` finding count;
- `extended-ansible` finding count;
- `review-range` finding count;
- diagnostics;
- source-partition check.

The current total row records:

```text
5,409 manifest rows
1,856 included production files
13,387 snapshot-source findings
1,250 research-core findings
12,137 extended-ansible findings
10 review-range findings
0 diagnostics
source partition check = pass
```

Other label files include:

- `five_project_core_spot_check_labels.csv`
- `nova_research_core_finding_labels.csv`
- `nova_research_core_negative_labels.csv`
- Nova calibration summaries

These files contain manual validation or aggregate interpretation. They are
not raw scanner output.

## 17. Older analysis directories

Under [`study/analysis`](study/analysis), several historical stages exist:

| Directory | Meaning |
|---|---|
| `five-project-pilot/` | Current five-project, four-profile pilot |
| `profiled-snapshots/` | Earlier Nova profile separation run |
| `calibrated-snapshots/` | Nova run after detector calibration |
| `standalone-role-fixed-snapshots/` | Nova run after standalone-role handling fixes |
| `classified-snapshots/` | Earlier classified-manifest Nova execution |

For current multi-repository results, start with `five-project-pilot/`.

For detector evolution and Nova calibration, compare the historical
directories.

## 18. Validation-corpus testing

The validation corpus is:

[`validation/ansible-role-apache`](validation/ansible-role-apache)

Results are stored in:

[`validation/results`](validation/results)

```text
validation/results/
├── baseline/
└── mutated/
```

### Baseline

[`validation/results/baseline`](validation/results/baseline)

Represents analysis of the baseline validation corpus.

### Mutated

[`validation/results/mutated`](validation/results/mutated)

Represents analysis after deliberate mutations were introduced to exercise
detectors.

Use this pair to check whether expected injected problems are detected and
whether the baseline remains comparatively clean.

Each result has project-wide normalized files and mirrored per-file result
directories, including real `ansiblelint.txt` files when the external tool
was run.

## 19. Automated Python unit and integration tests

The automated test source files are under:

[`tests`](tests)

Run the complete suite with:

```bash
cd /home/aymmzn/Documents/AnsibleChecklist
.venv/bin/pytest
```

Run selected profile/manifest/output tests with:

```bash
.venv/bin/pytest \
  tests/test_file_manifest.py \
  tests/test_profiles.py \
  tests/test_output_contract.py
```

### Where pytest results are stored

By default, pytest prints pass/fail results to the terminal. It does not write
a permanent human-readable test report.

It may create:

```text
.pytest_cache/
```

but this is a cache, not the authoritative study result.

To create a durable JUnit XML report:

```bash
.venv/bin/pytest --junitxml=test-output/pytest-results.xml
```

Then the permanent report is:

```text
test-output/pytest-results.xml
```

Do not confuse pytest pass/fail results with repository smell-analysis
findings. They answer different questions:

```text
pytest:
Does the AnsibleGuard software behave as expected?

repository scan:
What findings does AnsibleGuard report in a target repository?
```

## 20. Other local and legacy outputs

### `results/`

[`results`](results)

Contains older or manually generated CLI analysis output. It includes examples
where ansible-lint produced actual findings.

### `test-output/`

[`test-output`](test-output)

Contains generated end-to-end test output, including normalized project files.

### `TestData/Results/`

[`TestData/Results`](TestData/Results)

Contains legacy result fixtures such as:

- `IaC_Smells.csv`
- `Play_Level_Analysis.txt`
- `Technical_Analysis.json`
- `ansiblelint.txt`
- `gitleaks.txt`

These are useful for legacy behavior and fixtures, but they are not the
current five-project research output.

### `src/TestData/Results/`

[`src/TestData/Results`](src/TestData/Results)

Contains an additional legacy/package-oriented test-data location.

## 21. Useful commands for reading results

### List all project/profile result roots

```bash
find study/analysis/five-project-pilot \
  -mindepth 3 -maxdepth 3 -type d | sort
```

### List all project summaries

```bash
find study/analysis/five-project-pilot \
  -type f -name summary.csv | sort
```

### List all ansible-lint text files

```bash
find study/analysis/five-project-pilot \
  -type f -name ansiblelint.txt | sort
```

### Find actual ansible-lint issue lines

This excludes blank lines and heading-only lines:

```bash
rg -n \
  -g 'ansiblelint.txt' \
  -v '^$|^AnsibleLint analysis for playbook .*:$' \
  study/analysis/five-project-pilot
```

For the current research pilot, this produces no issue lines because
ansible-lint was not requested.

Search older and validation output with:

```bash
rg -n \
  -g 'ansiblelint.txt' \
  -v '^$|^AnsibleLint analysis for playbook .*:$' \
  validation/results results test-output
```

### Find normalized ansible-lint findings

```bash
rg -n '"rule_id": "ansible-lint-issue"' \
  study/analysis validation/results results test-output
```

### Find normalized GitLeaks findings

```bash
rg -n '"rule_id": "hardcoded-credentials"' \
  study/analysis validation/results results test-output
```

### Read one project’s profile metadata

```bash
python -m json.tool \
  study/analysis/five-project-pilot/<project>/<sha>/<profile>/run_metadata.json
```

### Read one project’s file-selection provenance

```bash
python -m json.tool \
  study/analysis/five-project-pilot/<project>/<sha>/<profile>/file_selection.json
```

### Read diagnostics

```bash
python -m json.tool \
  study/analysis/five-project-pilot/<project>/<sha>/<profile>/diagnostics.json
```

### Filter findings by rule

If `jq` is installed:

```bash
jq '.[] | select(.rule_id == "missing-abstraction")' \
  study/analysis/five-project-pilot/<project>/<sha>/<profile>/findings.json
```

### Count findings by rule

If `jq` is installed:

```bash
jq -r '.[].rule_id' \
  study/analysis/five-project-pilot/<project>/<sha>/<profile>/findings.json \
  | sort \
  | uniq -c \
  | sort -nr
```

## 22. Git tracking and generated-data warning

The following generated or machine-local paths are ignored by Git:

```text
results/
test-output/
validation/
study/cache/
study/repositories/
study/snapshots/
study/history/
study/analysis/
study/logs/
study/manifests/*-frozen.csv
```

This means the data may exist on the current machine without being committed
to the repository.

The file-classification manifests and reviewed source manifests can be tracked,
while large generated results, clones, logs, and machine-local frozen
manifests are intentionally kept out of normal Git commits.

Do not delete ignored directories merely because `git status` does not display
them. They contain the local study evidence.

## 23. Quick start: how to read the current study

Use this order:

1. Open
   [`study/labels/five_project_pilot_summary.csv`](study/labels/five_project_pilot_summary.csv)
   for all five projects.
2. Open
   [`study/manifests/pilot-five-frozen.csv`](study/manifests/pilot-five-frozen.csv)
   for exact repository SHAs.
3. Open the matching CSV under
   [`study/manifests/file-classification`](study/manifests/file-classification)
   to see every included and excluded YAML file.
4. Enter
   [`study/analysis/five-project-pilot`](study/analysis/five-project-pilot)
   for research/review profiles, or
   [`study/analysis/five-project-technical-full`](study/analysis/five-project-technical-full)
   for the combined internal, GitLeaks, and ansible-lint run.
5. Choose a repository.
6. Enter its full SHA directory.
7. In `five-project-pilot`, choose `research-core`, `extended-ansible`,
   `snapshot-source`, or `review-range`. In
   `five-project-technical-full`, the SHA directory itself is the profile
   result root.
8. Read `run_metadata.json`.
9. Read `file_selection.json`.
10. Read `diagnostics.json`.
11. Read `summary.csv`.
12. Filter `findings.csv`.
13. Follow a finding’s file path into its mirrored per-file directory.
14. Read `Play_Level_Analysis.txt` and `Technical_Analysis.json`.
15. In research-profile results, `ansiblelint.txt` and `gitleaks.txt` have
    headings only because external tools were not requested. In
    `five-project-technical-full`, they contain the completed external-tool
    output.

## 24. Which files are authoritative for which question?

| Question | Authoritative file or directory |
|---|---|
| Which repositories were tested? | `study/manifests/pilot-five-frozen.csv` |
| Which commit was tested? | `pilot-five-frozen.csv` and `run_metadata.json` |
| Which YAML files were considered? | `study/manifests/file-classification/*.csv` |
| Which files were included in one run? | `file_selection.json` |
| Which profile and rules were used? | `run_metadata.json` |
| Did parsing or a tool fail? | `diagnostics.json` |
| What are all normalized findings? | `findings.json` |
| What should be opened in a spreadsheet? | `findings.csv` |
| Which files have the most findings? | `summary.csv` |
| What are the raw metrics for one YAML file? | Per-file `Technical_Analysis.json` |
| What is the readable report for one YAML file? | Per-file `Play_Level_Analysis.txt` |
| What did ansible-lint report for one file? | Per-file `ansiblelint.txt` |
| What did GitLeaks report for one file? | Per-file `gitleaks.txt` |
| What happened during execution? | `study/logs/<run>/` |
| What is the overall five-project summary? | `study/labels/five_project_pilot_summary.csv` |
| Did the Python software tests pass? | pytest terminal output or an explicitly generated JUnit XML file |

## Final distinction

There are three separate types of “testing result” in this repository:

```text
1. Software tests
   tests/ + pytest output
   → verify AnsibleGuard itself

2. Validation-corpus tests
   validation/results/
   → verify detectors against baseline and deliberately mutated examples

3. Real-repository study scans
   study/manifests/
   study/repositories/
   study/analysis/five-project-pilot/
   study/logs/five-project-pilot/
   study/labels/
   → analyze frozen real OpenStack repositories
```

For the current research study, the third category is the principal evidence.
