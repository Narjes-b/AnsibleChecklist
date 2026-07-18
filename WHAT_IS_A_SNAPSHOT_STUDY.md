# What a snapshot study means in this project

## Short definition

A snapshot is the complete source state of one repository at one immutable Git
commit.

In this study, a snapshot is **not** a screenshot, a backup folder, the latest
moving branch, a pull request, or the repository's full history. It is:

```text
one project + one exact commit SHA + one file-selection manifest
+ one frozen rule profile/configuration
```

The snapshot question is:

> Which source-code smells are present in the selected production Ansible files
> at this exact repository state?

## Why the commit must be frozen

Branches such as `master` move. If a project is scanned today and again after a
merge, counts may change even though the command is identical. A 40-character
commit SHA identifies immutable Git content.

The collector records the SHA and checks out detached HEAD. The classifier and
pilot runner refuse to continue when the current checkout does not match the
frozen value.

For the current pilot:

```text
openstack/openstack-ansible-os_nova
e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

## Why a snapshot needs a file manifest

A repository can contain production Ansible, tests, CI configuration, release
notes, examples, generated content, and unrelated YAML. “All `.yaml` files” is
not a scientifically meaningful production-Ansible population.

The manifest records every YAML candidate and explicitly answers:

- what kind of file is this?;
- why was it assigned that class?;
- is it included in the production snapshot?;
- why was it excluded?;
- what is its LOC and parse/document type?

For Nova, 122 YAML candidates become 28 included production Ansible files. The
same 28 files form both the scan input and the prevalence denominator.

## Why a snapshot needs a source profile

Some findings describe a file at a commit. Others describe a change between
commits.

| Snapshot/source question | Review-range question |
|---|---|
| Is this expression complex? | Did the change add a release note? |
| Is this task file too large? | Did configuration change with no test update? |
| Does this task leak a credential to logs? | Is a commit message formatted correctly? |
| Is a role dependency broken at this SHA? | Was a copyright line removed from base to head? |

Only the left column belongs in snapshot prevalence. The
`snapshot-source` profile prevents right-column rules from entering that result.

## The snapshot evidence chain

```text
OpenDev project identity
        ↓
frozen 40-character commit SHA
        ↓
complete row-level YAML classification
        ↓
included production-Ansible paths
        ↓
snapshot/research rule allowlist
        ↓
normalized findings
        ↓
manual validation
        ↓
prevalence/co-occurrence evidence
```

Skipping any step weakens the claim. A raw scanner message is not automatically
a validated research finding.

## The three source views

### `snapshot-source`

Contains all 51 internal source rules. It is useful for calibration and seeing
which detectors dominate. It is not the primary research dataset.

### `research-core`

Contains a conservative eight-rule allowlist. It is still provisional pending
manual validation and supervisor approval. Its purpose is to make the intended
primary construct set explicit and hashable.

### `extended-ansible`

Contains the 43 other internal source rules. It is disjoint from core, allowing
secondary Ansible-specific results without changing primary research counts.

## What is excluded from a snapshot

- commit-message and trailer quality;
- release-note co-change requirements;
- test/override co-change requirements;
- copyright diffs;
- GitHub pull-request counts;
- aggregate ansible-lint/GitLeaks findings until native identity policy is
  frozen;
- test, documentation, CI, release-note, and other nonproduction YAML files;
- dynamic facts that cannot be inferred from source without explicit modeling.

Excluded does not mean useless. It means the evidence answers a different
research or engineering question.

## Exact snapshot command

```bash
cd /home/aymmzn/Documents/AnsibleChecklist

.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --limit 1 \
  --file-manifests-dir study/manifests/file-classification \
  --profile snapshot-source \
  --output-root study/analysis/profiled-snapshots \
  --logs-dir study/logs/profiled
```

For the provisional primary set, replace `snapshot-source` with
`research-core`.

## What to verify after a run

Open these files in this order:

1. `file_selection.json` — correct manifest, 122 candidates, 28 included;
2. `run_metadata.json` — correct profile, rule hash, commit, and tool statuses;
3. `diagnostics.json` — no unexplained parser/tool failures;
4. `summary.csv` — exactly the intended analyzed file population;
5. `findings.csv` or `findings.json` — rule counts and individual evidence;
6. `review_metrics.json` — must be `{}` for source snapshot profiles.

## Current Nova interpretation

The snapshot-source run has 1,091 findings, of which 816 are
`unguarded-variable`. This is not evidence that Nova contains 816 genuine
variable defects. It is evidence that this detector needs project-level
variable resolution and manual precision calibration.

The provisional core has 78 findings: 40 long statements and 38 complex
expressions. These also require manual validation before publication.

## What a snapshot cannot tell us

A snapshot cannot establish:

- when a smell was introduced;
- how long it survived;
- whether it caused a defect;
- whether reviewers discussed it;
- whether it increases change-proneness;
- whether a later commit fixed it;
- causal relationships.

Those questions require longitudinal Git history, Gerrit review data, labels,
and appropriate statistical designs. They belong after snapshot validity is
established.
