• The easiest way to understand the design is:

  > A snapshot fixes when we scan.
  > A manifest fixes what files we scan.
  > A profile fixes what questions/rules we apply.

  Together, they make the OpenStack experiment reproducible and scientifically meaningful.

  ## 1. What are we actually trying to study?

  Suppose we ask:

  > “How common are Ansible code smells in OpenStack projects?”

  Before counting anything, we must define three things:

  1. Which version of each OpenStack repository?
  2. Which files are genuinely production Ansible?
  3. Which detector rules count as research smells?

  If any of these changes during the experiment, our results become unreliable.

  That is why snapshots, manifests, and profiles exist.

  ———

  ## 2. What is a snapshot?

  A snapshot means:

  > One repository at one exact Git commit.

  For example, our current real-project pilot uses:

  Project:
  openstack/openstack-ansible-os_nova

  Commit:
  e06c7bceef3f7c365828116b7aadea6fc2d3e22b

  This 40-character value is the commit SHA.

  ### Why not simply scan master?

  Because master moves.

  Imagine this sequence:

  Monday:  master points to commit A
  Tuesday: developers merge changes
  Friday:  master points to commit B

  If we scan master on Monday and again on Friday, we are scanning different code. Finding
  counts might change even though our command is identical.

  A commit SHA does not move. Commit e06c... will always represent the same source code.

  ### What the collection script does

  The collection process:

  1. Clones the repository from OpenDev.
  2. determines the exact commit;
  3. checks out that commit in detached-HEAD mode;
  4. records the SHA, commit date and repository information;
  5. counts files, commits, contributors and lines of code.

  The frozen information is stored in:

  study/manifests/pilot-frozen.csv

  Before scanning, the pilot runner checks:

  Current repository HEAD == recorded frozen SHA?

  If they are different, the scan stops.

  This protects us from accidentally scanning a newer version.

  ### A snapshot is not a repository backup

  In this project, “snapshot” does not mean:

  - a screenshot;
  - a ZIP archive;
  - the repository’s full history;
  - the newest version of a branch.

  It means a controlled experimental state:

  project + exact commit + selected files + fixed rule profile

  ———

  ## 3. What is a manifest?

  A manifest is an explicit inventory.

  It says:

  > “These are the objects included in the experiment, and these are the reasons.”

  We use several related manifests.

  ### A. Candidate manifest

  The discovery script examines the authoritative OpenDev project registry and creates:

  study/manifests/candidates.csv

  It contains possible OpenStack repositories that might contain Ansible.

  Discovery found:

  150 candidate repositories
  81 active
  69 retired

  Being a candidate does not mean that the repository is automatically included. A human
  still reviews the candidates.

  ### B. Pilot project manifest

  The pilot manifest says which repositories we selected for initial testing:

  study/manifests/pilot.csv

  The five planned pilot projects are:

  1. openstack/openstack-ansible-os_nova
  2. openstack/openstack-ansible
  3. openstack/kolla-ansible
  4. openstack/kayobe
  5. openstack/ansible-collection-kolla

  At present, the complete profiled experiment has been performed on the first, smaller Nova
  role repository.

  ### C. Frozen repository manifest

  After cloning a selected repository, we write its exact immutable information to pilot-
  frozen.csv.

  For Nova, it records things such as:

  Commit:                    e06c7b...
  Total commits:             1,482
  Contributors:              162
  All YAML files:            122
  Production Ansible files:  28
  Test Ansible files:        8
  Other YAML files:          86
  Production Ansible LOC:    2,465

  This manifest answers:

  > “Exactly which repository state did we collect?”

  ### D. File-classification manifest

  This is especially important.

  A repository can contain many .yml and .yaml files, but not every YAML file is production
  Ansible.

  Examples include:

  - production tasks;
  - handlers;
  - role defaults;
  - role metadata;
  - Molecule tests;
  - Zuul CI configuration;
  - release notes;
  - documentation examples;
  - generic data files.

  Scanning every YAML file as if it were production Ansible would be incorrect.

  The file-classification manifest contains one row for every YAML candidate:

  study/manifests/file-classification/openstack__openstack-ansible-
  os_nova__e06c7bceef3f7c365828116b7aadea6fc2d3e22b.csv

  A simplified example looks like this:

   Path                     Classification                    Included?    Reason
  ━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━
   defaults/main.yml        production Ansible                      yes    role defaults
  ───────────────────────  ────────────────────────────────  ───────────  ───────────────────
   handlers/main.yml        production Ansible                      yes    Ansible tasks
  ───────────────────────  ────────────────────────────────  ───────────  ───────────────────
   meta/main.yml            production Ansible                      yes    role metadata
  ───────────────────────  ────────────────────────────────  ───────────  ───────────────────
   examples/playbook.yml    documentation example                    no    example path
  ───────────────────────  ────────────────────────────────  ───────────  ───────────────────
   releasenotes/...yaml     documentation/release material           no    release-note path

  For Nova:

  122 total YAML candidates
   ↓ classification
  28 included production Ansible files

  ### Why this matters mathematically

  Suppose the scanner finds smells in 28 production files.

  If we divide by all 122 YAML files, the denominator includes release notes, CI files and
  examples.

  If we produce findings from 122 files but divide by 28 production files, the numerator and
  denominator describe different populations.

  Both approaches are scientifically wrong.

  The manifest ensures:

  Files scanned = files used in the prevalence denominator

  ### The manifest is also hashed

  The scan calculates a SHA-256 hash of the file manifest and records it in
  file_selection.json.

  That lets us detect whether someone edited the manifest between two runs. Resume mode will
  not silently reuse results produced with a different manifest.

  ———

  ## 4. What is a profile?

  A profile is a controlled set of detector rules and execution stages.

  It answers:

  > “Which type of question are we asking during this run?”

  AnsibleGuard contains different kinds of rules. They do not all measure the same thing.

  For example:

  “Is this expression too complex?”

  is a property of source code at one commit.

  But:

  “Did this change include a test update?”

  is a property of a change between two commits.

  And:

  “Is this commit message formatted correctly?”

  is a property of Git history, not an Ansible file.

  Mixing these findings in one prevalence table would be like mixing:

  - properties of a house;
  - properties of its renovation;
  - properties of the renovation paperwork.

  They are related, but they are not the same measurement.

  Profiles keep them separate.

  ## 5. The five profiles

  The profile definitions live in:

  src/ansibleguard/profiles.py

   Profile             What it does                        Intended use
  ━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   technical-full      Runs all internal rules, review     Development and diagnostics
                       rules and external tools
  ──────────────────  ──────────────────────────────────  ───────────────────────────────────
   snapshot-source     Runs all 51 internal source         Detector calibration at one
                       rules                               snapshot
  ──────────────────  ──────────────────────────────────  ───────────────────────────────────
   research-core       Runs a conservative eight-rule      Provisional primary research
                       set
  ──────────────────  ──────────────────────────────────  ───────────────────────────────────
   extended-ansible    Runs the other 43 source rules      Secondary Ansible-specific
                                                           analysis
  ──────────────────  ──────────────────────────────────  ───────────────────────────────────
   review-range        Runs seven Git/change rules         Commit and review analysis

  ### technical-full

  This is the broad engineering mode.

  It includes:

  - source detectors;
  - Git review checks;
  - ansible-lint;
  - GitLeaks.

  It is useful for finding crashes and integration problems. However, it mixes several types
  of evidence, so we do not use it for final prevalence statistics.

  ### snapshot-source

  This asks:

  > “Which source findings exist in these selected files at this exact commit?”

  It:

  - requires a file manifest;
  - runs internal source detectors;
  - does not run review-range checks;
  - does not run aggregate ansible-lint or GitLeaks rules.

  This is useful for calibrating every internal source detector.

  ### research-core

  This is intended to become the primary research set.

  It currently contains eight rules:

  - complex-expression
  - incomplete-task
  - long-statement
  - unstructured-module
  - empty-abstraction
  - excessive-nesting
  - missing-abstraction
  - broken-role-dependency

  But this profile is still marked:

  status = provisional-pending-manual-calibration
  research_eligible = false

  That is intentional. Creating a profile does not prove that its detectors are accurate.

  We must manually evaluate their precision before calling the output research evidence.

  ### extended-ansible

  This contains the remaining 43 internal source rules.

  It is kept separate from research-core.

  One important example is unguarded-variable. In OpenStack, variables can come from:

  - role defaults;
  - role vars;
  - inventories;
  - include_vars;
  - parent playbooks;
  - CI;
  - deployment-time inputs.

  The current detector cannot resolve every cross-file and runtime source. Therefore, it
  produced 816 Nova occurrences, many of which may be false positives.

  Instead of allowing this rule to dominate the primary research results, it stays in
  extended-ansible until it is calibrated.

  ### review-range

  This analyzes a Git change range rather than source files at a single state.

  It checks things like:

  - missing release notes;
  - missing test updates;
  - untested override changes;
  - commit-message format;
  - missing bug references;
  - copyright removal.

  It processes zero YAML files through source detectors. Its evidence belongs to review or
  change analysis, not snapshot prevalence.

  ———

  ## 6. Why profiles are frozen and hashed

  Each run writes the following to run_metadata.json:

  - profile name;
  - exact ordered list of rule IDs;
  - rule count;
  - rule-list SHA-256;
  - whether source analysis ran;
  - whether review analysis ran;
  - whether external tools ran;
  - tool statuses.

  Why?

  Imagine we publish results using eight rules. Later, someone adds a ninth rule to the
  profile and reruns the scanner.

  Both output directories might say research-core, but they would not represent the same
  experiment.

  The rule hash exposes that difference.

  The code also verifies that:

  - every catalog rule belongs to a known family;
  - core and extended rules do not overlap;
  - snapshot rules do not contain review rules;
  - snapshot rules do not contain external aggregate rules.

  ———

  ## 7. How snapshot, manifest and profile work together

  Think of a medical experiment:

  - Snapshot = which patient and at what moment.
  - Manifest = which samples from that patient are examined.
  - Profile = which laboratory tests are performed.

  In our project:

  Snapshot
  openstack/openstack-ansible-os_nova
  at commit e06c7b...
          ↓
  Manifest
  select 28 production Ansible files
  from 122 YAML candidates
          ↓
  Profile
  apply snapshot-source, research-core,
  extended-ansible, or review-range
          ↓
  Outputs
  findings + metadata + diagnostics

  Without the snapshot, the code can change.

  Without the manifest, the file population is ambiguous.

  Without the profile, the meaning of the findings is ambiguous.

  ———

  ## 8. How we are testing with OpenStack

  There are two different meanings of “testing” here.

  ### We are not currently deploying an OpenStack cloud

  The current work does not create virtual machines or execute these roles against a live
  OpenStack installation.

  We are using real OpenStack Ansible repositories as an empirical corpus to test and
  calibrate AnsibleGuard.

  So the question is:

  > “Does our static analyzer behave correctly on large, real-world OpenStack Ansible code?”

  ### Layer 1: Automated unit and regression tests

  The tests/ directory contains focused tests for:

  - individual detectors;
  - YAML parsing;
  - unusual OpenStack-style variable files;
  - Vault files;
  - nested Ansible blocks;
  - output formats;
  - file manifest safety;
  - profile separation;
  - Git review-range analysis;
  - missing external tools;
  - previously discovered real-world crashes.

  For example, profile tests verify that a snapshot run does not accidentally execute:

  - GitLeaks;
  - ansible-lint;
  - Git review analysis.

  These tests answer:

  > “Does the code behave according to its implementation contract?”

  ### Layer 2: Real-project technical testing

  We run the broad technical-full profile against a real OpenStack repository.

  This helps expose problems that tiny fixtures do not reveal:

  - unexpected YAML shapes;
  - cross-file variables;
  - unusual role layouts;
  - external-tool integration issues;
  - performance problems;
  - parser crashes.

  The first Nova technical run processed all 122 YAML files and produced 1,175 findings. It
  completed successfully, but those numbers are engineering diagnostics—not research results.

  ### Layer 3: File-population testing

  Next, we classify every YAML file and scan only the 28 production Ansible files.

  This tests whether the numerator and denominator refer to the same population.

  The classified technical scan produced 1,111 findings rather than 1,175.

  That difference demonstrates why file selection matters.

  ### Layer 4: Profile-separation testing

  We ran all separated profiles on the same repository, commit and 28 selected files:

   Profile             Findings
  ━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━
   snapshot-source        1,091
  ──────────────────  ──────────
   research-core             78
  ──────────────────  ──────────
   extended-ansible       1,013
  ──────────────────  ──────────
   review-range               3

  Notice:

  78 core + 1,013 extended = 1,091 snapshot-source

  This confirms that core and extended are disjoint and together form the complete internal
  source population.

  The review-range findings remain separate.

  ### Layer 5: Manual detector validation

  This is the important unfinished research step.

  A human needs to inspect samples of:

  - reported findings;
  - clean locations where the detector reported nothing;
  - different rules;
  - different file types;
  - different projects.

  For each finding, we label:

  True positive?
  False positive?
  Uncertain?
  Why?

  This lets us calculate detector precision and identify systematic failures.

  For example, 816 unguarded-variable findings do not mean that Nova contains 816 genuine
  variable defects. They currently mean that the detector needs better project-level variable
  resolution.

  ### Layer 6: Five-project pilot

  Once the Nova classification and detectors are calibrated, the process expands to the five
  selected pilot projects.

  The goal is to discover whether problems are:

  - specific to Nova;
  - specific to role repositories;
  - specific to integrated repositories;
  - common throughout OpenStack Ansible.

  We should not scan all 150 candidates before this pilot is stable.

  ### Layer 7: Freeze the research configuration

  After manual calibration and supervisor approval, we freeze:

  - included projects;
  - commit SHAs;
  - file manifests;
  - core rule list;
  - rule hash;
  - thresholds;
  - detector configuration;
  - dependency/tool versions.

  Only then should we run the main corpus.

  ### Layer 8: Later history and Gerrit analysis

  Snapshot analysis can tell us:

  > “Which smells exist at this commit?”

  It cannot tell us:

  - when a smell was introduced;
  - how long it survived;
  - whether it caused a defect;
  - whether reviewers discussed it;
  - whether smelly files change more frequently.

  Those questions require longitudinal Git history and Gerrit data.

  For OpenStack:

  - OpenDev is authoritative for code and history;
  - Gerrit is authoritative for reviews;
  - GitHub is primarily a mirror;
  - GitHub pull requests should not be treated as OpenStack review activity.

  ———

  ## 9. Where we currently stand

  Completed:

  - OpenDev repository discovery;
  - candidate and pilot manifests;
  - freezing the Nova repository at an exact SHA;
  - classifying all 122 Nova YAML files;
  - selecting 28 production Ansible files;
  - implementing all five profiles;
  - running the separated profiles;
  - recording hashes and provenance;
  - adding automated tests for the separation.

  Still required:

  - human validation of the file-classification sample;
  - manual precision evaluation of core findings;
  - improved cross-file variable resolution;
  - decisions about false positives and thresholds;
  - running the complete five-project pilot;
  - supervisor approval;
  - freezing the final research-core profile;
  - main-corpus and history analysis.

  The most important principle is:

  > The current OpenStack outputs prove that the pipeline runs. They do not yet prove that
  > every reported smell is correct.

  The project’s clearest detailed references are WHAT_IS_A_SNAPSHOT_STUDY.md and
  RESEARCH_PROFILES_IMPLEMENTATION.md.
