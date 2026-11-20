# The SANER'24 Puppet-smells paper and this AnsibleGuard repository

## The shortest correct explanation

The paper studies whether 12 Puppet smell types are common, occur together,
and are associated with code changes and defects across 82 projects.

This repository builds an Ansible static-analysis tool with 60 normalized
rules and is preparing an OpenStack Ansible empirical study inspired by the
paper.

It is not currently a completed replication of the paper.

The reusable part is the research shape:

```text
select projects
  -> detect validated smells
  -> measure prevalence
  -> measure co-occurrence
  -> mine change history
  -> study defect history
```

The non-reusable part is a mechanical renaming of Puppet constructs as Ansible
constructs. Puppet and Ansible have different files, modules, variables,
dependencies, and execution models.

## Source being explained

Local paper:

```text
/home/aymmzn/Downloads/Narjes_PuppetSmells_SANER24 (2).pdf
```

Title: *On the Prevalence, Co-occurrence, and Impact of
Infrastructure-as-Code Smells*.

Authors: Narjes Bessghaier, Mahi Begoug, Chemseddine Mebarki, Ali Ouni,
Mohammed Sayagh, and Mohamed Wiem Mkaouer.

The paper points to its replication package at:

```text
https://zenodo.org/records/10060209
```

## Part 1 — what the paper wanted to learn

An IaC smell is a recurring implementation or design pattern that violates a
quality practice or makes infrastructure code harder to understand, change,
or trust.

The paper asks four questions:

- RQ1: How prevalent are Puppet IaC smells?
- RQ2: Which smell types tend to occur together?
- RQ3: Are smelly files changed more often or with more churn?
- RQ4: Are smelly files more defect-prone?

This is broader than building a linter. The detector creates measurements; Git
history and statistical analysis connect those measurements to maintenance
outcomes.

## Part 2 — how the paper selected projects

The paper's selection funnel was:

```text
22,177 GitHub projects with Puppet language
  -> remove forks, private, and archived projects
  -> require at least 5 stars and 80 commits
  -> 414 projects
  -> remove projects mixing in other IaC-tool artifacts
  -> 102 Puppet-only candidates
  -> remove inaccessible private/API cases
  -> 82 studied projects
```

Reported dataset statistics:

| Measure | Paper value |
|---|---:|
| projects | 82 |
| commits | 19,641 |
| smelly Puppet files | 1,462 |
| non-smelly Puppet files | 501 |
| smell instances | 5,213 |
| studied period | 2011–2023 |
| project star range | 5–79 |

Why each filter exists:

- no forks: reduce duplicate projects;
- no archived projects: focus on maintained systems;
- minimum stars/commits: avoid trivial repositories;
- Puppet-only: prevent other IaC files from contaminating Puppet
  change-proneness;
- public/API-accessible: make data collection possible.

## Part 3 — the 12 smells in the paper

The paper uses Puppeteer for design smells and an extended Puppet-Lint for
implementation smells.

### Four implementation smells

| Code | Name | Simple meaning | Level |
|---|---|---|---|
| ICE | Complex Expression | an expression is difficult to understand | file |
| IIT | Incomplete Tasks | TODO/FIXME-like unfinished work exists | file |
| IDS | Deprecated Statement Usage | obsolete syntax/instruction is used | file |
| IIC | Incomplete Conditional | `if/elsif` has no final `else` | file |

### Eight design smells

| Code | Name | Simple meaning | Level |
|---|---|---|---|
| DMF | Multifaceted Abstraction | one abstraction has several responsibilities | file |
| DIM | Insufficient Modularization | an abstraction is too large/complex and should be split | file |
| DTC | Tightly Coupled Modularization | modules depend too strongly on each other | file |
| DWM | Weakened Modularity | high coupling and low cohesion appear together | file |
| DUM | Unstructured Module | the module lacks a coherent standard structure | module |
| DMP | Missing Dependency | declared/included class dependencies do not agree | module |
| DDS | Dense Structure | dependency structure is excessively dense | module |
| DDE | Deficient Encapsulation | global variables leak across node/class boundaries | module |

The level matters. A module smell cannot safely be approximated by looking at
one YAML file in isolation.

## Part 4 — how the paper calculated prevalence

Let:

- `F_i` be a Puppet file;
- `s` be one smell type;
- `occ(F_i,s)` be the number of occurrences;
- `LOC` be nonblank source lines;
- `KLOC = LOC/1000`.

Useful prevalence forms are:

```text
affected-file rate(s) = files with s / all studied files
density(s) = total occurrences of s / total KLOC
smelly-file rate = files with at least one smell / all files
```

The paper examines both frequency and diffusion: a smell can occur many times
inside a few projects or occur once across nearly every project.

## Part 5 — how the paper calculated co-occurrence

The study uses Apriori association-rule mining and three measures.

For smell types `A` and `B`:

```text
support(A -> B) = transactions containing A and B / all transactions

confidence(A -> B) = support(A and B) / support(A)

lift(A -> B) = support(A and B) / (support(A) * support(B))
```

Interpretation:

- support: how often the pair appears;
- confidence: when A appears, how often B also appears;
- lift > 1: the pair appears together more often than independence predicts;
- lift = 1: approximately independent;
- lift < 1: they avoid co-occurring.

The paper also uses Chi-square and Cramer's V to test and size association.

One protocol lesson for our work: the transaction unit must be declared
unambiguously. The paper discusses file/module co-occurrence but its method
text also describes smells occurring in the same commit. Our planned primary
Ansible snapshot transaction is one production file. Commit-level
co-occurrence, if added, must be a separately named analysis.

## Part 6 — how the paper measured change-proneness

The paper mines every project's Git history and determines whether changed
Puppet files are smelly at their revisions.

Two main measurements:

```text
change frequency(F) = number of commits that modify file F

churn(F, commit) = added lines + removed lines

change proneness(F) = sum over commits of churn(F, commit)
```

The implementation uses PyDriller to obtain file changes and churn.

The important design principle is “smell status at the historical revision.”
Looking only at today's HEAD and applying that label to old changes would
create time-travel bias.

## Part 7 — how the paper measured defect-proneness

The paper distinguishes:

- DFC: defect-fixing commit;
- DIC: defect-inducing commit;
- CED: intermediate commits where the defective file/version still exists.

### Step A — find fixing commits

Select commits that modify Puppet files and whose messages contain established
defect keywords such as error, bug, fix, or issue.

### Step B — trace inducing commits

Use Meta-change Aware SZZ (MA-SZZ):

1. find changed Puppet files in the fixing commit;
2. find fixed/modified lines in the diff;
3. use blame/history to find earlier commits that last changed those lines;
4. treat those candidates as inducing commits under the algorithm's rules.

### Step C — validate the labels

Two experienced authors manually examined a random sample of 375 commits,
used True/False/Unclear decisions, and resolved uncertainty by discussion.

Reported precision:

| Classification | Precision |
|---|---:|
| defect-fixing commits | 85.6% |
| defect-inducing commits | 97.6% |

This manual step is essential. Keyword search and SZZ are algorithms, not
ground truth.

## Part 8 — statistics in the paper

For change and defect comparisons, the paper uses:

- Mann-Whitney U at 95% confidence (`p < 0.05`);
- Cliff's delta for effect size;
- Kendall correlation between LOC and churn;
- file-size groups based on quartiles:
  - small: at most 38 LOC;
  - medium: over 38 and at most 147 LOC;
  - large: over 147 LOC.

Reported Cliff's delta interpretation:

```text
negligible: |d| < 0.147
small:      |d| < 0.33
medium:     |d| < 0.474
large:      |d| >= 0.474
```

Statistical significance does not imply a large practical effect. That is why
the effect size is necessary.

## Part 9 — headline findings from the paper

The paper reports:

- about 74% of studied IaC files were smelly;
- over 52% of smelly files contained at least two smell types;
- modularity-related smells were especially prevalent;
- smelly files were modified about 3.8 times more often;
- smelly files had about 3.1 times more change churn;
- smelly files were about 3.3 times more defect-prone;
- defects in smelly files persisted through about 1.65 more commits;
- defect-fix churn was roughly similar between smelly and non-smelly files.

These are Puppet results for the selected population. They must not be copied
as expected Ansible results.

## Part 10 — what this repository contains

AnsibleGuard is both a tool repository and an in-progress study workspace.

### Static-analysis product

- Python package and CLI under `src/ansibleguard/`;
- safe YAML/Ansible document inspection;
- recursive repository scanning;
- 60 normalized rules;
- configurable thresholds and detector options;
- GitLeaks and ansible-lint wrappers;
- Git review-range checks;
- JSON, CSV, text, SARIF, summaries, diagnostics, and provenance metadata;
- 168 passing automated tests at this audit.

### Study engineering

- OpenDev candidate discovery;
- human-selected five-project pilot;
- full cloning and detached frozen SHAs;
- row-level classification of every YAML candidate;
- strict file-manifest safety/completeness validation;
- explicit source/core/extended/review profiles;
- profile and manifest SHA-256 provenance;
- five-project, four-profile pilot outputs;
- initial positive and negative labels.

### What is not yet here

- approved/frozen Puppet-to-Ansible construct mapping;
- completed manual precision/negative calibration;
- research-eligible core;
- native external rule identity and research occurrence deduplication;
- full population selection/execution;
- history miner;
- Gerrit review miner;
- Apriori/statistical RQ1/RQ2 pipeline;
- longitudinal RQ3 analysis;
- MA-SZZ/RQ4 implementation;
- final replication package.

## Part 11 — mapping the paper's 12 smells to AnsibleGuard

This is a conceptual mapping, not proof of equivalence.

| Puppet smell | Candidate AnsibleGuard mapping | Current judgment | What is missing |
|---|---|---|---|
| ICE Complex Expression | `complex-expression` | Strong candidate | broader human calibration and frozen score |
| IIT Incomplete Tasks | `incomplete-task` | Strong candidate | decide treatment of intentional roadmap comments |
| IDS Deprecated Statement | `deprecated-modules`, `deprecated-module-option`, selected ansible-lint deprecations | Strong family, not frozen as one construct | version/collection matrix and one occurrence definition |
| IIC Incomplete Conditional | no ordinary task-YAML equivalent | Not applicable unless Jinja templates enter scope | define template population and Jinja AST rule |
| DMF Multifaceted Abstraction | cohesion/name signals plus manual role responsibility | Weak/partial | operational single-responsibility definition at role/file level |
| DIM Insufficient Modularization | `missing-abstraction`, size rules | Candidate | calibrate thresholds and repository context |
| DTC Tightly Coupled Modularization | `high-coupling` | Partial candidate | repository dependency graph and calibrated coupling measure |
| DWM Weakened Modularity | high coupling + low cohesion composite | Not currently a frozen rule | define level, formula, thresholds, and handle NLP validity |
| DUM Unstructured Module | `unstructured-module`, `unexpected-task-location` | Strong structural candidate | accept valid Ansible layout variants/project policy |
| DMP Missing Dependency | `broken-role-dependency`, possibly `missing-handler` | Partial | external roles, includes, collections, cross-file handlers |
| DDS Dense Structure | no repository-level dependency-density rule | Missing | build dependency graph and define density/structure threshold |
| DDE Deficient Encapsulation | no equivalent; `unguarded-variable` is not the same | Missing | define Ansible scope leakage across role/inventory boundaries |

The crucial warning is:

```text
unguarded-variable != deficient encapsulation
```

One asks whether a use has a visible definition/guard. The other asks whether
global scope leaks through module boundaries. Treating them as the same smell
would be construct invalidity.

## Part 12 — why the current eight-rule research core is not the paper's 12

Current core:

```text
complex-expression
incomplete-task
long-statement
unstructured-module
empty-abstraction
excessive-nesting
missing-abstraction
broken-role-dependency
```

Only some correspond directly to the SANER paper's observed 12. Long
Statement, Empty Abstraction, and Excessive Nesting come from the broader
configuration-smell candidate lineage, not Table II's 12 studied types.

Conversely, the current core omits or does not directly represent several
SANER constructs: deprecated statement, incomplete conditional, multifaceted
abstraction, tightly coupled modularization, weakened modularity, dense
structure, and deficient encapsulation.

Therefore the honest label today is:

```text
Ansible-specific empirical extension inspired by the paper
```

not:

```text
completed exact replication of the paper's 12 smells
```

## Part 13 — how our project selection differs

| Question | Puppet paper | AnsibleGuard study |
|---|---|---|
| ecosystem | Puppet repositories | OpenStack repositories containing Ansible |
| authoritative host | GitHub | OpenDev Git + Gerrit |
| source file | `.pp` | playbooks, tasks, handlers, vars, defaults, meta, inventory configuration |
| broad discovery | GitHub language query | OpenDev project registry plus approved seeds/keywords |
| quality filters | stars and commits | active OpenStack status, content, history, contributors; stars not primary |
| foreign IaC | excluded to keep Puppet-only | non-Ansible YAML classified/excluded; other code can remain in repo |
| test files | not the central distinction | explicit separate test-Ansible stratum |
| version freeze | history studied | exact SHA and collection provenance recorded before scans |

The change is deliberate. GitHub PR/star data are misleading for OpenStack
because GitHub is a mirror.

## Part 14 — how our detection approach differs

| Question | Puppet paper | AnsibleGuard |
|---|---|---|
| detector tools | Puppeteer + extended Puppet-Lint | 58 internal rules + GitLeaks + ansible-lint |
| study smell count | 12 | provisional core 8; 43 extended source rules kept separate |
| design level | file and module | file/task/play/role/repository/review-range depending on rule |
| file population | Puppet `.pp` | complete YAML manifest, production/test separation |
| detector calibration order | manual DFC/DIC sample emphasized | detector precision calibration required before main study |
| external identities | tool smell types retained | currently collapsed, so excluded from source research profiles |
| review checks | not mixed into source smells | separate `review-range` profile |

## Part 15 — how our research pipeline improves reproducibility

The current repository adds explicit controls that are valuable for the
Ansible extension:

1. exact commit SHA per project;
2. one classification row for every YAML candidate;
3. manifest completeness and path-safety validation;
4. manifest SHA-256 written to output;
5. exact sorted rule allowlist and SHA-256 written to output;
6. disjoint source/core/extended/review strata;
7. structured diagnostics separate from code findings;
8. output directories keyed by project, SHA, and profile;
9. skip-existing only after provenance compatibility checks;
10. preserved run logs and human-label tables.

These controls do not make a weak detector scientifically valid. They make the
experiment repeatable enough to discover and correct weakness.

## Part 16 — current five-project evidence

The completed engineering pilot covers:

| Measure | Current result |
|---|---:|
| projects | 5 |
| frozen profile runs | 20 |
| YAML candidates | 5,409 |
| included production Ansible files | 1,856 |
| source findings | 13,387 |
| provisional core findings | 1,250 |
| extended findings | 12,137 |
| review findings | 10 |
| saved diagnostics | 0 |

Core composition:

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

The pilot proves the collection/classification/profile pipeline works on real
repositories. It does not prove 1,250 real defects or answer RQ1–RQ4.

## Part 17 — the correct order from here

1. review and freeze the 12-smell construct mapping with the supervisor;
2. decide whether the goal is a comparable subset replication or a broader
   Ansible extension;
3. finish balanced positive/negative detector labels;
4. calculate precision and reviewer agreement;
5. refine or demote context-sensitive rules;
6. freeze code, environment, thresholds, configuration, core IDs, and hashes;
7. normalize/deduplicate occurrences;
8. select and freeze the main population;
9. run RQ1/RQ2 on frozen head snapshots;
10. implement revision/blob-aware history mining for RQ3;
11. implement and manually validate Gerrit/defect/SZZ evidence only if RQ4
    remains in scope;
12. publish protocol, manifests, labels, scripts, raw/checksummed outputs,
    tables, tests, plots, and deviations.

## Part 18 — threats we must state honestly

### Construct validity

An Ansible rule may not represent the same idea as the similarly named Puppet
smell. The mapping table and supervisor decision are the defense.

### Detector validity

Static heuristics can produce false positives/negatives. Stratified labels,
negative samples, precision, limited recall claims, and frozen versions are the
defense.

### Population validity

Five pilot projects or OpenStack alone do not represent all Ansible. Report the
scope and do not generalize beyond it without evidence.

### Historical validity

HEAD smell status cannot label older revisions. Analyze each changed Git blob
with versioned caching.

### Defect-label validity

Keywords and SZZ can mislabel commits. Prefer Gerrit/bug trailers and manually
validate fixing and inducing samples.

### Statistical validity

Files and revisions within the same project are not independent. Report effect
sizes/confidence intervals, correct multiple tests, and model project/LOC/age
and repeated observations.

## Final answer

The SANER'24 paper gives us a strong research blueprint and important Puppet
baseline results. AnsibleGuard has already implemented the difficult
engineering foundations for a reproducible Ansible extension: frozen SHAs,
complete file manifests, separated rule profiles, provenance hashes, real
pilot runs, and structured outputs.

The study is currently between engineering pilot and scientific calibration.
Its next success condition is not “more findings.” It is a reviewed construct
mapping and measured detector validity on the five frozen repositories.
