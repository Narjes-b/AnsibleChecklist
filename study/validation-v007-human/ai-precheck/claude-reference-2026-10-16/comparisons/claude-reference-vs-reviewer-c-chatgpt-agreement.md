# Label comparison: claude-reference vs reviewer-c-chatgpt

Paired items: 350. Neither file is ground truth.

| Group | n | Raw agreement | Cohen κ | Gwet AC1 | Decided n | Decided agreement | Decided κ | claude-reference uncertain+unrev. | reviewer-c-chatgpt uncertain+unrev. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ALL | 350 | 0.683 | 0.516 | 0.595 | 232 | 0.858 | 0.715 | 75 | 84 |
| family: Objective correctness | 50 | 0.560 | 0.331 | 0.440 | 29 | 0.793 | 0.574 | 10 | 16 |
| family: Variable/reference reasoning | 50 | 0.680 | 0.482 | 0.599 | 35 | 0.886 | 0.750 | 12 | 6 |
| family: Security | 50 | 0.740 | 0.472 | 0.689 | 43 | 0.837 | 0.587 | 3 | 5 |
| family: Style/policy | 50 | 0.760 | 0.588 | 0.702 | 34 | 0.971 | 0.927 | 11 | 10 |
| family: Maintainability/complexity | 50 | 0.620 | 0.399 | 0.524 | 36 | 0.750 | 0.409 | 4 | 14 |
| family: Structure/reuse | 50 | 0.760 | 0.571 | 0.706 | 43 | 0.860 | 0.709 | 7 | 2 |
| family: Review/history | 50 | 0.660 | 0.417 | 0.579 | 12 | 1.000 | 1.000 | 28 | 31 |

## Confusion (claude-reference rows, reviewer-c-chatgpt columns)

| | positive | negative | uncertain | unreviewable |
|---|---:|---:|---:|---:|
| positive | 103 | 18 | 33 | 1 |
| negative | 15 | 96 | 8 | 1 |
| uncertain | 9 | 24 | 39 | 1 |
| unreviewable | 0 | 1 | 0 | 1 |

## Per rule (agreement on the 4-class label)

| Rule | n | Agree | Raw |
|---|---:|---:|---:|
| deprecated-modules | 5 | 0 | 0.00 |
| loop-legacy-syntax | 8 | 0 | 0.00 |
| missing-handler | 2 | 0 | 0.00 |
| missing-tags | 5 | 0 | 0.00 |
| unpinned-ansible-dependency | 7 | 1 | 0.14 |
| high-coupling | 5 | 1 | 0.20 |
| long-task-name | 5 | 1 | 0.20 |
| invalid-task-attribute-type | 4 | 1 | 0.25 |
| unstructured-module | 7 | 2 | 0.29 |
| missing-bool-filters | 5 | 2 | 0.40 |
| overriding-facts | 5 | 2 | 0.40 |
| become-scope-too-broad | 8 | 4 | 0.50 |
| excessive-nesting | 2 | 1 | 0.50 |
| incomplete-task | 4 | 2 | 0.50 |
| undocumented-complex-task | 4 | 2 | 0.50 |
| variable-naming-convention | 4 | 2 | 0.50 |
| unguarded-variable | 7 | 4 | 0.57 |
| complex-playbook | 5 | 3 | 0.60 |
| role-variable-precedence-collision | 5 | 3 | 0.60 |
| credentials-leaking-in-log | 8 | 5 | 0.62 |
| default-credentials | 8 | 5 | 0.62 |
| unnecessary-abstraction | 8 | 5 | 0.62 |
| commit-message-format | 25 | 16 | 0.64 |
| missing-bug-reference | 17 | 11 | 0.65 |
| redundant-default-value | 3 | 2 | 0.67 |
| unsafe-file-write | 3 | 2 | 0.67 |
| redirected-module | 7 | 5 | 0.71 |
| large-playbook | 4 | 3 | 0.75 |
| missing-release-note | 4 | 3 | 0.75 |
| missing-test-update | 4 | 3 | 0.75 |
| shell-instead-of-module | 4 | 3 | 0.75 |
| duplicated-code | 9 | 7 | 0.78 |
| complex-expression | 5 | 4 | 0.80 |
| inconsistent-naming-convention | 5 | 4 | 0.80 |
| unscoped-shell-variable | 6 | 5 | 0.83 |
| unused-registered-variable | 6 | 5 | 0.83 |
| variable-use-before-definition | 6 | 5 | 0.83 |
| plaintext-sensitive-variable | 7 | 6 | 0.86 |
| unnecessary-set-fact | 7 | 6 | 0.86 |
| missing-validate-certs | 8 | 7 | 0.88 |
| non-idempotent-command | 8 | 7 | 0.88 |
| role-readme-absent | 8 | 7 | 0.88 |
| missing-abstraction | 9 | 8 | 0.89 |
| duplicate-task-names | 5 | 5 | 1.00 |
| galaxy-meta-incomplete | 5 | 5 | 1.00 |
| insecure-permissions | 8 | 8 | 1.00 |
| insufficient-modularization | 9 | 9 | 1.00 |
| large-play | 4 | 4 | 1.00 |
| large-task | 4 | 4 | 1.00 |
| long-statement | 5 | 5 | 1.00 |
| missing-file-extension | 2 | 2 | 1.00 |
| molecule-test-absent | 5 | 5 | 1.00 |
| read-only-command-change | 7 | 7 | 1.00 |
| silent-error-suppression | 7 | 7 | 1.00 |
| unnamed-play | 5 | 5 | 1.00 |
| unnamed-task | 4 | 4 | 1.00 |
| unused-handler | 4 | 4 | 1.00 |
