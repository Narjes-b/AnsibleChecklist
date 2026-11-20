# v0.0.5 smoke scan — 25 real repositories

Not a substitute for the Phase 5-7 evaluation/validation pipeline. This is a
quick real-data smoke test of AnsibleGuard running on the `feat/v005-empirical-study`
branch against 25 already-cloned, real-world Ansible repositories, run while
Phase 3's full collection pipeline was executing separately. It has no
ground-truth labels, so it reports raw finding volume and detector
distribution, not precision/recall/false-positive counts.

## Repositories scanned

geerlingguy's 8 roles (docker, nginx, mysql, postgresql, jenkins, firewall,
security, kubernetes), 3 ansible-lockdown CIS hardening roles (RHEL8, RHEL9,
Ubuntu22), dev-sec/ansible-collection-hardening, konstruktoid/ansible-role-hardening,
debops/debops, freeipa/ansible-freeipa, wazuh/wazuh-ansible, roots/trellis,
davestephens/ansible-nas, khuedoan/homelab, saltyorg/Saltbox,
spantaleev/matrix-docker-ansible-deploy, mitogen-hq/mitogen, ceph/ceph-ansible,
trailofbits/algo, kubernetes-sigs/kubespray.

All 25 completed, 0 failed.

## Aggregate results

| Metric | Value |
|---|---|
| Raw findings | 52,572 |
| Canonical occurrences (post-dedup) | 48,296 |
| — errors | 2,755 |
| — warnings | 22,997 |
| — notes | 22,544 |

Top detectors by volume: `missing-tags` (15,598), `unguarded-variable` (12,586),
`complex-expression` (3,329), `credential-log-exposure` (2,583), `large-task`
(2,283), `long-yaml-line` (2,096), `long-task-name` (1,636),
`loop-legacy-syntax` (1,573).

Full breakdown: `aggregate.json`. Per-repo raw output: `<repo>/report.json`
(counts/health) and `<repo>/summary.csv` (one row per file).

## Known limitation — read before drawing conclusions

**Every run came back `status: partial`.** `ansible-lint` cannot run at all on
this Windows machine (`No module named 'grp'` -- a Unix-only module ansible-core
imports internally; ansible-lint does not run natively on Windows). Gitleaks
and every one of AnsibleGuard's own 41 detectors completed cleanly on all 25
repos. **These numbers are AnsibleGuard + Gitleaks only — ansible-lint's
findings are entirely absent, not zero-because-clean.** Running this on Linux
or WSL would add ansible-lint's findings on top of these counts.

## On precision / false positives

No ground truth exists for this sample, so no FP/precision number can be
computed from it. What exists elsewhere in the project:

- v0.0.4 (the engine's pre-rewrite milestone) has a completed, statistically
  bounded validation: 98.9% precision [94.2%, 99.8%] on PR-diff mode. That is
  not v0.0.5, and v0.0.5's own implementation ledger states its held-out
  precision/recall study has not yet been run.
- Getting a real number for the current v0.0.5 engine requires Phase 6/7 of
  the ongoing study (manual validation, stratified sampling, Wilson
  confidence intervals) against the actual collected corpus.

## Also fixed while producing this scan

The CLI crashed on Windows before any output was written, on the first
progress-emoji print (`UnicodeEncodeError` against the default cp1252 console
codepage). Fixed at the source in `src/ansibleguard/cli.py` on
`feat/v005-empirical-study` (commit `4bfbc57`) — stdout/stderr are now
reconfigured to UTF-8 at CLI entry. This scan was run after that fix.
