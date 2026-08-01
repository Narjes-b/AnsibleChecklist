# Parsing, GitLeaks, and GitHub PR Integration

> Historical implementation log with later validation appendices. Current
> verified state (July 14, 2026): repository-wide GitLeaks findings survive
> parse skips and non-YAML input, Git review rules analyze the complete
> base-to-head range, all normalized JSON/CSV/text/SARIF outputs are tested, and
> the full suite has 163 passing tests. Older command transcripts and counts are
> retained as chronological evidence.

This document records the implementation that separated Ansible structural
analysis from content-only secret scanning. It explains what changed, why it
changed, and how to use and verify the new workflow.

## The original problem

The old pipeline treated every `.yml`/`.yaml` file as though it were a
playbook. That mixed together three different questions:

1. Is the file valid YAML?
2. Is the YAML a playbook or task file that structural detectors understand?
3. Can a content scanner find a secret in the file?

A vars file is commonly valid YAML but is a mapping, not a playbook. An inline
Ansible `!vault` value is also legitimate Ansible syntax even though PyYAML's
default safe loader does not know its constructor. Most importantly, GitLeaks
does not need YAML parsing at all. Tying GitLeaks to successful structural
parsing meant precisely the files most likely to contain credentials could be
skipped.

## Step 1: safe loading and document classification

Added `src/ansibleguard/document.py`.

`inspect_document()` now returns a `DocumentInfo` containing:

- `parse_status`: `parsed`, `empty`, `invalid`, `unsupported`, or `read-error`;
- `document_type`: `playbook`, `tasks`, `vars`, `metadata`, `empty`,
  `vault-encrypted`, `multi-document`, or `unknown`;
- the parsed document when available;
- parser diagnostics;
- `structurally_analyzable`, which is true only for parsed playbooks and task
  files.

Classification uses both structure and conventional Ansible locations. For
example, mappings below `vars/`, `defaults/`, `group_vars/`, `host_vars/`, and
`env_vars/` are vars documents. Lists containing `hosts` or `tasks` are
playbooks, while ordinary lists of task mappings are task files.

`AnsibleSafeLoader` safely preserves unknown tagged values as data. It never
executes a tag-specific constructor. An inline value such as `!vault |` can
therefore be classified without decrypting or interpreting it. Fully encrypted
vault files remain `unsupported/vault-encrypted` because their YAML structure
is intentionally unavailable.

`parser.mainn()` now runs structural detectors only when the classifier says
the document is a playbook or task file. Vars and metadata are valid inputs,
but are deliberately skipped by play/task detectors.

## Step 2: GitLeaks no longer depends on YAML parsing

Added a structured `ToolResult` to `external/gitleaks.py` with:

- `completed` for a successful scan, including a clean scan;
- `tool-error` for a missing binary or failed invocation;
- the raw findings and an error message.

The old `scan_with_gitleaks_file_output()` function remains as a compatibility
wrapper for existing callers and tests.

The CLI now invokes GitLeaks once against the requested target before entering
the per-YAML structural loop. Findings are matched back to their YAML files.
GitLeaks results for non-YAML files are also retained in project-level JSON,
SARIF, and summary output.

`ensure_gitleaks_installed()` was removed from module import time. Importing
AnsibleGuard no longer downloads a binary or writes to the user's home
directory. Tool installation is explicit:

```bash
ansibleguard install-tools
```

A custom binary can be selected with:

```bash
ansibleguard . --gitleaks-path /usr/local/bin/gitleaks
```

## Step 3: findings survive structural failures

`report/findings.py` previously returned immediately when structural metrics
or threshold results were absent. That also discarded valid GitLeaks findings.

The builder now creates external findings first. It returns those findings even
when the YAML is invalid, encrypted, a vars mapping, or otherwise unavailable
to structural detectors. Structural findings are appended only when structural
results exist.

This behavior is locked in by a regression test where invalid YAML still
produces a hardcoded-credential finding.

## Step 4: honest run status and output

`summary.csv` now includes:

| Column | Meaning |
|---|---|
| `parse_status` | Result of YAML inspection |
| `document_type` | Classified Ansible/YAML role |
| `structural_status` | `analyzed`, `skipped`, or `not-applicable` |
| `gitleaks_status` | Whether the target-level content scan completed |
| severity totals | Errors, warnings, notes, and total findings |

The CLI prints discovered and structurally analyzed counts separately. It no
longer calls a vars file or parse failure a successful structural analysis.

New `diagnostics.json` contains parser and external-tool failures separately
from code findings. A missing GitLeaks binary therefore cannot masquerade as a
clean scan.

The CLI supports these policies:

```text
--fail-on never
--fail-on error
--fail-on warning
--fail-on tool-error
--fail-on parse-error
```

The default is `error`. `warning` means errors or warnings. Parsing and tool
failures can be enforced independently.

## Step 5: SARIF improvements

SARIF paths remain relative to the repository root so GitHub can map findings
to pull-request lines. The placeholder tool information URL was replaced.

The earlier implementation supplied a custom SHA-256 value under
`partialFingerprints.primaryLocationLineHash`. Live upload validation on
2026-08-01 proved that this name is reserved for GitHub's calculated line hash:
GitHub reported inconsistent-fingerprint warnings. AnsibleGuard therefore no
longer emits that field and lets GitHub calculate it. Stable AnsibleGuard
occurrence IDs remain in the canonical output and continue to drive base/head
comparison.

## Step 6: GitHub Actions and pull requests

Two workflows were added.

### `.github/workflows/ci.yml`

On pushes and pull requests it:

1. checks out the repository;
2. configures Python 3.12;
3. installs `.[dev]`;
4. runs the full pytest suite;
5. performs a package import smoke test.

### `.github/workflows/ansibleguard.yml`

On pull requests and pushes to `main` or `master` it:

1. checks out the exact commit being scanned;
2. installs AnsibleGuard;
3. explicitly installs the pinned GitLeaks binary;
4. scans the repository with `--fail-on never` so reports are always written;
5. writes the first summary rows to the GitHub job summary;
6. uploads `findings.sarif` through `github/codeql-action/upload-sarif@v4`;
7. uploads every detailed report as an artifact;
8. applies the blocking policy after report publication.

The final policy blocks a PR for AnsibleGuard `error` findings or a GitLeaks
tool failure. Warnings and notes annotate the PR without blocking it.

The workflow requests only `contents: read` and `security-events: write`.
Public repositories support code scanning directly. Private/internal
repositories may require GitHub Code Security to be enabled. Fork PRs remain
subject to GitHub's reduced token permissions; the artifact step still keeps
the generated reports when SARIF upload is not permitted.

## Step 7: tests and fixtures

Added coverage for:

- dict-shaped vars classification;
- safe inline `!vault` loading;
- invalid YAML diagnostics;
- task-file classification;
- multi-document classification;
- GitLeaks findings surviving structural failure;
- tool failures appearing in diagnostics;
- per-file status columns;
- SARIF fingerprints.

Verification command:

```bash
PATH="$PWD/.venv/bin:$PATH" \
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local \
ANSIBLE_REMOTE_TEMP=/tmp/ansible-remote \
.venv/bin/pytest -q
```

Result at implementation time:

```text
126 passed
```

The Ansible temporary-directory variables are needed only in restricted
environments where `$HOME/.ansible` is read-only.

## Files changed

- `src/ansibleguard/document.py`
- `src/ansibleguard/parser.py`
- `src/ansibleguard/smells.py`
- `src/ansibleguard/cli.py`
- `src/ansibleguard/external/gitleaks.py`
- `src/ansibleguard/external/ansible_lint.py`
- `src/ansibleguard/report/findings.py`
- `src/ansibleguard/report/sarif_writer.py`
- `.github/workflows/ci.yml`
- `.github/workflows/ansibleguard.yml`
- `.gitignore`
- regression tests and fixtures under `tests/`

## Current limitations

- Multi-document YAML is identified but not structurally analyzed.
- Fully encrypted vault files cannot be structurally analyzed without a vault
  password, but GitLeaks still scans their content.
- Ansible-lint now runs once at target scope and maps its findings back to the
  actual files reported by ansible-lint, including load failures for files the
  structural detector cannot parse.
- Some detectors still parse their input independently. The classifier prevents
  incompatible document types from reaching them, but a later cleanup should
  make detectors consume one shared parsed representation.
- Threshold and severity calibration remains provisional, as documented in the
  existing project status files.

## Real-project validation — July 13, 2026

Everything in this section was performed after the initial implementation. It
records the public-repository selection, untouched baseline, controlled
mutations, bugs discovered by real data, fixes, and final results.

### Repository selection

Several candidates were compared online:

- `ansible/ansible` was rejected for the first validation because it is much
  larger than needed and is primarily Ansible's Python implementation.
- `ansible/ansible-examples` has broad playbook variety, but it was archived in
  May 2024.
- `dev-sec/ansible-collection-hardening` is active and valuable for a later
  scale/security pass, but is a considerably larger collection.
- `geerlingguy/ansible-for-devops` is broad, but similar material had already
  appeared in previous local result data.
- [`geerlingguy/ansible-role-apache`](https://github.com/geerlingguy/ansible-role-apache)
  was selected because it is active, moderate in size, multi-platform, and has
  realistic defaults, OS-specific vars, task includes, handlers, metadata,
  templates, Molecule scenarios, and repeated `main.yml` filenames.

The repository was cloned shallowly outside this workspace:

```bash
git clone --depth 1 \
  https://github.com/geerlingguy/ansible-role-apache.git \
  /tmp/ansibleguard-validation-apache
```

The validated upstream revision was:

```text
4a6c870f20f2410f252996d684aa10a4ce9c3661
2026-05-18
Merge pull request #268 from Evaluation-Software-Development/ansible_2_20
```

The clone contained 21 YAML files. Two were below `molecule/`, leaving 19
files intentionally discoverable by AnsibleGuard.

### Untouched baseline

The first baseline command was:

```bash
PATH="$PWD/.venv/bin:$PATH" \
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local \
ANSIBLE_REMOTE_TEMP=/tmp/ansible-remote \
.venv/bin/ansibleguard \
  /tmp/ansibleguard-validation-apache \
  -o /tmp/ansibleguard-validation-apache-baseline \
  --gitleaks-path /usr/bin/gitleaks \
  --fail-on never
```

Baseline classification and coverage:

```text
19 YAML files discovered
19 parsed
10 task/handler files structurally analyzed
8 vars/defaults files classified as vars and structurally skipped
1 metadata file classified as metadata and structurally skipped
0 parser diagnostics
0 GitLeaks findings
72 total findings: 63 warnings, 9 notes, 0 errors
```

Baseline rule counts were:

```text
60 ansible-lint-issue
4 missing-file-extension
4 unused-include-vars
3 missing-bool-filters
1 unnamed-task
```

This proved Molecule exclusion, mirrored paths for repeated `main.yml` files,
vars/metadata classification, repository GitLeaks execution, and complete
rollup generation on an unmodified current public role.

### Controlled validation branch

A local-only branch was created in the clone:

```bash
git -C /tmp/ansibleguard-validation-apache \
  switch -c ansibleguard-controlled-validation
```

Only synthetic test credentials were used. No real credential was created or
committed. The following changes were made:

1. `vars/validation-secrets.yml`
   - valid vars mapping;
   - synthetic GitHub PAT-shaped string;
   - expected to be classified as vars, skipped structurally, and detected by
     GitLeaks.
2. `vars/invalid-validation.yml`
   - intentionally unclosed YAML sequence;
   - synthetic PAT-shaped string before the syntax error;
   - expected to produce both a parse diagnostic and GitLeaks finding.
3. `vars/vault-validation.yml`
   - inline `!vault |` value;
   - expected to load safely as a vars document without decryption.
4. `.env.validation`
   - non-YAML synthetic PAT-shaped value;
   - expected to prove repository-wide content scanning is not limited to
     YAML discovery.
5. `tasks/validation.yml`
   - unnamed task;
   - duplicate `mode` key;
   - bare boolean `when` condition;
   - password-handling task without `no_log: true`;
   - ordinary named task.
6. `tasks/main.yml`
   - a named `include_tasks: validation.yml` entry to exercise imports and
     ansible-lint's include behavior.

One initial low-entropy synthetic PAT-shaped string was not detected by
GitLeaks. It was replaced with a high-entropy synthetic string. This is an
important test-design lesson: a string matching only the prefix/length is not
guaranteed to exercise a secret scanner's complete rule.

### Raw GitLeaks verification

GitLeaks was executed directly before the combined scan. It detected the
invalid-YAML and non-YAML synthetic credentials, proving that those contents
were valid test inputs before AnsibleGuard path mapping was evaluated.

This raw run also exposed a compatibility issue: GitLeaks 8.30.1 warns that
`silent` is not a recognized log level. AnsibleGuard's invocation was changed
to `--log-level error`.

After increasing the valid-vars credential entropy, the combined scan found all
three expected secrets:

```text
.env.validation:2
vars/invalid-validation.yml:3
vars/validation-secrets.yml:3
```

### First mutated scan and structural results

The first mutated scan discovered 23 YAML files and structurally analyzed 11.
All controlled native findings were correct:

```text
tasks/validation.yml:3   unnamed-task
tasks/validation.yml:10  overriden-keys
tasks/validation.yml:18  credentials-leaking-in-log
tasks/validation.yml     missing-bool-filters
```

The invalid vars file was reported as `invalid/unknown`, while its GitLeaks
finding remained present. The inline-vault document was `parsed/vars`. The
`.env.validation` finding was represented as `non-yaml/not-applicable` in
`summary.csv` and appeared in JSON and SARIF.

### Real bug found: per-file ansible-lint duplication and lost locations

The first mutated result contained 75 ansible-lint findings. Investigation of
raw ansible-lint JSON showed two problems in AnsibleGuard:

1. Modern ansible-lint locations are nested under either
   `location.positions.begin.line` or `location.lines.begin`, but AnsibleGuard
   only checked `location.line`. Every lint annotation therefore fell back to
   line 1.
2. Running ansible-lint on every task file made `tasks/main.yml` follow
   `include_tasks`, after which `tasks/validation.yml` was linted again. Included
   findings were duplicated and sometimes attributed to the parent file.

The fix mirrors the GitLeaks architecture:

- ansible-lint runs once against the target;
- its result uses `ToolResult(completed|tool-error, findings, message)`;
- real nested line schemas are normalized by `lint_issue_line()`;
- reported paths are normalized by `lint_issue_path()`;
- findings are mapped back to their actual files;
- lint tool failure is added to `diagnostics.json` and the run's tool-error
  count;
- lint findings survive structural parse failure;
- `summary.csv` now has `ansible_lint_status`;
- missing binary, nested positions, nested lines, and parse-failure survival
  all have regression tests.

After this correction, the mutated ansible-lint count dropped from 75 to 68
before enabling lint load-failure findings for non-structural documents. The
remaining unusual offsets in the deliberately duplicate-key fixture are the
locations emitted by ansible-lint itself; AnsibleGuard now preserves the raw
tool locations instead of replacing them with line 1.

### Real behavior found: `.ansible` runtime cache

Ansible-lint created this cache/symlink inside the target clone:

```text
.ansible/roles/geerlingguy.apache -> /tmp/ansibleguard-validation-apache
```

That directory was untracked and was not part of the controlled mutation. To
prevent a later run from discovering cached role YAML or following a recursive
role layout, `.ansible` was added to `EXCLUDE_DIRS`. A regression test confirms
that YAML below `.ansible/roles/` is ignored.

### Corrected clean baseline

A detached clean worktree was created at the original commit:

```bash
git -C /tmp/ansibleguard-validation-apache worktree add --detach \
  /tmp/ansibleguard-validation-apache-clean \
  4a6c870f20f2410f252996d684aa10a4ce9c3661
```

The corrected target-level ansible-lint pipeline produced the same clean
baseline totals:

```text
72 findings: 63 warnings, 9 notes, 0 errors
```

This confirmed that the architecture change removed mutation-related duplicate
reporting without changing the established clean-role baseline.

### Final mutated result

Final output directory:

```text
/tmp/ansibleguard-validation-apache-mutated-final
```

Final run summary:

```text
23 YAML files discovered
11 structurally analyzed
gitleaks=completed
ansible-lint=completed
89 total findings
74 warnings
10 notes
5 errors
```

Corrected baseline-to-mutation rule delta:

| Rule | Baseline | Mutated | Delta |
|---|---:|---:|---:|
| `ansible-lint-issue` | 60 | 70 | +10 |
| `hardcoded-credentials` | 0 | 3 | +3 |
| `credentials-leaking-in-log` | 0 | 1 | +1 |
| `overriden-keys` | 0 | 1 | +1 |
| `missing-bool-filters` | 3 | 4 | +1 |
| `unnamed-task` | 1 | 2 | +1 |

The ten lint additions include validation-task lint results, the new include,
and the invalid-YAML load failure. The invalid file correctly has both:

```text
line 3: hardcoded-credentials (error)
line 5: ansible-lint load-failure (warning)
```

The native detector results point to the intended source lines, and all three
content-only findings are retained despite their three different file states:
valid vars, invalid YAML, and non-YAML.

### Final verification

The complete project test suite after all real-project fixes:

```text
126 passed in 16.19s
```

`git diff --check` also completed without whitespace errors.

At that stage, the public repository clone and injected synthetic files were
under `/tmp` and were not committed to AnsibleGuard. The following section
records their later recreation in the permanent workspace. The next step that
cannot be proven locally is pushing a dedicated fork and opening a real pull
request to validate GitHub SARIF permissions, annotations, alert closure,
artifact upload, and branch protection behavior.

## Permanent validation workspace — July 13, 2026

The `/tmp` validation above was useful for discovery, but `/tmp` can be removed
by the operating system. The entire experiment was therefore recreated under a
persistent workspace location so it can later be pushed to a fork and used for
GitHub annotation testing.

### Permanent directory layout

```text
/home/aymmzn/Documents/AnsibleChecklist/validation/
├── ansible-role-apache/          # permanent nested Git clone
│   ├── .git/
│   ├── tasks/validation.yml
│   ├── vars/validation-secrets.yml
│   ├── vars/invalid-validation.yml
│   ├── vars/vault-validation.yml
│   └── .env.validation
└── results/
    ├── baseline/                 # untouched upstream scan
    │   ├── summary.csv
    │   ├── findings.json
    │   ├── findings.sarif
    │   ├── diagnostics.json
    │   └── mirrored per-file reports
    └── mutated/                  # controlled validation branch scan
        ├── summary.csv
        ├── findings.json
        ├── findings.sarif
        ├── diagnostics.json
        └── mirrored per-file reports
```

`validation/` was added to the main AnsibleGuard `.gitignore`. This preserves
the clone and results on disk while preventing the nested repository, fake
credentials, and generated reports from accidentally being committed to the
AnsibleGuard repository.

The nested clone's local `.git/info/exclude` also contains `.ansible/`. This
hides ansible-lint's generated runtime cache from `git status` without changing
the upstream role's tracked `.gitignore` or the future validation PR.

### Permanent clone command

From the AnsibleGuard root:

```bash
mkdir -p validation/results
git clone --depth 1 \
  https://github.com/geerlingguy/ansible-role-apache.git \
  validation/ansible-role-apache
```

The permanent clone uses the same upstream revision and the controlled branch
is again named:

```text
ansibleguard-controlled-validation
```

### Permanent clean baseline command

The baseline was generated before creating the controlled branch changes:

```bash
PATH="$PWD/.venv/bin:$PATH" \
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local \
ANSIBLE_REMOTE_TEMP=/tmp/ansible-remote \
.venv/bin/ansibleguard \
  "$PWD/validation/ansible-role-apache" \
  -o "$PWD/validation/results/baseline" \
  --gitleaks-path /usr/bin/gitleaks \
  --fail-on never
```

Permanent baseline result:

```text
19 YAML files discovered
10 structurally analyzed
gitleaks=completed
ansible-lint=completed
73 findings: 64 warnings, 9 notes, 0 errors
```

This baseline has one more lint warning than the earlier intermediate `/tmp`
baseline because the finalized findings pipeline now retains ansible-lint's
metadata validation result even though `meta/main.yml` is not passed through
play/task structural detectors. The permanent baseline reflects the final code
and is the correct comparison source going forward.

### Permanent controlled branch and result

The branch was created with:

```bash
git -C validation/ansible-role-apache \
  switch -c ansibleguard-controlled-validation
```

The same six controlled changes described above were recreated exactly. The
mutated scan command was:

```bash
PATH="$PWD/.venv/bin:$PATH" \
ANSIBLE_LOCAL_TEMP=/tmp/ansible-local \
ANSIBLE_REMOTE_TEMP=/tmp/ansible-remote \
.venv/bin/ansibleguard \
  "$PWD/validation/ansible-role-apache" \
  -o "$PWD/validation/results/mutated" \
  --gitleaks-path /usr/bin/gitleaks \
  --fail-on never
```

Permanent mutated result:

```text
23 YAML files discovered
11 structurally analyzed
gitleaks=completed
ansible-lint=completed
89 findings: 74 warnings, 10 notes, 5 errors
```

Permanent baseline-to-mutation delta:

| Rule | Baseline | Mutated | Delta |
|---|---:|---:|---:|
| `ansible-lint-issue` | 61 | 70 | +9 |
| `hardcoded-credentials` | 0 | 3 | +3 |
| `credentials-leaking-in-log` | 0 | 1 | +1 |
| `overriden-keys` | 0 | 1 | +1 |
| `missing-bool-filters` | 3 | 4 | +1 |
| `unnamed-task` | 1 | 2 | +1 |

The persistent result retains all expected controlled behavior:

```text
tasks/validation.yml:3             unnamed-task
tasks/validation.yml:10            overriden-keys
tasks/validation.yml:18            credentials-leaking-in-log
tasks/validation.yml               missing-bool-filters
vars/invalid-validation.yml:3      hardcoded-credentials
vars/invalid-validation.yml:5      ansible-lint load-failure
vars/validation-secrets.yml:3      hardcoded-credentials
.env.validation:2                  hardcoded-credentials
```

`vars/vault-validation.yml` remains `parsed/vars` and produces no false
security finding. `diagnostics.json` contains the intentional YAML parse error
for `vars/invalid-validation.yml`.

### How to inspect the permanent setup

```bash
cd /home/aymmzn/Documents/AnsibleChecklist/validation/ansible-role-apache
git branch --show-current
git status
git diff
```

The main result files are permanently available at:

```text
/home/aymmzn/Documents/AnsibleChecklist/validation/results/baseline/summary.csv
/home/aymmzn/Documents/AnsibleChecklist/validation/results/baseline/findings.json
/home/aymmzn/Documents/AnsibleChecklist/validation/results/baseline/findings.sarif
/home/aymmzn/Documents/AnsibleChecklist/validation/results/mutated/summary.csv
/home/aymmzn/Documents/AnsibleChecklist/validation/results/mutated/findings.json
/home/aymmzn/Documents/AnsibleChecklist/validation/results/mutated/findings.sarif
/home/aymmzn/Documents/AnsibleChecklist/validation/results/mutated/diagnostics.json
```

These paths persist across restarts. The fake validation credentials remain
uncommitted in the nested clone until the dedicated GitHub fork/PR test is
prepared.

## GitHub SARIF repository setup — July 13, 2026

This section records the work performed to move from local validation to a
real GitHub pull request.

### Safe custom GitLeaks markers

Provider-shaped `ghp_...` test strings were removed before pushing. Even fake
provider tokens can trigger GitHub push protection or native Secret Scanning,
which would mix GitHub's own alerts with the AnsibleGuard SARIF test.

AnsibleGuard now detects and passes a target repository's `.gitleaks.toml`
explicitly using `--config`. The behavior works for directory targets and
single-file targets and has regression coverage.

The validation repository has this safe custom rule while retaining GitLeaks'
default rules:

```toml
title = "AnsibleGuard safe SARIF validation"

[extend]
useDefault = true

[[rules]]
id = "ansibleguard-test-secret"
description = "Synthetic AnsibleGuard validation marker"
regex = '''ANSIBLEGUARD_TEST_SECRET_[A-Z0-9]{24}'''
tags = ["test", "ansibleguard"]
```

The three committed test values now use the non-provider marker
`ANSIBLEGUARD_TEST_SECRET_...`. Raw GitLeaks validation found exactly three
`ansibleguard-test-secret` results in:

```text
.env.validation:2
vars/validation-secrets.yml:3
vars/invalid-validation.yml:3
```

The permanent mutated scan was regenerated and remained stable at 89 findings
and five errors. The project suite after target-local config support was:

```text
127 passed in 14.93s
```

### GitHub authentication and repositories

The existing GitHub CLI credential for `JedidiAymen` was expired. Browser
authentication was completed again, producing repository and workflow scopes,
and `gh auth setup-git` configured Git HTTPS credential usage.

The main AnsibleGuard checkout originally pointed to the private upstream:

```text
https://github.com/Narjes-b/AnsibleChecklist.git
```

A dedicated branch was created and committed locally:

```text
branch: sarif-validation-support
commit: 9553aec
message: Add resilient parsing and GitHub SARIF validation
```

A private fork was created and the tested branch pushed:

```text
https://github.com/JedidiAymen/AnsibleChecklist
https://github.com/JedidiAymen/AnsibleChecklist/tree/sarif-validation-support
```

The dedicated public validation repository was created at:

```text
https://github.com/JedidiAymen/ansibleguard-sarif-validation
```

The first clean push from the shallow role clone failed because GitHub did not
receive an older referenced object. `git fetch --unshallow origin` retrieved
the complete upstream history, after which the untouched Apache role was
successfully pushed as `main`.

The controlled files, custom GitLeaks rule, and validation workflow were
committed and pushed as:

```text
branch: ansibleguard-controlled-validation
commit: 0e837e0 (controlled findings)
commit: 31fef9f (standalone Python setup correction)
```

Pull request #1 is live:

```text
https://github.com/JedidiAymen/ansibleguard-sarif-validation/pull/1
```

The inherited Apache `CI`, `Release`, and `Close inactive issues` workflows
were disabled in this dedicated repository so Molecule and upstream release
automation do not obscure the SARIF test. Only `AnsibleGuard SARIF validation`
remains relevant.

### First GitHub workflow failure: inappropriate pip cache

Run `29237993627` failed during `actions/setup-python` because the validation
role has no `requirements.txt` or `pyproject.toml`, while `cache: pip` requires
one of those files. The pip cache option was removed and commit `31fef9f` was
pushed. This is specific to installing AnsibleGuard from another repository
rather than from the scanned repository itself.

### Second GitHub workflow failure: private cross-repository installation

Run `29238313686` progressed to the AnsibleGuard installation command:

```bash
pip install \
  "ansibleguard @ git+https://github.com/JedidiAymen/AnsibleChecklist.git@9553aec"
```

GitHub rejected the unauthenticated clone. Both the upstream AnsibleChecklist
repository and the `JedidiAymen/AnsibleChecklist` fork are private. The
validation repository is public, and its built-in `GITHUB_TOKEN` is scoped to
that validation repository; it cannot read another private repository.

No broad personal OAuth token was copied into repository secrets
automatically. The safe ways forward are:

1. add a read-only deploy key dedicated to the private AnsibleGuard fork and
   store only its private half as a validation-repository Actions secret; or
2. publish AnsibleGuard in a separate public repository/package, if making the
   source public is intended.

The least-privilege recommendation is option 1. Once access is configured, the
workflow can install commit `9553aec`, run the scanner, upload SARIF and the
artifact, and finally reach the intentionally failing five-error enforcement
step.

## Plain-language team handoff — what we are doing and why

This section explains the GitHub work for team members who are not yet
familiar with branches, forks, pull requests, or GitHub Actions.

### The final goal

The goal is to prove that AnsibleGuard works in a real GitHub pull request,
not only on one developer's computer. When somebody changes an Ansible file,
GitHub should automatically:

1. install AnsibleGuard;
2. scan every relevant file, including valid YAML, invalid YAML, vars files,
   vault files, and non-YAML files that GitLeaks can inspect;
3. create `findings.sarif` and the other permanent result files;
4. upload the SARIF report to GitHub code scanning;
5. show findings on the pull request at the affected files and lines; and
6. fail the final policy check when findings at the configured severity are
   present.

The last failure in step 6 is expected for the controlled validation branch.
It means the scanner found the five errors that we deliberately inserted. A
failure during installation is different: it means the test never reached the
scanner and therefore proves nothing about SARIF annotations.

### Why there are two repositories

There are two separate jobs, so there are two repositories:

```text
Private AnsibleGuard repository
  JedidiAymen/AnsibleChecklist
  Contains the scanner source code that GitHub Actions must install.

Public validation repository
  JedidiAymen/ansibleguard-sarif-validation
  Contains the Apache Ansible role, controlled test changes, workflow,
  pull request, and GitHub code-scanning results.
```

Keeping the validation repository separate gives the team a realistic target:
AnsibleGuard is installed as a tool and scans another project. It also keeps
intentional invalid YAML and synthetic secrets out of the scanner's own source
tree.

### What a fork means here

A fork is a GitHub copy of another repository under a different account. The
original AnsibleGuard repository belongs to `Narjes-b`; the working fork
belongs to `JedidiAymen`.

```text
Original: Narjes-b/AnsibleChecklist
Working fork: JedidiAymen/AnsibleChecklist
```

The fork lets us push and test the AnsibleGuard changes without changing the
team's original repository immediately. Later, after the work is reviewed, a
pull request can propose those changes back to the original repository. A
fork is not a temporary folder and it is not the test result; it is a real
GitHub repository with its own branches and permissions.

### What a branch and pull request mean

A branch is a separate line of changes inside a repository. The validation
repository currently uses:

```text
main
  Clean Apache role used as the starting point.

ansibleguard-controlled-validation
  Apache role plus deliberate findings and the AnsibleGuard workflow.
```

Pull request #1 asks GitHub to compare the controlled branch with `main`. This
comparison is the page where the team expects the workflow check and SARIF
annotations to appear. Opening a pull request does not immediately merge or
publish its changes into `main`; it creates a review and test area first.

### What GitHub Actions is doing

GitHub Actions is a clean computer started by GitHub for the workflow. It does
not automatically have the files, Python packages, login session, or private
repository access from the developer's computer. The workflow must explicitly
check out the validation repository, install Python, install AnsibleGuard, run
the scan, and upload the reports.

This explains why the local scan can succeed while the GitHub workflow can
still fail during setup. They run in different environments with different
credentials.

### What failed and what it means

The first run failed because Python package caching was enabled even though
the Apache role has no Python dependency file. Removing that cache setting
fixed the first setup problem.

The second run reached the AnsibleGuard installation step but could not clone
the private `JedidiAymen/AnsibleChecklist` repository. The validation
repository's automatic `GITHUB_TOKEN` only has access to the validation
repository. GitHub intentionally does not allow that token to read an
unrelated private repository.

Therefore, the current problem is not YAML parsing, GitLeaks, SARIF generation,
or the controlled findings. It is only private cross-repository authentication:

```text
GitHub Actions in the public validation repository
        needs read-only access to
the private AnsibleGuard working fork
```

### Why a read-only deploy key is recommended

A deploy key is a dedicated SSH key that gives one automated workflow access
to one repository. It has two halves:

- the public half is registered on the private AnsibleGuard fork with
  read-only access;
- the private half is stored as an encrypted GitHub Actions secret in the
  validation repository.

The workflow can then read and install AnsibleGuard, but the key cannot write
changes to it. This is safer than storing a developer's broad personal access
token, which could grant access to several repositories or account actions.
The key itself must never be committed to either Git repository or written in
this Markdown log.

### Current status

Completed:

- resilient document classification and parsing;
- GitLeaks coverage even when YAML is invalid;
- target-local `.gitleaks.toml` support;
- structured external-tool results and honest summaries;
- repository-relative SARIF paths and fingerprints;
- GitHub workflow files and automated tests;
- permanent baseline and mutated local results;
- safe synthetic secret markers;
- public validation repository, controlled branch, and pull request;
- diagnosis and correction of the first workflow setup failure; and
- documentation of every material action performed in this session.

Still required:

1. commit and push the latest target-local GitLeaks configuration support and
   documentation from the AnsibleGuard working branch;
2. update the validation workflow to install that newest exact commit;
3. create the dedicated SSH key pair without committing either key;
4. register its public half as a read-only deploy key on the private fork;
5. store its private half as an encrypted Actions secret in the validation
   repository;
6. update and rerun the workflow using SSH authentication;
7. confirm that the scan produces the expected five errors;
8. inspect the GitHub pull-request annotations, code-scanning result, SARIF
   upload, and downloadable result artifact; and
9. record the final run links, commit IDs, result counts, and any corrections
   in this file.

At this point in the session the exact key commands had not yet been executed.
The following section records the procedure prepared in the next chat. No
private key value will ever be added to this file.

## Planned deploy-key procedure — explained step by step

This procedure was prepared on July 13, 2026 from GitHub's current deploy-key,
Actions-secret, and SSH host-key documentation. It records what will be done;
no key has been generated or registered yet.

### Important idea: there are two different keys

Running `ssh-keygen` creates a matching pair:

```text
ansibleguard-actions-readonly.pub   Public key: safe to give to GitHub
ansibleguard-actions-readonly       Private key: secret; never commit or print
```

The public key is a lock that is attached to the private AnsibleGuard
repository. The private key is what lets the validation workflow open that
lock. A person who only sees the public key cannot use it to enter the private
repository.

### Step 1: finish the AnsibleGuard source commit first

The workflow currently installs commit `9553aec`, but additional tested work
for target-local `.gitleaks.toml` support and documentation exists after that
commit. Before configuring SSH access, the team will:

1. inspect the AnsibleGuard working tree and diff;
2. run the complete test suite again;
3. commit only the intended scanner, test, and documentation changes;
4. push `sarif-validation-support` to
   `JedidiAymen/AnsibleChecklist`; and
5. record the new full commit hash.

The workflow must be pinned to this new hash. Pinning means that every run
installs one known version instead of silently changing when a branch moves.

### Step 2: generate one new dedicated key pair

The key will be created in a private, ignored directory outside the nested
Apache repository:

```bash
mkdir -p /home/aymmzn/Documents/AnsibleChecklist/validation/private
chmod 700 /home/aymmzn/Documents/AnsibleChecklist/validation/private
ssh-keygen \
  -t ed25519 \
  -C "ansibleguard-actions-readonly" \
  -N "" \
  -f /home/aymmzn/Documents/AnsibleChecklist/validation/private/ansibleguard-actions-readonly
```

Explanation of the options:

- `-t ed25519` creates a modern Ed25519 SSH key;
- `-C` adds a recognizable label, not a password;
- `-N ""` creates it without a passphrase because the non-interactive GitHub
  runner cannot stop and type one; and
- `-f` uses an explicit unique filename so no existing personal SSH key can be
  overwritten.

The `validation/` directory is already ignored by the main AnsibleGuard
repository, and this location is outside the nested validation Git repository.
Before generation, we will still verify that neither destination file already
exists. We will not use `~/.ssh/id_ed25519` and will not reuse a personal key.

### Step 3: add only the public key to the private fork

The destination is the repository that must be read:

```text
JedidiAymen/AnsibleChecklist
```

In the GitHub web interface:

1. open `JedidiAymen/AnsibleChecklist`;
2. open **Settings**;
3. select **Deploy keys**;
4. click **Add deploy key**;
5. use the title `ansibleguard-sarif-validation-readonly`;
6. paste the contents of `ansibleguard-actions-readonly.pub`;
7. leave **Allow write access** unchecked; and
8. add the key.

We can perform the same operation with GitHub CLI after reviewing the public
key:

```bash
gh repo deploy-key add \
  /home/aymmzn/Documents/AnsibleChecklist/validation/private/ansibleguard-actions-readonly.pub \
  --repo JedidiAymen/AnsibleChecklist \
  --title ansibleguard-sarif-validation-readonly
```

The command intentionally omits `--allow-write`, so the key remains read-only.
Only the `.pub` file is sent in this step. The private file must never be
passed to `gh repo deploy-key add`.

One deploy key belongs to one repository. This dedicated pair must not be
reused for another repository.

### Step 4: put the private key into the validation repository's secret store

The destination is now the repository that runs the workflow:

```text
JedidiAymen/ansibleguard-sarif-validation
```

The repository-level Actions secret will be called
`ANSIBLEGUARD_DEPLOY_KEY`. GitHub CLI can encrypt and upload it directly from
the private-key file:

```bash
gh secret set ANSIBLEGUARD_DEPLOY_KEY \
  --repo JedidiAymen/ansibleguard-sarif-validation \
  --app actions \
  < /home/aymmzn/Documents/AnsibleChecklist/validation/private/ansibleguard-actions-readonly
```

GitHub stores the secret encrypted. The secret's value cannot be read back
through the web interface or CLI after it is saved. The team can verify the
secret name and update time, but not reveal its value:

```bash
gh secret list --repo JedidiAymen/ansibleguard-sarif-validation --app actions
```

This secret is added to the public validation repository, but it is not public
repository content. It must never be placed in the workflow YAML, a commit, a
Markdown file, an issue, a pull-request comment, or a command argument that
would display it.

### Step 5: update the workflow to use the secret safely

The HTTPS installation that failed will be replaced with an SSH installation.
The intended workflow step has this shape, with `NEW_COMMIT_HASH` replaced by
the full hash created in step 1:

```yaml
- name: Install pinned AnsibleGuard
  env:
    ANSIBLEGUARD_DEPLOY_KEY: ${{ secrets.ANSIBLEGUARD_DEPLOY_KEY }}
  run: |
    install -m 700 -d "$HOME/.ssh"
    printf '%s\n' "$ANSIBLEGUARD_DEPLOY_KEY" > "$HOME/.ssh/ansibleguard_deploy_key"
    chmod 600 "$HOME/.ssh/ansibleguard_deploy_key"
    printf '%s\n' \
      'github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl' \
      > "$HOME/.ssh/known_hosts"
    GIT_SSH_COMMAND="ssh -i $HOME/.ssh/ansibleguard_deploy_key -o IdentitiesOnly=yes" \
      pip install \
      "ansibleguard @ git+ssh://git@github.com/JedidiAymen/AnsibleChecklist.git@NEW_COMMIT_HASH"
```

This step does the following on GitHub's temporary runner:

1. creates an SSH directory with restricted permissions;
2. writes the encrypted Actions secret into a temporary key file;
3. limits the private file so only the current runner user can read it;
4. trusts GitHub's published Ed25519 host key, which protects against
   connecting to an impersonated server;
5. tells Git to use only the dedicated deploy key; and
6. installs the exact reviewed AnsibleGuard commit through SSH.

The workflow does not print the key. The runner is destroyed by GitHub after
the job, so its temporary copy disappears. The official published GitHub host
key is written explicitly instead of accepting an unverified key returned by
the network at runtime.

### Step 6: commit and push the validation workflow

The workflow change will be committed on:

```text
ansibleguard-controlled-validation
```

and pushed to the existing pull request. That push automatically starts a new
GitHub Actions run. Because pull request #1 comes from a branch in the same
validation repository, the repository secret is available to it. GitHub does
not normally pass Actions secrets to pull requests originating from an
untrusted external fork; that restriction is useful and should not be
disabled.

### Step 7: understand the expected workflow result

The expected order is:

```text
Checkout validation role
  -> Install Python
  -> Authenticate to private AnsibleGuard fork
  -> Install pinned AnsibleGuard
  -> Install GitLeaks
  -> Scan controlled files
  -> Upload SARIF
  -> Upload complete result artifact
  -> Enforce policy and fail because five intentional errors exist
```

Success does not mean that every workflow step is green. For this controlled
branch, the final policy step should be red because five error findings were
deliberately added. Installation, scanning, SARIF upload, and artifact upload
must succeed before that expected red policy result.

### Step 8: verify GitHub, not only the terminal output

The team will check all of the following:

- the installation step authenticated successfully;
- the summary reports 89 findings and five errors, or any intentional updated
  count is explained;
- no external tool is reported as a tool error;
- `findings.sarif` uploads successfully;
- GitHub code scanning shows the expected repository-relative file paths;
- pull-request annotations point to the intended lines;
- the complete `ansibleguard-controlled-results` artifact is downloadable;
- the final failure comes only from the five-error enforcement step; and
- no key material appears in logs, artifacts, commits, or result files.

The workflow run URL, final source and validation commit hashes, counts, and
any necessary corrections will then be added to this implementation log.

### Step 9: local key cleanup and future rotation

After the GitHub secret has been verified and the workflow works, the local
private-key file is no longer needed. It should be deleted from
`validation/private/` rather than kept beside project data. This cleanup does
not remove the GitHub deploy key or encrypted Actions secret and does not
remove any validation result. It only removes the extra local copy of the
credential.

If the key is ever exposed, the response is:

1. remove the deploy key from `JedidiAymen/AnsibleChecklist` immediately;
2. delete or replace `ANSIBLEGUARD_DEPLOY_KEY` in the validation repository;
3. generate a completely new key pair; and
4. repeat the registration steps.

Deploy keys do not expire automatically, so the team should remove this one
when the validation integration is no longer used.

Official references used for this procedure:

- [Managing deploy keys](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys)
- [Using secrets in GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets)
- [GitHub SSH key fingerprints](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)
- [REST API endpoints for deploy keys](https://docs.github.com/en/rest/deploy-keys/deploy-keys)
