# Phase 2 comparison report — Reviewer A vs. Reviewer C (stratified sample)

Denominator for every percentage below: **N = 400** (the full impact-weighted stratified sample, identical row set independently labeled by both reviewers; verified 1:1 ID match before comparison).

Reviewer identity is deliberately generic, consistent with Phase 1 — Reviewer A is the same reviewer as Phase 1's Reviewer A; Reviewer C is a new, third independent pass (not Phase 1's Reviewer B). Which underlying model produced which pass is not recorded here by design.

**This uses the same mechanical `classify()` rule as Phase 1** (`build_comparison_phase2.py`), so the two phases' numbers are directly comparable. Note this differs from the self-reported "both match" figure in `stratified-sample/CHATGPT_REVIEW_REPORT.md`, which counts a looser semantic+actionability match without requiring `reason_code` agreement — that report's 201/400 (50.3%) and this report's Agreement count below are not the same measurement and should not be conflated.

## Headline counts

| Status | Count | % of N |
| --- | ---: | ---: |
| Agreement | 151 | 37.8% |
| Partial agreement | 84 | 21.0% |
| Disagreement | 39 | 9.8% |
| Insufficient information | 126 | 31.5% |
| **Total** | **400** | **100.0%** |

**How `agreement_status` was assigned** (mechanical rule, identical to Phase 1 — see `build_comparison_phase2.py::classify()`):
- **Insufficient information**: at least one reviewer labeled the item `uncertain`/`unreviewable`, and the other did not make the same call for the same reason.
- **Disagreement**: both reviewers gave a decisive label (`positive`/`negative`), but a different one.
- **Agreement**: identical `semantic_label`, `actionability_label`, and `reason_code`.
- **Partial agreement**: identical `semantic_label`, but `actionability_label` and/or `reason_code` differ.

## Breakdown by review family

| Family | Agreement | Partial agreement | Disagreement | Insufficient info | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Style/policy | 77 | 29 | 14 | 13 | 133 |
| Maintainability/complexity | 17 | 15 | 16 | 44 | 92 |
| Variable/reference reasoning | 7 | 32 | 0 | 11 | 50 |
| Objective correctness | 18 | 3 | 3 | 24 | 48 |
| Security | 22 | 5 | 6 | 5 | 38 |
| Structure/reuse | 2 | 0 | 0 | 29 | 31 |
| Review/history | 8 | 0 | 0 | 0 | 8 |

## Breakdown by rule (top 15 by total occurrences in sample)

| Rule | Agreement | Partial agreement | Disagreement | Insufficient info | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| ansibleguard/large-task | 5 | 8 | 4 | 5 | 22 |
| ansibleguard/missing-tags | 22 | 0 | 0 | 0 | 22 |
| ansibleguard/unnamed-task | 18 | 4 | 0 | 0 | 22 |
| ansibleguard/variable-naming-convention | 2 | 9 | 11 | 0 | 22 |
| ansibleguard/unguarded-variable | 4 | 15 | 0 | 3 | 22 |
| ansibleguard/long-task-name | 16 | 4 | 0 | 0 | 20 |
| ansibleguard/credentials-leaking-in-log | 13 | 3 | 1 | 1 | 18 |
| ansibleguard/long-statement | 6 | 9 | 3 | 0 | 18 |
| ansibleguard/complex-expression | 5 | 6 | 5 | 1 | 17 |
| ansibleguard/loop-legacy-syntax | 0 | 1 | 0 | 13 | 14 |
| ansibleguard/large-playbook | 0 | 0 | 0 | 12 | 12 |
| ansibleguard/role-readme-absent | 0 | 0 | 0 | 11 | 11 |
| ansibleguard/complex-playbook | 0 | 0 | 0 | 10 | 10 |
| ansibleguard/large-play | 0 | 0 | 0 | 10 | 10 |
| ansibleguard/unnamed-play | 10 | 0 | 0 | 0 | 10 |

## Disagreement/partial-agreement categories

| Category | Count |
| --- | ---: |
| evidence-sufficiency | 126 |
| interpretation | 50 |
| classification | 39 |
| severity/remediation | 29 |
| severity/remediation and interpretation | 5 |

## Representative examples

### Agreement

**V007STRAT-COMPLEX-EXPRESSION-006** (Maintainability/complexity, `ansibleguard/complex-expression`, vndmtrx/k8s-in-a-box:ansible/infra-pki/tasks/101-root-ca.yml:25)
- Reviewer A: `positive` / `actionable` / reason=`complexity-supported`
  - pki_deve_gerar_root_ca ORs four conditions, one of which does certificate-expiry date arithmetic (to_datetime subtraction, .days, comparison against a configured threshold) -- genuinely intricate decision logic, not an a
- Reviewer C: `positive` / `actionable` / reason=`complexity-supported`
  - Root CA generation combines missing-file checks, expiration status, date parsing, and a validity threshold in one condition.

**V007STRAT-COMPLEX-EXPRESSION-007** (Maintainability/complexity, `ansibleguard/complex-expression`, ansible-collections/azure:roles/azure_arc/tasks/linux_install.yml:78)
- Reviewer A: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - Expression is a combine() merging a default-filtered dict with a literal dict of ~6 keys, each independently defaulted; it is a flat enumeration of environment keys, not nested branching logic.
- Reviewer C: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - The environment expression merges a proxy mapping with six straightforward metadata fields; this is declarative mapping.

**V007STRAT-COMPLEX-EXPRESSION-011** (Maintainability/complexity, `ansibleguard/complex-expression`, TylerHendrickson/home-ops:ansible/playbooks/cluster-installation.yaml:37)
- Reviewer A: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - Anchored when-list item ORs two length>0 checks on alternative manifest sources, combined via implicit AND with a sibling condition; a normal two-source existence guard.
- Reviewer C: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - The condition gates on a node flag or either of two list lengths; the branches are easy to follow.

### Partial agreement

**V007STRAT-COMPLEX-EXPRESSION-001** (Maintainability/complexity, `ansibleguard/complex-expression`, packit/deployment:playbooks/zuul-deploy.yml:24)
- Reviewer A: `negative` / `not-applicable` / reason=`threshold-only`
  - Anchored condition is a single AND of two equality checks (distribution == CentOS and major_version == '7'); easy to read and reason about despite crossing the detector's numeric threshold.
- Reviewer C: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - The when expression is one conjunction of two direct distribution-fact comparisons; it is manageable.
- Disagreement category: interpretation (reason_code: threshold-only vs cohesive-or-manageable)

**V007STRAT-COMPLEX-EXPRESSION-002** (Maintainability/complexity, `ansibleguard/complex-expression`, ansible-lockdown/RHEL7-STIG:defaults/main.yml:555)
- Reviewer A: `positive` / `advisory` / reason=`complexity-supported`
  - rhel7stig_logon_banner combines a ternary with a regex_replace using a negative lookbehind/lookahead ((?<!\n)...(?!(\n|$))); the regex semantics alone require careful reasoning, a genuine readability burden.
- Reviewer C: `positive` / `actionable` / reason=`complexity-supported`
  - The banner expression combines a ternary with a regex transformation across nested Jinja syntax; an intermediate value would clarify it.
- Disagreement category: severity/remediation (actionability: advisory vs actionable)

**V007STRAT-COMPLEX-EXPRESSION-008** (Maintainability/complexity, `ansibleguard/complex-expression`, ansible-lockdown/RHEL8-CIS:tasks/LE_audit_setup.yml:11)
- Reviewer A: `negative` / `not-applicable` / reason=`threshold-only`
  - Condition is a simple OR of two equality checks on ansible_facts['machine']; straightforward to read despite the numeric score.
- Reviewer C: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - The ARM64 task checks whether machine equals either of two architecture strings.
- Disagreement category: interpretation (reason_code: threshold-only vs cohesive-or-manageable)

### Disagreement

**V007STRAT-COMPLEX-EXPRESSION-003** (Maintainability/complexity, `ansibleguard/complex-expression`, mfin/homelab:ansible/k3s/inventory/group_vars/all/k3s.yaml:6)
- Reviewer A: `positive` / `advisory` / reason=`complexity-supported`
  - master_ip resolves via a triple level of indirection: groups['master'][0] is used to index hostvars, whose result is itself indexed and defaulted -- nested indirection that is a real source of confusion, independent of i
- Reviewer C: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - master_ip is a single hostvars lookup with an inventory-hostname fallback.
- Disagreement category: classification (different semantic_label: positive vs negative)

**V007STRAT-COMPLEX-EXPRESSION-004** (Maintainability/complexity, `ansibleguard/complex-expression`, stackhpc/stackhpc-release-train:ansible/dev-pulp-container-tag-query-kayobe.yml:18)
- Reviewer A: `positive` / `advisory` / reason=`complexity-supported`
  - Expression chains three filters (dict2items | selectattr | items2dict) to rebuild a filtered dict -- a genuine small functional pipeline that takes real effort to trace.
- Reviewer C: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - The tag selection is a short three-filter pipeline followed by items2dict.
- Disagreement category: classification (different semantic_label: positive vs negative)

**V007STRAT-COMPLEX-EXPRESSION-005** (Maintainability/complexity, `ansibleguard/complex-expression`, ansible-collections/ibm_zos_core:roles/gather_diagnostics/defaults/main.yml:34)
- Reviewer A: `positive` / `advisory` / reason=`complexity-supported`
  - Ternary condition ORs two separate lookup('env', ...) | default('') != '' checks before selecting a path; the duplicated lookup/default/compare pattern and ternary nesting is a real (if modest) readability cost.
- Reviewer C: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - The output-directory expression selects between two paths using two environment checks; its branches are clear.
- Disagreement category: classification (different semantic_label: positive vs negative)

### Insufficient information

**V007STRAT-COMPLEX-EXPRESSION-013** (Maintainability/complexity, `ansibleguard/complex-expression`, hyphacoop/cosmos-ansible:roles/configure-prometheus/tasks/cleanup.yml:1)
- Reviewer A: `unreviewable` / `not-applicable` / reason=`other`
  - The anchor (line 1) is a plain '# CLEANUP STALE TARGETS' comment with no Jinja or conditional expression on or near it in the supplied window; the condition the detector scored (complexity 9) cannot be located in the fro
- Reviewer C: `negative` / `not-applicable` / reason=`wrong-analysis-unit`
  - Line 1 is a comment; the two later basename-membership conditions are short, parallel cleanup checks.
- Disagreement category: evidence-sufficiency (one reviewer found the context sufficient to decide, the other did not)

**V007STRAT-COMPLEX-PLAYBOOK-001** (Maintainability/complexity, `ansibleguard/complex-playbook`, roots/trellis:dev.yml:1)
- Reviewer A: `uncertain` / `uncertain` / reason=`insufficient-source-context`
  - Only the first ~15 lines of dev.yml in roots/trellis are visible (roles/vars/pre_tasks header). Playbook complexity is measured across the whole file's branching/task structure, which extends beyond the shown window, so 
- Reviewer C: `negative` / `not-applicable` / reason=`cohesive-or-manageable`
  - One named WordPress development play delegates each service to a focused role.
- Disagreement category: evidence-sufficiency (one reviewer found the context sufficient to decide, the other did not)

**V007STRAT-COMPLEX-PLAYBOOK-002** (Maintainability/complexity, `ansibleguard/complex-playbook`, IDR/deployment:ansible/decommission/archive-logs.yml:1)
- Reviewer A: `uncertain` / `uncertain` / reason=`insufficient-source-context`
  - Only the first ~15 lines of ansible/decommission/archive-logs.yml in IDR/deployment are visible (roles/vars/pre_tasks header). Playbook complexity is measured across the whole file's branching/task structure, which exten
- Reviewer C: `positive` / `actionable` / reason=`repetition-supported`
  - Three host-specific plays repeat the archive, optional fetch, and archive-summary sequence.
- Disagreement category: evidence-sufficiency (one reviewer found the context sufficient to decide, the other did not)

## Issues requiring your decision

**249 of 400 items (62.2%) are not a full agreement** and are marked `validation_status = Initially unreviewed` with `final_validated_label` left blank in `consolidated-comparison-phase2.csv`. Filter that file on `agreement_status != Agreement` to get the full, traceable list (all 400 original rows are preserved — none were removed or merged).

- Disagreement: 39
- Partial agreement: 84
- Insufficient information: 126

## Note on deduplication

No deduplication or merging was performed. Both source files have exactly 400 rows, 1:1 matched by `sample_id` (verified by set equality before any comparison), and all 400 rows are present in the output unchanged in identity.
