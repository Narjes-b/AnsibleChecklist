# Nova Validation Results — Simple Explanation

## 1. What did we do?

We checked the first real OpenStack project used by AnsibleGuard:

```text
Project: openstack/openstack-ansible-os_nova
Commit:  e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

We performed three checks:

```text
1. Run all automated tests.
2. Check the Nova file manifest.
3. Check all 78 research-core findings.
```

The existing scanner results were not edited. Our validation results were saved separately.

---

## 2. Automated test result

We ran:

```bash
.venv/bin/pytest -q
```

Result:

```text
163 tests passed in 18.54 seconds
0 tests failed
```

Simple meaning:

> The existing automated behavior is stable before we make detector fixes.

---

## 3. Snapshot safety result

The repository currently has this Git commit:

```text
e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

The frozen manifest requires the same commit.

Result:

```text
Actual SHA = expected SHA
```

Simple meaning:

> We validated the correct frozen photograph of the project. The repository did not move to another version.

---

## 4. File-manifest result

The manifest contains:

| File class | Files | Included in production scan? |
|---|---:|---:|
| Production Ansible | 28 | Yes |
| Test Ansible | 8 | No |
| Documentation/examples | 84 | No |
| CI YAML | 1 | No |
| Internal symlink alias | 1 | No |
| **Total** | **122** | **28 included** |

We checked the paths, document types, inclusion values, and reasons.

Result:

```text
122 rows reviewed
122 accepted
0 wrong inclusion decisions found
```

The unusual symlink is:

```text
tasks/drivers/kvm/nova_compute_qemu.yml
```

It points to:

```text
nova_compute_kvm.yml
```

The real target is already included. Excluding the alias prevents the same task content from being counted twice.

Simple meaning:

> The Nova production scan used the correct 28-file population.

The manifest hash recorded by the run is:

```text
bdfd65b0ab2beae60cfd391e66d2ea45d47954a0e4e45d8a36753120c45de628
```

---

## 5. What did the research-core profile report?

The profile reported:

| Rule | Findings |
|---|---:|
| `complex-expression` | 38 |
| `long-statement` | 40 |
| Other six core rules | 0 |
| **Total** | **78** |

The research-core rule hash is:

```text
cf5cc34db16a20c356134d1d80b5e583e2066f68b5b58001ba324fee9d25a0b6
```

The profile is still correctly marked:

```text
provisional-pending-manual-calibration
research_eligible = false
```

---

## 6. How did we label the findings?

We used these labels:

```text
true_positive  = the reported source condition really exists
false_positive = the detector reported something that should not count
uncertain      = the available evidence is not enough for a decision
```

We also checked the source location:

```text
correct   = the reported line points to the evidence
incorrect = the expression is real, but the reported line is wrong
```

The row-by-row labels are saved in:

```text
study/labels/nova_research_core_finding_labels.csv
```

`finding_id` means the row number, starting at 1, in the original `research-core/findings.csv` file.

---

## 7. Semantic finding result

| Rule | True positives | False positives | Precision |
|---|---:|---:|---:|
| `complex-expression` | 38 | 0 | 100% |
| `long-statement` | 39 | 1 | 97.5% |
| **Combined** | **77** | **1** | **98.72%** |

Calculation:

```text
Precision = true positives / all reviewed positive findings
Precision = 77 / 78
Precision = 98.72%
```

Simple meaning:

> Almost every reported condition exists, but this does not yet make the complete research-core profile validated. Six rules produced no positive findings here, and false-negative validation is still incomplete.

---

## 8. Problem one: a comment was called a long statement

The one false positive is:

```text
File: defaults/main.yml
Line: 311
Rule: long-statement
```

The line is longer than 120 characters, but it is a comment.

The current detector counts every physical line. It does not skip comments.

Simple meaning:

> A long comment is not a long code statement. The detector should ignore blank lines and comment-only lines.

Required fix:

```text
Update detect_long_statements() to skip comment-only lines.
Add a regression test proving that long comments are ignored.
Keep detecting long YAML/Jinja code lines.
```

---

## 9. Problem two: thirteen correct expressions have wrong line numbers

All 38 complex expressions are real expressions meeting the current complexity threshold.

However:

```text
25 have correct reported locations
13 have incorrect locations
```

Location accuracy:

```text
25 / 38 = 65.79%
```

The affected findings are IDs:

```text
5, 7, 13, 15, 17, 43, 51, 61, 66, 67, 68, 73, 74
```

Most affected expressions span several YAML lines. The old detector searched for only the first 24 characters of an expression on one physical line. It could therefore fall back to line 1 or match a different expression with the same beginning.

Simple meaning:

> The detector found real complex expressions, but sometimes pointed to the beginning of the file instead of the real expression.

Required fix:

```text
Track YAML source positions while parsing, or use a multiline-aware location method.
Never silently use line 1 when the expression was not found.
Add regression tests for folded and literal multiline Jinja expressions.
```

If correct source location is required as part of a valid research occurrence, the strict result is:

```text
64 fully valid occurrences out of 78
Strict occurrence validity = 82.05%
```

This stricter number counts the false-positive comment and the thirteen wrong-location findings as invalid evidence.

---

## 10. What have we proved?

We have proved:

```text
The automated suite passes.
The frozen Nova SHA is correct.
The 122-row manifest matches the intended file population.
The 28 included files are appropriate production Ansible files.
All 78 positive core findings were reviewed.
One semantic false positive exists.
Thirteen findings have incorrect source locations.
```

We have not yet proved:

```text
That the six silent core rules have no false negatives.
That these precision values generalize to other OpenStack projects.
That the current research-core profile is ready for publication.
```

---

## 11. Exact next step

The next implementation work is:

```text
1. Fix long-statement so it ignores comment-only lines.
2. Fix multiline complex-expression source locations.
3. Add regression tests for both bugs.
4. Rerun the automated suite.
5. Rerun all Nova profiles at the same frozen SHA.
6. Compare the new output with this saved baseline.
7. Validate negative examples for all eight core rules.
8. Only then move to the other four pilot projects.
```

The most important conclusion is:

> The Nova pipeline and file population are sound, but the detector evidence needs two fixes and negative-example validation before expansion.
