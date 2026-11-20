# Selection Protocol v2: candidates, sequential filters, PRs, and validation

## Status and population claim

This is the supervisor-approved primary protocol for restarting repository and
pull-request validation. Earlier 173-candidate and small-pilot results remain
engineering evidence, not the final research population.

The population is deliberately described as:

> Public, non-fork, non-archived, non-mirror Ansible repositories whose latest
> commit is within six years of the frozen cutoff, with at least 1,000 commits,
> more than 50 total pull requests, and at least 50 merged pull requests that
> change production Ansible.

It must not be described as every Ansible repository.

## Frozen primary criteria

| Criterion | Primary value | Meaning |
|---|---:|---|
| Latest commit | within 6 years | recency measured from the frozen selection cutoff |
| Total commits | `>= 1000` | full Git commit count at the frozen SHA |
| Total PRs | `> 50` | inexpensive prefilter before PR file inspection |
| Merged Ansible-changing PRs | `>= 50` | real PR-study eligibility |
| Fork | false | candidate remains recorded but is excluded |
| Archived | false | candidate remains recorded but is excluded |
| Disabled | false | candidate remains recorded but is excluded |
| Mirror | false | prevents duplicated project histories |
| Production Ansible | at least one file | confirmed from the row-level classifier |
| Stars | information only | never an eligibility, quality, activity, or ranking score |

The commit precheck is applied before PR counting: one paginated default-branch
request estimates the count, and `git rev-list` confirms it at the frozen SHA.
Only projects passing 1,000 commits receive the initial total-PR request. The meaningful PR criterion is 50 merged
PRs that modify production Ansible paths. A repository with hundreds of
Python/documentation PRs but no Ansible changes is not suitable for validating
AnsibleGuard diff behavior.

## Seven descriptive evidence groups

Seven additional evidence groups are collected now, before deciding whether
any deserves to become a future gate. They are explicitly descriptive:
`descriptive_evidence_used_for_selection=false`. Missing descriptive evidence
does not reject a repository, and an automatic category never changes
`final_eligible`.

| Evidence group | Recorded fields and purpose |
|---|---|
| 1. Project purpose | automatic category, confidence, structural evidence, and blank two-reviewer fields for the eventual manual category: collection, role, infrastructure/deployment, mixed, example/training, or false positive |
| 2. Independence | owner, normalized repository family, ecosystem cluster, production-Ansible content fingerprint, exact-content duplicate group, and two-reviewer related-project assessment |
| 3. Ansible significance | production files and LOC, percentage of all tracked repository files, percentage of YAML files/LOC, and playbook/task/vars/metadata composition |
| 4. Ansible history | total repository commits separately from commits touching the frozen production paths, plus first/latest Ansible commit and history span |
| 5. PR decision evidence | every merged PR's changed paths, GitHub change status, previous path for renames, exact qualification basis, and base/head/merge SHAs |
| 6. Ansible-specific activity | latest production-Ansible commit separately from general repository `pushed_at`; this exposes README-only or non-Ansible recent activity |
| 7. Discovery coverage | source, discovery method, query provenance, declared coverage scope, and an explicit warning that metadata searches cannot claim every Ansible repository |

`select_study_candidates.py` reports each group as `recorded` or
`not-evaluated`, plus `descriptive_evidence_status` and
`descriptive_evidence_missing`. A blank field is therefore never mistaken for
a negative observation.

The automatic purpose classifier is only a review aid. Strong layouts can be
labelled as a collection or role; training/example metadata is flagged; all
ambiguous repositories remain `infrastructure-or-mixed-ansible-project` with
low confidence. Two reviewers make the final purpose and independence labels.
No percentage, Ansible-commit count, ecosystem size, or Ansible recency
threshold is introduced until the observed distributions and borderline cases
have been reviewed.

## Complete discovery before filtering

Discovery queries no longer contain `fork:false`, `archived:false`, or star
bands. If they did, repositories rejected by those criteria would disappear
before attrition could be measured.

GitHub omits forks from repository search unless `fork:true` is supplied, so
every primary query contains `fork:true`. This includes forks in the raw ledger;
the later `not_fork` gate excludes them and reports their loss.

The GitHub collector uses inclusive topic/name/description queries and
recursively partitions large searches by repository creation time. Every
partition must be at or below the search-result limit and must not report
`incomplete_results`. Results are deduplicated after collection, with every
discovery query retained as provenance.

Each row also declares the discovery methods and their limitation. The current
primary source union is GitHub repository search plus the Ansible Galaxy roles
and collections registries. Galaxy entries resolve to source repository URLs,
then canonical GitHub `owner/repository` identities are deduplicated and
hydrated with GitHub metadata. Unresolved and stale Galaxy entries remain in
the ledger with a resolution status; they are never silently deleted.

The earlier study's 972-project list will be added as a coverage source when its
replication data is obtained. GitHub and OpenDev/Gerrit review populations remain
separate because GitHub PR counts do not represent OpenStack Gerrit activity.
GitLab is deferred until a merge-request-equivalent protocol is approved.

### GitHub-only interim evidence strata

The complete 2026-08-05 GitHub discovery contains 667,044 rows. Because the
metadata-text query is intentionally broad, enrichment is stratified before
making hundreds of thousands of API requests:

- **strong evidence:** discovered by an explicit `topic:ansible`,
  `topic:ansible-role`, or `topic:ansible-collection` query, or later supplied
  by Ansible Galaxy;
- **weak evidence:** discovered only because “Ansible” appears in repository
  name, description, or topics through the broad metadata query.

Both strata remain stored. The strong stratum is enriched first; weak rows are
retained for sensitivity and later relevance analysis. This is a project-scope
definition, not a star, popularity, quality, or activity filter. The streaming
stratifier records the exact counts and does not load the 531 MB source CSV
fully into memory.

## Non-destructive sequential gates

No candidate row is deleted. Each gate is `true`, `false`, or
`not-evaluated`:

1. unique repository;
2. public;
3. not disabled;
4. not a fork;
5. not archived;
6. not a mirror;
7. latest commit within six years;
8. at least 1,000 default-branch commits (API precheck, frozen-Git confirmation);
9. more than 50 total PRs (one API request after the commit gate);
10. confirmed production Ansible;
11. at least 50 merged Ansible-changing PRs.

Every row records all failed reasons, all pending evaluations, its first
exclusion stage, screening eligibility, final eligibility, stars, source, and
collection provenance. The attrition CSV reports before, removed, pending,
remaining, and removal percentage at each cumulative stage.

## Commands

Discover GitHub candidates completely. Supplying `--pages` is explicitly a
bounded diagnostic run and is not valid for the final population:

```bash
.venv/bin/python scripts/discover_github_ansible.py \
  --as-of 2026-08-05T00:00:00Z \
  --output study/manifests/github-candidates-v2-discovered.csv
```

For a GitHub-only interim run, stratify the completed ledger before API
enrichment:

```bash
.venv/bin/python scripts/stratify_discovery_evidence.py \
  study/manifests/github-candidates-v2-discovered.csv \
  --strong-output study/manifests/github-candidates-v2-strong.csv \
  --weak-output study/manifests/github-candidates-v2-weak.csv \
  --summary-output study/manifests/github-discovery-strata-v2.json
```

Then enrich commits and total PRs in separate resumable stages. Do not use
`--refresh-cache`; cached completed repositories are reused after interruption:

```bash
.venv/bin/python scripts/discover_github_ansible.py \
  --input study/manifests/github-candidates-v2-strong.csv \
  --enrich-commits \
  --as-of 2026-08-05T00:00:00Z \
  --output study/manifests/github-candidates-v2-strong-commits.csv

.venv/bin/python scripts/discover_github_ansible.py \
  --input study/manifests/github-candidates-v2-strong-commits.csv \
  --enrich-prs \
  --as-of 2026-08-05T00:00:00Z \
  --output study/manifests/github-candidates-v2-strong-cheap-evidence.csv
```

The first call operates only on metadata-eligible strong rows and waits at
GitHub core-rate resets. The second makes one total-PR search request only for
rows that passed 1,000 commits. Galaxy collection can be run and merged later;
it does not invalidate this GitHub-only interim work.

Collect both Galaxy registries completely, merge sources, and hydrate
Galaxy-only GitHub repositories:

```bash
.venv/bin/python scripts/discover_ansible_galaxy.py \
  --kind both \
  --output study/manifests/galaxy-candidates-v2.csv

.venv/bin/python scripts/merge_study_candidates.py \
  study/manifests/github-candidates-v2-discovered.csv \
  study/manifests/galaxy-candidates-v2.csv \
  --output study/manifests/candidates-v2-merged.csv

.venv/bin/python scripts/hydrate_github_candidates.py \
  study/manifests/candidates-v2-merged.csv \
  --as-of 2026-08-05T00:00:00Z \
  --output study/manifests/candidates-v2-hydrated.csv
```

Apply the early commit precheck and then retrieve only total PRs for projects
passing 1,000 commits:

```bash
.venv/bin/python scripts/discover_github_ansible.py \
  --input study/manifests/candidates-v2-hydrated.csv \
  --enrich-commits \
  --enrich-prs \
  --as-of 2026-08-05T00:00:00Z \
  --output study/manifests/candidates-v2-cheap-evidence.csv
```

Apply the cheap gates and produce the first attrition report:

```bash
.venv/bin/python scripts/select_study_candidates.py \
  study/manifests/candidates-v2-cheap-evidence.csv \
  --as-of 2026-08-05T00:00:00Z \
  --output study/manifests/github-candidates-v2-screened.csv \
  --attrition-output study/manifests/github-attrition-v2.csv \
  --sensitivity-output study/manifests/github-sensitivity-v2.csv
```

Rows with `collect_for_screening=true` can then be fully cloned and classified:

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/github-candidates-v2-screened.csv \
  --output study/manifests/github-v2-frozen.csv

.venv/bin/python scripts/classify_study_files.py \
  study/manifests/github-v2-frozen.csv
```

Merge frozen history/content data and rerun the selection report. Then inspect
merged PR file lists only for projects that passed the cheap, content, and
1,000-commit gates:

```bash
.venv/bin/python scripts/select_study_candidates.py \
  study/manifests/candidates-v2-cheap-evidence.csv \
  --frozen study/manifests/github-v2-frozen.csv \
  --as-of 2026-08-05T00:00:00Z \
  --output study/manifests/github-candidates-v2-collected.csv \
  --attrition-output study/manifests/github-attrition-v2-collected.csv \
  --sensitivity-output study/manifests/github-sensitivity-v2-collected.csv

.venv/bin/python scripts/enrich_ansible_prs.py \
  study/manifests/github-candidates-v2-collected.csv \
  --output study/manifests/github-candidates-v2-prs.csv \
  --evidence-output study/manifests/github-ansible-pr-evidence-v2.csv
```

Finally rerun `select_study_candidates.py` on the PR-enriched file. That output
is the auditable eligible population. Stars remain in every row but do not
change `final_eligible`.

After scanning the frozen final projects, generate the complete playbook/file
distribution and two-reviewer ledger:

```bash
.venv/bin/python scripts/prepare_manual_validation.py \
  study/manifests/github-v2-final-frozen.csv \
  --classification-dir study/manifests/file-classification \
  --snapshots-root study/snapshots \
  --inventory-output study/labels/validation-inventory-v2.csv \
  --labels-output study/labels/manual-validation-v2.csv \
  --repository-review-output study/labels/repository-review-v2.csv
```

The label ledger contains every canonical occurrence plus one blind
`clean-file-review` unit for every production Ansible file with no occurrence.
This makes false-negative assessment part of the protocol.
The repository-review ledger separately carries the seven repository-level
evidence groups and blank independent labels for project purpose and project
independence. Initial reviewer decisions are preserved before consensus.

## PR classification

`enrich_ansible_prs.py` examines merged native-GitHub PRs and saves one evidence
row per PR with number, base/head SHA, merge time, changed-file count,
GitHub status (`added`, `modified`, `removed`, or `renamed`), previous names,
production Ansible paths, qualification basis, and qualification decision. It
uses exact paths from
the frozen file-classification manifest plus conservative Ansible layout
patterns. CI, Molecule, tests, docs, examples, and release-note paths do not
qualify merely because they contain YAML.

Renames qualify when either the new path or recorded previous path is a known
production Ansible path. Removed paths qualify through the frozen classifier or
conservative production layout. Unknown YAML paths qualify only when their
content at an available base/head/merge revision parses as an Ansible playbook
or task file. Thus a PR count remains auditable even when files move or vanish.

The evidence CSV, not only its aggregate count, is retained so every decision
can be audited and the same PRs can later be replayed with `ansibleguard diff`.
Every PR additionally records `primary_qualifies` and
`paper_comparable_qualifies`, so the broader tool population and prior-paper
comparison are never conflated.

## File populations and comparison cohort

The primary AnsibleGuard cohort contains every non-empty, classified production
Ansible artifact supported by the tool: playbooks, tasks, handlers, vars,
defaults, group/host vars, inventory/configuration, metadata, and import-only
task/playbook files. Tests, Molecule, CI, documentation/examples, generated or
vendored YAML, and invalid/empty YAML are recorded but not included in the
primary analyzable cohort.

Every classification row contains:

- `ansible_artifact_kind`;
- `import_only`;
- `primary_ansibleguard_cohort`;
- `paper_comparable_cohort`;
- `cohort_reason`.

The paper-comparable cohort is nested inside the primary cohort. It retains
parsed playbook/task-shaped YAML in playbook, task, or role paths and excludes
vars, inventory, empty, test, and import-only files. The paper uses this cohort
for comparison; the primary tool evaluation uses the broader cohort. We do not
adjust either population to reproduce a desired historical file count.

## Alternative thresholds

The primary values never change silently. A sensitivity CSV reports one-factor
alternatives while holding other primary gates fixed:

- latest commit within 4, 6, or 8 years;
- at least 500, 1,000, 1,500, or 2,000 commits;
- more than 25, 50, or 100 total PRs;
- at least 25, 50, or 100 merged Ansible-changing PRs.

Each scenario reports retained count and percentage. These results explain the
effect of our choices; they are not used to choose whichever threshold happens
to produce a desired number of repositories.

## Project and playbook validation

AnsibleGuard runs on every primary-cohort production Ansible file in each of the
approximately 100 final projects. Before manual sampling, record the complete
distribution per project: playbooks, task files, roles, handlers, variables,
tasks, LOC, findings, and diagnostics.

Repository-purpose and independence review happens before reporting the final
sample composition. Example/training-only and false-positive labels are
reported separately; related repositories are grouped by ecosystem/family so
the study never silently treats many repositories from one ecosystem as fully
independent observations. Whether those manual labels become exclusions is a
documented later decision, not an automatic v2 gate.

Manual validation is stratified by repository shape, project playbook count,
playbook task/LOC quartiles, finding/no-finding status, and rule. Large projects
must not dominate merely because they contain more playbooks. If the supervisor
requires a manual census of every playbook, workload is calculated first and
the census is performed; sampling is never substituted silently.

Two reviewers label independently before discussion. Each canonical occurrence
records both initial labels/reasons, agreement, consensus label, and consensus
reason. Agreed findings become true positives or false positives. Disagreements
are adjudicated without erasing the initial decisions. Clean playbook samples
are reviewed without seeing tool output so false negatives and recall can be
measured, not only precision.

## Current-data status

The existing frozen files contain 13 unique collected projects. Eight have at
least 1,000 commits; five do not. Six simultaneously have at least 1,000 commits
and more than six years of Git history, although history age is now descriptive
because the primary six-year gate is last-commit recency. PR evidence is
complete for only a small earlier shortlist, and merged Ansible-changing PR
counts have not yet been collected. Therefore no old sample should be called
the final Protocol v2 population.

The migrated current ledger is retained in:

- `study/manifests/github-candidates-v2-current.csv` — all 173 historical
  candidates, all available metadata/frozen metrics, every gate, and every
  pending evaluation;
- `study/manifests/github-attrition-v2-current.csv` — sequential current-data
  waterfall;
- `study/manifests/github-sensitivity-v2-current.csv` — primary and alternative
  threshold effects, including possible retention while evidence is pending.

This migration reports zero finally eligible repositories because
Ansible-changing PR inspection has not yet run, not because all candidates
failed. Total-PR evidence exists for only four rows; 169 are explicitly
pending. Three of those four pass the 1,000-commit gate and now await merged
Ansible-changing PR evidence. The old discovery queries already excluded forks
and archives, so their loss cannot be reconstructed from the old 173 rows; only
the new inclusive discovery run can measure those stages honestly.
