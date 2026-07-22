# Start here: project reading, running, and continuation guide

## Who this guide is for

Use this file when you are opening the repository for the first time, taking
over the work, reviewing it for a supervisor, or continuing the research after
the current implementation phase.

Do not try to read every Markdown file alphabetically. Some files are current
contracts, while others are historical implementation logs. Follow the order
below.

## The project in one paragraph

AnsibleGuard is a Python static-analysis CLI for Ansible. It normalizes 60
internal/external/review rules into JSON, CSV, text, and SARIF. The current
research goal is an Ansible-specific empirical extension inspired by the
supervisor's Puppet smell paper, using real OpenStack projects from OpenDev.
It is not a strict replication. Repository collection, frozen SHAs, auditable
file classification, and source/review profile separation now work. Detector
calibration and manual validation are the next phase.

## Read the documentation in this order

### 1. Orientation

1. **`START_HERE.md`** — this reading and handover map.
2. **`README.md`** — installation, everyday CLI usage, configuration, outputs,
   and documentation index.
3. **`HOW_IT_WORKS.md`** — the analysis pipeline in plain language.
4. **`ARCHITECTURE.md`** — modules, call flow, detector families, and technical
   ownership.
5. **`OUTPUT_FORMATS.md`** — what every generated file means.

After these five, the reader should be able to install the package, run a
technical scan, and trace findings through the code.

### 2. Understand what is detected

6. **`ALL_DETECTED_SMELLS.md`** — canonical inventory of all 60 active IDs.
7. **`inventory.md`** — detailed strategies and false-positive limitations.
8. **`CODE_REVIEW_CHECKLIST_COVERAGE.md`** — mapping to the 38 criteria from the
   supplied checklist paper.

For a slower explanation that combines the implementation, mathematics,
complexity, inspiration, and checklist status of all 60 IDs, read
**`ULTIMATE_SMELL_CATALOG.md`**. The external-tool boundary is explained in
**`ANSIBLE_LINT_GITLEAKS_OVERLAP.md`**.

Do not use historical implementation files as the canonical rule list. The
three files above describe the current detector surface.

### 3. Understand the empirical study

9. **`WHAT_IS_A_SNAPSHOT_STUDY.md`** — source snapshot versus review/history.
10. **`OPENSTACK_ANSIBLE_REAL_PROJECT_TESTING_PLAN.md`** — complete research
    methodology and gates.
11. **`RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md`** — decisions made after the
    first real Nova run and the remaining work packages.
12. **`CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md`** — how the numerator and
    denominator now use the same files.
13. **`RESEARCH_PROFILES_IMPLEMENTATION.md`** — how source, core, extended, and
    review results are separated.
14. **`LOCAL_OPENSTACK_STUDY_WORKFLOW.md`** — exact commands.
15. **`STUDY_SCRIPTS_REFERENCE.md`** — input/output schemas and behavior of
    every supplied and active script.

Two beginner-oriented companions are available:

- **`REAL_REPOSITORY_TESTING_ZERO_TO_HERO.md`** walks from project discovery
  through manifests, profiles, validation, calibration, statistics, and
  contribution;
- **`SANER24_PAPER_AND_ANSIBLEGUARD_APPROACH.md`** explains the SANER'24 paper,
  maps its 12 Puppet smells to Ansible candidates, and states what is and is
  not implemented here.

### 4. Read historical logs only when needed

Files such as `PROJECT_STATUS.md`, `CLI_STATUS.md`,
`PARSING_GITHUB_IMPLEMENTATION.md`, `PAPER_SMELLS_IMPLEMENTATION.md`,
`REVIEW_CHECKLIST_IMPLEMENTATION.md`, and `SESSION_IMPLEMENTATION_REPORT.md`
explain how bugs/features were discovered. They are useful for archaeology and
decisions, but they are not the first source for current behavior.

## Current state

### Complete

- package installation and `ansibleguard` CLI;
- 60 normalized rule IDs and multiple output formats;
- safe YAML/Ansible document parsing;
- OpenDev-first candidate discovery;
- human-selected five-project pilot manifest;
- full clones and immutable detached-HEAD SHAs;
- one-row-per-YAML classification manifests;
- complete/safe manifest validation in the scanner;
- real Nova-role technical and classified scans;
- five explicit execution profiles;
- source snapshot versus review-range separation;
- profile/file-selection hashes in output metadata;
- automated tests for the above.

### Real pilot evidence

```text
project: openstack/openstack-ansible-os_nova
commit:  e06c7bceef3f7c365828116b7aadea6fc2d3e22b
YAML candidates: 122
production files selected: 28
snapshot-source findings: 777
provisional research-core findings: 77
extended-Ansible findings: 700
review-range findings: 3
```

These are the post-standalone-role-fix calibration results recorded in
`FIVE_PROJECT_OPENSTACK_PILOT_RESULTS_SIMPLE.md`, not publishable empirical
conclusions.

### Not complete

- stratified human validation of file classes;
- repository-wide variable symbol/index resolution;
- precision calibration of `unguarded-variable`;
- manually labeled positive and negative detector examples;
- supervisor approval/freeze of the eight-rule provisional core;
- native ansible-lint/GitLeaks rule identity;
- research occurrence normalization/deduplication;
- five-project calibrated pilot;
- full-corpus selection and execution;
- longitudinal Git/Gerrit/statistical analysis.

## Make the project work locally

```bash
cd /home/aymmzn/Documents/AnsibleChecklist
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

If `.venv` already exists, activate it and verify:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ansibleguard.cli --help
```

Run a normal technical scan:

```bash
.venv/bin/python -m ansibleguard.cli /path/to/ansible-project \
  --profile technical-full \
  --output /tmp/ansibleguard-output \
  --fail-on never
```

## Reproduce the current Nova snapshot

The local clone and machine-specific frozen manifest must exist. If they do,
generate/verify file classification:

```bash
.venv/bin/python scripts/classify_study_files.py \
  study/manifests/pilot-frozen.csv \
  --limit 1
```

Run the source snapshot:

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --limit 1 \
  --file-manifests-dir study/manifests/file-classification \
  --profile snapshot-source \
  --output-root study/analysis/profiled-snapshots \
  --logs-dir study/logs/profiled
```

Run `research-core`, `extended-ansible`, and `review-range` by changing only
the profile. Outputs remain separated by profile.

## If the local repositories do not exist

Start with the versioned pilot selection:

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/pilot.csv \
  --limit 1 \
  --output study/manifests/pilot-frozen.csv
```

Then generate classification and run the snapshot commands above. Do not use
`--refresh` when reproducing an already frozen experiment.

## How to continue the work

Work in this order:

### Ticket 1 — manual file-class validation

Create a stratified sample covering every file class in Nova. Record reviewer,
expected class, observed class, decision, and rationale. Correct classifier
rules and regenerate the manifest if needed.

Gate: every class sampled, no unexplained/unclear production candidate, and
agreement documented.

### Ticket 2 — repository symbol index

Index definitions from defaults, vars, play vars, task vars, `set_fact`,
registers, `include_vars`, `vars_files`, group/host vars, and explicit known
runtime variables. Keep provenance for every definition.

Gate: deterministic index tests plus real Nova examples.

### Ticket 3 — calibrate `unguarded-variable`

Resolve uses against the symbol index, sample remaining findings, label true
positive/false positive/uncertain, and decide whether this rule stays extended
or enters core.

Gate: supervisor-approved precision threshold and documented limitations.

### Ticket 4 — research output normalization

Preserve native external identities, add unique occurrence keys, deduplicate
findings, and export project/SHA/file/class/LOC/profile/config/tool metadata.

### Ticket 5 — five-project pilot

Only after the earlier gates, collect/classify/run all five selected projects,
manually validate samples, and decide whether the main corpus can begin.

## Rules for future changes

- Never add a rule without assigning it to exactly one profile family.
- Never change the core allowlist during a frozen experiment without creating a
  new version/hash and rerunning all projects.
- Never combine snapshot and review-range findings in prevalence tables.
- Never scan a research repository without a frozen SHA and complete manifest.
- Never interpret raw `unguarded-variable` counts as defects before calibration.
- Never edit generated findings manually.
- Run focused tests, the full suite, `git diff --check`, and inspect output
  metadata before a PR.

## The immediate next action

Do not collect the remaining four projects yet. The next action is the manual
Nova file-classification sample, followed by the repository symbol-index
implementation. That preserves the calibration-first design and prevents the
same false-positive problem from being multiplied across the corpus.
