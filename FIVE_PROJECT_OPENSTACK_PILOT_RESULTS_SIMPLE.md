# Five Real OpenStack Projects: Simple Testing Results

> **Newer output-contract run:** This document describes the earlier
> profile/calibration pilot. The fresh `technical-full` output-v2 validation
> is documented in
> [FIVE_REPOSITORY_OUTPUT_V2_FINAL_RESULTS.md](FIVE_REPOSITORY_OUTPUT_V2_FINAL_RESULTS.md).

## First: what did we do?

We tested AnsibleGuard on five real OpenStack projects.

Very slowly, the work was:

1. Get each real project.
2. Freeze one exact version of each project.
3. Find all YAML files inside each project.
4. Decide which YAML files are real production Ansible files.
5. Save that decision in a manifest.
6. Run the different profiles on only the selected files.
7. Keep all findings and metadata.
8. Check that the saved results agree with each other.
9. Look at positive and negative examples by hand.

We did **not** deploy a real OpenStack cloud.

We tested the Ansible source code stored in real OpenStack repositories.

That is important.

This test answers:

> Can AnsibleGuard collect, select, scan, and save results from real OpenStack Ansible projects?

The answer is:

> Yes. The complete five-project pilot ran successfully.

But the findings are still provisional. They are not all confirmed bugs.

---

## The three small ideas again

### 1. Snapshot

A snapshot means:

> Keep one exact version of a project.

A project changes every day.

If we scan it today and scan it again later, the code may be different.

So we save the exact Git commit SHA.

The SHA is like the exact ID card of the project version.

This makes the experiment repeatable.

### 2. Manifest

A repository has many YAML files.

Not every YAML file is production Ansible code.

Some files are:

- documentation examples,
- CI configuration,
- tests,
- dependency lists,
- or real production Ansible.

The manifest is a CSV list that records the decision for every YAML file.

It says:

> include this file

or:

> do not include this file

It also saves the reason.

The manifest is like a teacher's attendance list for files.

Only the files marked `included=true` enter the source-code scan.

### 3. Profile

A profile is a named box of rules.

We used four boxes:

- `snapshot-source`: all 51 source rules.
- `research-core`: the small provisional set of 8 paper-derived rules.
- `extended-ansible`: the other 43 source rules.
- `review-range`: 7 rules about the latest Git change and commit context.

The profiles keep different questions separate.

The important source equation is:

```text
research-core + extended-ansible = snapshot-source
```

This equation passed for all five projects.

---

## Which real projects did we freeze?

| Project | Frozen commit SHA |
|---|---|
| `openstack/openstack-ansible-os_nova` | `e06c7bceef3f7c365828116b7aadea6fc2d3e22b` |
| `openstack/openstack-ansible` | `b7c10cbcc04a06207c2344a312d4f612a0810939` |
| `openstack/kolla-ansible` | `9c41bdca79d4c7267beeece141909e679f70dea8` |
| `openstack/kayobe` | `9a6e4333b2aa2fbe8dc80a93cd5aa3e2f1872970` |
| `openstack/ansible-collection-kolla` | `785982d7c09dda3d8e46f6c9b09597ca14820497` |

The frozen collection information is saved in:

```text
study/manifests/pilot-five-frozen.csv
```

---

## How did the scripts find the folders?

The collection CSV gives each project a name and repository path.

For example:

```text
project: openstack/kayobe
folder:  study/repositories/openstack/kayobe
```

The scripts do not guess a random folder.

They follow the saved repository path.

Inside the repository, the classification code walks through the folders and finds files ending in `.yml` or `.yaml`.

Then it studies the path and the YAML shape.

For example:

```text
roles/example/tasks/main.yml
```

looks like a real Ansible role task file.

But:

```text
doc/source/example.yml
```

looks like documentation.

And:

```text
.zuul.yaml
```

is CI configuration.

The final decision for every file is written to:

```text
study/manifests/file-classification/
```

The runner reads the frozen-project CSV.

Then it finds the matching manifest using:

```text
project name + exact commit SHA
```

This prevents a manifest from one version or project being silently used for another one.

---

## What classification problems did we find and fix?

The audit found three important folder cases.

### OpenStack deployment configuration

Real variables can live under folders such as:

```text
etc/kayobe/
etc/kolla/
etc/openstack_deploy/
```

The classifier now recognizes these as Ansible deployment configuration when appropriate.

### Dependency manifests

A file such as:

```text
ansible-role-requirements.yml
```

is a dependency list.

It is not a task file.

The classifier now excludes it with the reason:

```text
ansible_dependency_manifest
```

### A real folder beginning with a space

One repository contains a real path whose first folder begins with a space.

The classifier may normalize that name when deciding its class, but the manifest reader must preserve the real path exactly.

We fixed the reader so it does not destroy a legitimate leading space.

Tests were added for these cases.

The complete project test suite passed:

```text
168 passed
```

We also told pytest not to collect the cloned OpenStack repositories as if their own tests belonged to AnsibleGuard.

---

## How many files were selected?

| Project | All YAML candidates | Included production Ansible files |
|---|---:|---:|
| Nova role | 122 | 28 |
| OpenStack-Ansible | 1,708 | 216 |
| Kolla-Ansible | 2,570 | 1,228 |
| Kayobe | 938 | 342 |
| Ansible Collection Kolla | 71 | 42 |
| **Total** | **5,409** | **1,856** |

This does not mean the excluded files are bad.

It only means they were outside this production-source experiment.

---

## What results did the profiles produce?

| Project | All source findings | Research-core findings | Extended findings | Review findings | Diagnostics |
|---|---:|---:|---:|---:|---:|
| Nova role | 777 | 77 | 700 | 3 | 0 |
| OpenStack-Ansible | 731 | 192 | 539 | 1 | 0 |
| Kolla-Ansible | 7,795 | 703 | 7,092 | 1 | 0 |
| Kayobe | 3,712 | 247 | 3,465 | 1 | 0 |
| Ansible Collection Kolla | 372 | 31 | 341 | 4 | 0 |
| **Total** | **13,387** | **1,250** | **12,137** | **10** | **0** |

What does `0 diagnostics` mean?

It means the runner did not save scan errors or crashes in these 20 runs.

It does **not** mean every finding is a true bug.

The external tools `ansible-lint` and `gitleaks` were not requested in these profile runs. The metadata correctly records them as `not-requested`.

---

## What is inside the 1,250 research-core findings?

| Research-core rule | Count |
|---|---:|
| `long-statement` | 643 |
| `complex-expression` | 487 |
| `incomplete-task` | 51 |
| `empty-abstraction` | 41 |
| `missing-abstraction` | 24 |
| `unstructured-module` | 4 |
| `broken-role-dependency` | 0 |
| `excessive-nesting` | 0 |
| **Total** | **1,250** |

These counts tell us what the detector reported.

They do not yet tell us that OpenStack has 1,250 confirmed defects.

---

## What did the human spot check show?

We checked at least one positive example for every research-core rule that appeared, across the different project layouts.

We also checked one file with no research-core finding from each project.

The simple result is:

### Direct operational matches

These examples visibly match their written detector condition:

- physical lines longer than 120 characters,
- Jinja expressions reaching or exceeding the configured complexity threshold,
- source comments containing unresolved TODO markers.

### Context-sensitive matches

These require more human judgment:

- An empty YAML file can intentionally be a no-op placeholder.
- A large task file may be acceptable even when it crosses the configured split threshold.
- A role can intentionally have `vars/Debian.yml` and `vars/RedHat.yml` without `vars/main.yml` when it loads the operating-system file dynamically.

So the tool correctly saw the written structure, but the structure is not automatically a real defect.

This is why `research-core` still says:

```text
provisional-pending-manual-calibration
```

and:

```text
research_eligible = false
```

The exact spot-check labels are saved in:

```text
study/labels/five_project_core_spot_check_labels.csv
```

The earlier, deeper Nova positive and negative validation remains saved separately in the Nova result and label files.

---

## Where are all the results kept?

### Full machine results

```text
study/analysis/five-project-pilot/
```

Inside it, the folder structure is:

```text
project / commit SHA / profile / result files
```

For example:

```text
study/analysis/five-project-pilot/
  openstack__kayobe/
    9a6e4333b2aa2fbe8dc80a93cd5aa3e2f1872970/
      snapshot-source/
      research-core/
      extended-ansible/
      review-range/
```

Each profile folder keeps files such as:

```text
findings.json
findings.csv
summary.csv
diagnostics.json
run_metadata.json
file_selection.json
review_metrics.json
```

### Small combined summary

```text
study/labels/five_project_pilot_summary.csv
```

### Human spot-check labels

```text
study/labels/five_project_core_spot_check_labels.csv
```

### File manifests

```text
study/manifests/file-classification/
```

### Run logs

```text
study/logs/five-project-pilot/
```

---

## What exactly passed in the final validation?

For all five projects:

- the frozen commit SHA was saved,
- the matching manifest was used,
- the manifest hash was saved,
- the included-file count was the same across profiles,
- the profile name and rule hash were saved,
- external tools were correctly marked `not-requested`,
- source-profile review metrics were empty,
- all diagnostics were empty,
- and `research-core + extended-ansible = snapshot-source`.

There were 5 projects and 4 profiles.

So we produced and checked 20 profile runs.

---

## What is the next step now?

The collection and pilot execution step is finished.

The next step is **manual calibration**, not another blind large scan.

Very simply:

1. Take a balanced sample from the 1,250 research-core findings.
2. Make sure every project and every reported rule is represented.
3. Let a human label each sampled finding:
   - real problem,
   - not a real problem,
   - or unsure.
4. Add negative examples where no finding should appear.
5. Measure how often each rule is correct.
6. Improve or remove rules that create too many context-sensitive warnings.
7. Run the five frozen snapshots again with the calibrated rules.
8. Only after that decide whether the profile can become research-eligible.

The most important rules to study first are:

```text
empty-abstraction
missing-abstraction
unstructured-module
```

They are the rules where repository context can change the meaning.

We should not change the frozen snapshots while calibrating.

Keeping the same snapshots lets us compare the old results and new results fairly.

---

## Final tiny summary

We froze five real OpenStack repositories.

We created complete file manifests.

We selected 1,856 production Ansible files from 5,409 YAML candidates.

We completed 20 profile runs with zero saved diagnostics.

We preserved 13,387 source findings, including 1,250 provisional research-core findings.

We checked that all result partitions and metadata agree.

We also learned that some structural rules need human context.

So the real-project pilot works.

The next scientific gate is manual calibration before calling the core findings confirmed research data.
