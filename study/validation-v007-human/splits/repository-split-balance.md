# Repository split balance report

Seed: `v007-human-repo-split-20261005`. Repository-level split only; aggregate counts were used for the prescribed balance features. No source-context bundles, human labels, or held-out review samples were opened.

Calibration: 144 repositories. Held-out: 62 repositories. Total: 206.

## Distribution summary

| Split | Repositories | Mean selected LOC | Median selected LOC | Mean source density / 1,000 LOC | Median source density / 1,000 LOC |
|---|---:|---:|---:|---:|---:|
| calibration | 144 | 6567.48 | 3685.5 | 192.9119 | 183.4552 |
| heldout | 62 | 6321.19 | 3227.0 | 199.7916 | 184.5662 |

## Top-15 rule presence balance

| Rule | Present in calibration | Present in held-out | Calibration prevalence | Held-out prevalence | Difference (pp) | Flag >10 pp |
|---|---:|---:|---:|---:|---:|---|
| `ansibleguard/complex-expression` | 115 | 50 | 79.8611% | 80.6452% | 0.7841 | no |
| `ansibleguard/complex-playbook` | 123 | 53 | 85.4167% | 85.4839% | 0.0672 | no |
| `ansibleguard/credentials-leaking-in-log` | 114 | 48 | 79.1667% | 77.4194% | -1.7473 | no |
| `ansibleguard/large-playbook` | 127 | 56 | 88.1944% | 90.3226% | 2.1282 | no |
| `ansibleguard/large-task` | 130 | 54 | 90.2778% | 87.0968% | -3.181 | no |
| `ansibleguard/long-statement` | 62 | 27 | 43.0556% | 43.5484% | 0.4928 | no |
| `ansibleguard/long-task-name` | 95 | 39 | 65.9722% | 62.9032% | -3.069 | no |
| `ansibleguard/loop-legacy-syntax` | 100 | 41 | 69.4444% | 66.129% | -3.3154 | no |
| `ansibleguard/missing-tags` | 134 | 58 | 93.0556% | 93.5484% | 0.4928 | no |
| `ansibleguard/role-readme-absent` | 77 | 33 | 53.4722% | 53.2258% | -0.2464 | no |
| `ansibleguard/silent-error-suppression` | 89 | 38 | 61.8056% | 61.2903% | -0.5153 | no |
| `ansibleguard/unguarded-variable` | 128 | 58 | 88.8889% | 93.5484% | 4.6595 | no |
| `ansibleguard/unnamed-task` | 78 | 35 | 54.1667% | 56.4516% | 2.2849 | no |
| `ansibleguard/unnecessary-set-fact` | 90 | 39 | 62.5% | 62.9032% | 0.4032 | no |
| `ansibleguard/variable-naming-convention` | 108 | 46 | 75.0% | 74.1935% | -0.8065 | no |

Rules flagged for manual inspection: 0. Flags are diagnostic only; repositories were not manually reassigned.

Size and density quartiles use deterministic rank bins on `log1p(value)`, with equal feature values broken by the frozen SHA256 repository rank. Rule-presence tokens are exactly the 15 most prevalent static-source rules by occurrence count.
