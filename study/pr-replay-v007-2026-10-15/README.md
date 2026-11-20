# Replay of real merged pull requests through PR mode (2026-10-16)

Every row comes from running `ansibleguard diff --base M^1 --head M --profile
pr --policy ratchet` (and a second `--profile review-range` pass) on a real
first-parent merge commit `M` of a repository in the frozen v0.0.7
population, with the code on branch `fix/v007-audit-2026-10-15`.

## Selection

`scripts/pr_replay_study.py` considered all 206 split repositories
(`selection.csv`):

- 62 heldout repositories were excluded without being opened;
- 119 calibration repositories have only shallow clones (no PR history);
- 4 had no recent merge changing 1–10 Ansible YAML files;
- **21 pull requests** were selected — the most recent qualifying merge of
  each full-history calibration repository.

Repositories are cloned into a scratch directory; the source clones are not
modified.

## Files

| File | Content |
|---|---|
| `selection.csv` | every repository and why it was or was not used |
| `prs.csv` | one row per pull request: exit code, policy, excluded providers, counts, runtime, clean-clone and worktree checks |
| `introduced.csv`, `fixed.csv` | every introduced / fixed finding |
| `review.csv` | review-rule findings over the real `base..head` range |
| `attribution-check.csv` | whether each introduced/fixed finding is supported by the diff (`scripts/pr_replay_attribution_check.py`) |

## Results

| Measure | Value |
|---|---:|
| Pull requests replayed | 21 |
| Errors / aborted comparisons | 0 |
| Compared with ansible-lint excluded (provider partial) | 7 |
| Policy failures (`ratchet`) | 0 |
| Introduced findings (actionable) | 46 (18) |
| Fixed findings | 7 |
| Moved findings | 688 |
| Uncertain pairs | 3 |
| Unchanged findings | 51,995 |
| Clones left modified / worktrees left behind | 0 / 0 |

**Attribution.** All 46 introduced findings and all 7 fixed findings are
supported by the diff: 29 introduced in files the PR added, 10 on added or
rewritten lines, the rest in tasks whose content changed or aggregate metrics
of changed files. One fixed finding (`unnamed-play`, `usegalaxy-eu/vgcn`) was
flagged by the automatic check because it measures task spans, not plays;
manual review confirms the PR named that play.

## What the replay changed in the tool

Each problem below was found on these real pull requests and fixed before the
final run (details in `CHANGELOG.md`):

| Problem on real PRs | Before | After |
|---|---|---|
| Comparison aborted when ansible-lint was partial or any selected YAML (often a Jinja `templates/*.yml`) failed to parse | 13 of 21 PRs would abort (exit 2): 7 lint-partial, 11 with an unparseable file (overlapping) | 0 |
| Identical findings shifted by an edit reported as fixed + introduced; line-number and location-fingerprint coincidences paired different tasks | introduced/fixed 462/422 (IBM PR alone 373/368 for a 24-line change) | 46/7; 688 moves recognized |
| `environment:` as a list of mappings reported as an `error` → PR blocked | `cfpb/aurora` failed the policy | passes |
| Review rules counted Kubernetes/Kustomize YAML and changelog fragments as Ansible configuration; judged merge-commit messages | FPs on several PRs | removed |

## Limits

- 21 PRs from 21 repositories; one PR per repository. This is a functional
  validation of PR mode, not a population estimate.
- Attribution checks whether the diff supports a classification; whether each
  finding is a true smell is a separate (precision) question.
- A canonical occurrence can gain a native rule (an unnamed task that newly
  also has `jinja[spacing]`) and still count as moved.
