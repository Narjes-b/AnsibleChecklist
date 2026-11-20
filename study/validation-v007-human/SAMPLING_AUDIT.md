# V0.0.7 sampling audit — agreement pilot

Audit time: `2026-10-06T02:28:37.293307Z`
Integrity result: **PASS**

This is the calibration-only agreement pilot. It is not a representative precision sample, recall panel, threshold sample, or heldout evaluation.

## Frozen populations

- Detector-quality repository universe: 206 (144 calibration / 62 heldout).
- Full static-source occurrence universe: 265,434.
- Static-source candidates in calibration repositories: 189,029.
- Static-source candidates in heldout repositories: 76,405; no heldout rows/contexts were emitted.
- Agreement-pilot workload: 350 rows for Reviewer A and the same 350 rows for Reviewer B.

## Pilot counts by family, rule, and repository

| Family | Rule | Source candidates | Context-eligible | Missing first parent | Missing required parent | Selected | Eligible not selected |
|---|---|---:|---:|---:|---:|---:|---:|
| Objective correctness | `ansibleguard/broken-role-dependency` | 1 | 1 | 0 | 0 | 0 | 1 |
| Objective correctness | `ansibleguard/invalid-numeric-value` | 4 | 4 | 0 | 0 | 0 | 4 |
| Objective correctness | `ansibleguard/invalid-task-attribute-type` | 23 | 23 | 0 | 0 | 4 | 19 |
| Objective correctness | `ansibleguard/loop-legacy-syntax` | 4729 | 4729 | 0 | 0 | 8 | 4721 |
| Objective correctness | `ansibleguard/missing-handler` | 7 | 7 | 0 | 0 | 2 | 5 |
| Objective correctness | `ansibleguard/non-idempotent-command` | 1173 | 1173 | 0 | 0 | 8 | 1165 |
| Objective correctness | `ansibleguard/overriden-keys` | 4 | 4 | 0 | 0 | 0 | 4 |
| Objective correctness | `ansibleguard/read-only-command-change` | 679 | 679 | 0 | 0 | 7 | 672 |
| Objective correctness | `ansibleguard/redirected-module` | 674 | 674 | 0 | 0 | 7 | 667 |
| Objective correctness | `ansibleguard/silent-error-suppression` | 1446 | 1446 | 0 | 0 | 7 | 1439 |
| Objective correctness | `ansibleguard/unpinned-ansible-dependency` | 286 | 286 | 0 | 0 | 7 | 279 |
| Variable/reference reasoning | `ansibleguard/missing-bool-filters` | 6 | 6 | 0 | 0 | 5 | 1 |
| Variable/reference reasoning | `ansibleguard/overriding-facts` | 9 | 9 | 0 | 0 | 5 | 4 |
| Variable/reference reasoning | `ansibleguard/redundant-default-value` | 12 | 12 | 0 | 0 | 3 | 9 |
| Variable/reference reasoning | `ansibleguard/role-variable-precedence-collision` | 26 | 26 | 0 | 0 | 5 | 21 |
| Variable/reference reasoning | `ansibleguard/shell-environment-export` | 4 | 4 | 0 | 0 | 0 | 4 |
| Variable/reference reasoning | `ansibleguard/unguarded-variable` | 36864 | 36864 | 0 | 0 | 7 | 36857 |
| Variable/reference reasoning | `ansibleguard/unnecessary-set-fact` | 1423 | 1423 | 0 | 0 | 7 | 1416 |
| Variable/reference reasoning | `ansibleguard/unscoped-shell-variable` | 69 | 69 | 0 | 0 | 6 | 63 |
| Variable/reference reasoning | `ansibleguard/unused-registered-variable` | 843 | 843 | 0 | 0 | 6 | 837 |
| Variable/reference reasoning | `ansibleguard/variable-use-before-definition` | 147 | 147 | 0 | 0 | 6 | 141 |
| Security | `ansibleguard/become-scope-too-broad` | 334 | 334 | 0 | 0 | 8 | 326 |
| Security | `ansibleguard/credentials-leaking-in-log` | 4887 | 4887 | 0 | 0 | 8 | 4879 |
| Security | `ansibleguard/default-credentials` | 208 | 208 | 0 | 0 | 8 | 200 |
| Security | `ansibleguard/insecure-permissions` | 337 | 337 | 0 | 0 | 8 | 329 |
| Security | `ansibleguard/missing-validate-certs` | 482 | 482 | 0 | 0 | 8 | 474 |
| Security | `ansibleguard/plaintext-sensitive-variable` | 470 | 470 | 0 | 0 | 7 | 463 |
| Security | `ansibleguard/unsafe-file-write` | 6 | 6 | 0 | 0 | 3 | 3 |
| Security | `ansibleguard/vault-inline-overload` | 2 | 2 | 0 | 0 | 0 | 2 |
| Style/policy | `ansibleguard/duplicate-task-names` | 856 | 856 | 0 | 0 | 5 | 851 |
| Style/policy | `ansibleguard/galaxy-meta-incomplete` | 564 | 564 | 0 | 0 | 5 | 559 |
| Style/policy | `ansibleguard/inconsistent-naming-convention` | 43 | 43 | 0 | 0 | 5 | 38 |
| Style/policy | `ansibleguard/long-statement` | 4628 | 4628 | 0 | 0 | 5 | 4623 |
| Style/policy | `ansibleguard/long-task-name` | 4103 | 4103 | 0 | 0 | 5 | 4098 |
| Style/policy | `ansibleguard/missing-file-extension` | 8 | 8 | 0 | 0 | 2 | 6 |
| Style/policy | `ansibleguard/missing-tags` | 67830 | 67830 | 0 | 0 | 5 | 67825 |
| Style/policy | `ansibleguard/molecule-test-absent` | 1281 | 1281 | 0 | 0 | 5 | 1276 |
| Style/policy | `ansibleguard/unnamed-play` | 1221 | 1221 | 0 | 0 | 5 | 1216 |
| Style/policy | `ansibleguard/unnamed-task` | 7328 | 7328 | 0 | 0 | 4 | 7324 |
| Style/policy | `ansibleguard/variable-naming-convention` | 18645 | 18645 | 0 | 0 | 4 | 18641 |
| Maintainability/complexity | `ansibleguard/complex-expression` | 7442 | 7442 | 0 | 0 | 5 | 7437 |
| Maintainability/complexity | `ansibleguard/complex-playbook` | 1836 | 1836 | 0 | 0 | 5 | 1831 |
| Maintainability/complexity | `ansibleguard/deprecated-modules` | 291 | 291 | 0 | 0 | 5 | 286 |
| Maintainability/complexity | `ansibleguard/excessive-nesting` | 8 | 8 | 0 | 0 | 2 | 6 |
| Maintainability/complexity | `ansibleguard/high-coupling` | 371 | 371 | 0 | 0 | 5 | 366 |
| Maintainability/complexity | `ansibleguard/incomplete-task` | 27 | 27 | 0 | 0 | 4 | 23 |
| Maintainability/complexity | `ansibleguard/large-play` | 1150 | 1150 | 0 | 0 | 4 | 1146 |
| Maintainability/complexity | `ansibleguard/large-playbook` | 2304 | 2304 | 0 | 0 | 4 | 2300 |
| Maintainability/complexity | `ansibleguard/large-task` | 8322 | 8322 | 0 | 0 | 4 | 8318 |
| Maintainability/complexity | `ansibleguard/shell-instead-of-module` | 560 | 560 | 0 | 0 | 4 | 556 |
| Maintainability/complexity | `ansibleguard/undocumented-complex-task` | 793 | 793 | 0 | 0 | 4 | 789 |
| Maintainability/complexity | `ansibleguard/unused-handler` | 25 | 25 | 0 | 0 | 4 | 21 |
| Structure/reuse | `ansibleguard/duplicated-code` | 340 | 340 | 0 | 0 | 9 | 331 |
| Structure/reuse | `ansibleguard/insufficient-modularization` | 60 | 60 | 0 | 0 | 9 | 51 |
| Structure/reuse | `ansibleguard/missing-abstraction` | 1198 | 1198 | 0 | 0 | 9 | 1189 |
| Structure/reuse | `ansibleguard/role-readme-absent` | 2220 | 2220 | 0 | 0 | 8 | 2212 |
| Structure/reuse | `ansibleguard/unexpected-task-location` | 1 | 1 | 0 | 0 | 0 | 1 |
| Structure/reuse | `ansibleguard/unnecessary-abstraction` | 389 | 389 | 0 | 0 | 8 | 381 |
| Structure/reuse | `ansibleguard/unstructured-module` | 30 | 30 | 0 | 0 | 7 | 23 |
| Review/history | `ansibleguard/commit-message-format` | 98 | 98 | 88 | 0 | 25 | 73 |
| Review/history | `ansibleguard/missing-bug-reference` | 19 | 19 | 15 | 0 | 17 | 2 |
| Review/history | `ansibleguard/missing-release-note` | 133 | 9 | 124 | 124 | 4 | 5 |
| Review/history | `ansibleguard/missing-test-update` | 47 | 9 | 38 | 38 | 4 | 5 |
| Review/history | `ansibleguard/untested-override-change` | 38 | 4 | 34 | 34 | 0 | 4 |

Repository-level family/rule counts, including each selected and excluded calibration repository, are in `samples/agreement-pilot/pilot-selection-audit.csv`. The full nested counts also appear in the pilot manifest.

## Family and reviewer workload summary

| Family | Calibration candidates with usable context | Selected | Distinct repositories selected |
|---|---:|---:|---:|
| Objective correctness | 9026 | 50 | 50 |
| Variable/reference reasoning | 39403 | 50 | 50 |
| Security | 6726 | 50 | 50 |
| Style/policy | 106507 | 50 | 50 |
| Maintainability/complexity | 23129 | 50 | 50 |
| Structure/reuse | 4238 | 50 | 50 |
| Review/history | 139 | 50 | 50 |

Review/history source candidates: 335; context-eligible: 139; actual first parent missing: 299; parent required but missing: 196. Exact commit-message evidence keeps message-only cases eligible without a parent.

## Other panels and heldout status

- Representative precision core: not generated; it must wait for pilot agreement and codebook freeze.
- Rule/concept/security top-ups and rare-rule performance census: not generated.
- Source-first recall and threshold calibration panels: not generated.
- Heldout samples/results: not generated; heldout contexts opened = 0.
- The selected 350 agreement-pilot items are permanently excluded from performance scoring.
