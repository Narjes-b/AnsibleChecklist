# OpenStack Ansible real-project testing and empirical-study plan

## Purpose

Companion documents provide operational detail:

- [START_HERE.md](START_HERE.md) gives the required newcomer reading and
  continuation order;
- [WHAT_IS_A_SNAPSHOT_STUDY.md](WHAT_IS_A_SNAPSHOT_STUDY.md) defines the frozen
  source-study boundary;
- [RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md](RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md)
  explains the next-phase decisions, evidence model, work packages, and gates;
- [RESEARCH_PROFILES_IMPLEMENTATION.md](RESEARCH_PROFILES_IMPLEMENTATION.md)
  records the implemented profile contracts and Nova validation;
- [STUDY_SCRIPTS_REFERENCE.md](STUDY_SCRIPTS_REFERENCE.md) documents every
  supplied and active study script;
- [LOCAL_OPENSTACK_STUDY_WORKFLOW.md](LOCAL_OPENSTACK_STUDY_WORKFLOW.md)
  provides exact local commands.

This document plans the transition from detector development to validation on
real OpenStack Ansible projects. It adapts the methodology of *On the
Prevalence, Co-occurrence, and Impact of Infrastructure-as-Code Smells*
(SANER 2024) into an Ansible-specific extension. It is not a strict
replication, and it does not treat the two languages as semantically
interchangeable.

The supplied inputs are:

- `/home/aymmzn/Downloads/Narjes_PuppetSmells_SANER24.pdf`;
- `/home/aymmzn/Downloads/fetch.py`;
- `/home/aymmzn/Downloads/GithubAPI.py`;
- the current AnsibleGuard implementation and its 60 finding rules.

The intended outcome is a reproducible OpenStack dataset, a validated Ansible
smell detector, and analysis capable of answering prevalence, co-occurrence,
change-proneness, and—only after the earlier gates pass—defect-proneness
questions.

## Main methodological decision

OpenStack's GitHub organization is a read-only mirror of code maintained on
OpenDev. OpenStack-Ansible also states that changes are reviewed in Gerrit and
that GitHub pull requests are ignored. Therefore:

- GitHub may provide discovery metadata and convenient mirrors;
- OpenDev Git repositories are the authoritative source for code/history;
- Gerrit is the authoritative source for reviews and review metadata;
- GitHub pull-request counts must not be used as a proxy for OpenStack review
  activity.

Authoritative references:

- [OpenStack GitHub mirror organization](https://github.com/openstack)
- [OpenStack-Ansible source](https://opendev.org/openstack/openstack-ansible)
- [OpenStack-Ansible code-review rules](https://docs.openstack.org/openstack-ansible/latest/contributors/code-rules.html)
- [OpenStack Gerrit project registry](https://opendev.org/openstack/project-config/src/branch/master/gerrit/projects.yaml)

## What the Puppet paper did

The SANER study followed three broad steps:

1. selected 82 Puppet-only projects from GitHub using project-quality filters;
2. detected 12 implementation/design smells with Puppeteer and Puppet-Lint;
3. analyzed:
   - RQ1: prevalence and density per KLOC;
   - RQ2: smell co-occurrence using association rules, Chi-square, and
     Cramer's V;
   - RQ3: change frequency/churn using Git history and PyDriller;
   - RQ4: defect-fixing and defect-inducing commits using keywords and MA-SZZ.

The paper manually evaluated 375 defect-related commits and reported precision
for the defect-fixing and defect-inducing classifications. Its replication
package is [available on Zenodo](https://zenodo.org/records/10060209).

## Why a direct Puppet-to-Ansible replacement is unsafe

The study design transfers, but several smell definitions do not:

- Puppet manifests use `.pp`; Ansible uses playbooks, task files, handlers,
  defaults, vars, metadata, inventories, and Jinja templates.
- Puppet classes/modules and Ansible roles/collections have different scope,
  dependency, and execution models.
- Puppet's `if/elsif` without `else` has no direct equivalent in ordinary
  Ansible task YAML.
- Puppet global-variable/encapsulation rules cannot be renamed as Ansible
  variable rules without a new operational definition.
- AnsibleGuard has 60 narrow rules; these are not automatically 60 independent
  research constructs.

We must publish an explicit construct mapping before collecting final results.

## Proposed research questions

### Detector-validation questions

- **DV1:** What precision does each selected AnsibleGuard rule achieve on real
  OpenStack Ansible code?
- **DV2:** Which file types, repositories, or coding conventions cause false
  positives and false negatives?
- **DV3:** What rule/configuration changes are required before freezing the
  detector for the empirical study?

### Replication questions

- **RQ1:** How prevalent are validated Ansible IaC smells in OpenStack Ansible
  projects at file, role, repository, and KLOC levels?
- **RQ2:** Which validated Ansible smell types co-occur in the same file, and
  how strong are those associations?
- **RQ3:** Are smelly Ansible files changed more frequently or with more churn
  than non-smelly Ansible files after accounting for file size and project?
- **RQ4:** Are smelly Ansible files more defect-prone than non-smelly files?

RQ4 is conditional: it begins only after detector precision and history mining
are stable. SZZ is expensive and introduces an additional classification layer.

## Construct-mapping protocol

Create `study/construct_mapping.csv` with these columns:

```text
puppet_smell,paper_level,ansible_construct,ansibleguard_rule_ids,
mapping_status,rationale,validation_required,supervisor_decision
```

Initial mapping candidates:

| Puppet construct | Candidate Ansible mapping | Initial status |
|---|---|---|
| Complex Expression | `complex-expression` | Strong candidate |
| Incomplete Tasks | `incomplete-task` | Strong candidate |
| Deprecated Statement | `deprecated-modules`, `deprecated-module-option` | Strong candidate, combine as one construct |
| Incomplete Conditional | No direct task-YAML equivalent | Not applicable unless Jinja templates enter scope |
| Multifaceted Abstraction | play/task-name cohesion plus manual role responsibility | Needs validation |
| Insufficient Modularization | `missing-abstraction`, size rules | Strong candidate after threshold calibration |
| Tightly Coupled Modularization | `high-coupling` | Needs threshold calibration |
| Weakened Modularity | high coupling combined with low cohesion | Composite construct; implement/freeze definition first |
| Unstructured Module | `unstructured-module`, `unexpected-task-location` | Strong candidate |
| Missing Dependency | `broken-role-dependency`, missing handlers | Partial candidate |
| Dense Structure | dependency density/graph complexity | Requires a repository-level definition |
| Deficient Encapsulation | Ansible variable-scope leakage | Requires a new Ansible-specific definition |

Two analysis sets should be kept separate:

- **Replication core:** only supervisor-approved mappings to the Puppet paper.
- **AnsibleGuard extended set:** validated Ansible-specific security,
  reliability, review, and maintainability rules.

This prevents the extended checklist from silently changing the replicated
research constructs.

## Repository population and selection

### Discovery sources

Use the following sources in priority order:

1. active entries in OpenStack `project-config`;
2. current OpenStack release-team deliverables;
3. OpenDev repository metadata and local Git history;
4. optional GitHub mirror metadata, never GitHub PR activity.

Seed project families include:

- `openstack/openstack-ansible` and its active role repositories;
- `openstack/kolla-ansible`;
- `openstack/kayobe` and relevant configuration repositories;
- `openstack/ansible-collection-kolla`;
- other active OpenStack projects passing the Ansible-content filters.

The current Kolla release index lists Kolla-Ansible, Kayobe, and the Kolla
Ansible collection, while OpenStack-Ansible documents its integrated repository
and individual role repositories.

### Inclusion criteria

A repository is eligible when it is:

- public and cloneable from OpenDev;
- active and not marked `RETIRED` at the dataset freeze date;
- maintained by an OpenStack project team;
- contains at least 10 production Ansible YAML files after classification;
- contains at least 80 commits overall, matching the Puppet study's minimum;
- contains meaningful history touching Ansible files;
- has a resolvable default branch and complete Git history.

The 10-file threshold is a pilot value. Record the sensitivity of the final
population to thresholds of 5, 10, and 20 files.

### Exclusion and stratification

Exclude from the production stratum:

- `.github`, `.zuul.yaml`, and unrelated CI YAML;
- generated/vendor files;
- documentation examples;
- encrypted or unreadable files that cannot be analyzed;
- YAML belonging exclusively to another tool or data format.

Do not silently discard tests. Classify Molecule and test playbooks into a
separate **test Ansible** stratum so production and test findings can be
reported independently.

Do not use GitHub stars as the main quality filter: stars belong to mirrors and
do not measure OpenDev project activity reliably. Use active release status,
Ansible-file count, Ansible-touching commits, contributors, and project age.

### Dataset freeze

For every included repository, record:

- OpenDev and GitHub URLs;
- exact commit SHA and commit date;
- default branch;
- clone timestamp in UTC;
- active/retired status source;
- total commits and Ansible-touching commits;
- contributors after `.mailmap` normalization when available;
- production/test/non-Ansible YAML counts;
- production Ansible LOC;
- tool and dependency versions.

Never analyze a floating `master` without storing its SHA.

## Problems in the supplied scripts

### `fetch.py`

The script is a useful retry/pagination skeleton, but currently:

- searches Terraform/HCL rather than Ansible/OpenStack;
- contains a placeholder token as a nonempty literal, so the environment-token
  check never protects the user;
- writes to an absolute macOS path;
- limits discovery to five search pages and repositories created since 2020;
- uses stars/forks from GitHub mirrors as study-quality measures;
- approximates contributor and commit counts through pagination;
- leaves file and IaC-file counts empty;
- uses `<=` filters, making the effective minimum strictly greater than the
  configured number;
- has no manifest, SHA pinning, checksums, or content classification.

### `GithubAPI.py`

This script should not be used for the final dataset because it:

- hardcodes a token and one repository;
- treats GitHub pull requests as authoritative for an OpenDev/Gerrit project;
- prints every commit author, which is slow and noisy;
- counts commits returned with `author='all'` as “developers”;
- does not handle rate limits, retries, resumability, or missing authors;
- has no CSV/JSON schema or reproducibility metadata.

## Replacement data pipeline

Create a dedicated `study/` workspace rather than mixing downloaded projects
with detector source code.

```text
study/
├── protocol.md
├── construct_mapping.csv
├── data_dictionary.md
├── manifests/
│   ├── candidates.csv
│   └── included_projects.csv
├── repositories/              # ignored by Git
├── snapshots/                 # immutable raw outputs
├── history/                   # per-commit/file longitudinal data
├── labels/                    # manual-validation forms
├── analysis/                  # derived tables and statistics
└── logs/
```

Proposed scripts:

| Script | Responsibility |
|---|---|
| `scripts/discover_openstack_ansible.py` | Read OpenStack project/release metadata and produce candidate repositories. |
| `scripts/clone_study_repositories.py` | Clone/fetch OpenDev repositories, checkout frozen SHAs, and record checksums. |
| `scripts/classify_study_files.py` | Implemented: classify every frozen-repository YAML candidate and record inclusion/reason. |
| `scripts/run_snapshot_study.py` | Run frozen AnsibleGuard over each repository and normalize outputs into study tables. |
| `scripts/mine_ansible_history.py` | Mine changed Ansible files, renames, churn, and revisions with PyDriller/Git. |
| `scripts/mine_gerrit_reviews.py` | Retrieve authoritative Gerrit changes, bug trailers, and review metadata when required. |
| `scripts/run_study_analysis.py` | Produce RQ1–RQ4 tables, statistical tests, plots, and machine-readable results. |

Every script must support command-line paths, resume mode, structured logging,
bounded retries, and no hardcoded credentials. Tokens must come from
environment variables and never be printed or stored in artifacts.

## Required AnsibleGuard changes before the main run

### 1. Separate analysis profiles

Implemented explicit profiles:

- `snapshot-source`: source/static rules only;
- `review-range`: Git-aware commit/review rules;
- `extended-ansible`: non-core internal source rules in a separate stratum;
- `research-core`: provisional eight-rule construct allowlist.

The current local `HEAD^..HEAD` fallback can produce review findings during a
snapshot scan. Those findings must not enter prevalence or co-occurrence data.

Classified scan input is now implemented independently through
`--file-manifest`; the frozen Nova validation processed 28 production files
from a complete 122-row manifest. See
[CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md](CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md).
Profile separation is also implemented and validated on Nova; see
[RESEARCH_PROFILES_IMPLEMENTATION.md](RESEARCH_PROFILES_IMPLEMENTATION.md).
The core remains provisional until manual calibration and supervisor approval.

### 2. Preserve native rule identity

The aggregate `ansible-lint-issue` rule must not be treated as one scientific
smell type. Either preserve ansible-lint's native rule IDs or exclude it from
the replication core and report it separately.

### 3. Export a study-friendly table

Add a normalized record containing at least:

```text
project,commit_sha,file,file_class,loc,rule_id,detector_family,severity,
line,message,tool_version,config_hash
```

### 4. Cache immutable blobs

For history mining, cache results by Git blob SHA plus detector/config version.
Identical file contents should be analyzed once even if they occur in many
commits or branches.

### 5. Freeze thresholds and dependencies

Pin Python, Ansible, ansible-lint, collections, spaCy model, GitLeaks, detector
configuration, and thresholds. Store `pip freeze`, tool versions, and a hash of
`.ansibleguard.yml` with every run.

## Execution phases and gates

### Phase 0 — protocol and construct freeze

Deliverables:

- supervisor-approved RQs;
- Puppet-to-Ansible construct mapping;
- inclusion/exclusion rules;
- production/test file taxonomy;
- analysis profiles and data dictionary.

Gate: no large-scale collection until ambiguous mappings are accepted,
rejected, or marked Ansible-specific.

### Phase 1 — five-repository technical pilot

Use deliberately different repository shapes:

1. OpenStack-Ansible integrated repository;
2. one OpenStack-Ansible role;
3. Kolla-Ansible;
4. Kayobe;
5. one Ansible collection/configuration repository.

Measure:

- discovery and classification accuracy;
- runtime, peak memory, disk usage, and tool failures;
- parsed/skipped/invalid file counts;
- findings per rule, file, KLOC, and project;
- duplicate findings and unstable output;
- effects of excluding tests and external tools.

Gate: all runs are reproducible from frozen SHAs, no silent crashes occur, and
file classification has been manually checked.

### Phase 2 — detector precision and calibration

Build a stratified sample across repositories, rules, severities, and file
types. Include all instances of rare rules and a randomized sample of common
rules. Also sample files with no findings to examine false negatives.

Two reviewers independently label each sampled instance:

- true positive;
- false positive;
- unclear/not applicable.

Record rationale and resolve disagreement by discussion. Report per-rule and
overall precision with confidence intervals plus inter-rater agreement
(Cohen's kappa or Krippendorff's alpha). Recall may only be claimed for a
separately labeled file/line sample; absence of findings is not proof of no
smell.

Pilot target: at least 100 findings. Main target: calculate the sample after
the population is known; 384 is the conservative starting point for 95%
confidence and 5% margin at maximum variance, with stratified oversampling for
rare rules.

Gate: low-precision rules are fixed, configured per project, downgraded to the
extended set, or excluded before the detector/configuration is frozen.

### Phase 3 — snapshot prevalence and co-occurrence

Run `research-core` on the frozen head snapshot of every included repository.

RQ1 outputs:

- total and smelly production Ansible files;
- smell instances by rule/project/file type;
- percentage of affected files, roles, and projects;
- density per KLOC;
- distributions by file-size quartile;
- separate production and test results.

RQ2 transaction unit must be fixed before analysis. The recommended primary
unit is one production Ansible file at the frozen snapshot. If commit-level
co-occurrence is also studied, label it as a separate analysis rather than
mixing the two definitions.

RQ2 outputs:

- number of distinct smell types per file;
- support, confidence, and lift;
- Chi-square/Fisher exact tests where appropriate;
- Cramer's V effect size;
- multiple-testing correction;
- minimum support and minimum cell-count policy.

Gate: raw tables reproduce all reported aggregate counts exactly.

### Phase 4 — longitudinal change-proneness

Mine the default-branch history for production Ansible files. Track renames and
deletions. For each changed revision, determine smell status at that revision,
not only at current `HEAD`; this avoids time-travel bias.

Use Git blob caching to make historical scanning feasible. Record:

- commits touching each file;
- added, deleted, and churn lines;
- file LOC at the revision;
- smell presence/count/type at the revision;
- file age and project;
- rename lineage.

Replicate Mann-Whitney U and Cliff's delta for comparability. Add a robustness
analysis using regression or mixed-effects models with project, LOC, age, and
file type as confounders. Report effect sizes and confidence intervals rather
than relying only on p-values.

Gate: manually verify histories for renamed, deleted, smelly, and non-smelly
files in every pilot repository.

### Phase 5 — defect-proneness feasibility pilot

Identify defect-fixing changes using a hierarchy of evidence:

1. Gerrit/OpenStack bug trailers such as `Closes-Bug` and `Related-Bug`;
2. linked Launchpad/story/task references;
3. conservative commit-message keywords as fallback.

Run MA-SZZ or a documented reproducible SZZ implementation only on confirmed
fixing changes that modify production Ansible lines. Exclude or flag merges,
mass formatting, generated files, renames, and refactor-only changes.

Manually validate a statistically justified sample of defect-fixing and
defect-inducing classifications with two reviewers. Report precision and
agreement before answering RQ4.

Gate: if fixing-commit precision or SZZ precision is inadequate, report RQ4 as
a feasibility result rather than making a defect-proneness claim.

### Phase 6 — final run and replication package

Publish, subject to repository/data licensing:

- frozen repository manifest and SHAs;
- construct mapping and detector configuration;
- scripts and locked dependencies;
- raw AnsibleGuard outputs or checksums/derivation instructions;
- normalized anonymized labels;
- RQ tables, statistical notebooks/scripts, and plots;
- runtime/failure log;
- threats-to-validity and deviation log;
- one-command or Makefile workflow for reproduction.

## Statistical analysis requirements

- Pre-register the unit of analysis for every RQ: project, role, file,
  file-revision, or commit.
- Never treat multiple revisions of one file as independent without modeling
  repeated observations.
- Report medians and distributions for skewed repository metrics.
- Report effect sizes and confidence intervals with every significance test.
- Correct for multiple comparisons in per-rule analyses.
- Separate correlation/association from causation.
- Run sensitivity analyses for file thresholds, test-file inclusion, external
  rules, and project families.
- Keep the replication-core and extended-Ansible results in separate tables.

## Reproducibility and operational safeguards

- Use full clones for longitudinal analysis; shallow clones are acceptable only
  for an explicitly labeled snapshot pilot.
- Never store GitHub/OpenDev tokens in source files.
- Respect GitHub and Gerrit rate limits with resumable cached requests.
- Store API version, request timestamp, and response provenance.
- Keep downloaded repositories and generated datasets out of Git.
- Save command lines, exit codes, stdout/stderr logs, and tool diagnostics.
- Use immutable raw data; derived tables must be regenerated, not hand-edited.
- Hash manifests, configs, and raw output files.
- Record every exclusion with a machine-readable reason.

GitHub documents separate core and search rate-limit buckets and recommends
waiting for reset/retry headers. The supplied retry logic can be retained after
removing its hardcoded study assumptions.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| GitHub mirror metadata mistaken for OpenStack review activity | Use OpenDev Git and Gerrit as authoritative sources. |
| Non-Ansible YAML contaminates the denominator | Create and manually validate a file classifier. |
| Test YAML dominates findings | Separate production and test strata. |
| Git-aware review rules contaminate snapshot prevalence | Add explicit AnsibleGuard profiles. |
| Detector false positives invalidate downstream statistics | Complete manual precision/calibration before the main run. |
| Different Ansible/collection versions change results | Pin the environment and record versions/config hashes. |
| HEAD-only smell status creates time-travel bias | Analyze each changed blob/revision with content-addressed caching. |
| Large history makes scanning infeasible | Pilot runtime, cache by blob SHA, resume per repository. |
| SZZ mislabels defects | Prefer Gerrit bug evidence, validate manually, and keep RQ4 conditional. |
| Puppet constructs are renamed without semantic equivalence | Freeze a reviewed construct mapping and report non-applicable items. |

## Immediate next actions

1. Review the Ansible-specific construct mapping with the supervisor and keep
   replication-core comparisons separate from extended Ansible results.
2. Inspect the Zenodo replication package to recover reusable schemas, scripts,
   co-occurrence transaction units, and MA-SZZ assumptions.
3. Implement `snapshot-source` and `research-core` AnsibleGuard profiles.
4. Replace the two supplied scripts with manifest-driven OpenDev discovery and
   cloning scripts; retain GitHub only as optional metadata.
5. Build the five-repository pilot manifest and freeze exact commit SHAs.
6. Run classification and technical-performance pilots before labeling
   detector findings.
7. Conduct detector calibration, freeze the tool/configuration, and only then
   begin the full snapshot and historical analyses.

## Decisions required from the supervisor

- Must the population be only OpenStack-Ansible team repositories, or all
  active OpenStack repositories containing substantial Ansible code?
- Are Jinja templates in scope? This determines whether an Ansible analogue of
  incomplete conditionals can be studied.
- Are Molecule/test playbooks part of the main corpus or a separate stratum?
- Which AnsibleGuard rules constitute the official research-core smell set?
- Is RQ4/SZZ required for the current thesis phase, or should it follow the
  validated RQ1–RQ3 study?
