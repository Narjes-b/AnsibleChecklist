# Nova Standalone-Role Fix — Simple Results

## 1. What was the problem?

Ansible roles can appear in two shapes.

### Shape one: a project containing several roles

```text
project/
└── roles/
    └── web_role/
        ├── tasks/
        ├── handlers/
        └── meta/
```

### Shape two: one repository that is itself a role

```text
openstack-ansible-os_nova/
├── tasks/
├── handlers/
├── defaults/
├── vars/
└── meta/
```

Nova uses the second shape.

The old code only recognized the first shape because it searched for a folder literally named `roles`.

Simple meaning:

> AnsibleGuard could see roles inside another project, but it did not understand that the Nova repository was itself one role.

---

## 2. What did we change?

Role-context detection now recognizes both layouts.

A standalone role is recognized when:

```text
the analyzed file is under a known role directory
and
the repository has meta/main.yml or meta/main.yaml
```

Known role directories include:

```text
tasks
handlers
defaults
vars
meta
```

This avoids treating every ordinary repository as an Ansible role.

---

## 3. What does unstructured-module do now?

For a standalone role, it can now check:

```text
Does tasks/main.yml or tasks/main.yaml exist?
Does each existing role directory have its main entry point?
```

Controlled test:

```text
Standalone role with no tasks/main.yml
Before fix: 0 findings
After fix:  1 finding
```

Result:

> The confirmed false negative is fixed.

---

## 4. What does broken-role-dependency do now?

For a standalone role, it can now detect an unambiguous self-dependency.

Controlled test:

```text
Standalone role depends on itself
Before fix: 0 findings
After fix:  1 finding
```

The detector does not automatically call another missing standalone dependency broken.

Why?

```text
That dependency may come from Ansible Galaxy.
It does not need to exist as a sibling directory.
```

This conservative policy prevents false positives for external Galaxy roles.

---

## 5. Duplicate self-dependency result

The first focused test revealed that a self-dependency could be reported twice:

```text
once as a self-dependency
once as a one-role cycle
```

We corrected that behavior.

Now:

```text
one self-dependency = one finding
```

---

## 6. Automated tests

We added tests for:

```text
standalone role missing tasks/main.yml
standalone role depending on itself
standalone external dependency not assumed broken
```

Full result:

```text
167 tests passed in 17.39 seconds
0 tests failed
```

---

## 7. Did the Nova experiment remain frozen?

Yes.

```text
Commit SHA: e06c7bceef3f7c365828116b7aadea6fc2d3e22b
Included production files: 28
Manifest hash: bdfd65b0ab2beae60cfd391e66d2ea45d47954a0e4e45d8a36753120c45de628
Diagnostics: 0
```

The new output was written separately under:

```text
study/analysis/standalone-role-fixed-snapshots/
```

Earlier evidence was not overwritten.

---

## 8. Nova before and after

| Profile or rule | Before role fix | After role fix | Change |
|---|---:|---:|---:|
| `research-core` | 77 | 77 | 0 |
| `snapshot-source` | 1,090 | 777 | -313 |
| `extended-ansible` | 1,013 | 700 | -313 |
| `unguarded-variable` | 816 | 503 | -313 |
| `review-range` | 3 | 3 | 0 |

The main research-core result stayed unchanged.

Why did 313 extended findings disappear?

Before the fix, task files did not know they belonged to the standalone Nova role. They could not see variables defined in:

```text
defaults/main.yml
vars/main.yml
```

After the fix, those visible role variables are loaded into the detector's project context.

Simple meaning:

> AnsibleGuard stopped calling 313 visible role variables unguarded.

The remaining 503 `unguarded-variable` findings still require calibration. They are not automatically genuine defects.

---

## 9. What do the Nova role rules report?

Nova has:

```text
tasks/main.yml
handlers/main.yml
defaults/main.yml
vars/main.yml
meta/main.yml
```

It declares no dependencies.

Therefore:

```text
unstructured-module findings: 0
broken-role-dependency findings: 0
```

These zero results now mean:

> The detector evaluated the standalone role and found it clean.

Before the fix, zero only meant that the detector did not understand the layout.

---

## 10. Final result

We fixed:

```text
standalone role recognition
missing tasks/main detection for standalone roles
self-dependency detection for standalone roles
duplicate self-dependency reporting
standalone role variable visibility
```

The result is protected by automated tests and a new frozen Nova rerun.

The machine-readable summary is:

```text
study/labels/nova_standalone_role_fix_summary.csv
```

---

## 11. What is next?

The two confirmed standalone-role gaps are fixed.

The next controlled step is now the remaining four-project pilot:

```text
1. Clone and freeze the other four selected repositories.
2. Create a complete YAML classification manifest for each one.
3. Manually review their file classifications.
4. Run the separated profiles.
5. Validate positive and negative examples across different project layouts.
6. Do not freeze the final research profile until that cross-project validation is complete.
```

The most important conclusion is:

> Nova is now correctly understood as a standalone Ansible role, but cross-project validation is still required before the main study.
