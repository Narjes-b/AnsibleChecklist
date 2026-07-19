# Nova Calibrated Rerun — Simple Results

## 1. What did we fix?

We fixed two problems found during manual validation:

```text
Problem 1: long-statement counted a comment as code.
Problem 2: complex-expression sometimes reported the wrong source line.
```

The project being tested did not change:

```text
Project: openstack/openstack-ansible-os_nova
Commit:  e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

This means the old and new results examine the same source code.

---

## 2. What code changed?

### Long statements

The detector now ignores:

```text
blank lines
comment-only lines beginning with #
```

It still reports real YAML and Jinja code lines longer than 120 characters.

### Complex-expression locations

The detector now compares expressions after normalizing whitespace while preserving a map back to original source lines.

Simple meaning:

> A multiline expression can be found even when YAML spreads it over several lines.

The detector no longer depends on matching only the first 24 characters on one physical line.

---

## 3. Automated tests

Two regression tests were added:

```text
A long comment must not become a long-statement finding.
A multiline Jinja expression must report its opening source line.
```

Full result:

```text
165 tests passed in 17.99 seconds
0 tests failed
```

Before the fix there were 163 tests. The two new tests explain the new total of 165.

---

## 4. Did we preserve the experiment?

Yes.

```text
Frozen commit SHA: unchanged
Manifest hash: unchanged
Included production files: 28
Diagnostics: 0
External tools in source profiles: not requested
```

Manifest hash:

```text
bdfd65b0ab2beae60cfd391e66d2ea45d47954a0e4e45d8a36753120c45de628
```

Research-core rule hash:

```text
cf5cc34db16a20c356134d1d80b5e583e2066f68b5b58001ba324fee9d25a0b6
```

The corrected outputs were written to a new folder:

```text
study/analysis/calibrated-snapshots/
```

The old baseline remains in:

```text
study/analysis/profiled-snapshots/
```

---

## 5. Before-and-after results

| Profile | Before | After | Change |
|---|---:|---:|---:|
| `snapshot-source` | 1,091 | 1,090 | -1 |
| `research-core` | 78 | 77 | -1 |
| `extended-ansible` | 1,013 | 1,013 | 0 |
| `review-range` | 3 | 3 | 0 |

Why did only one finding disappear?

```text
The long comment at defaults/main.yml line 311 is no longer treated as code.
```

The complex expressions did not disappear because they were real expressions. Their source locations were corrected.

---

## 6. Corrected research-core result

| Rule | Findings | Valid meaning | Valid location |
|---|---:|---:|---:|
| `complex-expression` | 38 | 38 | 38 |
| `long-statement` | 39 | 39 | 39 |
| **Total** | **77** | **77** | **77** |

For the reviewed positive findings:

```text
Semantic precision = 77 / 77 = 100%
Location validity  = 77 / 77 = 100%
```

This is the calibrated positive-finding result for Nova.

---

## 7. What happened to the wrong expression locations?

The old output had 13 incorrect locations among 38 complex-expression findings.

The corrected output reports the real locations, including multiline expressions at lines such as:

```text
defaults/main.yml:42
defaults/main.yml:100
defaults/main.yml:407
defaults/main.yml:638
defaults/main.yml:837
vars/debian.yml:26
vars/main.yml:20
vars/main.yml:26
vars/main.yml:33
vars/main.yml:100
vars/main.yml:103
```

No corrected complex-expression finding falls back to line 1.

---

## 8. What do these results prove?

They prove:

```text
The two known detector defects were fixed.
The fixes are protected by automated tests.
The same frozen project and file manifest were reused.
The corrected positive findings have valid meanings and locations.
The profile separation still works.
No scan diagnostics were produced.
```

They do not yet prove:

```text
That AnsibleGuard found every smell that exists.
That the six core rules with zero Nova findings have no false negatives.
That Nova results automatically generalize to other projects.
That research-core is ready for final publication.
```

---

## 9. Exact next step

Next we must validate negative examples.

Simple meaning:

> Until now we checked whether reported findings were correct. Now we must check whether AnsibleGuard missed problems.

The next sequence is:

```text
1. Select clean examples for all eight research-core rules.
2. Manually inspect them for missed smells.
3. Record false negatives and explanations.
4. Fix any newly confirmed detector gaps.
5. Rerun Nova again if detector logic changes.
6. Only then collect the other four pilot projects.
```

The main conclusion is:

> Nova’s positive research-core evidence is now clean, but negative-example validation is still required before expanding the pilot.
