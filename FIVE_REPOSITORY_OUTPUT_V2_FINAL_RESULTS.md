# Five-repository technical-full output v2 results

Related implementation records:

- `DEVELOPER_PROFILES_OVERLAP_PR_IMPLEMENTATION.md` — profiles, provenance,
  overlap, security, dependencies, and detector changes;
- `OUTPUT_CONTRACT_V2_SIX_CHANGES.md` — the six output changes implemented
  before this test;
- `PULL_REQUEST_TESTING_STEP_BY_STEP.md` — how to reproduce base/head PR
  behavior locally and in GitHub.

## Outcome

All five frozen OpenStack repositories completed a fresh `technical-full`
scan using output contract v2.

The final validated population was:

```text
5 repositories
1,856 manifest-selected production Ansible files
13,439 raw provider findings
10,927 canonical developer-visible occurrences
2,512 raw findings grouped with other evidence
18.69% raw-to-canonical reduction
0 diagnostics
```

This is evidence that the new output organization works at the five-project
scale. It is not a precision or recall claim.

## Pre-scan gate

The repository scan started only after:

```text
196 automated tests passed
Python source and scripts compiled
profile definitions validated
output schema JSON parsed
workflow YAML parsed
git diff --check passed
```

During the real-repository run, one additional manifest-cache regression test
was added. Final verification after all work is recorded in `README.md`.

## Exact frozen repositories

| Project | Frozen SHA | Selected files |
|---|---|---:|
| `openstack/openstack-ansible-os_nova` | `e06c7bceef3f7c365828116b7aadea6fc2d3e22b` | 28 |
| `openstack/openstack-ansible` | `b7c10cbcc04a06207c2344a312d4f612a0810939` | 216 |
| `openstack/kolla-ansible` | `9c41bdca79d4c7267beeece141909e679f70dea8` | 1,228 |
| `openstack/kayobe` | `9a6e4333b2aa2fbe8dc80a93cd5aa3e2f1872970` | 342 |
| `openstack/ansible-collection-kolla` | `785982d7c09dda3d8e46f6c9b09597ca14820497` | 42 |

The source of truth for paths and SHAs is:

```text
study/manifests/pilot-five-frozen.csv
study/manifests/file-classification/
```

## Result table

| Project | Raw | Canonical | Grouped reduction | Errors | Warnings | Notes | Diagnostics |
|---|---:|---:|---:|---:|---:|---:|---:|
| `ansible-collection-kolla` | 377 | 347 | 30 | 2 | 118 | 227 | 0 |
| `kayobe` | 3,711 | 3,130 | 581 | 211 | 1,374 | 1,545 | 0 |
| `kolla-ansible` | 7,817 | 6,525 | 1,292 | 235 | 2,273 | 4,017 | 0 |
| `openstack-ansible` | 733 | 452 | 281 | 2 | 278 | 172 | 0 |
| `openstack-ansible-os_nova` | 801 | 473 | 328 | 45 | 295 | 133 | 0 |
| **Total** | **13,439** | **10,927** | **2,512** | **495** | **4,338** | **6,094** | **0** |

Severity counts above are canonical occurrence severities. They are candidates
for review, not confirmed defects.

## Provider results

Raw provider totals:

```text
AnsibleGuard:  13,413
ansible-lint:      24
GitLeaks:           2
```

Both external tools reported `completed` for all five repositories.

Only Nova contributed ansible-lint findings:

```text
23 var-naming[no-role-prefix]
1 key-order[task]
```

This is explainable rather than a missing-tool failure. Four projects contain
their own `.ansible-lint` configurations and currently pass with those
project-specific skip/exclude rules. Nova has no project configuration, so the
default native rules produced 24 results.

This behavior differs from older AnsibleGuard output because ansible-lint now
runs from the scanned repository root and respects that repository's
configuration. The older absolute-target execution did not provide the same
project-local behavior.

GitLeaks produced two redacted findings:

- one in `kolla-ansible` documentation;
- one in `openstack-ansible` inventory variables.

These require human review. The persisted normalized reports contain rule,
description, location, and fingerprint identity, not the raw secret value.

## New-rule evidence

The five rules introduced with the profile/file-kind work produced:

| Rule | Count | Repositories |
|---|---:|---|
| `redirected-module` | 15 | `kayobe` |
| `unsafe-file-write` | 0 | none |
| `plaintext-sensitive-variable` | 5 | `kolla-ansible` (4), Nova (1) |
| `unpinned-ansible-dependency` | 3 | `kayobe` |
| `role-variable-precedence-collision` | 1 | `kolla-ansible` |

Zero findings does not mean a detector failed. Provider statuses, rule profile
membership, schema validation, and automated fixtures separately verify
execution.

## Canonical grouping evidence

Across all repositories:

```text
13,439 raw findings
- 2,512 additional overlapping detector/evidence records
= 10,927 canonical occurrences
```

There were 1,089 occurrences with more than one contributing raw finding.
Canonical grouping therefore reduced review volume without deleting evidence.

The largest common concepts included:

- missing tags;
- unguarded variables;
- long or large tasks;
- complex expressions;
- duplicate mapping keys;
- credential-log exposure.

The exact distribution is stored in each `summary/report.json` under
`counts.canonical_by_concept`.

## Output-contract validation

For every repository, the validation checked:

- `summary/report.json`;
- `summary/diagnostics.json`;
- `raw/findings.json`;
- `canonical/occurrences.json`;
- `metadata/run.json`;
- `metadata/file-selection.json`;
- `metadata/review-metrics.json`;
- `legacy/layout.json`.

Every document validated against:

```text
src/ansibleguard/report/schemas/output-v2.json
```

Additional invariants passed:

- legacy raw findings equal the v2 raw `items`;
- legacy occurrences equal the v2 occurrence `items`;
- report totals equal detailed JSON totals;
- per-file summary raw totals equal project raw totals;
- per-file summary canonical totals equal project canonical totals;
- all tool statuses are `completed`;
- all diagnostic arrays are empty.

## Manifest-cache issue discovered and fixed

The first attempt stopped before scanning `kayobe`. Its repository contained
runtime data under:

```text
.ansible/roles/
```

Normal CLI discovery already excluded `.ansible`, but manifest completeness
validation still treated those cached YAML files as repository candidates.
That made an older frozen manifest appear incomplete.

The fix:

- `file_manifest.yaml_candidates()` now excludes `.ansible`, matching the CLI;
- a regression test proves runtime cache YAML never enters classification;
- focused manifest, output-contract, and study-runner tests passed;
- the runner resumed with `--skip-existing`, preserving the three completed
  immutable results.

This was a useful real-repository finding: tool-generated cache must not change
the scientific source population.

## Result locations

Primary results:

```text
study/analysis/five-project-technical-full-v2/
```

Logs:

```text
study/logs/five-project-technical-full-v2/
```

Per repository, start with:

```text
<project>/<sha>/summary/report.json
<project>/<sha>/summary/summary.csv
<project>/<sha>/canonical/occurrences.txt
```

The complete output occupies approximately 145 MiB, mostly from preserved
per-file legacy reports. The organized project-level v2 files do not duplicate
those per-file directories.

## Reproduction command

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-five-frozen.csv \
  --file-manifests-dir study/manifests/file-classification \
  --profile technical-full \
  --output-root study/analysis/five-project-technical-full-v2 \
  --logs-dir study/logs/five-project-technical-full-v2
```

For an interrupted rerun:

```bash
...same command... --skip-existing
```

The runner verifies the frozen HEAD, profile identity, and classification
manifest hash before accepting an existing result.

## What these results do and do not prove

They prove:

- all six output changes work on five differently sized real repositories;
- v2 schemas and count invariants hold;
- compatibility aliases preserve data;
- canonical grouping materially reduces review volume;
- project-local ansible-lint configuration is respected;
- GitLeaks and ansible-lint failures remain distinguishable from clean runs.

They do not prove:

- that all 10,927 occurrences are true defects;
- precision or recall for any detector;
- that severity calibration is final;
- that `unguarded-variable` is ready to block PRs;
- that two GitLeaks candidates are exploitable secrets;
- that every Ansible repository shape is covered.

The next evidence step is stratified human labeling by repository, rule,
severity, and provider, followed by deciding whether to enable the `ratchet`
PR policy.
