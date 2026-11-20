# Approach: Building, Testing, and Evaluating AnsibleGuard

> **Article draft status.** This section is written as article-ready prose for
> later conversion into the ACM LaTeX manuscript. It covers the construction
> and static-analysis evaluation of AnsibleGuard. The LLM-assisted explanation
> and pull-request integration are intentionally left for later sections.

## 1. Approach

We designed AnsibleGuard as a reproducible static-analysis pipeline for
detecting quality, maintainability, correctness, and security smells in
Ansible infrastructure-as-code repositories. The design was motivated by an
important characteristic of Ansible: files that share the `.yml` or `.yaml`
extension may serve substantially different purposes. A repository can contain
playbooks, task and handler files, role metadata, deployment variables, test
fixtures, CI configuration, documentation examples, release notes, and
dependency manifests. Treating all YAML files as equivalent would therefore
mix different source populations and weaken the validity of any prevalence or
comparison study.

The approach consequently separates four concerns:

1. **repository and file selection**, which defines the exact source
   population;
2. **rule execution**, which assigns detectors to explicit analysis profiles;
3. **finding normalization**, which converts detector and external-tool output
   into one common representation; and
4. **provenance and reporting**, which records enough information to reproduce
   and audit each run.

This separation also prepares the tool for later use in pull-request review.
The present work evaluates the deterministic static-analysis core. LLM-based
explanations and automated pull-request feedback will be layered over this
core rather than used as substitutes for source selection or rule execution.

## 2. From Smell Definitions to Executable Rules

### 2.1 Sources of rule definitions

The initial smell catalog combined three sources of evidence:

- infrastructure-as-code smell definitions from prior empirical studies,
  including work that originally studied Puppet and required adaptation to
  Ansible [25, 34];
- Ansible-specific maintainability and variable-smell literature [27, 32];
- recurring concerns observed in Ansible and OpenStack code-review
  discussions, such as unsafe defaults, missing Boolean conversion, leaked
  credentials, inappropriate error suppression, and invalid file references
  [33, 38, 41, 43, 48, 60, 61].

This process produced both metric-based smells and predicate-based checks.
Metric-based smells include large playbooks, large plays, large tasks,
complex expressions, and excessive nesting. Predicate-based checks include
duplicate mapping keys, missing handlers, insecure file permissions, default
credentials, deprecated modules, missing `no_log`, non-idempotent commands,
and invalid role dependencies.

The current catalog contains **65 stable rule identifiers**. These identifiers
are used consistently in JSON, CSV, text, and SARIF output. Stable identifiers
are necessary because descriptions and severities can be refined while result
consumers continue to refer to the same logical rule.

### 2.2 Adapting definitions to Ansible

Definitions originating outside the Ansible ecosystem could not be transferred
verbatim. For example, insufficient modularization in a class- or
module-oriented language must be expressed in terms of Ansible roles, task
files, and include/import operations. AnsibleGuard therefore reports
`missing-abstraction` when a file exceeds a configurable leaf-task threshold
and contains no role or task-file abstraction. Similarly, unnecessary
abstraction is represented by structures such as a `block` containing only
one task.

Other rules are intrinsically Ansible-specific. Examples include:

- `missing-handler` and `unused-handler`, which cross-reference `notify`
  targets with handler definitions;
- `credentials-leaking-in-log`, which checks whether tasks handling
  credential-related values omit `no_log: true`;
- `missing-bool-filters`, which identifies conditions whose values may be
  interpreted incorrectly without Boolean conversion;
- `non-idempotent-command`, which recognizes mutating command families and
  checks for guards such as `creates`, `removes`, or `changed_when`;
- `unexpected-task-location`, which relates a YAML document’s structure to
  its position under `tasks`, `handlers`, `defaults`, `vars`, or `meta`; and
- `broken-role-dependency`, which analyzes local role dependencies for
  missing targets, self-dependencies, and cycles.

The resulting catalog is therefore not only a direct reimplementation of
existing linters. It combines adapted research smells, Ansible-specific
structural rules, and two explicitly identified external-tool integrations.

### 2.3 Metrics and configurable thresholds

Several rules require thresholds rather than Boolean syntax checks. Examples
include physical line length, expression complexity, nesting depth, task-name
length, and the number of leaf tasks used to indicate missing abstraction.
AnsibleGuard stores default thresholds in versioned configuration and permits
project-level overrides. The current research-core configuration uses, among
others, a 120-character threshold for `long-statement`, a complexity score
threshold for `complex-expression`, a nesting threshold greater than three,
and a leaf-task threshold greater than ten for `missing-abstraction`.

Thresholds are part of the experiment rather than hidden implementation
details. The tool records the profile’s exact ordered rule list and a SHA-256
hash in `run_metadata.json`. File-selection manifests are also hashed. This
allows a rerun to distinguish a real source-code difference from a changed
rule population or changed file selection.

The earlier manuscript text describes threshold tuning through box plots over
a larger historical collection. That analysis can remain as motivation after
the corresponding dataset, scripts, and threshold values are recovered and
linked to reproducible artifacts. The evaluation reported here uses the
versioned thresholds implemented in the current repository and does not claim
that repeated post-hoc tuning was performed on the five-project outcome.

## 3. Tool Architecture

### 3.1 Repository discovery and freezing

For the real-repository study, we selected five active OpenStack Ansible
projects hosted on OpenDev. Each repository was cloned locally and frozen at
one full Git commit SHA. The frozen manifest records the repository URL, local
path, default branch, exact SHA, commit date, collection time, repository
history statistics, YAML counts, and collection status.

Before every study run, the runner executes `git rev-parse HEAD` and compares
the result with the frozen manifest. A mismatch aborts the run. This prevents
a branch update or manual checkout from silently changing the analyzed
snapshot.

### 3.2 Complete file-classification manifests

For each frozen repository, AnsibleGuard inventories every `.yml` and `.yaml`
file and writes one row to a classification manifest. Each row records the
project, commit, repository-relative path, file class, inclusion decision,
and exclusion reason.

The classifier uses both path context and YAML document shape. It distinguishes
production Ansible files from:

- test and integration-test files;
- CI and Zuul configuration;
- documentation examples;
- release-note fragments;
- dependency manifests;
- generic configuration YAML; and
- invalid or unsupported YAML documents.

Production variable files are not categorically discarded. Files under
`defaults`, `vars`, `group_vars`, `host_vars`, or deployment configuration
directories can affect Ansible behavior and are included when the path and
content indicate production use. This corrects the overly broad filtering
description in the earlier draft, which proposed excluding all variable files.

The manifest reader validates complete repository coverage before a
manifest-locked scan begins. Research scans process only rows marked
`included=true`, but excluded rows remain in the manifest so the population
decision can be audited.

### 3.3 Document inspection and detector execution

AnsibleGuard first inspects each selected document and classifies it as a
playbook, task list, variable mapping, role metadata file, empty document, or
invalid document. Full play/task metrics are computed when the document shape
supports structural traversal. Source and role-layout checks that remain
meaningful for variable, metadata, or empty documents execute even when the
legacy playbook metric parser is not applicable.

The detector layer combines:

- syntax- and source-line checks;
- playbook, play, and task metrics;
- recursive traversal of `block`, `rescue`, and `always`;
- cross-file and repository-layout checks;
- local role-dependency analysis;
- project-configured suppressions and overrides; and
- optional external-tool results.

Source locations are preserved through line-aware YAML parsing or dedicated
source-location recovery. Location validity is important because the later
pull-request integration must attach feedback to the correct changed line.

### 3.4 Finding normalization

All detectors emit or are converted into a common finding model:

```text
file
line
rule_id
severity
message
```

The normalized list is the single source for:

- `findings.json`;
- `findings.csv`;
- `findings.txt`; and
- `findings.sarif`.

Producing all four representations from the same in-memory list prevents
format-specific counting differences. The project output also contains
`summary.csv`, `diagnostics.json`, `review_metrics.json`,
`file_selection.json`, and `run_metadata.json`.

For backward compatibility and detector debugging, AnsibleGuard mirrors the
repository-relative path of each analyzed source file and writes:

- `Technical_Analysis.json`, containing raw detector metrics;
- `IaC_Smells.csv`, containing the legacy metric summary;
- `Play_Level_Analysis.txt`, containing the human-readable file report;
- `ansiblelint.txt`; and
- `gitleaks.txt`.

For example, `roles/example/tasks/main.yml` is represented by the result
directory `roles/example/tasks/main/`.

### 3.5 External-tool integration

The `technical-full` profile runs GitLeaks and ansible-lint once at repository
scope. Results are then assigned to their corresponding source files and
included in the normalized output.

Each GitLeaks result becomes an AnsibleGuard finding with rule identifier
`hardcoded-credentials`. Each ansible-lint result becomes an
`ansible-lint-issue`. These two rules are adapters, not independent
reimplementations of secret detection or ansible-lint’s native rules. Native
ansible-lint rule identities are retained in the raw text but collapsed under
the normalized aggregate identifier. This distinction is necessary when
interpreting total findings or comparing AnsibleGuard with existing tools
[24].

Repository-wide GitLeaks findings from non-YAML files are retained even though
those files do not enter the Ansible structural-analysis loop. Tool failures
are recorded in `diagnostics.json` and are not represented as clean scans.

## 4. Analysis Profiles

The 65 rules are divided into explicit profiles so that different empirical
questions do not contaminate one another.

| Profile | Rules | Source analysis | Review analysis | External tools | Intended purpose |
|---|---:|---:|---:|---:|---|
| `technical-full` | 65 | Yes | Yes | Yes | Complete engineering report and tool comparison |
| `snapshot-source` | 56 | Yes | No | No | All internal source findings at one frozen commit |
| `research-core` | 8 | Yes | No | No | Conservative primary research stratum |
| `extended-ansible` | 48 | Yes | No | No | Secondary Ansible-specific stratum |
| `review-range` | 7 | No | Yes | No | Base-to-head Git review findings |

The source profiles satisfy:

```text
research-core ∪ extended-ansible = snapshot-source
research-core ∩ extended-ansible = ∅
```

The `snapshot-source`, `research-core`, and `extended-ansible` profiles require
a complete classification manifest. Git review rules are excluded from
snapshot prevalence because they describe changes between commits rather than
properties of one frozen source state. GitLeaks and ansible-lint are also
excluded from the source research profiles because their results are imported
external findings rather than independently implemented research detectors.

The current eight-rule `research-core` is deliberately marked
`provisional-pending-manual-calibration` and `research_eligible=false`.
Profile separation establishes a valid experimental boundary; it does not by
itself prove detector precision or recall.

## 5. Evaluation Method

We evaluated AnsibleGuard in four complementary layers.

### 5.1 Automated software tests

The automated suite covers detector behavior, YAML and document-shape
handling, manifest completeness and path safety, profile membership, profile
hashes, external-tool status propagation, project-wide output parity, SARIF
generation, study-runner behavior, and regression cases discovered during
manual validation.

At the time of this draft, the complete suite reports:

```text
230 passed in 27.13 seconds
0 failed
```

This result verifies the implementation against its executable test
specification. It is not a precision or recall measurement over real-world
smells.

### 5.2 Synthetic and mutated validation

Controlled examples are used when a real repository does not contain a
positive instance of a rule. The validation corpus includes baseline and
deliberately mutated variants, allowing checks that an injected defect is
reported while its clean counterpart remains unreported.

This process revealed concrete detector defects. For example, early
role-layout analysis recognized only paths shaped as
`roles/<role-name>/...`. Controlled standalone roles showed that
`unstructured-module` and `broken-role-dependency` could miss missing entry
points and self-dependencies in repositories that are themselves a role. The
role-context algorithm was extended, regression tests were added, and the
frozen Nova snapshot was rerun. The repair reduced 313 spurious
`unguarded-variable` findings while leaving the 77 research-core findings
unchanged.

Corpus-level testing also revealed false-positive sources involving empty
variable files and variables supplied through inventory context. Detector
scope and visible-variable loading were corrected rather than accepting raw
candidate counts as valid defects.

### 5.3 Manual positive and negative validation

We first calibrated the research-core findings on the frozen Nova repository.
The corrected run contained:

| Rule | Reviewed findings | Semantically valid | Correct source location |
|---|---:|---:|---:|
| `complex-expression` | 38 | 38 | 38 |
| `long-statement` | 39 | 39 | 39 |
| **Total** | **77** | **77** | **77** |

These results establish 100% observed precision and location validity for the
77 reviewed Nova findings from these two active rules. They must not be
reported as 100% precision for all 65 rules or for the five-project corpus.

Negative validation independently checked unreported candidates. All 39
non-comment lines longer than 120 characters were recovered by
`long-statement`, while a long comment was correctly excluded. For
`complex-expression`, 17 unreported candidates immediately below the
threshold were manually reviewed and labeled as true negatives; this is a
boundary sample, not exhaustive recall evidence. The negative audit also
identified the standalone-role gaps discussed above, illustrating why both
reported and unreported cases must be examined.

After expanding to five projects, we manually reviewed positive examples for
every research-core rule that appeared and one no-finding file from each
project. Long physical lines, high-scoring expressions, and unresolved TODO
markers were direct operational matches. In contrast,
`empty-abstraction`, `missing-abstraction`, and `unstructured-module` were
context-sensitive: an empty file may intentionally be a no-op placeholder, a
large task file may be an acceptable design choice, and a role may load
operating-system-specific variable files without a `vars/main.yml`. These
observations motivate rule-level calibration rather than treating every
candidate as a confirmed defect.

### 5.4 Frozen real-repository pilot

The final integration test used five real OpenStack repositories. The study
did not deploy OpenStack or execute the playbooks against managed hosts; it
performed static analysis of production Ansible source at frozen commits.

| Project | Frozen commit | YAML candidates | Included production files |
|---|---|---:|---:|
| `openstack/openstack-ansible-os_nova` | `e06c7bceef3f7c365828116b7aadea6fc2d3e22b` | 122 | 28 |
| `openstack/openstack-ansible` | `b7c10cbcc04a06207c2344a312d4f612a0810939` | 1,708 | 216 |
| `openstack/kolla-ansible` | `9c41bdca79d4c7267beeece141909e679f70dea8` | 2,570 | 1,228 |
| `openstack/kayobe` | `9a6e4333b2aa2fbe8dc80a93cd5aa3e2f1872970` | 938 | 342 |
| `openstack/ansible-collection-kolla` | `785982d7c09dda3d8e46f6c9b09597ca14820497` | 71 | 42 |
| **Total** | — | **5,409** | **1,856** |

The 3,553 excluded candidates were retained in the manifests with explicit
classes and reasons. Exclusion does not indicate poor quality; it indicates
that a file falls outside the production-source population defined for this
experiment.

## 6. Evaluation Results and Operational Performance

### 6.1 Source and review profiles

We executed four separated profiles on each of the five projects, producing 20
profile runs.

| Project | `snapshot-source` | `research-core` | `extended-ansible` | `review-range` | Diagnostics |
|---|---:|---:|---:|---:|---:|
| Nova role | 777 | 77 | 700 | 3 | 0 |
| OpenStack-Ansible | 731 | 192 | 539 | 1 | 0 |
| Kolla-Ansible | 7,795 | 703 | 7,092 | 1 | 0 |
| Kayobe | 3,712 | 247 | 3,465 | 1 | 0 |
| Ansible Collection Kolla | 372 | 31 | 341 | 4 | 0 |
| **Total** | **13,387** | **1,250** | **12,137** | **10** | **0** |

For every project, the stored counts satisfy:

```text
research-core + extended-ansible = snapshot-source
```

All 20 runs recorded the expected commit, manifest hash, profile name, and
rule-list hash. All source-profile review metrics were empty, and GitLeaks and
ansible-lint were recorded as `not-requested`. Zero diagnostics means that the
runner recorded no parse-stage or tool-stage failures in these runs; it does
not mean that every reported candidate is a true defect.

The 1,250 research-core findings are distributed as follows:

| Rule | Findings |
|---|---:|
| `long-statement` | 643 |
| `complex-expression` | 487 |
| `incomplete-task` | 51 |
| `empty-abstraction` | 41 |
| `missing-abstraction` | 24 |
| `unstructured-module` | 4 |
| `broken-role-dependency` | 0 |
| `excessive-nesting` | 0 |
| **Total** | **1,250** |

These are detector outputs, not 1,250 independently confirmed OpenStack
defects. The distribution also shows that conclusions about research-core
prevalence would be dominated by `long-statement` and `complex-expression`
unless results are reported by rule.

### 6.2 Full technical profile

We subsequently ran `technical-full` on the same five frozen repositories and
the same 1,856 manifest-selected production files. All five runs completed
with GitLeaks and ansible-lint marked `completed` and with zero diagnostics.

| Project | Included files | All findings | ansible-lint findings | GitLeaks findings |
|---|---:|---:|---:|---:|
| Ansible Collection Kolla | 42 | 330 | 0 | 0 |
| Kayobe | 342 | 3,285 | 40 | 0 |
| Kolla-Ansible | 1,228 | 6,116 | 59 | 1 |
| Nova role | 28 | 509 | 32 | 0 |
| OpenStack-Ansible | 216 | 729 | 362 | 1 |
| **Total** | **1,856** | **10,969** | **493** | **2** |

The total is internally consistent:

```text
10,474 AnsibleGuard detector observations
+   493 imported ansible-lint findings
+     2 imported GitLeaks findings
= 10,969 technical-full raw findings
```

This equality validates profile composition and external-result integration.
It does not imply that AnsibleGuard and ansible-lint found 3,358 independent
problems. Under `technical-full`, one source construct can generate both an
internal AnsibleGuard finding and an imported `ansible-lint-issue`.

### 6.3 What “performance” is established

The current evaluation establishes the following operational properties:

- the tool processed 1,856 production Ansible files selected from 5,409 YAML
  candidates;
- all 20 separated source/review profile runs completed without recorded
  diagnostics;
- all five `technical-full` runs completed with both external tools;
- project-wide JSON, CSV, text, and SARIF views were generated from a common
  normalized finding list;
- per-file reports were generated in mirrored source-path directories;
- profile partition identities held for every repository;
- exact commit, manifest, and rule provenance was retained; and
- the complete automated test suite passed.

These properties demonstrate scalability to the five selected repositories
and show that the end-to-end pipeline can process different OpenStack
repository layouts. They do not yet constitute a runtime or resource-efficiency
benchmark.

The current study artifacts do not record controlled wall-clock time, CPU
utilization, peak memory, cold- versus warm-cache state, or dependency-download
time. External-tool execution can also depend on installed Ansible collections
and network access. We therefore do not report unsupported throughput,
latency, or memory claims. A later performance experiment should record, for
each repository and profile:

- wall-clock duration;
- user and system CPU time;
- peak resident memory;
- file count and lines of code;
- external dependency preparation time;
- cold- and warm-cache conditions; and
- tool versions and machine characteristics.

This measurement should be executed separately from detector calibration so
that performance tuning does not alter the frozen rule definitions.

## 7. Reproducibility and Artifact Organization

The experiment’s main artifacts are organized as follows:

```text
study/manifests/pilot-five-frozen.csv
    frozen repositories and commit SHAs

study/manifests/file-classification/
    complete per-repository YAML populations and inclusion decisions

study/repositories/openstack/
    locally cloned repositories at the frozen commits

study/analysis/five-project-pilot/
    snapshot-source, research-core, extended-ansible, and review-range results

study/analysis/five-project-technical-full/
    combined internal, review, GitLeaks, and ansible-lint results

study/logs/five-project-pilot/
study/logs/five-project-technical-full/
    execution traces

study/labels/
    manual validation labels and combined summaries
```

Every result root contains `run_metadata.json`, `file_selection.json`, and
`diagnostics.json`. These artifacts allow an evaluator to determine which
source population and rule population produced a finding before interpreting
the finding itself.

## 8. Threats to Validity and Current Limitations

### Construct validity

Several detectors encode operational thresholds or structural proxies rather
than universally accepted defects. A physical line longer than 120 characters
is directly observable, but whether a task file with eleven leaf tasks requires
further abstraction is contextual. Results must therefore be reported by rule
and accompanied by manual labels.

### Internal validity

Manifest locking, SHA verification, profile hashing, and zero-diagnostic
checks reduce the risk that different runs analyze different source
populations. However, external tools can depend on installed collections and
environment configuration. Tool status and version provenance should remain
part of every technical comparison.

### External validity

The pilot contains five OpenStack projects and 1,856 production files. These
projects exercise standalone roles, large deployment repositories, and an
Ansible collection, but they do not represent all Ansible ecosystems.
Findings cannot yet be generalized to GitHub, Ansible Galaxy, private
enterprise repositories, or other infrastructure-as-code languages.

### Conclusion validity

The five-project corpus has not been exhaustively labeled for all 65 rules.
The Nova 77/77 result covers two active research-core rules, while the broader
five-project review is a targeted spot check. An overall precision or recall
percentage would therefore be misleading at this stage.

### Static-analysis boundary

AnsibleGuard analyzes source code; it does not execute playbooks against real
hosts. Dynamic inventory, runtime variables, collection behavior, environment
state, and target-system effects can make a statically suspicious construct
safe or make a statically clean construct fail at runtime.

## 9. Transition to the Next Article Sections

The current approach yields deterministic, source-located findings with
explicit provenance. This output is the foundation for the next two parts of
the system:

1. **LLM-assisted interpretation**, which will transform a structured finding
   into a contextual explanation and candidate remediation while preserving
   the detector’s evidence; and
2. **pull-request integration**, which will select findings relevant to a
   change range, attach feedback to valid diff locations, and enforce controls
   for duplicate, stale, or unsafe automated comments.

Those later stages must be evaluated independently. In particular, detector
correctness, explanation quality, patch correctness, and pull-request comment
usefulness are different outcomes and should not be collapsed into one
accuracy measure.

## Notes for integration into the ACM manuscript

- Replace bracketed numeric citation placeholders with the actual BibTeX keys
  used in the manuscript.
- Do not retain duplicate `Introduction`, `Tool design`, `Tool evaluation`, or
  `Conclusion` sections from the supplied LaTeX draft.
- The historical values of 972 repositories and 16,557 filtered YAML files
  should only be restored after locating the exact dataset, selection script,
  date, and frozen manifest that produced them.
- Replace screenshot placeholders with reproducible figures generated from
  the current architecture and result tables.
- A pipeline figure should show:
  `frozen repository → file manifest → profile → detectors/external tools →
  normalized findings → reports`.
- A profile figure or table should preserve the disjoint relationship between
  `research-core`, `extended-ansible`, and `review-range`.
- The author, conference, copyright, CCS, keyword, and bibliography metadata
  in the sample ACM file are placeholders and must be replaced before
  submission.
