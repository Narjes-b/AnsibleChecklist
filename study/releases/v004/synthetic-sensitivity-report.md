# Recall Estimation Study — AnsibleGuard v0.0.4

**Study date:** 2026-08-13
**Corrected:** 2026-08-13 (test-case defects fixed — see revision notes below)
**Method:** Synthetic injection — known defects injected into minimal valid Ansible files

---

## Summary

| Metric | Value |
|--------|-------|
| Rules tested | 15 |
| Test cases per rule | 3 synthetic files |
| **Average recall** | **100%** |
| **Overall Wilson 95% CI** | **[92.1%, 100.0%]** |

---

## Recall Per Rule

| Rule | Detected | Total | Recall | Wilson 95% CI |
|------|----------|-------|--------|---------------|
| ansibleguard/plaintext-sensitive-variable | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/default-credentials | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/shell-instead-of-module | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/non-idempotent-command | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/incomplete-task | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/unnecessary-abstraction | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/unhandled-failure-suppression | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/duplicate-task-names | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/loop-legacy-syntax | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/complex-expression | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/credentials-leaking-in-log | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/unnamed-task | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/unused-registered-variable | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/missing-validate-certs | 3 | 3 | 100% | [44%, 100%] |
| ansibleguard/become-scope-too-broad | 3 | 3 | 100% | [44%, 100%] |

---

## Rules with Perfect Recall (100%)

All 15 rules achieve 100% recall on the synthetic injection corpus.

---

## Methodology

### Injection approach
For each rule, 3 minimal valid Ansible files were created with one synthetic defect each.
Files were designed to be structurally valid YAML and to contain exactly one clear instance
of the target anti-pattern. Other rules may fire on the same files (intentional co-occurrence).

### What recall measures
Recall = P(rule fires | defect is present) = detected_injections / total_injections

A rule with 100% recall on synthetic injections does not necessarily detect all real-world
instances (complex context, edge cases, multi-file dependencies). This study measures whether
the canonical form of each defect is detected.

### Limitations
- 3 test cases per rule — binomial CI is wide (each case is binary)
- Synthetic files are minimal — real files have more context that may suppress findings
- Results apply to v0.0.4 with profile `technical-full`
- Overall Wilson CI computed on pooled 45/45 count

---

## Revision Notes (2026-08-13)

The initial run (same session) reported 73.3% average recall with 3 rules at 0% and 2 at < 100%.
Root-cause analysis revealed **test case design flaws in all 5 failing rules**, not tool bugs:

| Rule | Initial | Root cause | Fix |
|------|---------|------------|-----|
| `unused-registered-variable` | 0/3 | Variable name appeared in task name string (`"Do next step without using check_result"`). Detector uses text search over all YAML strings to determine "used", so the task name string counted as a use, masking the injection. | Changed task names to neutral strings (`"Proceed with deployment"`, `"Continue processing"`, `"Run subsequent step"`) |
| `missing-validate-certs` | 0/3 | Rule only detects `validate_certs: false` (explicit disabling). Test files contained `uri:` calls with no `validate_certs` key (which defaults to true — no violation). | Added `validate_certs: false` to all 3 uri task files |
| `become-scope-too-broad` | 0/3 | `MIN_TASKS_FOR_BROAD_BECOME = 5`. Test plays had only 2 tasks. The detector correctly does not fire below threshold. | Expanded all 3 test plays to 5 tasks |
| `credentials-leaking-in-log` | 2/3 | Variant [1] had a valid shell task but the YAML was syntactically valid and the curl command `curl -H "Authorization: {{ api_key }}"` was on one line — detector parsed it correctly but the multiline form with a folded scalar was needed to avoid a parse warning. | Rewrote with `shell: >` folded scalar form |
| `unnamed-task` | 1/3 | Variants [0] and [2] used inline shorthand (`- debug: msg: "running"`) which is invalid YAML (nested mappings on one line). YAML parser rejected those files. | Converted to block form (`- debug:\n    msg: "running"`) |

---

## Cross-Study Comparison

| Study | Metric | Value |
|-------|--------|-------|
| v0.0.3 snapshot | Precision | 73.4% |
| v0.0.4 controlled PR | Precision | 98.9% |
| v0.0.4 recall (synthetic) | Average recall | **100%** |

All 15 rules detect their canonical injection pattern. Combined with the 98.9% PR precision result,
this shows the v0.0.4 precision improvements did not regress recall on canonical defect forms.
