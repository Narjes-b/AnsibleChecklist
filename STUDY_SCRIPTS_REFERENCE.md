# Study scripts: complete technical reference

This reference complements the
[research-profile and calibration plan](RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md),
the [full empirical-study plan](OPENSTACK_ANSIBLE_REAL_PROJECT_TESTING_PLAN.md),
the [local workflow](LOCAL_OPENSTACK_STUDY_WORKFLOW.md), and the implemented
[research-profile contract](RESEARCH_PROFILES_IMPLEMENTATION.md).

## Purpose

This document explains the scripts supplied by the supervisor and the scripts
added for the OpenStack Ansible study. It describes what each script does, why
it is designed that way, how to run it, what it reads and writes, and what it
must not be used to conclude.

## Script inventory

| Script | Status | Role |
|---|---|---|
| `/home/aymmzn/Downloads/fetch.py` | Reference only | Original generic GitHub/Terraform crawler supplied as a starting point |
| `/home/aymmzn/Downloads/GithubAPI.py` | Reference only | Original one-repository GitHub metadata experiment |
| `scripts/discover_openstack_ansible.py` | Active | Discover likely OpenStack Ansible repositories from OpenDev |
| `scripts/clone_study_repositories.py` | Active | Clone explicitly selected repositories and freeze exact SHAs |
| `scripts/classify_study_files.py` | Active | Generate one explained classification row per YAML candidate at a frozen SHA |
| `scripts/run_study_pilot.py` | Active technical pilot | Run AnsibleGuard only against frozen repository checkouts |
| `scripts/validate_detector_corpus.py` | Active developer validation | Run detector bundles over the repository's bundled YAML corpus |

## End-to-end script flow

```text
OpenDev project registry
        │
        ▼
discover_openstack_ansible.py
        │
        ├── study/cache/openstack-projects.yaml
        └── study/manifests/candidates.csv
                    │
                    │ human review / selected=true
                    ▼
           study/manifests/pilot.csv
                    │
                    ▼
clone_study_repositories.py
        │
        ├── study/repositories/<namespace>/<repo>/
        └── study/manifests/pilot-frozen.csv
                    │
                    ▼
         classify_study_files.py
        │
        └── study/manifests/file-classification/<project>__<sha>.csv
                    │
                    ▼
          run_study_pilot.py
        │
        ├── study/snapshots/<project>/<sha>/
        └── study/logs/<project>__<sha>.log
```

The candidate and selection manifests are versionable. Repositories, caches,
snapshots, logs, and machine-local frozen manifests are ignored by Git.

## Supplied script: `fetch.py`

### Original intent

The script queries GitHub repository search, applies simple quality filters,
retrieves contributor and commit counts, and appends results to CSV. It has
useful generic ideas:

- bounded HTTP retries;
- primary and secondary rate-limit handling;
- incremental CSV writing;
- resuming from previously saved URLs;
- applying cheap filters before expensive API requests.

### Current behavior

It currently searches:

```text
language:HCL stars:>1 archived:false created:>=2020-01-01
```

That is a Terraform/HCL population, not OpenStack Ansible. It writes fields
such as stars, forks, contributor count, commit count, and empty Terraform-file
counts.

### Why we do not modify it in Downloads

The Downloads copy is treated as supervisor-provided evidence. Keeping it
unchanged lets us explain exactly what was inherited. The active replacement
lives in the repository where it can be tested, reviewed, and versioned.

### Problems for this study

- `TOKEN = "add your token here"` is nonempty, so `if not TOKEN` does not catch
  the missing real token.
- The output path is a hardcoded macOS user path.
- The query is HCL and excludes older repositories.
- Five search pages are not a complete OpenStack registry.
- GitHub stars/forks describe mirrors poorly as OpenStack quality measures.
- GitHub search has result and rate-limit constraints.
- Contributor counts inferred from pagination are approximate.
- File counts are left empty until an unspecified later phase.
- It has no frozen SHA, content classifier, provenance hash, or audit reason.

### Reusable concepts

We retained retry, cache, resume, cheap-filter-first, and structured-manifest
principles, but changed the authoritative source and study schema.

## Supplied script: `GithubAPI.py`

### Original intent

The script uses PyGithub to inspect one repository:

```text
openstack/ansible-config_template
```

It experiments with pull-request, contributor, commit-author, developer, and
commit counts.

### Why it is reference only

OpenStack GitHub repositories are read-only mirrors. The authoritative review
system is Gerrit on OpenDev, so GitHub pull requests do not represent the real
OpenStack review process.

### Correctness and operational issues

- token is embedded in source;
- repository is hardcoded;
- no retries, rate-limit handling, cache, or resume;
- iterating all pull requests and commit authors can be expensive;
- printing every author creates large logs;
- null authors require special handling;
- bot filtering is incomplete;
- `get_commits(author='all')` does not calculate unique developers;
- output is console text with no reproducible schema;
- no commit SHA or collection timestamp is recorded.

### Future replacement for review data

If the study later analyzes review behavior, create a dedicated Gerrit/OpenDev
collector. It should retrieve Gerrit change IDs, patch sets, reviewers,
messages, votes, bug trailers, and merge timestamps. It should not revive the
GitHub PR approach.

## Active script: `discover_openstack_ansible.py`

### Responsibility

Discover repositories that may contain meaningful Ansible code and create a
human-reviewable candidate manifest.

### Authoritative input

Default URL:

```text
https://opendev.org/openstack/project-config/raw/branch/master/gerrit/projects.yaml
```

This registry includes project names, descriptions, groups, and retirement
configuration.

### Default outputs

```text
study/cache/openstack-projects.yaml
study/manifests/candidates.csv
```

### Candidate-selection algorithm

For each registry entry:

1. require the project namespace to start with `openstack/`;
2. combine project name, description, and groups into searchable text;
3. include it when:
   - it is an approved seed; or
   - searchable text contains `ansible`; or
   - it belongs to the Bifrost/Kayobe Ansible project family;
4. detect retirement from a `RETIRED` description or retired ACL;
5. emit OpenDev and GitHub mirror URLs;
6. set `selected=false` for every discovered row;
7. sort deterministically by project name.

### Why `selected=false` is mandatory

Keyword discovery has false positives and false negatives. A repository named
for an Ansible plugin may contain mostly Python; a project such as Kayobe may
contain substantial Ansible without `ansible` in its name. Discovery proposes
candidates; it does not define the research population.

### Candidate CSV fields

| Field | Meaning |
|---|---|
| `project` | OpenDev project identifier, such as `openstack/kolla-ansible` |
| `description` | Registry description |
| `groups` | Semicolon-separated OpenStack groups |
| `opendev_url` | Authoritative clone URL |
| `github_url` | Convenience read-only mirror URL |
| `discovery_reason` | Seed/keyword/project-family reason |
| `retired` | Whether registry evidence marks the project retired |
| `selected` | Human-controlled collection decision; defaults to false |
| `exclusion_reason` | Initially `retired` where applicable |
| `registry_source` | Exact registry URL |
| `registry_fetched_at_utc` | Cache provenance timestamp |

### Network behavior

- a descriptive user agent is sent;
- requests have a timeout;
- transient failures and HTTP 429/5xx responses are retried;
- `Retry-After` is honored when present;
- the raw registry is cached;
- offline mode makes no network call;
- the cache mtime becomes the provenance timestamp so offline regeneration is
  byte-for-byte stable.

### Commands

Online refresh:

```bash
.venv/bin/python scripts/discover_openstack_ansible.py
```

Offline reproduction:

```bash
.venv/bin/python scripts/discover_openstack_ansible.py --offline \
  --output /tmp/candidates.csv
```

Custom paths/source:

```bash
.venv/bin/python scripts/discover_openstack_ansible.py \
  --source-url <registry-url> \
  --cache /tmp/projects.yaml \
  --output /tmp/candidates.csv
```

### Current live result

The current registry produced:

- 150 candidates;
- 81 active;
- 69 retired.

### Limitations

- keyword discovery is not content validation;
- retirement status depends on registry conventions;
- project activity and Ansible-file counts require cloning;
- it does not automatically discover every project that embeds Ansible under
  an unrelated name;
- GitHub metadata is not enriched because it is unnecessary for authoritative
  selection.

## Active script: `clone_study_repositories.py`

### Responsibility

Clone only human-selected repositories, freeze exact commits, and inventory
their YAML/Ansible content.

### Input contract

CSV with at least:

```text
project,opendev_url,selected,revision
```

Only values such as `true`, `yes`, `1`, or `y` in `selected` are processed.

### Clone/update algorithm

For each selected row:

1. derive `study/repositories/<namespace>/<repository>`;
2. perform a full `git clone --no-single-branch` when absent;
3. reuse an existing repository without fetching by default;
4. fetch branches/tags only with `--refresh`;
5. resolve the remote default branch;
6. use the manifest `revision` when provided, otherwise current remote default;
7. resolve the target to an immutable commit SHA;
8. checkout detached HEAD at that SHA;
9. inventory history, contributors, YAML, file classes, and LOC;
10. write success or failure to the frozen manifest.

### Why full clones

The later change-proneness phase needs complete history, renames, blame, and
SZZ-style analysis. A shallow clone would make early collection faster but
would have to be replaced later and could silently invalidate history metrics.

### Why detached HEAD

A branch name moves. Detached HEAD at a recorded SHA ensures later commands
analyze the same content even after the remote branch changes.

### Refresh semantics

Default behavior is conservative and reproducible: an existing local clone is
not fetched. `--refresh` is an explicit dataset-update operation.

For exact reproduction, put the recorded SHA in `revision` and do not use
`--refresh` as part of the experiment.

### YAML inventory algorithm

For every `.yml`/`.yaml` outside `.git`:

1. parse/classify with `ansibleguard.document.inspect_document`;
2. count invalid/read-error YAML separately;
3. classify `molecule`, `test`, and `tests` paths as test Ansible;
4. classify GitHub/Zuul/docs/release-note paths as other YAML;
5. recognize playbook/task document shapes as Ansible;
6. recognize vars/metadata/playbooks/tasks under Ansible role/inventory paths;
7. otherwise classify the document as other YAML;
8. calculate nonblank, non-comment physical LOC for production Ansible.

These aggregate counts now come from the same reusable row-level classifier as
`classify_study_files.py`. This prevents collection inventory and research scan
selection from drifting apart. Manual validation is still required before the
main study.

### Frozen output fields

| Group | Fields |
|---|---|
| Identity | `project`, `opendev_url`, `repository_path` |
| Revision | `default_branch`, `commit_sha`, `commit_date_utc`, `collected_at_utc` |
| History | `total_commits`, `contributors` |
| Content | YAML, production, test, other, invalid counts and production LOC |
| Result | `status`, `error` |

### Failure behavior

One project failure is recorded instead of erasing previously completed rows.
The command exits nonzero when any selected project failed, which makes local
and CI failures visible.

### Commands

One-project smoke collection:

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/pilot.csv \
  --limit 1 \
  --output study/manifests/pilot-frozen.csv
```

Refresh the pilot population:

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/pilot.csv \
  --refresh \
  --output study/manifests/pilot-frozen.csv
```

### Limitations

- contributor count is based on distinct `git shortlog -sne` identities and
  can split one person using several emails;
- the pilot classifier may misclassify unconventional layouts;
- test classification currently trusts path names before document semantics;
- physical LOC is not logical task count;
- collection does not yet count commits that specifically touch Ansible files;
- generated/submodule/LFS content needs additional policy if encountered.

## Active script: `classify_study_files.py`

### Responsibility

Convert each collected frozen-repository row into a complete CSV containing
one explained row per YAML candidate. It verifies repository `HEAD` against
the frozen SHA before reading files.

### Input and output

Only `status=collected` rows from `pilot-frozen.csv` are processed. The default
output is:

```text
study/manifests/file-classification/
<namespace>__<repository>__<full-commit-sha>.csv
```

The schema is:

```text
project,commit_sha,path,file_class,document_type,parse_status,
classification_reason,loc,included,exclusion_reason
```

Only `production_ansible` starts with `included=true`. Every excluded YAML
remains visible with its class and reason.

### Safety

The scanner later requires complete YAML coverage, safe repository-relative
paths, controlled classes, explicit booleans, unique paths, classification
reasons, and exclusion reasons. A stale or partial manifest is rejected.

### Command and Nova result

```bash
.venv/bin/python scripts/classify_study_files.py \
  study/manifests/pilot-frozen.csv \
  --limit 1
```

The frozen Nova role produced 122 rows: 28 production Ansible, 8 test Ansible,
84 documentation/example, 1 CI YAML, and 1 excluded internal symlink alias.
Exactly 28 rows are included.

## Active script: `run_study_pilot.py`

### Responsibility

Run a technical AnsibleGuard scan against exactly the commit recorded in the
frozen manifest.

### Input

The frozen CSV produced by `clone_study_repositories.py`. Only rows with:

```text
status=collected
```

are processed.

### Safety check

Before scanning, it runs:

```text
git rev-parse HEAD
```

and compares the result with `commit_sha`. A mismatch stops that project. This
prevents a developer checkout or later fetch from silently changing the study
input.

### Execution

Conceptually it runs:

```bash
python -m ansibleguard.cli <repository> \
  --output <snapshot-directory> \
  --fail-on never \
  --profile <profile>
```

`--fail-on never` is intentional for data collection: findings are study data,
not a reason to abort the scan. Actual process failures still cause the runner
to fail.

With `--file-manifests-dir`, the runner resolves the exact project/SHA CSV and
passes `--file-manifest` to AnsibleGuard. A missing manifest stops the project.
With `--skip-existing`, it also requires the existing output's recorded
manifest hash to match; technical or differently classified output is rejected.
Profile provenance must also match.

### Output organization

```text
study/snapshots/<project-with-double-underscore>/<full-sha>/
study/logs/<project>__<short-sha>.log
```

For nontechnical profiles, the runner appends `<profile>/` below the SHA and
adds the profile to the log name. Results cannot overwrite one another.

Using the full SHA prevents output from different snapshots overwriting each
other.

### Resume behavior

With `--skip-existing`, a snapshot containing `findings.json` is not rerun.
Without it, output may be regenerated for the same SHA.

### Commands

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv

.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --skip-existing

.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --limit 1 \
  --file-manifests-dir study/manifests/file-classification \
  --profile snapshot-source \
  --output-root study/analysis/profiled-snapshots
```

### Current limitation

Without `--file-manifests-dir`, the runner may still use recursive selection.
Without `--profile`, it defaults to `technical-full`. Research runs require
both a classified manifest and an explicit source profile. The provisional
core is not publishable until manual calibration and supervisor approval.

## Active script: `validate_detector_corpus.py`

### Responsibility

Run source detector bundles over the small YAML corpus already stored under
`TestData/projects`. This is developer regression/candidate-rate validation,
not OpenStack project collection.

### Detector families

It invokes:

- paper-derived candidates;
- review-checklist source rules;
- strengthened partial rules;
- formerly missing checklist rules;
- missing/unused handlers;
- missing tags;
- deprecated modules;
- disabled certificate validation;
- shell/native-module alternatives.

### Output

JSON containing:

- corpus path;
- YAML-file count;
- files processed;
- finding and affected-file counts by metric;
- up to five samples per active metric.

### Command

```bash
.venv/bin/python scripts/validate_detector_corpus.py TestData/projects
```

### Why this remains separate

The bundled corpus is fast and reproducible, making it useful during detector
development. It has no complete ground-truth labels, so it cannot establish
precision or recall and does not replace the OpenStack calibration sample.

## Manifest relationships

### `study/manifests/candidates.csv`

Generated discovery snapshot. No row is automatically selected.

### `study/manifests/pilot.csv`

Versioned human decision selecting the five heterogeneous pilot projects.

### `study/manifests/pilot-frozen.csv`

Generated machine-local result with absolute clone paths and frozen SHAs. It is
ignored by Git. Stable SHAs intended for sharing should later be copied into a
portable lock manifest without absolute paths.

### `study/manifests/file-classification/*.csv`

Portable rows keyed by project and full SHA. They use repository-relative
paths only. The CLI records the exact CSV SHA-256 in `file_selection.json`.

## Local verification of scripts

### Syntax

```bash
python -m py_compile \
  scripts/discover_openstack_ansible.py \
  scripts/clone_study_repositories.py \
  scripts/classify_study_files.py \
  scripts/run_study_pilot.py \
  scripts/validate_detector_corpus.py
```

### Focused tests

```bash
.venv/bin/pytest -q \
  tests/test_study_scripts.py \
  tests/test_file_manifest.py \
  tests/test_profiles.py
```

The tests cover:

- OpenStack-only discovery;
- retirement detection;
- no automatic selection;
- deterministic manifest writing;
- cloning a local Git fixture;
- exact SHA freezing;
- production/test/other YAML inventory;
- complete row-level classification and reasons;
- incomplete/unsafe manifest rejection;
- included-only CLI behavior and selection provenance;
- refusing a checkout whose HEAD moved;
- pilot command/output behavior.
- complete/disjoint profile-family mapping;
- source/review/external stage separation;
- profile-specific paths and resume provenance.

### Full regression

```bash
.venv/bin/pytest -q
```

Current result: 163 passing tests.

### Offline reproducibility

```bash
.venv/bin/python scripts/discover_openstack_ansible.py --offline \
  --output /tmp/candidates.csv
diff -u study/manifests/candidates.csv /tmp/candidates.csv
```

## Security rules for every study script

- credentials come from environment variables, never literals;
- credentials are never written to manifests/logs;
- URLs and paths are parameters rather than user-specific constants;
- network calls use timeouts and bounded retries;
- raw inputs are cached for provenance;
- generated repositories/results remain outside version control;
- failures are recorded and produce nonzero exit status;
- scripts never delete repositories automatically;
- destructive Git reset/cleanup is not part of the workflow.

## How to add the next study scripts

Every new script must include:

1. one clear responsibility;
2. `argparse` CLI with non-user-specific defaults;
3. importable functions for offline testing;
4. deterministic structured output;
5. explicit input/output schema;
6. resume or cache behavior for expensive work;
7. provenance: project, SHA, timestamp, tool/config version;
8. bounded network/subprocess behavior;
9. recorded failures rather than silent skipping;
10. tests using fixtures, not live network dependencies;
11. documentation here and in the local workflow;
12. generated-output ignore rules.

The classified generator and profile-aware pilot runner are complete.
Remaining planned scripts include:

- project symbol-index builder;
- finding sampler and labeling exporter;
- unique-occurrence normalizer;
- longitudinal Git/blob miner;
- Gerrit review/bug collector;
- statistical analysis generator.

## Troubleshooting

### Discovery cannot resolve OpenDev

Use the cache:

```bash
.venv/bin/python scripts/discover_openstack_ansible.py --offline
```

If no cache exists, establish network access once and run the online command.

### Clone failed

Read the `error` field in the frozen manifest. Confirm the OpenDev URL and
network access. Rerun with `--refresh` only when updating remote refs is
intended.

### Pilot says HEAD moved

Do not override the check. Either restore the frozen commit:

```bash
git -C <repository-path> checkout --detach <commit-sha>
```

or deliberately collect a new frozen manifest.

### Output already exists

Use `--skip-existing` to resume. Delete/move an output directory manually only
when intentionally regenerating it; the runner does not destroy results.

### Finding count is unexpectedly large

Inspect rule distribution and file classes before interpreting it. A dominant
rule or non-Ansible files indicate calibration/classification work, as the
first Nova-role pilot demonstrated.
