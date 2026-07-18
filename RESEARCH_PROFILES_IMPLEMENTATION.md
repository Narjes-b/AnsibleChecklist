# Research scan profiles: implementation and Nova validation

## Outcome

AnsibleGuard now separates five different questions through explicit execution
profiles. A frozen source snapshot can no longer silently contain commit-range
review findings, and the provisional research core can no longer silently grow
when a new detector is added to the technical catalog.

Use:

```bash
ansibleguard <target> --profile <profile-name>
```

The profile name, exact ordered rule list, rule-list SHA-256, execution flags,
and tool statuses are written to `run_metadata.json`.

`snapshot-source`, `research-core`, and `extended-ansible` require
`--file-manifest`. The CLI refuses to run them with recursive source discovery.

## Why filtering by file manifest was not enough

The classified manifest fixed which YAML files enter a scan. It did not fix
which questions are mixed in the result. The previous technical scan could
still combine:

- source properties at one commit;
- GitLeaks and ansible-lint output;
- release-note and test co-change checks;
- commit-message rules;
- copyright differences between commits.

A release-note omission is a property of a change range, not a property of
`tasks/main.yml` at one frozen state. Combining it with source smells makes
prevalence and co-occurrence tables scientifically ambiguous.

## Implemented profiles

| Profile | Rules | Source parsing | Review range | External tools | Intended use |
|---|---:|---:|---:|---:|---|
| `technical-full` | 60 | yes | yes | yes | Development, CI, diagnostics |
| `snapshot-source` | 51 | yes | no | no | Calibrate all internal source detectors at one commit |
| `research-core` | 8 | yes | no | no | Provisional primary construct set |
| `extended-ansible` | 43 | yes | no | no | Secondary Ansible-specific source results |
| `review-range` | 7 | no | yes | no | Base-to-head commit/review evaluation |

`research-core` and `extended-ansible` are disjoint. Their union is
`snapshot-source`. The two external aggregate rules are technical-only until
native identity and study policy are implemented.

## The provisional research core

The versioned v1 allowlist is:

- `complex-expression`;
- `incomplete-task`;
- `long-statement`;
- `unstructured-module`;
- `empty-abstraction`;
- `excessive-nesting`;
- `missing-abstraction`;
- `broken-role-dependency`.

These are the stable paper-derived source candidates. This list is
**provisional**, not supervisor-approved final evidence. `run_metadata.json`
records:

```text
status=provisional-pending-manual-calibration
research_eligible=false
```

The setting prevents the existence of a profile from being mistaken for
completion of manual validation.

`unguarded-variable` deliberately remains in `extended-ansible`. The Nova run
still produces 816 occurrences because the detector cannot yet resolve all
role defaults, included vars, inventory, and runtime inputs across files.

## Review-range rules

Only these rules enter `review-range`:

- `missing-release-note`;
- `missing-bug-reference`;
- `invalid-depends-on-reference`;
- `commit-message-format`;
- `removed-copyright-notice`;
- `missing-test-update`;
- `untested-override-change`.

This profile discovers/validates the requested file population for provenance
but processes zero YAML files through source detectors. It evaluates Git
history over `ANSIBLEGUARD_BASE_SHA...ANSIBLEGUARD_HEAD_SHA`, or the documented
local fallback when those variables are absent.

## External tools

`technical-full` runs GitLeaks and ansible-lint. The four research-oriented
profiles do not invoke them and record both statuses as `not-requested`.

This is intentional:

- `ansible-lint-issue` currently aggregates multiple native lint rules;
- GitLeaks secret subtypes are not yet represented as research constructs;
- external-tool versions and identities require a separate freeze policy;
- their absence must not be reported as a tool failure.

Internal security rules such as `credentials-leaking-in-log`,
`insecure-permissions`, and `default-credentials` remain source rules and are
available in `snapshot-source`/`extended-ansible`.

## Implementation

[`src/ansibleguard/profiles.py`](src/ansibleguard/profiles.py) owns:

- profile names and descriptions;
- the review/external/core/extended rule sets;
- complete catalog-partition validation;
- finding filtering;
- scientific family lookup;
- deterministic profile metadata and hashes.

Module import fails if a catalog rule is unassigned or the core and extended
sets overlap. Therefore, adding rule 61 requires an explicit scientific-family
decision rather than silently changing results.

[`src/ansibleguard/cli.py`](src/ansibleguard/cli.py) now:

1. validates the profile;
2. selects files using recursive discovery or a classification manifest;
3. decides whether source, review, and external stages should execute;
4. applies ordinary project suppressions;
5. applies the profile allowlist before every per-file/project rollup;
6. writes profile-consistent JSON, CSV, text, and SARIF results;
7. writes `run_metadata.json`.

[`scripts/run_study_pilot.py`](scripts/run_study_pilot.py) accepts `--profile`,
places nontechnical results under a profile-specific directory, gives each
profile a separate log, and validates both manifest and profile provenance
before resume mode skips output.

## Output organization

```text
study/analysis/profiled-snapshots/
└── openstack__openstack-ansible-os_nova/
    └── <full-sha>/
        ├── snapshot-source/
        ├── research-core/
        ├── extended-ansible/
        └── review-range/
```

This prevents one profile from overwriting or being resumed as another.

## Exact commands

```bash
cd /home/aymmzn/Documents/AnsibleChecklist

.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --limit 1 \
  --file-manifests-dir study/manifests/file-classification \
  --profile snapshot-source \
  --output-root study/analysis/profiled-snapshots \
  --logs-dir study/logs/profiled

.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --limit 1 \
  --file-manifests-dir study/manifests/file-classification \
  --profile research-core \
  --output-root study/analysis/profiled-snapshots \
  --logs-dir study/logs/profiled
```

Replace the profile with `extended-ansible` or `review-range` for the other
strata. Use `--skip-existing` only when the recorded manifest and profile
metadata match.

## Frozen Nova evidence

Input:

```text
project: openstack/openstack-ansible-os_nova
commit:  e06c7bceef3f7c365828116b7aadea6fc2d3e22b
selected production files: 28 of 122 YAML candidates
```

| Profile/run | Source files processed | Findings | Review findings | External tools |
|---|---:|---:|---:|---|
| Original technical baseline | 122 | 1,175 | mixed | executed |
| Classified technical | 28 | 1,111 | mixed | executed |
| `snapshot-source` | 28 | 1,091 | 0 | not requested |
| `research-core` | 28 | 78 | 0 | not requested |
| `extended-ansible` | 28 | 1,013 | 0 | not requested |
| `review-range` | 0 | 3 | 3 | not requested |

The core and extended counts sum to the snapshot count: `78 + 1,013 = 1,091`.
That equality demonstrates disjoint source strata.

The provisional core contains:

| Rule | Findings |
|---|---:|
| `long-statement` | 40 |
| `complex-expression` | 38 |

The review-range run found one missing release note, one missing test update,
and one untested override change in the latest local commit range. None appears
in snapshot output.

## Verification

Tests cover:

- complete one-family assignment for all 60 catalog rules;
- disjoint core/extended sets;
- snapshot exclusion of review and external rules;
- external/review stages not executing under snapshot mode;
- review-range processing Git evidence without source/external execution;
- profile metadata and rule hashes;
- profile-specific study output directories;
- output contract for `run_metadata.json`.

## Remaining work

Profile separation fixes experimental boundaries; it does not validate detector
precision. Before the five-project pilot:

1. manually validate the Nova file-classification sample;
2. build a project symbol index;
3. calibrate `unguarded-variable` and decide whether it can enter core;
4. manually label core findings and negative examples;
5. preserve native external rule identity;
6. normalize and deduplicate occurrence exports;
7. obtain supervisor approval and freeze the final core rule hash.
