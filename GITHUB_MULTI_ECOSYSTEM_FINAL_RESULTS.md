# GitHub multi-ecosystem study: final session results

## Outcome

AnsibleGuard's reproducible real-repository workflow now supports both the
OpenDev/OpenStack stratum and native GitHub repositories. GitHub candidates are
discovered with cached, star-stratified searches; PR activity is enriched only
for an explicit shortlist; full SHAs are frozen; and final inclusion is decided
from production-Ansible file/LOC/history evidence rather than popularity.

## Conditions used

A native GitHub repository must be public, active within 24 months, non-fork,
non-mirror, non-archived, licensed or manually justified, and must have:

- at least 80 total commits and two contributors;
- at least 10 production Ansible YAML files and 500 production Ansible LOC;
- at least 20 commits touching those production Ansible paths;
- either at least 20% production-Ansible share among YAML files or at least
  2,000 production Ansible LOC;
- either five merged PRs in the last 24 months or two recent contributors.

Stars are context only. The candidate pool is split into 0-9, 10-99, 100-999,
and 1,000+ star bands, and no organization may dominate the pilot.

## Discovery result

The final discovery snapshot contains 173 candidates from 129 organizations:

| Star band | Candidates |
|---|---:|
| 0-9 | 71 |
| 10-99 | 36 |
| 100-999 | 34 |
| 1,000+ | 32 |

136 passed metadata-only gates; 37 required license review. Discovery never
sets final selection automatically.

## Screened repositories

| Repository | Stars | Merged PRs, 24m | Production files | Production LOC | YAML file share | Decision |
|---|---:|---:|---:|---:|---:|---|
| `kubernetes-sigs/kubespray` | 18,653 | 1,038 | 445 | 18,472 | 76.20% | selected |
| `O-X-L/ansible-opnsense` | 485 | 208 | 2 | 854 | 1.05% | excluded |
| `Linuxfabrik/lfops` | 88 | 101 | 783 | 32,533 | 83.03% | selected |
| `adfinis/ansible-role-the_bastion` | 2 | 49 | 17 | 1,264 | 48.57% | selected |

`ansible-opnsense` is a valid Python-module-heavy collection, but its YAML is
mostly tests, so it is outside this YAML-focused study rather than low quality.

## Technical-full scan result

| Repository | Files | Raw detectors | Canonical occurrences | Reduction | Provider status |
|---|---:|---:|---:|---:|---|
| Kubespray | 445 | 5,977 | 4,899 | 1,078 | internal/GitLeaks complete; original Ansible-Lint dependency error |
| Linuxfabrik/lfops | 783 | 11,380 | 9,617 | 1,763 | all providers complete |
| Adfinis role | 17 | 195 | 172 | 23 | all providers complete |

Kubespray exposed an Ansible Core compatibility conflict during Ansible-Lint's
automatic collection installation. The adapter now uses `--offline` so scans
cannot auto-install repository dependencies. A separate Kubespray `lint`
profile validation then completed with zero diagnostics and recorded
`dependency_mode=offline-no-auto-install`. The original partial result remains
unchanged for audit honesty.

## Other defect found by the expanded sample

Fourteen comment-only Kubespray `group_vars` files were initially described as
multi-document. The parser now distinguishes zero YAML documents from multiple
documents, allowing Ansible path classification to include these files while
genuine multi-document YAML remains unsupported.

## PR implementation

The PR workflow scans head and detached base, compares canonical occurrences,
protects SARIF upload on fork PRs, uploads all reports, and blocks provider
tool errors. The base review range is now pinned to `base..base`; comparator
policy failures are deferred with `continue-on-error`, but a missing decision
file blocks the final enforcement step.

## Verification

```text
210 passed in 26.23s
workflow YAML parsed
```

The detailed decisions, commands, failures, recoveries, API throttling, frozen
SHAs, and implementation explanation are in
`GITHUB_MULTI_ECOSYSTEM_AND_PR_SESSION.md`.
