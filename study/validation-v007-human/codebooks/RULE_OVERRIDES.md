# Rule-to-family semantic overrides

The authoritative row-by-row assignment is `mappings/rule-family-map.csv`; this note explains mappings that intentionally differ from an automatic category/taxonomy assignment. The rule catalog remains the source for rule descriptions and metadata. These are review-family decisions, not detector changes.

| Rule | Assigned family | Why it is an exception |
|---|---|---|
| `ansibleguard/unguarded-variable` | Variable/reference reasoning | Its interpretation depends on visible definitions, guards, role/caller contracts, and runtime inputs; the three concepts must remain distinguishable and uncertainty is expected. |
| `ansibleguard/role-readme-absent` | Structure/reuse | The supplied validation plan explicitly groups role README absence with structural review. Absence is not a correctness failure. |
| `ansibleguard/unnecessary-set-fact` | Variable/reference reasoning | The key decision is whether the fact is truly unused in scope, not whether `set_fact` is generally stylistically desirable. |
| `ansibleguard/unused-registered-variable` | Variable/reference reasoning | Requires reference/scope reasoning; dynamic uses may make a static absence uncertain. |
| `ansibleguard/variable-use-before-definition` | Variable/reference reasoning | Requires ordering, scope, and external/runtime-definition analysis. |
| `ansibleguard/unscoped-shell-variable` | Variable/reference reasoning | Requires shell expansion and Ansible task-environment reasoning. |
| `ansibleguard/role-variable-precedence-collision` | Variable/reference reasoning | Requires the Ansible role-variable precedence model. |
| `ansibleguard/overriding-facts` | Variable/reference reasoning | Requires comparing effective values and execution order. |
| `ansibleguard/redundant-default-value` | Variable/reference reasoning | Requires comparing assignments with role defaults and the effective input contract. |
| `ansibleguard/missing-bool-filters` | Variable/reference reasoning | Requires expression/value-type reasoning, not only style judgment. |
| `ansibleguard/shell-environment-export` | Variable/reference reasoning | The reported condition concerns environment-variable scope/propagation. |
| `ansibleguard/missing-abstraction` | Structure/reuse | The substantive judgment is whether task decomposition or reuse is appropriate, not whether a size limit was exceeded. |
| `ansibleguard/unnecessary-abstraction` | Structure/reuse | A one-task block is not automatically harmful; judge its interface/caller role. |
| `ansibleguard/duplicated-code` | Structure/reuse | Review semantic equivalence and reuse value; textual similarity is insufficient. |
| `ansibleguard/insufficient-modularization` | Structure/reuse | The decision concerns organization and useful module boundaries. |
| `ansibleguard/unsafe-file-write` | Security | The plan names unsafe writes as a security-review example; inspect actual write safeguards and destination context. |
| `ansibleguard/loop-legacy-syntax` | Objective correctness | Evaluate actual compatibility/deprecation for the supported Ansible context. |
| `ansibleguard/redirected-module` | Objective correctness | Verify module identity and redirect target in the frozen version/context. |
| `ansibleguard/non-idempotent-command` | Objective correctness | Judge repeat-execution behavior and the actual idempotency guard. |
| `ansibleguard/read-only-command-change` | Objective correctness | Judge whether the specific command is read-only and whether the task reports a false change. |
| `ansibleguard/unpinned-ansible-dependency` | Objective correctness | Verify whether the declared dependency is actually unconstrained; report reproducibility impact separately. |
| `ansibleguard/molecule-test-absent` | Style/policy | Testing-practice presence is not a universal defect; repository role/testing context determines actionability. |
| `ansibleguard/galaxy-meta-incomplete` | Style/policy | Galaxy publication metadata is optional unless publication is in scope. |
| `ansibleguard/deprecated-modules` | Maintainability/complexity | Keep the rule in its catalog maintenance family, but apply its specific version/deprecation and migration-context test. |
| `ansibleguard/vault-inline-overload` | Security | Review the encrypted-secret handling risk while separating any organization-specific volume policy from actual exposure. |

All five `review-history` panel rules map to `Review/history` regardless of their catalog taxonomy because their evidence unit is a commit message or Git change range, not an isolated static YAML finding.
