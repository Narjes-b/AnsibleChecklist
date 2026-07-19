# Nova Negative Validation — Simple Results

## 1. What did we check?

Previously, we checked the findings that AnsibleGuard reported.

This time, we checked things that AnsibleGuard did not report.

The question was:

> Did AnsibleGuard miss any problems?

We used the same frozen project:

```text
Project: openstack/openstack-ansible-os_nova
Commit:  e06c7bceef3f7c365828116b7aadea6fc2d3e22b
Files:   28 production Ansible files
```

The project version and file population did not change.

---

## 2. What was saved?

The detailed negative labels are stored in:

```text
study/labels/nova_research_core_negative_labels.csv
```

The CSV uses these labels:

```text
true_negative  = AnsibleGuard was silent and there was no smell
false_negative = AnsibleGuard was silent but a smell existed
uncertain      = we could not make a safe decision
```

It also records coverage:

```text
covered      = the detector understands this layout
coverage_gap = the detector cannot properly evaluate this layout
```

---

## 3. Complex-expression negative check

The 28 files contained:

```text
604 unique Jinja or conditional candidates
38 candidates at or above score 6
17 strongest unreported candidates at score 5
```

We manually reviewed all 17 score-5 boundary candidates.

Result:

```text
17 true negatives
0 observed false negatives in the boundary sample
```

They were not reported because their score is 5 and the frozen threshold is 6.

Important limitation:

> This was a boundary sample, not a manual review of all 604 expressions. It does not prove perfect recall.

---

## 4. Long-statement negative check

We independently counted every non-comment line longer than 120 characters.

```text
Independent result: 39 long code lines and 1 long comment
AnsibleGuard result: 39 long-statement findings
Missed long code lines: 0
```

The comment at `defaults/main.yml:311` was correctly ignored.

Simple meaning:

> For this Nova population, the corrected detector found every line defined by its current rule.

---

## 5. Incomplete-task negative check

The rule looks for:

```text
TODO
FIXME
HACK
XXX
```

We independently searched all 28 files.

```text
Markers found: 0
Markers missed: 0
```

This is a true negative under the current definition.

---

## 6. Empty-abstraction negative check

We checked for empty YAML documents and empty `block`, `rescue`, or `always` sections.

```text
Empty abstractions found: 0
Empty abstractions missed: 0
```

This is a true negative for Nova.

---

## 7. Excessive-nesting negative check

The frozen threshold is nesting deeper than 3.

The independent task walk found:

```text
121 tasks at depth 0
7 tasks at depth 1
Maximum depth: 1
```

Maximum depth 1 is below threshold 3, so no nesting smell was missed.

---

## 8. Missing-abstraction negative check

Three files contain more than ten leaf tasks:

| File | Leaf tasks | Includes |
|---|---:|---:|
| `tasks/drivers/kvm/nova_compute_kvm.yml` | 13 | 5 |
| `tasks/main.yml` | 22 | 16 |
| `tasks/nova_install.yml` | 13 | 3 |

The rule reports a smell only when a large file has no task or role abstraction.

All three files use includes.

```text
True negatives: 3
Observed missed smells: 0
```

---

## 9. Unstructured-module negative check

Manual inspection shows that Nova has all expected role entry points:

```text
tasks/main.yml
handlers/main.yml
defaults/main.yml
vars/main.yml
meta/main.yml
```

Nova itself is clean for this rule.

But we found an important coverage problem.

The detector recognizes only paths shaped like:

```text
roles/<role-name>/...
```

Nova is a standalone role repository:

```text
openstack-ansible-os_nova/tasks/main.yml
openstack-ansible-os_nova/meta/main.yml
```

We made a temporary controlled standalone role without `tasks/main.yml`.

```text
Expected findings: 1
Actual findings:   0
```

That controlled probe is a confirmed false negative.

---

## 10. Broken-role-dependency negative check

Nova's `meta/main.yml` declares no dependencies, so Nova itself has no broken dependency.

However, this detector uses the same `roles/` path assumption.

We made a temporary standalone role that depends on itself.

```text
Expected findings: 1
Actual findings:   0
```

That controlled probe is another confirmed false negative.

---

## 11. Final result

| Rule | Nova result | Coverage conclusion |
|---|---|---|
| `complex-expression` | No miss in 17 boundary examples | Sample only |
| `long-statement` | No missed qualifying lines | Exhaustive for current definition |
| `incomplete-task` | No unresolved markers | Exhaustive for current definition |
| `empty-abstraction` | No empty abstractions | Exhaustive for current definition |
| `excessive-nesting` | Maximum depth is 1 | Exhaustive for current definition |
| `missing-abstraction` | Large files use includes | Exhaustive for current definition |
| `unstructured-module` | Nova is clean | Standalone-role gap confirmed |
| `broken-role-dependency` | Nova has no dependencies | Standalone-role gap confirmed |

Simple conclusion:

```text
Six rules produced no observed Nova false negatives in their audited scope.
Two role-level rules cannot be trusted on standalone role repositories yet.
```

We must not calculate one overall recall percentage because:

```text
The complex-expression audit used a boundary sample.
Two role rules have a known coverage gap.
Nova contains no positive example for six rules.
```

---

## 12. Are we ready for the other four projects?

Not yet.

The next exact work is:

```text
1. Teach role detection to recognize standalone role repositories.
2. Add a regression test for a standalone role missing tasks/main.yml.
3. Add a regression test for a standalone role depending on itself.
4. Decide how external Galaxy dependencies should be treated.
5. Run all automated tests.
6. Rerun the frozen Nova profiles.
7. Update the validation evidence.
8. Then move to the other four pilot projects.
```

The most important conclusion is:

> Negative validation did its job: it found a real blind spot before we expanded the study.
