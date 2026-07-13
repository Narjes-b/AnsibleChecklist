# Parsing, GitLeaks, and GitHub PR Integration

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
to pull-request lines. Each result now also receives a stable SHA-256
`partialFingerprints.primaryLocationLineHash`, derived from rule, path, line,
and message. This helps GitHub match the same alert across repeated scans.

The placeholder tool information URL was replaced, and SARIF tests now confirm
that every result contains a 64-character fingerprint.

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
