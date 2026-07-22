# Testing real repositories: zero to hero

## The goal in one sentence

We want to test AnsibleGuard on real OpenStack Ansible source code in a way
that another researcher can repeat, inspect, and challenge.

We are not deploying OpenStack. We are studying configuration source files and
Git/review evidence.

## Why “just clone a repository and run the tool” is not enough

A real repository changes over time and contains many kinds of YAML. If we run
against a moving branch and count every YAML file, tomorrow's result can differ
and our denominator may include CI, documentation, or unrelated data.

A defensible study needs answers to four questions before it counts a smell:

```text
Which project?
Which exact version?
Which exact files?
Which exact rules and settings?
```

This project answers those questions with four records:

```text
project selection manifest
        + frozen commit SHA (snapshot)
        + file-classification manifest
        + versioned rule profile and hash
```

## The four words to learn first

### Snapshot

A snapshot is one exact Git commit of a repository.

Think of a living repository as a movie. A snapshot is one frozen frame. Its
identifier is the full commit SHA, for example:

```text
e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

Why we need it: “master on Tuesday” is not reproducible; a commit SHA is.

### Manifest

A manifest is a CSV attendance sheet.

The project manifest records which repositories were considered or selected.
The file manifest records every YAML candidate and whether it enters the
production-source study.

Why we need it: the findings numerator and the file/LOC denominator must refer
to the same population.

### Profile

A profile is a named, versioned box of rules.

Why we need it: source smells, Git review checks, and external-tool findings
answer different research questions. Mixing them would make prevalence and
co-occurrence statistics invalid.

### Calibration

Calibration means humans inspect sampled results and decide whether the
detector condition represents a real problem in this kind of project.

Why we need it: a static rule can match its written condition perfectly while
the condition is inappropriate for an OpenStack convention.

## The complete journey

```text
define the study
  -> discover candidates
  -> choose eligible projects
  -> clone complete repositories
  -> freeze exact SHAs
  -> classify every YAML file
  -> manually check classifications
  -> run separated profiles
  -> verify outputs and hashes
  -> label findings and non-findings
  -> calibrate and freeze detectors
  -> run the main snapshot study
  -> calculate prevalence/co-occurrence
  -> mine history for change-proneness
  -> optionally validate defects with SZZ
  -> publish a replication package
```

Do not jump from discovery directly to final statistics.

## Stage 0 — write the protocol before collecting data

The protocol should freeze:

- research questions;
- project population;
- inclusion and exclusion criteria;
- production/test file taxonomy;
- Puppet-to-Ansible construct mapping;
- core and extended rule sets;
- unit of analysis: project, role, file, file revision, or commit;
- sampling and human-label procedure;
- statistical tests and multiple-comparison policy;
- handling of failures, unknowns, and exclusions.

The proposed questions are:

- DV1: What precision does each chosen rule achieve on real OpenStack code?
- DV2: Which layouts and conventions cause false positives/negatives?
- DV3: What changes are needed before the detector is frozen?
- RQ1: How prevalent are validated smells?
- RQ2: Which validated smell types co-occur in the same file?
- RQ3: Are smelly file revisions changed more often or with more churn?
- RQ4: Are smelly file revisions more defect-prone?

RQ4 is conditional because SZZ introduces another difficult classification
layer.

## Stage 1 — discover projects

### Why OpenDev is authoritative

The GitHub `openstack` organization is a mirror. OpenStack development and
review occur through OpenDev Git and Gerrit. Therefore:

- OpenDev project registry: authoritative project discovery;
- OpenDev Git: authoritative code and history;
- Gerrit: authoritative review evidence;
- GitHub: optional mirror metadata only;
- GitHub pull-request counts: not evidence of OpenStack review activity.

### The active discovery script

File: `scripts/discover_openstack_ansible.py`.

Its input is the OpenDev `project-config` registry:

```text
https://opendev.org/openstack/project-config/raw/branch/master/gerrit/projects.yaml
```

Its logic, slowly:

1. `_download()` requests the registry with a user agent.
2. It retries temporary network/server/rate-limit errors with bounded
   exponential backoff.
3. `load_registry()` saves the response under `study/cache/` or reads it in
   `--offline` mode.
4. `candidate_rows()` keeps `openstack/*` entries that match approved seed
   projects or Ansible/project-family keywords.
5. `_retired()` marks projects whose description/ACL indicates retirement.
6. Every row starts with `selected=false`.
7. `write_manifest()` writes stable, sorted CSV rows with discovery reason,
   source URL, and fetch timestamp.

This script discovers. It deliberately does not make the scientific selection
decision.

Run online:

```bash
.venv/bin/python scripts/discover_openstack_ansible.py
```

Repeat from the cached registry:

```bash
.venv/bin/python scripts/discover_openstack_ansible.py --offline
```

Output:

```text
study/manifests/candidates.csv
```

### Why the supplied `fetch.py` was not reused as the final collector

The downloaded `/home/aymmzn/Downloads/fetch.py` contains useful retry and
pagination ideas, but it searches Terraform/HCL projects created since 2020,
uses stars/forks from GitHub, limits search pages, writes to a macOS absolute
path, leaves file counts blank, and sets a nonempty placeholder token. Its
effective minimum comparisons also use `<=`, so the retained population is
strictly above the displayed minimum.

Those assumptions do not match this OpenStack Ansible study. We retained the
good engineering idea—bounded retries—and replaced the population logic.

The downloaded `GithubAPI.py` is also unsuitable for the dataset because it
hardcodes a token and repository, treats mirror pull requests as authoritative,
prints large author lists, confuses a commit query with developer count, and
has no reproducible output schema or retry/resume design.

## Stage 2 — choose eligible projects

Discovery is broad. Selection is a documented human/research decision.

Proposed eligibility criteria:

- public and cloneable from OpenDev;
- active, not marked retired at the freeze date;
- maintained by an OpenStack team;
- at least 10 production Ansible YAML files after classification;
- at least 80 commits overall, matching the Puppet paper's minimum;
- meaningful history touching Ansible files;
- resolvable default branch and complete history.

The 10-file threshold is a pilot value. The final study should report
sensitivity at 5, 10, and 20 files.

Do not silently delete a candidate. Keep either:

```text
selected=true
```

or:

```text
selected=false, exclusion_reason=<clear reason>
```

The versioned five-project pilot intentionally covers different shapes:

1. one OpenStack-Ansible role;
2. the integrated OpenStack-Ansible repository;
3. Kolla-Ansible;
4. Kayobe;
5. the Kolla Ansible collection.

This is variation sampling for engineering/calibration, not a claim that five
projects represent the whole population.

## Stage 3 — clone and freeze

### The script

File: `scripts/clone_study_repositories.py`.

Its code connects selection to reproducibility:

1. `read_selected()` reads only rows with a truthy `selected` value.
2. `_repo_path()` converts `openstack/kayobe` into the predictable local path
   `study/repositories/openstack/kayobe`.
3. `_clone_or_update()` performs a full multi-branch clone. Existing clones are
   fetched only when `--refresh` is explicitly requested.
4. `_default_ref()` identifies the remote default branch.
5. `_checkout_frozen()` resolves the requested revision or remote default head
   to a full SHA and checks it out in detached-HEAD mode.
6. `collect_row()` records commit date, collection time, commit count,
   contributor count, classified file counts, production LOC, status, and
   error.
7. `write_rows()` writes a machine-specific frozen manifest.

Run the pilot:

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/pilot.csv \
  --output study/manifests/pilot-frozen.csv
```

Important rule: do not use `--refresh` when reproducing an already frozen
experiment. Refresh is for creating a new freeze, not replaying the old one.

### What the frozen manifest proves

Each successful row connects:

```text
project -> authoritative URL -> local repository -> exact SHA -> collection metadata
```

Machine-specific frozen manifests contain absolute repository paths and are
ignored by Git. The versioned selection manifest and file-classification
manifests remain portable.

## Stage 4 — classify every YAML file

### Why classification is a scientific requirement

A `.yml` extension does not mean “production Ansible.” A repository can hold:

- production playbooks/tasks/handlers/defaults/vars/meta;
- test and Molecule Ansible;
- Zuul/GitHub/GitLab CI;
- documentation examples;
- release notes;
- dependency manifests;
- generated/vendor YAML;
- generic data YAML;
- encrypted Vault files;
- invalid or unclear YAML.

If 28 production files generate findings, dividing by all 122 YAML files would
answer the wrong question.

### The classifier

Core code: `src/ansibleguard/file_manifest.py`.

Runner: `scripts/classify_study_files.py`.

`yaml_candidates()` enumerates every `.yml`/`.yaml` file except Git internals.
`inspect_document()` safely parses unknown Ansible tags and classifies document
shape. `classify_yaml_file()` combines path and document evidence.

The available classes are:

| Class | Meaning | Included by default? |
|---|---|---:|
| `production_ansible` | approved production source/configuration | Yes |
| `test_ansible` | tests or Molecule content | No, separate stratum |
| `ci_yaml` | Zuul/GitHub/GitLab/CI | No |
| `documentation_example` | docs/examples/release material | No |
| `generated_or_vendor` | generated, build, venv, vendor | No |
| `other_yaml` | YAML without approved Ansible source role | No |
| `invalid_yaml` | parse/read failure | No |
| `vault_encrypted` | fully encrypted Vault document | No |
| `unclear` | unsupported/unsafe classification | No pending review |

Each CSV row records:

```text
project, commit_sha, path, file_class, document_type, parse_status,
classification_reason, loc, included, exclusion_reason
```

Run:

```bash
.venv/bin/python scripts/classify_study_files.py \
  study/manifests/pilot-frozen.csv
```

The script first verifies that each clone's current `HEAD` equals the frozen
SHA. It then writes a manifest named by both project and SHA:

```text
study/manifests/file-classification/
  openstack__kayobe__<full-sha>.csv
```

### Manifest validation before a scan

`included_files_from_manifest()` refuses to scan when:

- a path is absolute or contains `..`;
- a path escapes the repository;
- a row is duplicated;
- `included` is not a known true/false value;
- a class is unknown;
- the classification reason is missing;
- an excluded row has no exclusion reason;
- a repository YAML file has no row;
- a stale manifest row points to a missing file;
- an included path is not a real YAML file.

This is stronger than “read the rows marked true.” It proves the manifest is a
complete description of the repository's YAML population at scan time.

### Human classification validation

Automation is not the last judge. Sample every file class and record:

```text
project, sha, path, predicted_class, human_class, decision, reviewer, rationale
```

Oversample `unclear`, unusual deployment configuration paths, symlinks, empty
documents, and path patterns newly added to the classifier.

## Stage 5 — choose the correct profile

Profiles live in `src/ansibleguard/profiles.py`. Their sorted rule IDs and
SHA-256 hash are written to `run_metadata.json`.

| Profile | Rules | Source? | Review? | External? | Manifest required? | Research use |
|---|---:|---:|---:|---:|---:|---|
| `technical-full` | 60 | Yes | Yes | Yes | No | engineering/CI only |
| `snapshot-source` | 51 | Yes | No | No | Yes | all internal snapshot results, not primary research |
| `research-core` | 8 | Yes | No | No | Yes | provisional primary candidates |
| `extended-ansible` | 43 | Yes | No | No | Yes | disjoint secondary stratum |
| `review-range` | 7 | No | Yes | No | No | commit/review questions only |

Why a manifest is mandatory for the three research source profiles: the code
being counted must be exactly the code being scanned.

Why external tools are absent: GitLeaks and ansible-lint are valuable, but the
current wrapper aggregates native rule identities. They remain in
`technical-full` until research normalization is improved.

Why review rules are separate: “this commit lacks a release note” is not a
property of one source file at the frozen snapshot.

## Stage 6 — run the frozen pilot

### The runner

File: `scripts/run_study_pilot.py`.

Its logic:

1. read rows with `status=collected`;
2. verify the clone is still at the exact frozen SHA;
3. derive the matching classification-manifest filename from project + SHA;
4. choose an output directory keyed by project + SHA + profile;
5. when `--skip-existing` is used, verify the existing manifest hash and
   profile identity before trusting the output;
6. invoke the installed package through `python -m ansibleguard.cli`;
7. use `--fail-on never` so findings do not abort dataset collection;
8. redirect stdout/stderr to one project/profile log;
9. treat a nonzero process status as a failed run, not as missing data.

Run one profile:

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --file-manifests-dir study/manifests/file-classification \
  --profile research-core \
  --output-root study/analysis/five-project-pilot \
  --logs-dir study/logs/five-project-pilot
```

Repeat for:

```text
snapshot-source
research-core
extended-ansible
review-range
```

Do not put different profiles in the same result directory.

## Stage 7 — understand every output

A successful profile directory contains the evidence needed to audit the run:

| File | What it answers |
|---|---|
| `findings.json` | What normalized occurrences were reported? |
| `findings.csv` | Same findings in table form |
| `findings.txt` | Same findings for humans |
| `findings.sarif` | Same findings for code-scanning tools |
| `summary.csv` | How many errors/warnings/notes per file? |
| `diagnostics.json` | Did parsing or an external tool fail? |
| `review_metrics.json` | What raw Git review evidence was collected? |
| `file_selection.json` | Which manifest and SHA-256 hash selected the files? |
| `run_metadata.json` | Which profile/rules/hash and tool states were used? |
| per-file legacy files | Raw metrics and compatibility output |

Important: zero diagnostics means the scan recorded no parsing/tool failures.
It does not mean every finding is a true defect.

## Stage 8 — validation checks after every run

For every project/profile, verify:

- repository SHA equals the frozen manifest;
- file-selection manifest hash matches the requested manifest;
- included-file count matches the manifest;
- profile name and rule hash are present;
- source profiles report external tools as `not-requested`;
- source profiles have no review metrics;
- diagnostics are inspected, never silently discarded;
- every finding path belongs to the selected population;
- JSON, CSV, text, and SARIF normalized counts agree;
- `research-core + extended-ansible = snapshot-source` by rule set and findings
  count for the same code/configuration;
- commands, logs, versions, and exit statuses are retained.

The current five-project pilot satisfied these checks across 20 profile runs.

## What has already been completed

Frozen projects and SHAs:

| Project | SHA |
|---|---|
| `openstack/openstack-ansible-os_nova` | `e06c7bceef3f7c365828116b7aadea6fc2d3e22b` |
| `openstack/openstack-ansible` | `b7c10cbcc04a06207c2344a312d4f612a0810939` |
| `openstack/kolla-ansible` | `9c41bdca79d4c7267beeece141909e679f70dea8` |
| `openstack/kayobe` | `9a6e4333b2aa2fbe8dc80a93cd5aa3e2f1872970` |
| `openstack/ansible-collection-kolla` | `785982d7c09dda3d8e46f6c9b09597ca14820497` |

File population:

| Measure | Count |
|---|---:|
| YAML candidates | 5,409 |
| selected production Ansible files | 1,856 |

Profile findings:

| Measure | Count |
|---|---:|
| all source findings | 13,387 |
| provisional research-core | 1,250 |
| extended Ansible | 12,137 |
| review-range | 10 |
| saved diagnostics | 0 |

The source identity holds: `1,250 + 12,137 = 13,387`.

These are detector outputs, not 13,387 confirmed defects.

## Stage 9 — label findings and non-findings

### Positive labels

Sample reported occurrences across:

- every project;
- every rule;
- every severity;
- different file types and repository layouts;
- rare rules, ideally all occurrences;
- common rules, randomized or stratified samples.

### Negative labels

Also inspect files/lines where the detector did not report the rule. Without
negative examples we cannot study false negatives or recall.

### Label schema

Each row should contain at least:

```text
label_id, project, commit_sha, profile, rule_id, file, line,
detector_reported, human_label, rationale, reviewer, resolution_status
```

Use three human labels:

- true positive;
- false positive;
- unclear/not applicable.

Prefer two independent reviewers. Resolve disagreements by discussion and
report Cohen's kappa or Krippendorff's alpha. Precision can be measured from
reported findings; recall requires a separately labeled population where
missed occurrences can be counted.

Pilot target: at least 100 findings. For a large unknown population, 384 is a
conservative starting point for 95% confidence and 5% margin at maximum
variance, then stratify/oversample rare rules.

## Stage 10 — calibrate and freeze

For each rule:

1. inspect true positives, false positives, unclear cases, and negatives;
2. identify the cause: threshold, parser, missing context, or invalid construct;
3. fix the detector or document a project configuration;
4. rerun the same five frozen SHAs;
5. compare old/new results;
6. repeat labels where the behavior changed;
7. move a weak rule to extended analysis or remove it from the core;
8. obtain supervisor approval;
9. freeze code commit, rule allowlist/hash, thresholds, configuration,
   dependencies, model versions, and tool versions.

The context-sensitive core rules to study first are:

```text
empty-abstraction
missing-abstraction
unstructured-module
```

`research-core` must remain `research_eligible=false` until this gate passes.

## Stage 11 — main prevalence and co-occurrence study

Only validated core findings enter the primary tables.

### RQ1 prevalence

For rule `s`, files `F`, occurrences `occ`, and total production KLOC:

```text
affected_file_rate(s) = files containing s / all included files
density_per_KLOC(s) = occurrences of s / production KLOC
smelly_file_rate = files with at least one core finding / all included files
```

Report by project, role, file type, and file-size quartile. Keep test files in a
separate stratum.

### RQ2 co-occurrence

Recommended transaction: one production Ansible file at the frozen snapshot.

For smell types `A` and `B`:

```text
support(A -> B) = files containing both A and B / all files
confidence(A -> B) = support(A and B) / support(A)
lift(A -> B) = support(A and B) / (support(A) * support(B))
```

Also use Chi-square or Fisher's exact test as appropriate, Cramer's V effect
size, and multiple-testing correction. Association is not causation.

## Stage 12 — history and change-proneness

The snapshot answers “what exists at one SHA.” RQ3 needs every relevant file
revision.

For each production Ansible file lineage:

- track renames and deletions;
- record commits touching the file;
- record added, deleted, and churn lines;
- record LOC at that revision;
- detect smell state at that revision, not only current HEAD;
- record file age, project, and file type;
- cache analysis by Git blob SHA + detector/config version.

```text
churn(file, commit) = added lines + deleted lines
total_change_proneness(file) = sum churn(file, commit_i)
change_frequency(file) = number of commits touching the file
```

Use Mann-Whitney U and Cliff's delta for comparison with the Puppet paper, but
also model project, LOC, age, file type, and repeated file revisions. A
mixed-effects/regression robustness analysis is safer than treating every
revision as independent.

The history-mining script described in the study plan is not yet implemented.

## Stage 13 — defect-proneness only after the earlier gates

Prefer defect evidence in this order:

1. Gerrit/OpenStack trailers such as `Closes-Bug`/`Related-Bug`;
2. linked Launchpad/story/task evidence;
3. conservative keywords as fallback.

For confirmed fixing commits that touch production Ansible, a documented SZZ
implementation can trace fixed lines backward to candidate inducing commits.
Merges, mass formatting, generated files, renames, and refactors require
special handling.

Humans must validate samples of both fixing and inducing classifications. If
precision is weak, report a feasibility result instead of a strong RQ4 claim.

The Gerrit miner, history miner, analysis script, and SZZ pipeline are planned,
not implemented in the current repository.

## How the study keeps track of everything

```text
study/
  manifests/          versioned candidate, pilot, and file decisions
  repositories/       local full clones; ignored by Git
  cache/              downloaded registries; ignored by Git
  snapshots/analysis/ generated raw and derived outputs; mostly local
  history/            future revision/churn tables
  labels/             human labels and compact summaries
  logs/               command output and failures
```

Rules for evidence:

- never manually edit generated findings;
- never overwrite a frozen experiment with new settings;
- store a new profile/config hash and output directory;
- keep raw data immutable;
- derive summary tables by script;
- record every exclusion and failure;
- use full SHAs, not short or floating branch names;
- keep secrets in environment variables, never source files;
- record tool/dependency versions and configuration hashes.

## How to contribute code safely

### Before coding

1. Read `START_HERE.md`, `ARCHITECTURE.md`, this guide, and the relevant
   detector document.
2. Decide whether the change affects engineering scans, the research
   construct, the file population, or the study protocol.
3. Do not silently change a frozen rule set or manifest.

### Adding or changing a detector

1. Give the rule one stable kebab-case ID in `RULE_CATALOG`.
2. Assign severity/category.
3. Put source logic in a focused detector module.
4. Return both a count and line-addressable details.
5. Integrate parser metrics, assessment, normalized findings, CSV/text/SARIF.
6. Assign the rule to exactly one profile family.
7. Add positive, negative, nested, malformed, and integration tests.
8. Explain the algorithm, limitations, complexity, checklist relationship, and
   research status.
9. If a frozen core changes, version it and rerun all frozen projects.

### Changing classification

1. Add a fixture for the new path/document shape.
2. Preserve exact real relative paths.
3. Add both inclusion and exclusion tests.
4. Regenerate affected manifests rather than hand-editing generated results.
5. repeat human samples for the changed class.

### Changing study scripts

Require:

- CLI-configurable paths;
- deterministic ordering;
- structured CSV/JSON output;
- bounded retries and timeouts for network calls;
- clear nonzero failure status;
- resume/skip behavior that verifies hashes;
- no hardcoded credentials;
- unit tests for pure functions and integration tests for filesystem/Git
  behavior.

### Verification before a pull request

```bash
.venv/bin/python -m pytest -q
git diff --check
```

Then run the smallest relevant frozen-pilot slice and inspect:

```text
diagnostics.json
run_metadata.json
file_selection.json
findings.json
the run log
```

## Current stop/go board

| Item | State |
|---|---|
| OpenDev discovery script | Implemented |
| human-selected five-project pilot | Implemented |
| full clone and SHA freeze | Implemented |
| row-level YAML classification | Implemented |
| safe complete manifest validation | Implemented |
| five explicit scan profiles | Implemented |
| five-project, four-profile execution | Completed |
| automated suite | 168 passing on this audit |
| spot checks and some Nova labels | Started/partially completed |
| complete stratified classification validation | Still required |
| full core precision/negative calibration | Still required |
| supervisor/core freeze | Still required |
| native external rule identity | Still required |
| normalized research occurrence/deduplication | Still required |
| history miner | Not implemented |
| Gerrit review miner | Not implemented |
| RQ1/RQ2 main-corpus analysis | Not started |
| RQ3 longitudinal analysis | Not started |
| RQ4/SZZ | Conditional, not implemented |

## The next action

Do not start a larger blind scan. Use the five frozen repositories to finish a
balanced manual calibration of the 1,250 provisional core findings, including
negative examples. Refine the context-sensitive rules, freeze the core, and
rerun those same SHAs before expanding the corpus.

## Related evidence

- `study/README.md`
- `STUDY_SCRIPTS_REFERENCE.md`
- `CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md`
- `RESEARCH_PROFILES_IMPLEMENTATION.md`
- `FIVE_PROJECT_OPENSTACK_PILOT_RESULTS_SIMPLE.md`
- `RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md`
- `OPENSTACK_ANSIBLE_REAL_PROJECT_TESTING_PLAN.md`
- `LOCAL_OPENSTACK_STUDY_WORKFLOW.md`
