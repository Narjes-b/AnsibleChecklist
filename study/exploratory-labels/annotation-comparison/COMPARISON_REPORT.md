# Phase 1 comparison report — Reviewer A vs. Reviewer B

Denominator for every percentage below: **N = 350** (the full agreement-pilot sample, identical row set independently labeled by both reviewers; verified 1:1 ID match before comparison).

Reviewer identity is deliberately generic — both passes are AI-generated, independent, and blind to each other, but which underlying model produced which pass is not recorded here by design.

## Headline counts

| Status | Count | % of N |
| --- | ---: | ---: |
| Agreement | 143 | 40.9% |
| Partial agreement | 88 | 25.1% |
| Disagreement | 42 | 12.0% |
| Insufficient information | 77 | 22.0% |
| **Total** | **350** | **100.0%** |

**How `agreement_status` was assigned** (mechanical rule, not a judgment call — see `build_comparison.py::classify()` for the exact logic):
- **Insufficient information**: at least one reviewer labeled the item `uncertain`/`unreviewable`. If both did, and for the same reason, that is scored as `Agreement` on the uncertainty call itself; any other mix (one reviewer decisive, or both uncertain for different reasons) is `Insufficient information`, since the two records cannot be meaningfully compared as a semantic agreement or disagreement.
- **Disagreement**: both reviewers gave a decisive label (`positive`/`negative`), but a different one.
- **Agreement**: identical `semantic_label`, `actionability_label`, and `reason_code`.
- **Partial agreement**: identical `semantic_label`, but `actionability_label` and/or `reason_code` differ — i.e. the two reviewers agree on *whether* the condition is present, but not on severity, remediation, or the specific reasoning.

## Breakdown by review family

| Family | Agreement | Partial agreement | Disagreement | Insufficient info | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Maintainability/complexity | 21 | 15 | 6 | 8 | 50 |
| Objective correctness | 18 | 7 | 6 | 19 | 50 |
| Review/history | 15 | 0 | 8 | 27 | 50 |
| Security | 24 | 15 | 9 | 2 | 50 |
| Structure/reuse | 22 | 15 | 10 | 3 | 50 |
| Style/policy | 23 | 18 | 1 | 8 | 50 |
| Variable/reference reasoning | 20 | 18 | 2 | 10 | 50 |

## Disagreement/partial-agreement categories

(counts rows whose `disagreement_category` starts with this label; a row can only have one category)

| Category | Count |
| --- | ---: |
| evidence-sufficiency | 77 |
| interpretation | 63 |
| classification | 42 |
| severity/remediation | 24 |
| severity/remediation and interpretation | 1 |

## Representative examples

### Agreement

**V007PILOT-MAINTAINABILITY_COMPLEXITY-001** (Maintainability/complexity, `ansibleguard/complex-expression`, redhat-cop/infra.aap_configuration:roles/hub_publish/tasks/evaluate_tarball_item.yml:6)
- Reviewer A: `positive` / `advisory` / reason=`complexity-supported`
  - Line 6 chains basename, split, a slice, join, and two sequential splitext|first calls in a single Jinja expression to derive a semantic version from a filename; genuinely hard to parse at a glance despite working correct
- Reviewer B: `positive` / `advisory` / reason=`complexity-supported`
  - The version expression chains basename, split, slice, join, and two splitext/first operations in one Jinja line. A named intermediate or helper would make the filename-parsing steps easier to understand and test.

**V007PILOT-MAINTAINABILITY_COMPLEXITY-002** (Maintainability/complexity, `ansibleguard/complex-playbook`, pjbriggs/ansible-palfinder-galaxy:centaurus.yml:1)
- Reviewer A: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - Single host-specific deployment playbook: vars, vars_files, and roles are flatly listed with explanatory comments and only a few simple when-guards; large but not structurally complex.
- Reviewer B: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - This is one deployment play: most of the file is declarative host configuration, vars files, and a short ordered role list with a few optional services. That is a cohesive, manageable playbook in the supplied context.

**V007PILOT-MAINTAINABILITY_COMPLEXITY-005** (Maintainability/complexity, `ansibleguard/high-coupling`, AtlasOfLivingAustralia/ala-install:ansible/profiles.yml:1)
- Reviewer A: `uncertain` / `uncertain` / reason=`architecture-context-needed`
  - Play only lists roles with simple when-guards and one inline param passed from inventory vars; without the roles' internal variable contracts we cannot confirm genuine tight coupling versus ordinary composition.
- Reviewer B: `uncertain` / `uncertain` / reason=`architecture-context-needed`
  - The play lists many roles and a comment notes one role cannot use the primary-host condition because it creates Mongo roles. This suggests coordination, but the role interfaces and dependency/reference graph needed to ju

### Partial agreement

**V007PILOT-MAINTAINABILITY_COMPLEXITY-004** (Maintainability/complexity, `ansibleguard/excessive-nesting`, IBM/ibm-spectrum-scale-install-infra:roles/auth_upgrade/tasks/auth.yml:194)
- Reviewer A: `positive` / `actionable` / reason=`complexity-supported`
  - Anchor at line 194 sits five block levels deep (outer when -> block -> block -> block -> block), each gated by its own condition; genuinely hard to trace cause-and-effect.
- Reviewer B: `positive` / `advisory` / reason=`complexity-supported`
  - The auth task has several nested blocks and conditions, including a five-level path around LDAP/TLS updates and cleanup. The nesting makes the control flow difficult to scan; extracting the flows into task files would cl
- Disagreement category: severity/remediation (actionability: actionable vs advisory)

**V007PILOT-MAINTAINABILITY_COMPLEXITY-009** (Maintainability/complexity, `ansibleguard/large-task`, spantaleev/matrix-docker-ansible-deploy:roles/custom/matrix_playbook_migration/tasks/validate_config.yml:600)
- Reviewer A: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - Anchored task is an approximately 11-line fail+message block, one of many formulaic deprecation-notice tasks in this file; not structurally large or complex on its own.
- Reviewer B: `negative` / `not-applicable` / reason=`threshold-only`
  - The anchored task is a single fail action with a multi-paragraph migration message and variable lookup. The message is lengthy, but the task has no branching or coupled behavior; the supplied evidence does not show a mai
- Disagreement category: interpretation (reason_code: cohesive-or-manageable vs threshold-only)

**V007PILOT-MAINTAINABILITY_COMPLEXITY-012** (Maintainability/complexity, `ansibleguard/unused-handler`, roots/trellis:xdebug-tunnel.yml:16)
- Reviewer A: `uncertain` / `uncertain` / reason=`insufficient-source-context`
  - Handler is only reachable via notify from the sshd/xdebug/xdebug-tunnel roles' task files, none of which are in the frozen bundle; cannot confirm the absence of a notify reference.
- Reviewer B: `uncertain` / `uncertain` / reason=`dynamic-reference`
  - The play defines a reload php-fpm handler, but the supplied playbook excerpt contains no notify references. The three referenced roles' task trees may notify it, so this partial role graph cannot establish that the handl
- Disagreement category: interpretation (same uncertainty call, different reason_code)

### Disagreement

**V007PILOT-MAINTAINABILITY_COMPLEXITY-011** (Maintainability/complexity, `ansibleguard/undocumented-complex-task`, autobase-tech/autobase:automation/roles/cloud_resources/tasks/aws.yml:473)
- Reviewer A: `positive` / `advisory` / reason=`complexity-supported`
  - Task has 14 module parameters, a loop with loop_control/register/until/retries, and a 3-way nested boolean when-clause, with no comment explaining the condition (unlike the pattern elsewhere in this file).
- Reviewer B: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - This is a declarative AWS target-group module task with an explicit NLB section comment, descriptive name, and individually named settings. The supplied context does not show undocumented control flow or a maintenance bu
- Disagreement category: classification (different semantic_label: positive vs negative)

**V007PILOT-MAINTAINABILITY_COMPLEXITY-016** (Maintainability/complexity, `ansibleguard/excessive-nesting`, axivo/k3s-cluster:roles/cluster/tasks/configuration.yaml:70)
- Reviewer A: `positive` / `actionable` / reason=`complexity-supported`
  - Anchor sits five block levels deep (Hardware Configuration > USB Device Configuration > Device Trim > Device Rule Setup > block), each with its own when-condition.
- Reviewer B: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - The anchored block groups two related device-rule tasks under one validation condition: construct the rule fact and write it. This shallow nesting makes the shared guard explicit rather than obscuring control flow.
- Disagreement category: classification (different semantic_label: positive vs negative)

**V007PILOT-MAINTAINABILITY_COMPLEXITY-017** (Maintainability/complexity, `ansibleguard/high-coupling`, Linuxfabrik/lfops:playbooks/clamav.yml:1)
- Reviewer A: `positive` / `advisory` / reason=`complexity-supported`
  - Playbook explicitly wires one role's variable into another's expected variable name (e.g. repo_baseos__crb_repo_enabled__dependent_var fed from repo_epel__...), visible direct inter-role variable coupling.
- Reviewer B: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - This is a focused ClamAV orchestration play that imports shared start/end logging and composes the repo, SELinux, Python-venv, ClamAV, and fangfrisch roles with explicit conditions and dependent variables. Those dependen
- Disagreement category: classification (different semantic_label: positive vs negative)

### Insufficient information

**V007PILOT-MAINTAINABILITY_COMPLEXITY-003** (Maintainability/complexity, `ansibleguard/deprecated-modules`, redhat-openstack/infrared:plugins/tripleo-overcloud/tasks/upgrade/10/main.yml:174)
- Reviewer A: `positive` / `advisory` / reason=`migration-context`
  - Anchored task (inside the block ending at line 174) uses the legacy bare include: directive, deprecated in favor of include_tasks/import_tasks and removed in modern Ansible.
- Reviewer B: `uncertain` / `uncertain` / reason=`migration-context`
  - The task uses the legacy generic include form for endping.yaml. Its deprecation and replacement implications depend on the Ansible versions this plugin supports and whether the include's dynamic behavior is relied on; ne
- Disagreement category: evidence-sufficiency (one reviewer found the context sufficient to decide, the other did not)

**V007PILOT-MAINTAINABILITY_COMPLEXITY-010** (Maintainability/complexity, `ansibleguard/shell-instead-of-module`, ric03uec/clawrium:src/clawrium/platform/registry/openclaw/playbooks/install.yaml:351)
- Reviewer A: `positive` / `actionable` / reason=`migration-context`
  - community.general.npm provides equivalent install-by-name/path semantics for a local npm install; the current command task also hardcodes changed_when: true, losing the idempotency tracking a native module would restore.
- Reviewer B: `uncertain` / `uncertain` / reason=`migration-context`
  - The command installs one Node package with npm in the agent's home, for use by the pairing script. A community.general.npm module may manage the same package more idempotently, but the collection dependency and exact man
- Disagreement category: evidence-sufficiency (one reviewer found the context sufficient to decide, the other did not)

**V007PILOT-MAINTAINABILITY_COMPLEXITY-015** (Maintainability/complexity, `ansibleguard/deprecated-modules`, RedHatGov/redhatgov.workshops:jboss-aws-setup/roles/aws-teardown/tasks/04_dns.yml:29)
- Reviewer A: `positive` / `advisory` / reason=`migration-context`
  - Anchored task uses the legacy bare include: directive with inline key=value arguments, a deprecated/removed Ansible construct.
- Reviewer B: `uncertain` / `uncertain` / reason=`migration-context`
  - The task uses the legacy generic include form with inline variables. Whether it is deprecated for the project's supported Ansible range, and the safe replacement preserving dynamic behavior, is not shown.
- Disagreement category: evidence-sufficiency (one reviewer found the context sufficient to decide, the other did not)

## Issues requiring your decision

**207 of 350 items (59.1%) are not a full agreement** and are marked `validation_status = Initially unreviewed` with `final_validated_label` left blank in `consolidated-comparison.csv`. Filter that file on `agreement_status != Agreement` to get the full, traceable list (all 350 original rows are preserved — none were removed or merged).

- Disagreement (both reviewers confident, different label): 42  — highest priority, since this is a direct semantic conflict.
- Partial agreement (same label, different severity/reasoning): 88 — lower priority, but still affects actionability/remediation guidance.
- Insufficient information (evidence-sufficiency mismatch): 77 — these may need a richer context bundle before a human can even adjudicate them, not just a decision.

## Note on deduplication

No deduplication or merging was performed. Both source files have exactly 350 rows, 1:1 matched by `sample_id` (verified by set equality before any comparison), and all 350 rows are present in the output unchanged in identity. No rows were judged to refer to "the same underlying problem" as another row — each `sample_id` is already a distinct frozen occurrence from the agreement-pilot protocol's own deterministic sampling, not something this task re-sampled or re-grouped.
