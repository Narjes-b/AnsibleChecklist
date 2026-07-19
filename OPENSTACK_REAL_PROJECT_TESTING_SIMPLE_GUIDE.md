Let us forget the code details for a moment and explain the whole system as a very simple story.

## 1. What are we trying to do?

We created a tool called AnsibleGuard.

AnsibleGuard reads Ansible files and says things like:

```text
This task is too complicated.
This statement is too long.
This variable may be missing.
This file may contain a security problem.
```

But our small test files are not enough. We want to know:

> Does AnsibleGuard work correctly on large, real projects?

For that reason, we use real OpenStack Ansible projects.

Important: we are not installing OpenStack or running virtual machines.

We are downloading OpenStack’s source code and asking AnsibleGuard to inspect it.

---

# 2. What is an OpenStack project?

An OpenStack project is a Git repository.

A repository is simply a folder containing:

- source code;
- Ansible files;
- documentation;
- tests;
- configuration;
- Git history.

For example:

```text
openstack/openstack-ansible-os_nova
```

After downloading it, the folder looks approximately like:

```text
openstack-ansible-os_nova/
├── defaults/
├── handlers/
├── tasks/
├── vars/
├── tests/
├── examples/
├── releasenotes/
├── zuul.d/
└── .git/
```

Some folders contain real production Ansible.

Other folders contain tests, documentation or CI configuration.

That difference is very important.

---

# 3. The whole process in one small picture

```text
Find OpenStack projects
        ↓
Choose a few projects
        ↓
Download them
        ↓
Freeze each project at one version
        ↓
Find all YAML files
        ↓
Decide which files are real production Ansible
        ↓
Choose which AnsibleGuard rules to run
        ↓
Run AnsibleGuard
        ↓
Save the results
        ↓
Manually check whether the findings are correct
```

Now we will explain every step.

---

# 4. Step one: finding OpenStack projects

OpenStack has a large list of projects on OpenDev.

OpenDev is where the authoritative OpenStack code is maintained.

We created this script:

```text
scripts/discover_openstack_ansible.py
```

Its job is:

> Read the OpenDev project list and find projects that may use Ansible.

The script looks for:

- project names containing `ansible`;
- descriptions containing `ansible`;
- known families such as Kayobe and Bifrost;
- a small list of projects we already know are relevant.

For example, it may discover:

```text
openstack/kolla-ansible
openstack/openstack-ansible
openstack/kayobe
openstack/bifrost
```

## What does “fetching” mean here?

Fetching simply means:

> Getting information from another computer through the internet.

The discovery script fetches the OpenDev project list.

It saves a local copy here:

```text
study/cache/openstack-projects.yaml
```

This local copy is called a cache.

The cache means we do not always need to download the project list again.

The script creates:

```text
study/manifests/candidates.csv
```

This file is a list of possible projects.

“Candidate” means:

> This project may be useful, but we have not accepted it yet.

The script does not automatically select every project.

Every project starts with:

```text
selected=false
```

A human must review the list.

---

# 5. Step two: choosing projects

We do not immediately test 150 projects.

That would be dangerous because:

- some may not contain useful Ansible;
- some may be retired;
- our detectors may still have mistakes;
- downloading everything would take time;
- incorrect detectors would produce thousands of bad results.

We first choose a small pilot.

A pilot is a small experiment before the large experiment.

Our pilot list is:

```text
study/manifests/pilot.csv
```

It selects five projects:

```text
1. openstack/openstack-ansible-os_nova
2. openstack/openstack-ansible
3. openstack/kolla-ansible
4. openstack/kayobe
5. openstack/ansible-collection-kolla
```

We started with Nova because it is smaller and easier to understand.

The line in `pilot.csv` contains:

```text
project = openstack/openstack-ansible-os_nova
selected = true
```

This tells the next script:

> Yes, you are allowed to download this repository.

---

# 6. Step three: downloading the real repository

We created:

```text
scripts/clone_study_repositories.py
```

Its job is:

> Download the selected repositories and put them in our study folder.

Git calls downloading a repository “cloning.”

The script runs something similar to:

```bash
git clone https://opendev.org/openstack/openstack-ansible-os_nova.git
```

The repository is stored here:

```text
study/repositories/
└── openstack/
    └── openstack-ansible-os_nova/
```

## How does the script choose that folder?

It starts with the project name:

```text
openstack/openstack-ansible-os_nova
```

It separates the two parts:

```text
openstack
openstack-ansible-os_nova
```

Then it puts them under:

```text
study/repositories/
```

The result is:

```text
study/repositories/openstack/openstack-ansible-os_nova/
```

Now we have a real local copy of the OpenStack project.

---

# 7. What is a Git commit?

Developers change a project over time.

For example:

```text
Version on Monday
        ↓
Developer changes a task
        ↓
Version on Tuesday
        ↓
Developer adds a feature
        ↓
Version on Wednesday
```

Git saves each important version as a commit.

Every commit has a unique name called a SHA.

A SHA looks like this:

```text
e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

Think of the SHA as the identification number of one exact version.

---

# 8. What is a snapshot?

A snapshot means:

> One project at one exact commit.

Think about taking a photograph.

A real project continues changing every day. But a photograph shows it at one exact moment.

Our snapshot is like that photograph.

For Nova, our snapshot is:

```text
Project:
openstack/openstack-ansible-os_nova

Exact version:
e06c7bceef3f7c365828116b7aadea6fc2d3e22b
```

## Why do we need a snapshot?

Imagine we scan the project today and find:

```text
100 problems
```

Next week, developers change the project. We scan again and find:

```text
80 problems
```

Why did the number change?

Maybe:

- AnsibleGuard changed;
- the project changed;
- the selected files changed;
- the rules changed.

We would not know.

Freezing the project at one commit removes one of these uncertainties.

Every time we scan commit `e06c7b...`, we scan the same source code.

## What does “freeze” mean?

The script tells Git:

```text
Go to this exact commit.
Do not stay on the moving master branch.
```

The repository is placed in detached-HEAD mode.

This simply means:

> The repository is sitting on an exact commit instead of following a branch that can move.

---

# 9. What does the frozen manifest contain?

After downloading and freezing the project, the script creates:

```text
study/manifests/pilot-frozen.csv
```

This file records:

```text
Which project?
Where is its folder?
Which commit?
When was it collected?
How many commits?
How many contributors?
How many YAML files?
How many production Ansible files?
How many test files?
How many lines of code?
Did collection succeed?
```

For Nova, it records approximately:

```text
Project:                  openstack/openstack-ansible-os_nova
Repository folder:        study/repositories/openstack/...
Commit SHA:               e06c7b...
Commits:                  1,482
Contributors:             162
All YAML files:           122
Production Ansible:       28
Test Ansible:             8
Other YAML:               86
Production lines:         2,465
Status:                   collected
```

This is our receipt.

It proves exactly what we downloaded.

---

# 10. What is a manifest?

A manifest is simply a list.

Think about a teacher taking students on a trip.

The teacher has a list:

```text
Ali       included
Sara      included
John      not included
Mary      included
```

That list is a manifest.

Our file manifest says:

```text
This file exists.
This is its type.
Include it or exclude it.
This is the reason.
```

---

# 11. Why do we need a file manifest?

The Nova repository has 122 YAML files.

But not all 122 files are production Ansible.

For example:

```text
tasks/main.yml
```

is production Ansible.

But:

```text
releasenotes/notes/fix.yaml
```

is a release note.

And:

```text
zuul.d/jobs.yaml
```

is CI configuration.

And:

```text
examples/playbook.yml
```

is documentation/example code.

They all use YAML, but they have different purposes.

If we scan everything as production Ansible, the study becomes incorrect.

Therefore, we create a list describing every YAML file.

That list is the file-classification manifest.

---

# 12. How do we find all the YAML files?

We created:

```text
scripts/classify_study_files.py
```

It uses code from:

```text
src/ansibleguard/file_manifest.py
```

First, it reads `pilot-frozen.csv`.

From that file it learns:

```text
The repository is located here:
study/repositories/openstack/openstack-ansible-os_nova
```

Then it checks:

```text
Is the repository still at commit e06c7b...?
```

If the commit is different, it stops.

If the commit is correct, it walks through every folder.

It looks for files ending with:

```text
.yml
.yaml
```

For example:

```text
defaults/main.yml
handlers/main.yml
tasks/main.yml
tasks/install.yml
vars/main.yml
tests/test.yml
examples/playbook.yml
zuul.d/jobs.yaml
```

It also walks inside nested folders:

```text
tasks/
└── drivers/
    └── kvm/
        └── main.yml
```

“Recursive search” means:

> Look in the main folder, then look in every folder inside it, then every folder inside those folders.

---

# 13. How does it classify the files?

For every YAML file, the classifier asks simple questions.

## Is it in a generated folder?

Examples:

```text
.venv/
vendor/
node_modules/
build/
```

Then:

```text
Class: generated or vendor
Included: no
```

## Is it a CI file?

Examples:

```text
.github/
zuul.d/
.gitlab-ci.yml
```

Then:

```text
Class: CI YAML
Included: no
```

## Is it documentation or an example?

Examples:

```text
docs/
examples/
releasenotes/
```

Then:

```text
Class: documentation/example
Included: no
```

## Is it a test?

Examples:

```text
tests/
test/
molecule/
```

Then:

```text
Class: test Ansible
Included in production snapshot: no
```

We keep the test files in the list, but we separate them from production files.

## Is it in a normal Ansible folder?

Examples:

```text
tasks/
handlers/
defaults/
vars/
meta/
group_vars/
host_vars/
playbooks/
```

Then the classifier also looks at the contents of the file.

If the path and contents look like production Ansible:

```text
Class: production Ansible
Included: yes
```

---

# 14. What does the file manifest look like?

It creates a CSV file here:

```text
study/manifests/file-classification/
```

For Nova, the filename contains the project and commit:

```text
openstack__openstack-ansible-os_nova__
e06c7bceef3f7c365828116b7aadea6fc2d3e22b.csv
```

Inside, we have rows like:

| File | Class | Included? | Reason |
|---|---|---:|---|
| `tasks/main.yml` | production Ansible | yes | task structure |
| `defaults/main.yml` | production Ansible | yes | Ansible role path |
| `tests/test.yml` | test Ansible | no | test path |
| `examples/playbook.yml` | documentation | no | example path |
| `zuul.d/jobs.yaml` | CI YAML | no | Zuul path |
| `releasenotes/note.yaml` | documentation | no | release-note path |

For Nova, the result is:

```text
122 total YAML files
        ↓
28 production Ansible files included
8 test Ansible files kept separately
86 other YAML files excluded
```

---

# 15. Why not simply delete the excluded files?

Because we want proof.

We do not want to say:

> “We scanned 28 files.”

We want to say:

> “The repository contained 122 YAML files. We examined every one. We included 28, and here is the reason for every inclusion and exclusion.”

The manifest makes the decision visible and reviewable.

A human can open the CSV and say:

```text
Yes, tasks/main.yml should be included.
No, this example file should not be included.
This file was classified incorrectly.
```

That is part of manual validation.

---

# 16. What is a profile?

Now we have:

```text
One project
One exact commit
28 selected production files
```

But AnsibleGuard contains many different rules.

A profile is a list of rules that we choose to use.

Think about a doctor.

A doctor can perform:

- an eye test;
- a blood test;
- a hearing test;
- an X-ray.

The doctor does not always perform every test.

The chosen group of tests is like our profile.

For AnsibleGuard:

```text
Profile = which rules should run?
```

---

# 17. Why do we need different profiles?

Some rules inspect source code.

For example:

```text
Is this expression complicated?
Is this statement too long?
Is this task incomplete?
```

Other rules inspect Git changes.

For example:

```text
Did the developer add a test?
Did the developer add a release note?
Is the commit message correct?
```

These are different questions.

One asks:

> What is inside the source code now?

The other asks:

> What happened between two commits?

We must keep them separate.

---

# 18. The simple meaning of every profile

## `technical-full`

This means:

> Run almost everything.

It includes:

- source rules;
- Git review rules;
- ansible-lint;
- GitLeaks.

We use it for engineering tests.

It helps us see:

- does the program crash?
- do integrations work?
- can it process the real repository?

But we do not use its total findings as final research results because it mixes different types of questions.

## `snapshot-source`

This means:

> Look only at source-code properties at this exact snapshot.

It uses the selected production files.

It does not include:

- commit-message checks;
- test-update checks;
- release-note checks;
- external aggregate tools.

For Nova it produced:

```text
1,091 findings
```

These are raw findings. They are not automatically 1,091 real problems.

## `research-core`

This means:

> Run only our small, conservative set of main research rules.

It currently contains eight rules.

For Nova it produced:

```text
78 findings
```

But the profile is still provisional.

That means:

> We created it, but humans still need to verify whether its findings are correct.

## `extended-ansible`

This means:

> Run the other Ansible-specific source rules, but keep them outside the main research results.

For Nova it produced:

```text
1,013 findings
```

A large part comes from `unguarded-variable`.

That detector may not understand variables coming from other files or from runtime input. Therefore, many findings may be false positives.

We keep these findings separate so they do not damage the main research results.

## `review-range`

This means:

> Inspect a Git change, not the source snapshot.

It checks things like:

- missing release note;
- missing test update;
- bad commit message.

For Nova it produced:

```text
3 findings
```

These findings do not belong in source-code prevalence statistics.

---

# 19. How the scanner runs everything

We created:

```text
scripts/run_study_pilot.py
```

This script connects all the pieces.

It reads:

```text
pilot-frozen.csv
```

From it, the script learns:

```text
Project name
Repository folder
Exact commit SHA
```

Then it checks the repository’s current commit.

Next, it finds the corresponding file manifest.

Then it chooses the requested profile.

Finally, it calls AnsibleGuard.

The process is:

```text
Frozen project
    +
File manifest
    +
Profile
    =
Controlled scan
```

---

# 20. Where are the results stored?

The results are separated by:

1. project;
2. commit SHA;
3. profile.

For example:

```text
study/analysis/profiled-snapshots/
└── openstack__openstack-ansible-os_nova/
    └── e06c7bceef3f7c365828116b7aadea6fc2d3e22b/
        ├── snapshot-source/
        ├── research-core/
        ├── extended-ansible/
        └── review-range/
```

This prevents results from overwriting each other.

Inside every profile folder, we have files such as:

```text
findings.json
findings.csv
findings.txt
summary.csv
diagnostics.json
file_selection.json
run_metadata.json
```

## `findings.json`

Contains all individual findings.

## `summary.csv`

Shows finding totals for every analyzed file.

## `diagnostics.json`

Shows parser or tool failures.

## `file_selection.json`

Records which manifest was used and its hash.

## `run_metadata.json`

Records which profile and rules were used.

---

# 21. What are we creating for the real-project test?

Here is the simplest list.

## We create a candidate list

```text
study/manifests/candidates.csv
```

Meaning:

> These OpenStack projects might contain Ansible.

## We create a pilot selection

```text
study/manifests/pilot.csv
```

Meaning:

> These are the small number of projects we chose to test first.

## We create local repository clones

```text
study/repositories/openstack/<project>/
```

Meaning:

> This is the downloaded real source code.

## We create a frozen-project manifest

```text
study/manifests/pilot-frozen.csv
```

Meaning:

> This is the exact project folder and exact commit we collected.

## We create a file-classification manifest

```text
study/manifests/file-classification/<project>__<SHA>.csv
```

Meaning:

> These are all the YAML files, their types and their inclusion decisions.

## We create profile-specific snapshot results

```text
study/analysis/profiled-snapshots/<project>/<SHA>/<profile>/
```

Meaning:

> These are the findings for this project, commit, file selection and rule profile.

## We create logs

```text
study/logs/
```

Meaning:

> This is what the scripts printed while running.

---

# 22. How are we testing AnsibleGuard?

There are three simple levels.

## Level 1: Small automated tests

The `tests/` folder contains small examples.

They check things such as:

```text
Does this detector find a known problem?
Does it avoid a false positive?
Does invalid YAML crash the program?
Does the profile exclude the correct rules?
Does the manifest reject unsafe paths?
```

These tests check the code.

## Level 2: Real OpenStack project test

We run AnsibleGuard against real OpenStack code.

This checks:

```text
Can AnsibleGuard handle a real, large repository?
Can it understand real folder layouts?
Does it crash on unusual files?
Which detectors produce too many findings?
```

Nova revealed that `unguarded-variable` produces too many questionable results.

That is useful information. It tells us the detector needs improvement.

## Level 3: Human validation

A human must inspect findings and decide:

```text
Correct finding?
Incorrect finding?
Uncertain?
```

Only after manual validation can we calculate detector precision.

For example:

```text
100 findings inspected
80 correct
20 incorrect
```

Then precision is:

```text
80 / 100 = 80%
```

This manual step has not been completed for the final research profile.

---

# 23. What is finished, and what is not finished?

## Finished

We have:

- discovered OpenStack candidates;
- selected a five-project pilot;
- downloaded the Nova repository;
- frozen it at an exact commit;
- found its 122 YAML files;
- classified those files;
- selected 28 production Ansible files;
- created the different profiles;
- run every profile;
- saved separate results;
- added automated tests.

## Not finished

We still need to:

- manually verify file classifications;
- manually inspect detector findings;
- calculate precision;
- improve problematic detectors;
- run the remaining pilot projects;
- freeze the final research rule set;
- run the larger study.

---

# 24. The four most important words

If you remember only this, remember:

## Fetch

```text
Download the OpenStack project list or repository.
```

## Snapshot

```text
One project frozen at one exact commit.
```

## Manifest

```text
A list explaining exactly which projects or files are included.
```

## Profile

```text
A list deciding exactly which AnsibleGuard rules are used.
```

And together:

```text
Snapshot = which version?
Manifest = which files?
Profile  = which rules?
```

That is the foundation of the entire real-project testing process.

---

# 25. Our exact next steps

We should do these in this order:

1. Run `.venv/bin/pytest -q` and confirm all automated tests pass.
2. Manually review the Nova file-classification manifest. Check that production, test, CI, documentation, and other YAML files were classified correctly.
3. Manually label the 78 Nova `research-core` findings as `true positive`, `false positive`, or `uncertain`, with a short reason.
4. Inspect clean Nova examples too, so we can discover false negatives that AnsibleGuard missed.
5. Calculate precision separately for every research-core rule.
6. Fix detectors that produced incorrect results, and add an automated regression test for every confirmed detector bug.
7. Improve project-level variable resolution before trusting `unguarded-variable`. It must understand role defaults, role vars, `include_vars`, `vars_files`, inventories, parent playbooks, and other known inputs.
8. Rerun Nova with `snapshot-source`, `research-core`, `extended-ansible`, and `review-range`.
9. Verify the frozen SHA, file-manifest hash, profile rule hash, processed-file count, diagnostics, and profile separation after the rerun.
10. Only after Nova is understood, clone and freeze the other four pilot projects.
11. Generate and manually review a file-classification manifest for each of those projects.
12. Run the separated profiles on all five pilot projects.
13. Manually validate findings across all five projects and produce a detector-validation report.
14. Obtain supervisor approval for the final rule set, thresholds, file policy, tool versions, and research-core hash.
15. Freeze that approved configuration. Do not change it during the main dataset run.
16. Select, clone, freeze, classify, and scan the main OpenStack corpus.
17. Calculate snapshot prevalence, density per KLOC, smelly-file percentages, and co-occurrence.
18. After snapshot results are trustworthy, begin the separate Git-history and Gerrit analysis for change-proneness and defect-related questions.

## The next action right now

```text
1. Run the automated tests.
2. Review the Nova file-classification manifest.
3. Label the 78 Nova research-core findings.
```

We should not expand to the other projects until these three tasks show that our file selection and primary detectors are trustworthy.
