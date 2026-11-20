# PR Diff-Mode Validation Study — v1

## Purpose

Measure the precision of AnsibleGuard v0.0.4 in pull-request diff mode:

- Are "introduced" findings (new issues added by a PR) correctly identified?
- What is the false-positive rate for PR annotations?
- Do negative controls (integer configuration values) correctly NOT fire?
- Is SARIF upload and GitHub code scanning integration working end-to-end?

This is distinct from the snapshot-mode validation (149 repos, v0.0.3) because diff mode has a
different error model (introduced / unchanged / fixed) and PR annotations must be actionable.

## Repositories Under Study

| Fork | Original | Study branch | PR URL | SARIF uploaded |
|------|---------|-------------|--------|----------------|
| JedidiAymen/ansible-role-nginx | geerlingguy/ansible-role-nginx | test/pr-validation | [PR #1](https://github.com/JedidiAymen/ansible-role-nginx/pull/1) | yes |
| JedidiAymen/ansible-role-docker | geerlingguy/ansible-role-docker | test/pr-validation | [PR #1](https://github.com/JedidiAymen/ansible-role-docker/pull/1) | yes |
| JedidiAymen/ansible-role-mysql | geerlingguy/ansible-role-mysql | test/pr-validation | [PR #1](https://github.com/JedidiAymen/ansible-role-mysql/pull/1) | yes |
| JedidiAymen/ansible-role-security | geerlingguy/ansible-role-security | test/pr-validation | [PR #1](https://github.com/JedidiAymen/ansible-role-security/pull/1) | yes |
| JedidiAymen/ansible-role-nodejs | geerlingguy/ansible-role-nodejs | test/pr-validation | [PR #1](https://github.com/JedidiAymen/ansible-role-nodejs/pull/1) | yes |

## Key Results

- **Precision: 98.9%** (92/93 actionable introduced findings are TPs)
- **Wilson 95% CI: [94.2%, 99.8%]**
- **Negative controls: 10/10 passed** — no integer values flagged as secrets
- **SARIF ingestion: 5/5** repos with live code scanning alerts

See `PR_VALIDATION_RESULTS.md` for full per-finding labels and analysis.

## Files in This Directory

| File | Description |
|------|-------------|
| `README.md` | This file |
| `PR_VALIDATION_RESULTS.md` | Full findings, labels, precision metrics |
| `labels.csv` | Per-finding TP/FP labels with notes |
| `ansible-role-nginx/` | Local clone, base SHA: 5ff0b235 → head SHA: e8c806b5 |
| `ansible-role-docker/` | Local clone, base SHA: 243dba6c → head SHA: d2cbd53a |
| `ansible-role-mysql/` | Local clone, base SHA: 0a0ea6b7 → head SHA: b10c4be3 |
| `ansible-role-security/` | Local clone, base SHA: 06cb934b → head SHA: e1983689 |
| `ansible-role-nodejs/` | Local clone, base SHA: 8665848e → head SHA: 403e5810 |

## Completion Status

- [x] Repos forked (2026-08-13)
- [x] Repos cloned locally (2026-08-13)
- [x] Test branches created with controlled changes (2026-08-13)
- [x] Local diff runs completed (2026-08-13)
- [x] PRs opened on GitHub forks (2026-08-13)
- [x] SARIF uploaded to GitHub code scanning (2026-08-13)
- [x] Findings labelled (2026-08-13)
- [x] Precision computed and documented (2026-08-13)
