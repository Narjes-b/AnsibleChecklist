# Local OpenStack Ansible study workflow

> **Output v2 note:** Fresh technical-full results use
> `study/analysis/five-project-technical-full-v2/` and start at each
> repository's `summary/report.json`. See
> `FIVE_REPOSITORY_OUTPUT_V2_FINAL_RESULTS.md`.

For the decision rationale, evidence gates, and detector-calibration work, see
[RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md](RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md).
For a function-by-function account of the supplied and active scripts, see
[STUDY_SCRIPTS_REFERENCE.md](STUDY_SCRIPTS_REFERENCE.md).
For the meaning of snapshot evidence and the implemented rule strata, see
[WHAT_IS_A_SNAPSHOT_STUDY.md](WHAT_IS_A_SNAPSHOT_STUDY.md) and
[RESEARCH_PROFILES_IMPLEMENTATION.md](RESEARCH_PROFILES_IMPLEMENTATION.md).

## Senior recommendation

Start with repository discovery and a small technical pilot, but do not scan
all candidate projects yet. The correct sequence is:

1. discover and review candidates;
2. clone and freeze one repository;
3. verify file classification and detector behavior;
4. fix/calibrate the research scan profile;
5. repeat on five repositories;
6. run manual precision validation;
7. only then collect the main corpus.

This is an Ansible-specific extension inspired by the Puppet paper, not a
strict replication. Puppet constructs remain useful background, but the final
research rule set must be validated against Ansible semantics.

## What is implemented now

### Discovery

`scripts/discover_openstack_ansible.py` downloads the authoritative OpenDev
project registry, caches it, selects likely Ansible project families, marks
retired repositories, and writes a reviewable manifest. It never automatically
selects a project.

Current discovery snapshot:

- 150 candidate repositories;
- 81 active candidates;
- 69 retired candidates retained for audit but excluded by default;
- all five pilot projects were present and active.

### Collection

`scripts/clone_study_repositories.py` reads only rows with `selected=true`,
performs full clones, checks out a detached immutable commit, classifies YAML,
and writes a frozen local manifest containing the exact SHA and inventory.

### Pilot runner

`scripts/run_study_pilot.py` reads the frozen manifest, verifies that repository
`HEAD` still equals the recorded SHA, runs AnsibleGuard, and stores output under
`study/snapshots/<project>/<sha>/`. It refuses to analyze a moved checkout.

## Environment setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m spacy download en_core_web_lg
python -c "import nltk; nltk.download('wordnet')"
ansibleguard install-tools
```

Confirm the tool before any study command:

```bash
.venv/bin/pytest -q
.venv/bin/python -m ansibleguard.cli --help
```

## Step 1 — refresh discovery

Online:

```bash
.venv/bin/python scripts/discover_openstack_ansible.py
```

This writes:

```text
study/manifests/candidates.csv
```

The downloaded registry is cached locally. To reproduce discovery without a
network request:

```bash
.venv/bin/python scripts/discover_openstack_ansible.py --offline \
  --output /tmp/openstack-ansible-candidates.csv
```

Never bulk-change every active row to `selected=true`. Review descriptions,
groups, retirement status, and actual Ansible content first.

## Step 2 — use the technical pilot

The versioned pilot manifest is:

```text
study/manifests/pilot.csv
```

It currently selects:

1. `openstack/openstack-ansible-os_nova`;
2. `openstack/openstack-ansible`;
3. `openstack/kolla-ansible`;
4. `openstack/kayobe`;
5. `openstack/ansible-collection-kolla`.

The role repository is first because it provides a smaller, faster end-to-end
check before downloading the larger integrated projects.

## Step 3 — collect one repository

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/pilot.csv \
  --limit 1 \
  --output study/manifests/pilot-frozen.csv
```

Review the frozen row:

```bash
column -s, -t study/manifests/pilot-frozen.csv | less -S
```

Expected guarantees:

- `status=collected`;
- a 40-character `commit_sha`;
- nonzero commit/contributor counts;
- production/test/other YAML counts;
- `repository_path` points to an ignored local clone;
- the repository is in detached-HEAD state at the frozen SHA.

To refresh remote refs before freezing a new dataset:

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/pilot.csv \
  --refresh \
  --limit 1 \
  --output study/manifests/pilot-frozen.csv
```

Do not use `--refresh` when reproducing an already frozen experiment. Put the
recorded SHA into the manifest's `revision` column instead.

## Step 4 — run the technical scan

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv
```

Resume without rerunning completed output:

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --skip-existing
```

Outputs are organized as:

```text
study/snapshots/
└── openstack__openstack-ansible-os_nova/
    └── <commit-sha>/
        ├── summary.csv
        ├── findings.json
        ├── findings.csv
        ├── findings.txt
        ├── findings.sarif
        ├── diagnostics.json
        ├── review_metrics.json
        └── mirrored per-file reports
```

Logs are stored under `study/logs/`.

## First real-pilot result

The collection and scan workflow was exercised on
`openstack/openstack-ansible-os_nova` at:

```text
e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

Collection inventory:

| Metric | Result |
|---|---:|
| Total commits | 1,482 |
| Contributors | 162 |
| YAML files | 122 |
| Classified production Ansible | 28 |
| Classified test Ansible | 8 |
| Other YAML | 86 |
| Invalid YAML | 0 |
| Production Ansible physical LOC | 2,465 |

Technical scan:

| Metric | Result |
|---|---:|
| Files discovered by current CLI | 122 |
| Structurally analyzed | 25 |
| Findings | 1,175 |
| Errors | 50 |
| Warnings | 949 |
| Notes | 176 |
| Diagnostics | 0 |
| `unguarded-variable` findings | 823 |

The run completed cleanly, including GitLeaks and ansible-lint, but these
numbers are **not research results**.

## Step 4A — generate the classified research input

Generate one explained row for every YAML file at the frozen SHA:

```bash
.venv/bin/python scripts/classify_study_files.py \
  study/manifests/pilot-frozen.csv \
  --limit 1
```

The Nova manifest under `study/manifests/file-classification/` contains 122
rows and includes exactly 28 production Ansible files. Every excluded row has
a class and reason.

## Step 4B — run the classified scan separately

Do not overwrite the original technical baseline:

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --limit 1 \
  --file-manifests-dir study/manifests/file-classification \
  --output-root study/analysis/classified-snapshots \
  --logs-dir study/logs/classified
```

Observed comparison:

| Metric | Technical baseline | Classified scan |
|---|---:|---:|
| YAML files processed | 122 | 28 |
| Structurally analyzed | 25 | 20 |
| Findings | 1,175 | 1,111 |
| `unguarded-variable` | 823 | 816 |

Check `file_selection.json` in the output before interpreting findings. It
must report 122 candidates, 28 included files, the expected project/SHA, and a
64-character manifest hash.

## Step 4C — run separated snapshot/core/review profiles

Profile separation is implemented. Run each profile into the same root; the
runner creates separate subdirectories and logs:

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --limit 1 \
  --file-manifests-dir study/manifests/file-classification \
  --profile snapshot-source \
  --output-root study/analysis/profiled-snapshots \
  --logs-dir study/logs/profiled
```

Repeat with `research-core`, `extended-ansible`, and `review-range`.

Observed results:

| Profile | Source files processed | Findings | Review metrics |
|---|---:|---:|---|
| `snapshot-source` | 28 | 1,091 | empty |
| `research-core` | 28 | 78 | empty |
| `extended-ansible` | 28 | 1,013 | empty |
| `review-range` | 0 | 3 | populated |

Verify `run_metadata.json`: profile name/hash must match, and source profiles
must show GitLeaks/ansible-lint as `not-requested`.

## Why we must stop before the five-project scan

The first pilot exposed two validity problems:

1. the study classifier found only 28 production and 8 test Ansible files, but
   the current CLI scanned all 122 YAML files, including Zuul/project YAML;
2. after correct file selection, `unguarded-variable` still contributes 816 of
   1,111 findings, indicating that
   OpenStack role variables loaded through includes, inventory, or runtime
   conventions are not sufficiently resolved.

Scaling now would multiply detector false positives. Before the complete
pilot, continue with:

- manual validation of a stratified classification sample;
- preservation or separation of native ansible-lint rule IDs;
- cross-file/OpenStack-aware variable resolution and precision sampling.

## Step 5 — expand to five repositories only after that gate

When the research profile and variable calibration are ready:

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/pilot.csv \
  --refresh \
  --output study/manifests/pilot-frozen.csv

.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --skip-existing
```

Do not select the 81 active candidates until all five pilot projects pass the
classification, runtime, diagnostics, and manual-precision gates.

## Local test layers before a PR

Run tests from cheapest to most expensive.

### Layer A — syntax and focused study tests

```bash
python -m py_compile \
  scripts/discover_openstack_ansible.py \
  scripts/clone_study_repositories.py \
  scripts/classify_study_files.py \
  scripts/run_study_pilot.py

.venv/bin/pytest -q \
  tests/test_study_scripts.py \
  tests/test_file_manifest.py \
  tests/test_profiles.py
```

### Layer B — complete regression suite

```bash
.venv/bin/pytest -q
```

### Layer C — offline discovery reproducibility

```bash
.venv/bin/python scripts/discover_openstack_ansible.py --offline \
  --output /tmp/candidates.csv
diff -u study/manifests/candidates.csv /tmp/candidates.csv
```

The timestamps will remain stable because offline mode uses the cache mtime.
If comparing against an older committed discovery snapshot, review expected
registry changes rather than overwriting them blindly.

### Layer D — real one-project smoke test

Run the one-repository collection and pilot commands from Steps 3 and 4. Check:

- no collection failure;
- exact frozen SHA;
- zero unexpected diagnostics;
- expected report files exist;
- no repository or generated-output directory appears in `git status`.

### Layer E — final change review

```bash
git diff --check
git status --short
git diff --stat
```

Review the scripts, tests, versioned manifests, and documentation. Do not add
`study/repositories`, `study/snapshots`, `study/logs`, caches, or machine-local
frozen manifests.

## Recommended PR organization

Keep research infrastructure separate from detector calibration:

### PR 1 — collection foundation

- OpenDev-first discovery;
- reviewable candidate and pilot manifests;
- clone/SHA-freeze collector;
- technical pilot runner;
- offline tests and workflow documentation.

### PR 2 — research scan profile

- classified file inputs;
- snapshot/review profile separation;
- native external rule identity;
- study-friendly output schema.

### PR 3 — OpenStack detector calibration

- cross-file variable resolution;
- manually labeled findings;
- precision results and justified rule/threshold changes.

### PR 4 — full five-project pilot

- frozen SHAs and environment lock;
- runtime/diagnostic report;
- approved main-corpus selection decision.

This separation keeps collection mechanics reviewable and prevents early pilot
observations from being presented as finalized empirical findings.
