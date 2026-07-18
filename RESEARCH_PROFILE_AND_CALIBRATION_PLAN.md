# Research profile and OpenStack detector-calibration plan

This decision document complements the full
[empirical-study plan](OPENSTACK_ANSIBLE_REAL_PROJECT_TESTING_PLAN.md), the
[local workflow](LOCAL_OPENSTACK_STUDY_WORKFLOW.md), and the complete
[study-script reference](STUDY_SCRIPTS_REFERENCE.md). New readers should begin
with [START_HERE.md](START_HERE.md); the snapshot boundary is explained in
[WHAT_IS_A_SNAPSHOT_STUDY.md](WHAT_IS_A_SNAPSHOT_STUDY.md).

## Executive decision

We will continue with an Ansible-specific empirical study inspired by the
Puppet paper. We will not treat it as a strict replication, and we will not
start by scanning every discovered OpenStack repository.

The chosen sequence is:

1. collect repositories reproducibly;
2. classify their files correctly;
3. introduce research-specific scan profiles;
4. calibrate detectors on real OpenStack code;
5. run a five-project pilot;
6. manually validate findings;
7. freeze the tool and configuration;
8. only then collect and analyze the main corpus.

This sequence protects the study from producing precise-looking statistics
from incorrectly selected files or poorly calibrated detectors.

## Why we chose this approach

### Evidence from the first real project

We successfully collected and scanned:

```text
Project: openstack/openstack-ansible-os_nova
Commit:  e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

Repository inventory:

| Measure | Result |
|---|---:|
| Commits | 1,482 |
| Contributors | 162 |
| YAML files | 122 |
| Classified production Ansible files | 28 |
| Classified test Ansible files | 8 |
| Other YAML files | 86 |
| Invalid YAML files | 0 |
| Production Ansible physical LOC | 2,465 |

Current technical scan:

| Measure | Result |
|---|---:|
| YAML files discovered by the CLI | 122 |
| Structurally analyzed files | 25 |
| Total findings | 1,175 |
| Error findings | 50 |
| Warning findings | 949 |
| Note findings | 176 |
| Diagnostics | 0 |
| `unguarded-variable` findings | 823 |

The pipeline completed without crashing. That demonstrates engineering
readiness for a pilot, but not research validity.

### Problem 1 — the denominator is wrong

The collector classified only 36 files as production or test Ansible, while
the current CLI discovered all 122 YAML files. The remaining files include
Zuul configuration, metadata, release material, and other YAML documents.

If we calculate smell prevalence using all YAML files, the denominator is not
“Ansible files.” If we calculate findings using all YAML files but divide by
only production files, the numerator and denominator describe different
populations. Either choice invalidates the result.

### Problem 2 — one rule dominates the result

`unguarded-variable` produced 823 of 1,175 findings, approximately 70% of the
technical output. OpenStack roles commonly load variables through:

- `include_vars`;
- `vars_files`;
- role defaults and role vars split across multiple files;
- group and host variables;
- inventory plugins;
- parent playbooks and integrated repositories;
- variables supplied by CI or deployment tooling.

The current rule cannot see every one of these sources. Scaling it unchanged
would mostly measure missing static context, not necessarily defective Ansible.

### Problem 3 — review rules and snapshot rules answer different questions

Snapshot prevalence asks, “What source smells are present in this repository
at this commit?” Git-aware rules ask, “Does this commit range contain a release
note, test update, valid commit message, or copyright preservation?”

Those are both useful, but mixing them creates invalid co-occurrence and
prevalence results. A missing release note is not a property of one Ansible
file at the frozen snapshot.

### Problem 4 — external aggregate findings lose scientific identity

AnsibleGuard currently normalizes all ansible-lint results under the general
`ansible-lint-issue` rule. That is useful for CI, but it combines multiple
different lint constructs into one research category. Scientific analysis
must preserve the native rule identity or keep external lint results separate.

## The evidence pipeline

A raw detector message is not automatically a research finding.

```text
OpenDev registry
    ↓
eligible repository
    ↓
frozen commit SHA
    ↓
classified Ansible file
    ↓
applicable research-profile rule
    ↓
normalized and deduplicated occurrence
    ↓
manually calibrated rule
    ↓
research evidence
```

Each transition must be recorded so exclusions can be audited.

## Important terms

### Candidate repository

A repository discovered through OpenDev names, descriptions, groups, or an
approved project-family seed. A candidate has not yet passed content/history
filters.

### Included repository

A candidate that is active, cloneable, contains sufficient production Ansible
content and history, and has an exact frozen commit SHA.

### Production Ansible file

A playbook, task file, handler, role defaults/vars/metadata file, inventory
variable file, or other approved Ansible artifact used to configure or deploy
the system. CI YAML, documentation examples, generated files, and unrelated
data YAML are not production Ansible.

### Test Ansible file

Ansible content under Molecule or project test paths. Tests are retained as a
separate stratum rather than silently discarded.

### Raw finding

One detector output before research filtering, deduplication, and validation.

### Research finding

A normalized raw finding from an included file, produced by an approved rule
under a frozen profile whose precision has been evaluated.

### Smelly file

An included file with at least one research finding from the analysis set being
reported. Replication-core and extended-Ansible findings must define separate
smelly-file flags.

## Implemented scan profiles

The five profiles below are implemented in `src/ansibleguard/profiles.py`.
Their exact rule IDs and hashes are written to `run_metadata.json`.

### `technical-full`

Purpose: engineering diagnostics and local CI.

Includes:

- all internal source rules;
- Git-aware review rules;
- GitLeaks;
- ansible-lint;
- all eligible YAML discovered by the current CLI.

This describes current behavior. It is not used for prevalence statistics.

### `snapshot-source`

Purpose: calibrating source detectors at a frozen repository snapshot.

Includes:

- internal file/source rules;
- role/repository structural rules that can be assigned to the snapshot;
- only explicitly classified production or test Ansible files.

Excludes:

- release-note and test co-change checks;
- commit-message rules;
- copyright diff rules;
- other base-to-head review metadata;
- aggregate external rules unless requested separately.

### `research-core`

Purpose: the main empirical analysis.

Includes only:

- supervisor-approved Ansible smell constructs;
- rules that passed calibration;
- frozen thresholds and configuration;
- production Ansible by default;
- test Ansible only in its separate result stratum.

The current eight-rule allowlist is versioned but explicitly provisional. It
records `research_eligible=false` until manual calibration and supervisor
approval. It must not change after the main dataset run begins.

### `extended-ansible`

Purpose: report useful Ansible-specific security, reliability, correctness, and
maintainability findings that are outside the core constructs.

These results may become a secondary contribution, but they must not silently
alter the core research questions.

### `review-range`

Purpose: PR/Gerrit/commit-range evaluation.

Includes:

- release notes;
- bug and dependency trailers;
- commit formatting;
- copyright preservation;
- production/test co-changes;
- other review-specific evidence.

This profile is useful for the eventual review bot, not snapshot prevalence.

## Work package 1 — classified scan inputs

**Implementation status:** code-complete and exercised on the frozen Nova role.
Automated completeness and safety checks pass. A stratified human sample is
still required before the five-project pilot.

### Goal

Make the files scanned for research identical to the files counted in the
research denominator.

### Required output

Create one row per YAML candidate:

```text
project,commit_sha,path,file_class,document_type,parse_status,
classification_reason,loc,included,exclusion_reason
```

Proposed `file_class` values:

- `production_ansible`;
- `test_ansible`;
- `ci_yaml`;
- `documentation_example`;
- `generated_or_vendor`;
- `other_yaml`;
- `invalid_yaml`;
- `vault_encrypted`;
- `unclear`.

### Classification process

1. Apply explicit path exclusions and test-path rules.
2. Parse YAML safely.
3. Identify playbook/task shapes.
4. use role/inventory path context for vars and metadata.
5. record the rule responsible for every classification.
6. manually inspect a stratified sample.
7. keep unclear files out of the primary dataset until resolved.

### Acceptance gate

- every discovered YAML file has exactly one class;
- included files have a recorded reason;
- excluded files have a recorded reason;
- a manual sample covers every class and every pilot repository;
- research scans accept the classification manifest rather than rediscovering
  all YAML independently.

### Implemented Nova evidence

`scripts/classify_study_files.py` produced 122 rows at the frozen SHA: 28
production Ansible included, 8 test Ansible excluded, 84 documentation/example
excluded, 1 CI YAML excluded, and 1 in-repository symlink alias excluded to
prevent duplicate content. The manifest-enabled CLI processed exactly the 28
included files and wrote the manifest SHA-256 to `file_selection.json`.

See
[CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md](CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md)
for the schema, validation rules, commands, tests, and comparison.

## Work package 2 — snapshot/review profile separation

**Implementation status:** complete. Remaining environment/configuration/tool
version locks belong to the later study-export freeze, not profile separation.

### Goal

Prevent commit-range rules from entering snapshot findings.

### Implemented interface

```text
--profile technical-full
--profile snapshot-source
--profile research-core
--profile extended-ansible
--profile review-range
```

Profiles are declarative allowlists plus stage switches, not duplicated CLI
branches. All 60 rules have exactly one scientific family.

Every output must record:

- profile name;
- included rule IDs;
- excluded rule IDs or detector families;
- configuration hash;
- tool version;
- commit SHA.

### Acceptance gate

- snapshot runs produce no Git review findings;
- review-range tests continue passing;
- the same profile/config produces deterministic results;
- profile identity appears in study metadata;
- tests verify that a known review finding is absent from `snapshot-source`
  and present in `review-range`.

### Implemented Nova evidence

At the frozen Nova SHA, `snapshot-source` processed 28 production files and
produced 1,091 internal source findings, empty review metrics, and
`not-requested` external statuses. `research-core` produced 78 provisional
core findings; `extended-ansible` produced 1,013 disjoint findings;
`review-range` processed zero source files and produced three Git-change
findings. See
[RESEARCH_PROFILES_IMPLEMENTATION.md](RESEARCH_PROFILES_IMPLEMENTATION.md).

## Work package 3 — OpenStack cross-file variable resolution

### Goal

Reduce false `unguarded-variable` findings without hiding real undefined
variables.

### Project symbol index

Build a repository-level index containing:

- role `defaults/**/*.yml` and `vars/**/*.yml` keys;
- play and task `vars`;
- `vars_files` targets;
- statically resolvable `include_vars` targets and directories;
- `group_vars` and `host_vars` keys;
- inventory-variable files;
- `set_fact` definitions;
- registered variables and their task order;
- loop variables;
- configured runtime/extra variables;
- definition provenance: file, line, scope, and mechanism.

### Resolution rules

- Prefer a visible definition over a configured exception.
- Preserve scope: a definition in an unrelated role is not globally valid.
- Treat dynamic Jinja-computed include paths as unresolved, not automatically
  valid or invalid.
- Record why a variable was accepted or reported.
- Keep `known_variables` as an explicit project escape hatch, not a growing
  built-in ignore list.

### Calibration method

From the 823 pilot occurrences:

1. group by variable name and source file;
2. sample common and rare patterns;
3. trace definitions manually;
4. implement one resolution source at a time;
5. rerun and compare removed, retained, and new findings;
6. manually verify retained findings.

### Acceptance gate

- each finding includes searched scopes/provenance in raw details;
- common OpenStack include patterns are resolved;
- no broad name-prefix suppression is introduced;
- per-rule precision is measured on a held-out sample;
- the supervisor approves the minimum acceptable precision. A proposed gate is
  at least 0.80 for exploratory extended rules and a preferred 0.90 for core
  rules, with confidence intervals reported.

## Work package 4 — external rule identity

### Goal

Prevent distinct ansible-lint checks from being merged into one scientific
construct.

### Direction

Keep the normalized output contract but add fields such as:

```text
detector_family,native_rule_id,normalized_rule_id
```

For example:

```text
ansible-lint,name[missing],ansible-lint/name[missing]
ansible-lint,yaml[line-length],ansible-lint/yaml[line-length]
```

GitLeaks should similarly retain its native secret rule ID while remaining
separate from the core smell set unless explicitly approved.

### Acceptance gate

- native IDs are present in JSON, CSV, text, and SARIF;
- occurrence parity across formats remains tested;
- external rules are excluded or reported separately in `research-core`;
- no existing CI consumer loses the stable normalized fields.

## Work package 5 — finding normalization and deduplication

### Goal

Ensure one underlying problem is not counted repeatedly merely because several
views report it.

### Proposed unique occurrence key

```text
project + commit_sha + file + rule_id + line + normalized_message
```

Rules without a meaningful line use a rule-specific structural identity such
as role, variable, handler, or commit ID.

Keep both:

- raw occurrences for auditability;
- unique research occurrences for analysis.

Do not deduplicate different rule types simply because they occur on the same
line. Co-occurrence analysis needs distinct constructs, but overlapping rules
must be documented.

### Acceptance gate

- rerunning a scan does not change unique occurrence counts;
- project-wide rules occur once per intended unit;
- file-level findings are not duplicated by skipped-document fallback paths;
- raw-to-unique differences are reported.

## Work package 6 — manual validation

### Pilot labeling

Start with at least 100 findings across the five repositories. Stratify by:

- rule;
- severity;
- repository family;
- production/test file class;
- common and rare findings;
- source and structural detector families.

Also sample included files with no findings to investigate false negatives.

### Label schema

```text
finding_id,project,commit_sha,file,line,rule_id,
reviewer_1_label,reviewer_1_reason,
reviewer_2_label,reviewer_2_reason,
resolution,final_label,notes
```

Labels:

- `true_positive`;
- `false_positive`;
- `unclear`;
- `not_applicable`.

### Rules

- reviewers label independently first;
- disagreements are resolved after independent labels are saved;
- unclear cases are not silently counted as true;
- examples and decisions become a versioned labeling guide;
- precision is reported per rule where sample size permits;
- inter-rater agreement is reported;
- recall is not claimed without separately labeled negative examples.

### Acceptance gate

Every core rule is either:

- accepted with measured evidence;
- fixed and revalidated;
- moved to the extended set;
- excluded with a documented reason.

## Work package 7 — the five-project pilot

The pilot deliberately mixes repository shapes:

| Project | Purpose |
|---|---|
| `openstack/openstack-ansible-os_nova` | Individual OpenStack-Ansible role |
| `openstack/openstack-ansible` | Large integrated deployment repository |
| `openstack/kolla-ansible` | Large independent Ansible deployment system |
| `openstack/kayobe` | Bare-metal/OpenStack automation with different conventions |
| `openstack/ansible-collection-kolla` | Collection-oriented organization |

For each project record:

- frozen SHA;
- default branch and commit date;
- commits and contributors;
- classification counts;
- production/test LOC;
- runtime and peak memory;
- tool failures and parse diagnostics;
- raw and unique findings by profile/rule;
- manual-validation sample membership.

### Five-project gate

- zero unexplained collection failures;
- zero silent scan failures;
- classification reviewed in every project;
- source/review profiles separated;
- dominant rules manually investigated;
- output counts reproducible from frozen SHAs;
- estimated cost of the main corpus is documented.

## How the main corpus will be found

### Step 1 — OpenDev discovery

Read the authoritative OpenStack project registry. Select candidate rows when:

- project name, description, or group contains `ansible`; or
- it belongs to an approved Ansible-based family such as Kayobe or Bifrost; or
- it is an explicitly approved seed project.

Retired projects remain in the candidate file for audit but are not selected.

### Step 2 — content and history inventory

Clone candidates and calculate:

- production/test Ansible files;
- production LOC;
- overall and Ansible-touching commits;
- contributors;
- project age;
- default branch and current SHA.

### Step 3 — eligibility

The provisional filters are:

- active OpenStack repository;
- public and cloneable;
- at least 10 production Ansible files;
- at least 80 commits overall;
- meaningful commit history touching Ansible files;
- complete history available.

Sensitivity at 5, 10, and 20 production files will be reported before freezing
the threshold.

### Step 4 — human approval

No discovery script automatically selects the main corpus. A reviewed manifest
records `selected=true` and a reason for every inclusion or exclusion.

## Analysis tables we will produce

### Repository table

One row per frozen repository with selection evidence and size/history metrics.

### File table

One row per classified file with class, document type, LOC, and inclusion
reason.

### Raw-finding table

One row per detector occurrence, retaining full tool provenance.

### Unique-finding table

Deduplicated occurrences used for aggregate counts.

### File-smell table

One row per included file and smell construct, including zero rows where
needed for proper denominators.

### Label table

Independent and resolved manual-validation judgments.

## PR sequence

### PR 1 — collection foundation

Already prepared locally:

- OpenDev discovery;
- candidate and pilot manifests;
- full-clone/SHA-freeze collection;
- manifest-locked pilot runner;
- offline tests;
- study documentation.

### PR 2 — classified research profiles

- file-classification manifest;
- CLI profile selection;
- snapshot/review separation;
- profile metadata in outputs;
- tests proving rule-family isolation.

### PR 3 — OpenStack calibration

- project symbol index;
- cross-file variable resolution;
- native external IDs;
- deduplication contract;
- labeled pilot findings and precision report.

### PR 4 — five-project pilot evidence

- frozen project SHAs;
- environment/configuration lock;
- classification and runtime report;
- validated finding distribution;
- decision on the main corpus.

## Immediate next implementation order

1. ~~Add a reusable file-classification manifest generator.~~ Completed.
2. ~~Make the scanner accept classified file inputs.~~ Completed.
3. ~~Add profile selection and disable review rules for snapshots.~~ Completed.
4. ~~Record profile/rule/tool-status metadata in outputs.~~ Completed.
5. Manually validate a stratified sample of the Nova classifications.
6. Build the repository symbol index.
7. Calibrate `unguarded-variable` on the Nova-role sample.
8. Preserve native ansible-lint/GitLeaks rule identity.
9. Add configuration/tool-version locks and unique-occurrence export.
10. rerun the Nova role after calibration.
11. proceed to all five pilot repositories only after the gates pass.

## What we will not do

- We will not call all YAML files Ansible files.
- We will not use GitHub PR counts for OpenStack review activity.
- We will not classify an entire history using only current-HEAD smell status.
- We will not claim recall without labeled negative examples.
- We will not interpret association as causation.
- We will not change thresholds during the final run without restarting and
  versioning the experiment.
- We will not publish the first technical scan as empirical results.
