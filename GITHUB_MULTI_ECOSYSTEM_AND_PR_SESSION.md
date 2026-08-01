# GitHub multi-ecosystem repository study and PR session

## Session rule

Every design decision, code change, command, test, result, and unresolved
question from this session is recorded in this file.

Session date: 1 August 2026.

## User goals

1. Do not limit real-repository testing to OpenStack.
2. Add well-maintained GitHub repositories from other organizations and use
   defensible selection conditions.
3. Discuss commits, Ansible/YAML percentage, stars, and pull-request evidence.
4. Prepare the AnsibleGuard implementation for a real pull request.
5. Preserve reproducibility and write all session work to Markdown.

## Initial audit

Current branch:

```text
sarif-validation-support
```

Current remote:

```text
origin https://github.com/Narjes-b/AnsibleChecklist.git
```

The worktree already contains the completed profile, detector, output-v2,
five-repository, and documentation changes from the previous sessions. These
changes must not be lost or mixed with unrelated cleanup.

Existing repository collection is OpenStack-specific:

- `scripts/discover_openstack_ansible.py` reads the authoritative OpenDev
  project registry;
- discovery deliberately does not auto-select candidates;
- `scripts/clone_study_repositories.py` clones selected rows, freezes a full
  commit SHA, and records commit/date/contributor/YAML metrics;
- `scripts/classify_study_files.py` creates a row-level YAML population;
- `scripts/run_study_pilot.py` verifies frozen HEAD and manifest/profile
  provenance before scanning.

The existing OpenStack design correctly rejects GitHub stars and GitHub pull
requests as OpenStack quality evidence because the `openstack` GitHub
organization is a mirror and review occurs in Gerrit/OpenDev.

For native GitHub repositories, GitHub stars and PR history can be recorded,
but neither should be the only inclusion gate.

## Initial PR implementation audit

The local workflow already implements:

- full-history checkout;
- head scan using profile `pr`;
- detached base worktree scan;
- validated GitLeaks `base..head` history scan;
- canonical occurrence comparison;
- `observe` policy enforcement;
- v2 summary enrichment;
- SARIF upload for trusted PRs;
- artifact fallback for fork PRs;
- external-tool failure blocking.

This session strengthened that implementation in two places:

1. The detached base scan now sets both review SHAs to the base commit. This
   produces an empty review delta for the baseline instead of accidentally
   inspecting `base~1..base`.
2. The comparator uses `continue-on-error: true` so its policy exit code is
   deferred to the final enforcement step, but no longer uses shell
   `|| true`. On pull requests, a missing decision file now blocks the job,
   distinguishing an expected policy failure from a comparator crash.

Static workflow-contract tests lock full-history checkout, canonical base/head
paths, base-range pinning, delayed enforcement, tool-error blocking, and safe
SARIF behavior for fork pull requests.

The implementation has not yet been pushed or opened as a GitHub pull request
in this session. Creating an external PR will be done only after local branch,
diff, commit structure, and workflow checks are prepared and reviewed.

The branch already exists on `origin` at the same commit as local `HEAD`.
There are more than 2,000 lines of uncommitted implementation/documentation
changes from the connected sessions, plus pre-existing draft files. Therefore
publication must use an explicit file/commit boundary; blindly committing the
whole worktree would make the PR difficult to review.

## Direction for multi-ecosystem selection

Repository selection will use three layers:

1. **Eligibility gates** remove repositories that cannot support a meaningful
   Ansible study.
2. **Quality/context metadata** records stars, forks, contributors, PRs,
   releases, activity, and licensing without treating popularity as truth.
3. **Stratified sampling** deliberately chooses different repository sizes,
   purposes, organizations, and popularity/activity bands.

The exact thresholds and implementation are developed in the next sections of
this document during this session.

## Proposed selection model

### Why one score is not enough

Stars measure attention, not Ansible quality. Pull-request counts measure a
workflow style, not correctness. YAML percentage can be inflated by CI,
documentation, generated data, or test fixtures. The study will therefore not
rank repositories with a single popularity score.

Discovery queries are stratified by the four star bands rather than taking the
most recently updated repositories from one global search. Additional
`ansible-role` and `ansible-collection` topic queries improve repository-shape
coverage. The default search requires an Ansible-specific GitHub topic; a
broad README mention created too many Kubernetes/dotfiles false candidates in
the first trial.

Selection uses hard eligibility gates, recorded context fields, and stratified
sampling.

### Hard eligibility gates

A native GitHub candidate is eligible only when all of these are true:

1. public and cloneable;
2. not archived or disabled;
3. not a fork and not declared as a mirror;
4. has an identifiable open-source SPDX license, or is manually reviewed and
   explicitly justified;
5. default branch received a push within the last 24 months;
6. at least 80 commits overall, preserving comparability with the earlier
   study threshold;
7. at least two contributors overall;
8. at least 10 production Ansible YAML files;
9. at least 500 nonblank/non-comment production Ansible lines;
10. at least 20 commits touch the manifest-selected production Ansible paths;
11. Ansible relevance is demonstrated by either:
    - production Ansible files are at least 20% of all repository YAML
      candidates; or
    - production Ansible code contains at least 2,000 physical lines.

The dual relevance condition allows a large infrastructure repository with a
substantial Ansible subsystem without accepting a general project containing
only one example playbook.

### Pull-request activity

For repositories developed natively on GitHub, record:

- total pull requests;
- total merged pull requests;
- merged pull requests in the last 24 months;
- open pull requests;
- median time to merge when a bounded sample is collected;
- reviewed/approved PR evidence when the API budget permits.

PR activity is a maintenance/collaboration signal, not a correctness label.
The primary sample should normally require either five merged PRs in the last
24 months or documented recent multi-contributor commit activity. This
alternative avoids excluding projects that use a reviewed non-PR workflow.

OpenStack remains a separate source stratum: Gerrit/OpenDev evidence is
authoritative there, and GitHub mirror PR counts remain excluded.

### Stars and forks

Record stars, forks, subscribers, and repository age as context. Do not use a
single minimum-star gate for the entire sample. Stratify native GitHub
projects into popularity bands:

```text
0-9 stars       low-visibility validation stratum
10-99 stars     small/community
100-999 stars   established
1,000+ stars    highly visible
```

The main sample should include multiple bands. A sensitivity analysis can
repeat conclusions with the 0-9 band removed. This makes popularity bias
visible instead of hiding it inside eligibility.

### Repository-shape strata

Sample across:

- standalone roles;
- Ansible collections;
- deployment/orchestration repositories;
- application infrastructure repositories;
- inventory/configuration repositories.

Limit any one organization to at most two native-GitHub repositories in the
first expanded pilot. Keep the five OpenStack projects as their own ecosystem
stratum rather than allowing them to dominate the sample.

### Exclusions requiring an explicit reason

- tutorial/course/example-only repository;
- generated or vendored Ansible majority;
- CI YAML mistaken for production Ansible;
- mirror/fork/duplicate of another selected repository;
- missing license;
- stale activity;
- insufficient commits, contributors, Ansible files, LOC, or
  Ansible-touching commits;
- inaccessible/submodule-only source;
- unclear production-file classification after manual review.

## Official GitHub API facts checked

Current GitHub REST documentation confirms that repository metadata exposes
stars, forks, archive/disabled state, push timestamps, default branch, topics,
license, mirror information, and contributor/language endpoints. Language
values are bytes, but they are not sufficient for this study because GitHub's
language summary does not distinguish production Ansible YAML from CI or data
YAML.

GitHub documents 60 unauthenticated REST requests per hour and normally 5,000
authenticated requests per hour. Search uses a more restrictive, separate
bucket. The implementation must therefore cache responses, inspect rate-limit
headers, use bounded retries, avoid concurrent request bursts, and never store
tokens in source or manifests.

Official references:

- https://docs.github.com/en/rest/repos/repos
- https://docs.github.com/en/rest/pulls/pulls
- https://docs.github.com/en/rest/pulls/reviews
- https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

## Planned manifest fields

Discovery-time fields:

```text
source_host, project, source_url, clone_url, html_url
description, topics, default_branch
created_at, updated_at, pushed_at
archived, disabled, fork, mirror_url
license_spdx, stars, forks, subscribers, repository_size_kb
open_issues, discovery_query, discovered_at_utc
selection_as_of_utc
total_prs, merged_prs, merged_prs_last_24_months, open_prs
collect_for_screening, selected, exclusion_reason, manual_review_note
```

Selection uses two distinct states:

- `collect_for_screening=true` permits cloning and measurement but does not
  admit the repository to the study;
- `selected=true` is set only after all post-clone gates and manual file-scope
  review pass.

Post-clone/freeze fields:

```text
commit_sha, commit_date_utc, total_commits, contributors
yaml_candidates, yaml_loc
production_ansible_files, production_ansible_loc
production_ansible_yaml_file_percent, production_ansible_yaml_loc_percent
ansible_touching_commits
eligibility_status, eligibility_reasons
```

## First cross-band screening decision

Four native-GitHub repositories were screened at full immutable SHAs. The
shortlist uses four organizations and one repository from each star band.

| Repository | Stars | Merged PRs, 24m | Commits | Contributors | Production Ansible files | Production Ansible LOC | YAML file share | Ansible-touching commits | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `kubernetes-sigs/kubespray` | 18,653 | 1,038 | 8,874 | 1,483 | 445 | 18,472 | 76.20% | 3,036 | eligible |
| `O-X-L/ansible-opnsense` | 485 | 208 | 1,206 | 47 | 2 | 854 | 1.05% | 80 | excluded |
| `Linuxfabrik/lfops` | 88 | 101 | 3,594 | 32 | 783 | 32,533 | 83.03% | 1,986 | eligible |
| `adfinis/ansible-role-the_bastion` | 2 | 49 | 94 | 4 | 17 | 1,264 | 48.57% | 41 | eligible |

The O-X-L repository is not a bad repository. It is a Python-module-heavy
Ansible collection whose YAML population is predominantly tests: 178 test
files and only two production Ansible YAML files. It is excluded because the
study evaluates YAML playbooks/roles/configuration and it fails both the
10-production-file gate and the 20%-or-2,000-LOC relevance gate.

The decision is frozen in `study/manifests/github-final-selection.csv`.
Screened-but-rejected rows remain in that file with explicit reasons; the
three passing rows alone have `selected=true` and immutable revisions.

## Dependency isolation found during the real scan

The first Kubespray `technical-full` scan produced valid internal/GitLeaks
output but an Ansible-Lint `tool-error`. Ansible-Lint tried to install the
repository as collection `kubernetes_sigs.kubespray:2.32.0`; that collection
requires Ansible Core `>=2.18,<2.19`, while this tool environment contains
Ansible Core 2.21 through Ansible-Lint 26.4. The dependency solver correctly
refused the incompatible installation.

This revealed that allowing Ansible-Lint to auto-install arbitrary scanned
repository dependencies is both non-reproducible and an unnecessary execution
and network risk. The adapter now always passes `--offline`, which disables
requirements installation and schema refreshing, and records
`dependency_mode=offline-no-auto-install` in run metadata. Missing project
dependencies can therefore appear as normal Ansible-Lint findings/diagnostics
without mutating the study environment. A unit test verifies both the command
flag and provenance metadata.

The original Kubespray result remains recorded as partial and is not silently
rewritten. A clean validation run is performed in a new output root after this
change.

## Files inspected

- `scripts/discover_openstack_ansible.py`
- `scripts/clone_study_repositories.py`
- `scripts/run_study_pilot.py`
- `study/manifests/pilot.csv`
- `.github/workflows/ansibleguard.yml`
- existing real-repository and calibration plans

## Work log

- Created this session record before changing the multi-ecosystem discovery
  implementation.
- Confirmed the existing OpenStack provenance and PR workflow boundaries.
- Added `scripts/discover_github_ansible.py`. It discovers native GitHub
  candidates through six bounded, star/shape-stratified searches, deduplicates projects,
  caches API responses, supports offline replay and a frozen `--as-of` time,
  records popularity/licensing/activity/provenance fields, and never
  auto-selects a repository.
- Added optional bounded PR-count enrichment. It records total, merged,
  recently merged, and open pull-request counts for native GitHub projects.
  The token is read only from `GITHUB_TOKEN` and is never written to the cache
  or manifest.
- PR enrichment accepts repeatable `--enrich-project owner/repository`
  arguments. This lets us query a manually reviewed, cross-band shortlist
  instead of spending API quota on the highest-star rows only.
- Cached responses are reused by default; `--refresh-cache` explicitly asks
  for current API data, and `--offline` guarantees no network access.
  `discovered_at_utc` records the real collection time while
  `selection_as_of_utc` separately records the activity-gate cutoff.
- Added `tests/test_github_discovery.py` for eligibility explanations,
  popularity bands, query deduplication, bounded PR enrichment, and offline
  cache behavior.
- Extended `scripts/clone_study_repositories.py` to accept both OpenDev and
  GitHub-native manifest rows. Frozen rows now retain source and popularity
  provenance and calculate YAML LOC, production-Ansible file and LOC shares,
  recent contributors, commits touching the production Ansible paths, and
  explicit post-clone eligibility reasons.
- Kept OpenDev rows in a separate eligibility stratum. A GitHub URL is no
  longer written into the `opendev_url` column, and source-host inference is
  shared by cloning and eligibility evaluation.
- Final GitHub eligibility now enforces the maintenance alternative described
  above: at least five merged PRs in the last 24 months, or at least two recent
  contributors. Pre-clone eligibility and its reasons are copied into the
  frozen manifest and participate in the final decision.
- Separated screening authorization from final inclusion. The collector reads
  either `collect_for_screening=true` or legacy/final `selected=true`, while
  discovery initializes both to false.
- Row-level manual review exposed 14 comment-only Kubespray `group_vars`
  files reported as unsupported multi-document YAML. The root cause was in
  `inspect_document`: `yaml.load_all` returns zero documents for comment-only
  content, and zero was grouped with two-or-more documents. Zero documents now
  return `parse_status=empty` and `document_type=empty`; path classification
  then correctly includes `group_vars`, while real multi-document files remain
  unsupported. A regression test covers this exact case.
- Added a local GitHub-style repository collection test. It verifies source
  provenance, frozen SHA, YAML/Ansible percentages, Ansible-touching commits,
  and transparent rejection reasons without requiring network access.

### Focused test run 1

Command:

```text
.venv/bin/python -m pytest -q tests/test_github_discovery.py tests/test_study_scripts.py
```

Result: 11 passed and 1 failed. The failure was an incorrect new test
expectation: the fixture contains eight physical YAML lines (three production,
three test, and two Zuul), not six. The implementation correctly returned
eight and a 37.5% production-Ansible YAML LOC share. The test was corrected;
no production logic was changed for this failure.

### Focused test run 2

The same 12 focused tests passed after correcting the expectation. A Ruff
command was also attempted, but Ruff is not declared in `pyproject.toml` and
is not installed in `.venv`; it failed with `No module named ruff`. No package
was installed and no project dependency was changed. The repository's declared
CI validation is `pytest -q`, so subsequent verification uses that contract.

### First live discovery trial

The initial three-query trial retrieved 86 deduplicated repositories and 64
passed pre-clone gates; all 86 remained `selected=false`. Distribution was 72
in the 0-9-star band, 10 in 10-99, two in 100-999, and two in 1,000+. Twenty-two
repositories needed license review. The result demonstrated recency and README
mention bias, so it is retained as a documented experiment but replaced by
star-stratified, Ansible-topic default queries.

## Live discovery and PR evidence results

- Final topic/stratified discovery: 173 candidates, 136 metadata-eligible,
  129 organizations, and star-band counts 71/36/34/32.
- Exactly four manually named shortlist rows received PR enrichment; every
  other row kept empty PR fields and every row remained `selected=false`.
- GitHub's unauthenticated search limit interrupted the enrichment command
  twice. Ten, then five more responses were cached. The final resume retrieved
  the last response and atomically wrote all four enriched rows; no partial CSV
  was presented as complete.

PR evidence was 1,038/208/101/49 merged PRs in the last 24 months for
Kubespray, O-X-L, Linuxfabrik, and Adfinis respectively.

## Clone, classification, and scan execution log

The first four-repository clone command was interrupted after creating an
incomplete Kubespray `.git` directory. Three other repositories then froze
successfully, while Kubespray failed transparently with no usable branch. The
clone was repaired with `git fetch --prune --tags origin`—no directory was
deleted—and the resumed collector froze all four successfully.

Row-level classification generated 1,753 YAML rows: 584 Kubespray, 191 O-X-L,
943 Linuxfabrik, and 35 Adfinis. A first summary command used stale column names
(`classification`, `reason`) and failed with `KeyError`; rerunning with the
current `file_class` and `classification_reason` schema succeeded. This did not
alter any manifest.

The three eligible repositories were scanned with `technical-full` and their
SHA-bound classification manifests:

| Repository | Included files | Raw findings | Canonical occurrences | Reduction | Diagnostics |
|---|---:|---:|---:|---:|---:|
| Kubespray | 445 | 5,977 | 4,899 | 1,078 | 1 Ansible-Lint dependency error |
| Linuxfabrik/lfops | 783 | 11,380 | 9,617 | 1,763 | 0 |
| Adfinis role | 17 | 195 | 172 | 23 | 0 |

The separate post-fix Kubespray `lint` validation produced zero raw/canonical
findings, zero diagnostics, `ansible_lint=completed`, and
`dependency_mode=offline-no-auto-install`.

## Verification results

Focused progression:

- 12 focused discovery/study tests passed after correcting one fixture LOC
  expectation;
- 15 tests passed after cache, PR-shortlist, and screening-state changes;
- 22 parser/file-manifest/discovery/study tests passed after the comment-only
  YAML fix;
- 16 adapter/profile/status tests passed after offline dependency isolation;
- 17 workflow/comparison/adapter tests passed after PR enforcement hardening.

Final commands and outcomes:

```text
.venv/bin/python -m pytest -q
210 passed in 26.23s

.venv/bin/python -c '<parse every .github/workflows/*.yml with yaml.safe_load>'
workflow YAML parsed

git diff --check
initial staging found CRLF-generated CSV rows; manifest writers were changed to
explicit LF line endings, evidence was regenerated, and the final check passed
```

Ruff was not installed or declared and was not added merely for this session.

## Pull-request handoff

Remote refresh showed that `sarif-validation-support` already has open pull
request #1, titled `Sarif validation support`, against `main`. Therefore this
session updates that PR rather than creating a duplicate. Before the new
commits, the branch was 37 commits ahead and five commits behind current
`origin/main`; no history rewrite, rebase, or force push was performed.

The unrelated untracked draft
`ARTICLE_APPROACH_TOOL_BUILD_TESTING_PERFORMANCE.md` is explicitly excluded
from the session commits. Generated repository clones, API cache, frozen
working manifests, logs, and scan snapshots remain ignored; only auditable
candidate/decision/classification manifests are committed.

The first `git add` attempt failed because `.git/index.lock` is read-only in
the default workspace sandbox; it made no index change. The same explicit file
list was then staged with approved Git metadata access. The implementation,
tests, workflow, and auditable study evidence were committed as:

```text
28e20eb feat: add auditable profiles PR ratcheting and GitHub study
```

Documentation is committed separately so reviewers can distinguish behavior
from explanation. No broad `git add .`, rebase, force push, or history rewrite
is used.

## Explicit no-merge decision

After the two commits were pushed, GitHub reported PR #1 as `CONFLICTING`
because `main` has five commits not present on this branch. A proposed
`git merge origin/main` approval was interrupted and rejected by the user.
The command made no repository change: there was no `MERGE_HEAD` or conflict
state, and immediately after interruption local/remote
`sarif-validation-support` both remained at `c951801`. Later documentation-only
commits do not integrate `main`.

Per the user's instruction, this session will not merge, rebase, or otherwise
integrate `main`. PR #1 therefore remains open with its existing base and
conflicting status until the user chooses a different PR base or integration
strategy.
