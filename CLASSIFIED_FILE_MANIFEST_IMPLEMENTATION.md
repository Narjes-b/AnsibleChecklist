# Classified file-manifest implementation

## Outcome

AnsibleGuard can now generate and consume an auditable, row-level file
classification manifest. This closes the first validity gap found by the real
OpenStack pilot: the research numerator and denominator can now use the same
explicit production-Ansible file population.

The implementation does not introduce research profiles or cross-file variable
resolution. Those remain separate tickets so that file-selection correctness
can be tested and reviewed independently.

## Why this ticket was necessary

The first scan of `openstack/openstack-ansible-os_nova` found 122 YAML files,
although the collector counted only 28 production Ansible files. The scan
therefore included release notes, Zuul configuration, tests, examples, and
other YAML in a result intended to describe production Ansible.

That creates a population mismatch:

```text
research numerator = findings from all YAML
research denominator = production Ansible files
```

No later statistical method can repair that mismatch. File selection must be
explicit before detector calibration or corpus expansion.

## What was implemented

### Shared classifier

[`src/ansibleguard/file_manifest.py`](src/ansibleguard/file_manifest.py) is now
the single owner of repository-level file classification. The collection
script uses this module for its aggregate counts, and the new manifest script
uses the same module for row-level evidence. This prevents two classifiers
from silently producing different populations.

The public operations are:

- `yaml_candidates()` — finds every `.yml` and `.yaml` candidate outside Git
  internals;
- `classify_yaml_file()` — assigns one class and an explicit reason;
- `classify_repository()` — produces deterministic rows sorted by path;
- `write_file_manifest()` — writes the stable CSV schema;
- `summarize_classification()` — derives collection counts from those rows;
- `included_files_from_manifest()` — validates a manifest and returns only
  selected files;
- `file_manifest_metadata()` — records manifest provenance in scan output.

### Generator script

[`scripts/classify_study_files.py`](scripts/classify_study_files.py) reads the
frozen repository manifest. For every `status=collected` row, it:

1. reads the repository path and expected commit SHA;
2. verifies that the checkout is still at exactly that SHA;
3. classifies every YAML candidate;
4. writes one per-project, per-SHA CSV;
5. reports total and included row counts.

The output name contains both project identity and the full commit SHA:

```text
study/manifests/file-classification/
  openstack__openstack-ansible-os_nova__<full-sha>.csv
```

This makes accidental reuse across revisions visible.

### CLI manifest input

The AnsibleGuard CLI now accepts:

```text
--file-manifest PATH
```

When this option is absent, recursive discovery remains backward compatible.
When it is present, the CLI scans only rows explicitly marked
`included=true`, after checking that the manifest describes the complete YAML
population currently present under the target.

### Pilot-runner integration

[`scripts/run_study_pilot.py`](scripts/run_study_pilot.py) now accepts:

```text
--file-manifests-dir PATH
```

For each frozen project, it resolves the manifest using the project name and
full SHA, refuses to continue if that file is missing, and passes the exact
manifest to AnsibleGuard. Resume mode verifies the existing output's recorded
manifest hash before skipping it, so a recursive baseline cannot masquerade as
a completed classified scan.

## Manifest schema

Every YAML candidate has exactly one row:

| Column | Meaning |
|---|---|
| `project` | OpenDev/Git project identity |
| `commit_sha` | Immutable source revision |
| `path` | POSIX repository-relative YAML path |
| `file_class` | Exactly one controlled classification |
| `document_type` | Safe YAML/Ansible document-shape result |
| `parse_status` | Parsed, invalid, unsupported, empty, or not inspected |
| `classification_reason` | Stable rule explaining the class |
| `loc` | Nonblank, non-comment physical lines |
| `included` | Explicit `true`/`false` scan decision |
| `exclusion_reason` | Required reason when `included=false` |

Supported classes are:

- `production_ansible`;
- `test_ansible`;
- `ci_yaml`;
- `documentation_example`;
- `generated_or_vendor`;
- `other_yaml`;
- `invalid_yaml`;
- `vault_encrypted`;
- `unclear`.

The primary snapshot currently includes only `production_ansible`. Test files
remain represented in the manifest so later test/co-change analyses can use a
known population without mixing them into production prevalence.

## Classification order and rationale

Classification uses explicit rules in this order:

1. do not follow YAML symlinks blindly;
2. exclude generated/vendor paths;
3. identify CI and Zuul paths;
4. identify documentation, examples, and release notes;
5. identify Ansible data/template paths that are not executable source;
6. record invalid/read-error YAML;
7. identify fully encrypted Vault documents;
8. identify test and Molecule paths;
9. identify playbook/task document shapes;
10. use precise role/inventory path context for vars, metadata, and empty
    Ansible source files;
11. classify unsupported shapes as unclear;
12. classify the remainder as other YAML.

Path context is intentionally narrower than “anything below `roles/`.” For
example, a YAML file under a role's `files/` or `templates/` directory is data
or a rendered template, not an Ansible task file.

Internal YAML symlink aliases are excluded with
`symlink_alias_to_repository_file`. Scanning both the alias and its target
would double-count identical source content. Broken or external symlinks stay
`unclear` and are never followed automatically.

## Safety and validity checks

A manifest scan fails before analysis when:

- a required column is absent;
- an `included` value is not an explicit true/false value;
- a path is absolute, contains `..`, or resolves outside the target;
- a path appears more than once;
- a class is outside the controlled vocabulary;
- a classification reason is empty;
- an excluded row has no exclusion reason;
- a YAML file exists in the repository without a manifest row;
- a manifest row names a YAML file no longer present;
- an included path is not a real YAML file.

The completeness comparison is essential. Without it, a stale manifest could
silently omit newly added YAML and still appear valid.

## Output provenance

Every scan now writes `file_selection.json`.

For ordinary scans it records:

```json
{"mode": "recursive-discovery"}
```

For manifest scans it records:

- absolute manifest path;
- SHA-256 of the exact CSV bytes;
- total candidate rows;
- number of included files;
- counts by file class;
- project identities;
- commit SHAs.

This allows a result directory to prove which selection artifact produced it.

## Exact local commands

Generate the Nova classification manifest from the already frozen checkout:

```bash
cd /home/aymmzn/Documents/AnsibleChecklist

.venv/bin/python scripts/classify_study_files.py \
  study/manifests/pilot-frozen.csv \
  --limit 1
```

Run a classified scan without overwriting the original baseline:

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/pilot-frozen.csv \
  --limit 1 \
  --file-manifests-dir study/manifests/file-classification \
  --output-root study/analysis/classified-snapshots \
  --logs-dir study/logs/classified
```

Direct CLI usage is also supported:

```bash
.venv/bin/python -m ansibleguard.cli \
  study/repositories/openstack/openstack-ansible-os_nova \
  --file-manifest \
  study/manifests/file-classification/openstack__openstack-ansible-os_nova__e06c7bceef3f7c365828116b7aadea6fc2d3e22b.csv \
  --output /tmp/nova-classified \
  --fail-on never
```

## Real Nova result

Frozen input:

```text
project: openstack/openstack-ansible-os_nova
commit:  e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

Classification:

| Class | Rows | Included |
|---|---:|---:|
| `production_ansible` | 28 | 28 |
| `test_ansible` | 8 | 0 |
| `documentation_example` | 84 | 0 |
| `ci_yaml` | 1 | 0 |
| `other_yaml` | 1 | 0 |
| **Total** | **122** | **28** |

The single `other_yaml` row is an inspected in-repository symlink alias whose
target is already included. There are no unresolved rows in this repository.

Baseline versus classified scan:

| Measure | Technical baseline | Classified input |
|---|---:|---:|
| YAML files processed | 122 | 28 |
| Structurally analyzed | 25 | 20 |
| Findings | 1,175 | 1,111 |
| Errors | 50 | 49 |
| Warnings | 949 | 928 |
| Notes | 176 | 134 |
| `unguarded-variable` | 823 | 816 |

The selection gate passed: only the 28 intended production files entered the
YAML loop. The small reduction in `unguarded-variable` is also useful evidence:
its dominant false-positive risk is cross-file/runtime variable resolution,
not merely unrelated YAML selection.

The classified scan still contains project-level review checks and repository
external-tool behavior. Profile separation is the next ticket and must happen
before these findings become prevalence data.

## Tests

Focused tests cover:

- one explained row per YAML candidate;
- all controlled classes used by the fixture;
- deterministic production/test/other/invalid counts;
- complete-coverage validation;
- path-traversal rejection;
- included-only CLI processing;
- suppression of excluded-YAML GitLeaks results;
- selection-provenance output;
- frozen-SHA generation;
- pilot-runner manifest forwarding.

Run them with:

```bash
.venv/bin/python -m pytest \
  tests/test_file_manifest.py \
  tests/test_study_scripts.py \
  tests/test_cli.py \
  tests/test_cli_statuses.py \
  tests/test_output_contract.py -q
```

## Remaining gates

Before the five-project pilot:

1. manually review a stratified sample of production, test, documentation,
   CI, other, and any unclear rows;
2. ~~implement `snapshot-source`, `research-core`, `extended-ansible`, and
   `review-range` profile separation;~~ completed;
3. ~~exclude project review findings from snapshot prevalence;~~ completed;
4. build cross-file variable resolution and recalibrate
   `unguarded-variable`;
5. preserve native external-rule identity;
6. normalize and deduplicate research occurrences.

The next work is the stratified manual classification sample, followed by the
repository symbol index—not collection of more projects.
