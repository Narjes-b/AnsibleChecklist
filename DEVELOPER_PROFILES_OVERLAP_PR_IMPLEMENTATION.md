# Developer profiles, overlap, PR, and dependency implementation

## What changed

This work turns AnsibleGuard from one large scan into an explicit,
auditable set of developer workflows. It also keeps native ansible-lint and
GitLeaks evidence instead of hiding it behind AnsibleGuard rule names.

The main design is:

1. Run only the providers requested by the selected profile.
2. Save every provider result in `findings.raw.json`.
3. Group results about the same physical problem in `occurrences.json`.
4. Keep the provider and native rule identity inside every group.
5. Use canonical occurrences for SARIF and pull-request comparison.

No detector result is deleted merely because another tool reports the same
concept.

## Profiles

| Profile | Providers | Intended use |
|---|---|---|
| `developer-fast` | AnsibleGuard | Quick local security, correctness, and reliability feedback |
| `security` | AnsibleGuard, selected ansible-lint security rules, GitLeaks | Security review |
| `lint` | ansible-lint | Native lint output only |
| `quality` | AnsibleGuard | Maintainability, correctness, structure, dependencies, and testing |
| `pr` | AnsibleGuard, ansible-lint, GitLeaks | Stable base/head PR comparison without review-metadata rules |
| `technical-full` | All three providers | Complete technical and Git review scan |
| `review-range` | AnsibleGuard | Git/base-to-head review metadata only |
| research profiles | AnsibleGuard | Existing controlled research populations |

Examples:

```bash
ansibleguard . --profile developer-fast -o results-fast
ansibleguard . --profile security -o results-security
ansibleguard . --profile lint -o results-lint
ansibleguard . --profile quality -o results-quality
```

The selected providers, native ansible-lint allowlist, rule IDs, and rule-set
hash are recorded in `run_metadata.json`.

## How ansible-lint and AnsibleGuard remain distinguishable

Each raw finding now includes:

- `provider`: `ansibleguard`, `ansible-lint`, or `gitleaks`;
- `native_rule_id`: the provider's original rule name;
- `concept_id`: the shared problem represented by possibly different rules;
- `finding_id`: a stable hash of the raw finding;
- native severity, categories, fingerprint, and help URL when supplied.

Therefore a developer can see both:

```text
ansible-lint/yaml[key-duplicates]
ansibleguard/overriden-keys
```

while `occurrences.json` says that both detectors contributed to one
`duplicate-mapping-key` occurrence. SARIF uses that canonical occurrence so a
PR does not receive two annotations for one line.

## Decisions for substantial and partial overlap

The decisions are machine-readable in
`src/ansibleguard/report/overlap.py`.

| Concept | Decision |
|---|---|
| Duplicate mapping keys | ansible-lint is canonical. The internal detector is retained as shadow/comparison evidence, not removed. This justifies keeping it for environments where ansible-lint is unavailable and for detector evaluation. |
| Deprecated modules | ansible-lint is canonical for its known set. AnsibleGuard augments it with installed `ansible-doc` deprecation metadata and replacement evidence. |
| Shell instead of module | Both results remain. AnsibleGuard is canonical because it supplies command-to-module migration advice. |
| Credential log exposure | Both results remain. AnsibleGuard is canonical because its scope is broader than ansible-lint's password-loop rule. |
| Silent failure suppression | Both results remain. AnsibleGuard is canonical because it checks `ignore_errors`, `failed_when: false`, and whether a registered result is actually inspected later. |

This policy can be changed later without changing the raw evidence.

## Deprecated modules are now dynamic

AnsibleGuard now asks the installed Ansible environment for module
documentation through `ansible-doc`. If that metadata marks a module as
deprecated, the finding records that installed metadata was the source.

A small curated fallback remains for removed modules that the installed
version may no longer document. Legacy short names and redirected modules are
reported separately as `redirected-module`; they are no longer incorrectly
called deprecated.

Limitation: the answer reflects the Ansible and collections installed on the
machine performing the scan. `run_metadata.json` records external-tool
versions/configuration, but reproducible CI should also install dependencies
from a reviewed lock or constraints file.

## Credential logging

The credential-log detector now:

- analyzes structured module arguments instead of matching task names;
- recognizes password, token, API/access key, client secret, credential, and
  private-key names;
- recognizes sensitive Jinja variable references in display modules;
- handles tasks inside `block`, `rescue`, and `always`;
- inherits `no_log` from play/block scope;
- distinguishes literal `no_log: true` from a dynamic value that cannot be
  proven safe;
- never writes the secret value to its finding message.

GitLeaks and credential-log exposure remain separate concepts. GitLeaks proves
that secret-like material exists in source/history; the AnsibleGuard rule
proves that a task may expose a sensitive value at runtime. Combining those
into one finding would lose this important distinction.

The legacy GitLeaks report is now allowlisted and excludes `Secret` and
`Match`. GitLeaks is invoked with `--redact=100`.

## Permissions and file safety

Permission checks now include:

- setuid and setgid bits;
- world-writable files;
- world-writable directories without the sticky bit;
- private keys readable by group or other users;
- sensitive files readable by other users;
- symbolic modes that grant write access to others.

The separate `unsafe-file-write` rule detects `unsafe_writes: true`, which
disables Ansible's atomic replacement behavior.

## Vars, group_vars, requirements, and meta

File-kind checks run even when a YAML document is correctly classified as a
variable or metadata file rather than a playbook.

They now detect:

- plaintext sensitive literals in `vars`, `defaults`, `group_vars`,
  `host_vars`, and `env_vars`;
- unpinned roles/collections in recognized requirements files;
- unpinned external role dependencies in `roles/*/meta/main.yml`;
- the same role variable defined in both `defaults/main` and `vars/main`.

Vault values, Jinja lookups, and ordinary local role dependencies are excluded
from these new checks. Meta schema correctness continues to come from
ansible-lint.

## Pull-request behavior

The workflow scans the PR head and a detached worktree at the base commit with
the `pr` profile. It then compares `occurrences.json` and classifies findings
as:

- `unchanged`;
- `moved` by a provider fingerprint or semantic identity;
- `introduced`;
- `fixed`;
- `uncertain` when non-secret detector evidence matches but movement cannot
  be proven.

GitLeaks also scans the validated full-hex `base..head` commit range. History
and directory findings have different `scan_mode` values and cannot be
silently merged.

Two policies exist:

- `observe`: block only an introduced `hardcoded-secret`;
- `ratchet`: also block every introduced error-severity occurrence.

Changed secret fingerprints are never downgraded to `uncertain`; they remain
introduced and therefore block in `observe` mode.

The workflow starts with `observe` to collect a trustworthy baseline. Change
`--policy observe` to `--policy ratchet` after reviewing uncertain matches and
baseline noise. External-tool failures block in both modes. Fork PRs retain
artifacts but skip SARIF upload when the repository token cannot safely write
security events.

## Dependency and tool provenance

Python dependencies now have deliberate compatible ranges instead of being
unbounded. Packages tied closely to current detector behavior remain exactly
pinned where appropriate.

GitLeaks installation is hardened by:

- a pinned GitLeaks version;
- a pinned SHA-256 for every supported archive;
- checksum verification before extraction;
- archive path validation;
- rejection of tar links.

Ansible-lint runs from the scanned project root, so its local configuration
and relative paths behave normally. `run_metadata.json` records tool version,
executable, working directory, target, configuration path, and configuration
hash where available.

`requirements.txt` remains a historical environment snapshot. `pyproject.toml`
is the maintained install contract. A future release process should generate
and review a platform-specific lock/constraints file rather than hand-editing
the snapshot.

## Outputs

The later output-contract v2 implementation organizes these artifacts under
`summary/`, `raw/`, `canonical/`, `metadata/`, and `legacy/`. See
`OUTPUT_CONTRACT_V2_SIX_CHANGES.md` for the complete six-change design and
compatibility policy.

| File | Purpose |
|---|---|
| `findings.raw.json` | Lossless normalized detector findings with provider identity |
| `findings.json` | Backward-compatible alias of the raw normalized findings |
| `occurrences.json` | Canonical grouped problems with all contributing detectors |
| `findings.sarif` | Canonical occurrences for GitHub annotations |
| `run_metadata.json` | Profile, provider, configuration, version, and hash provenance |
| `diagnostics.json` | Parse failures and external-tool failures |

CSV and text output also include provider, native rule, and shared concept
fields.

## Complete session implementation record

This section records the changes file by file. It is intended as a handoff for
a developer who did not participate in the design discussion.

### 1. Profile model

Changed file: `src/ansibleguard/profiles.py`

Before this work, profiles were mainly research-oriented rule allowlists.
They did not fully express which analysis provider was allowed to run.

The profile definition now contains both:

- a set of AnsibleGuard rule IDs;
- a set of providers: `internal`, `ansible-lint`, and/or `gitleaks`.

`provider_enabled()` gives the CLI one place to decide whether a provider
should execute. `filter_profile_findings()` checks both provider and rule
membership. For the `security` profile, it additionally filters native
ansible-lint rules to:

- `no-log-password`;
- `no-same-owner`;
- `risky-file-permissions`;
- `risky-octal`.

This matters because selecting a profile now saves execution time as well as
filtering output. For example, `lint` does not execute internal structural
detectors or GitLeaks, and `developer-fast` does not start either external
tool.

The existing research profile families and their disjoint validation were
kept. The new operational profiles do not alter the frozen research
populations.

### 2. CLI execution and rollups

Changed file: `src/ansibleguard/cli.py`

The CLI now:

1. reads the selected profile;
2. runs only its requested providers;
3. still normalizes ansible-lint results when internal source analysis is
   disabled;
4. runs file-kind checks on variable, metadata, empty, or otherwise
   structurally skipped YAML;
5. performs project-level role variable collision checks;
6. optionally adds a GitLeaks `base..head` history scan when both PR SHA
   environment variables exist;
7. records provider details in `run_metadata.json`;
8. writes raw findings and canonical occurrences;
9. sends canonical occurrences, rather than duplicate raw findings, to SARIF.

The two GitLeaks scans are combined only at the raw-result layer. Each finding
keeps `scan_mode: dir` or `scan_mode: git-range`, so the occurrence builder and
PR comparator do not mistake working-tree evidence for commit-history
evidence.

### 3. Finding identity and provider provenance

Changed file: `src/ansibleguard/report/findings.py`

The normalized finding schema was extended without deleting the old fields.
The original `file`, `line`, `rule_id`, `severity`, and `message` fields remain
available to existing consumers.

New fields include:

| Field | Meaning |
|---|---|
| `provider` | Tool that produced the evidence |
| `native_rule_id` | Original provider rule, such as `yaml[key-duplicates]` |
| `concept_id` | Shared cross-provider concept |
| `native_severity` | Provider severity before AnsibleGuard normalization |
| `native_categories` | Provider categories when available |
| `native_fingerprint` | Stable evidence identity supplied by a provider |
| `help_url` | Provider documentation link when supplied |
| `scan_mode` | Source/tree/history origin |
| `finding_id` | Stable hash identifying the raw finding |

Cross-provider concept mappings were added for duplicate keys, module
deprecation, command-to-module migration, credential-log exposure, and
failure suppression.

Five public rules were added to the catalog, increasing the active catalog
from 60 to 65 rules:

- `redirected-module`;
- `unsafe-file-write`;
- `plaintext-sensitive-variable`;
- `unpinned-ansible-dependency`;
- `role-variable-precedence-collision`.

### 4. Raw findings versus canonical occurrences

New files:

- `src/ansibleguard/report/overlap.py`;
- `src/ansibleguard/report/occurrences.py`.

`overlap.py` is the policy table. It says which provider is canonical and why,
but it does not discard the other provider.

`occurrences.py` groups raw findings using concept, normalized path, line, and
scan mode. Each occurrence contains:

- one canonical message/provider for developer display;
- the highest contributing severity;
- every native provider/rule that detected it;
- all available native fingerprints;
- all contributing raw detector identities;
- a semantic key;
- a stable occurrence ID.

The semantic key includes the concept, file, scan mode, normalized message,
native rules, and evidence fingerprints. This prevents a changed secret on
the same source line from being incorrectly considered unchanged.

### 5. Text, CSV, and SARIF writers

Changed files:

- `src/ansibleguard/report/text_writer.py`;
- `src/ansibleguard/report/csv_writer.py`;
- `src/ansibleguard/report/sarif_writer.py`.

Text output now displays `provider/native-rule` and the shared concept when it
differs. CSV gained provider, native-rule, concept, native-severity, and
finding-ID columns.

SARIF can create rules dynamically for canonical concepts. Each SARIF result
includes provider/native/concept properties and the contributing detector
list. The PR interface therefore receives one annotation for a grouped
occurrence while JSON still proves exactly which tools reported it.

The legacy `gitleaks.txt` writer now uses a safe-field allowlist. It retains
useful location/rule/fingerprint data and removes raw `Secret` and `Match`
content. Lowercase `rule` and `file` aliases remain supported for backward
compatibility.

### 6. ansible-lint adapter

Changed file: `src/ansibleguard/external/ansible_lint.py`

ansible-lint now executes with the scanned project as its working directory
and uses a relative target. This allows its normal configuration discovery,
role resolution, and relative paths to work as expected.

The adapter records:

- installed ansible-lint version;
- executable;
- working directory;
- relative target;
- output format;
- discovered configuration path;
- SHA-256 of the configuration.

Native `check_name`, severity, categories, fingerprint, and URL are preserved
when ansible-lint supplies them.

### 7. GitLeaks adapter and installer

Changed files:

- `src/ansibleguard/external/gitleaks.py`;
- `src/ansibleguard/external/install_gitleaks.py`.

The directory scan now uses the current `gitleaks dir` command and requests
full redaction. A second function scans Git history with `gitleaks git` and
`--log-opts base..head`.

Only full hexadecimal 40-to-64-character revisions are accepted by the
history wrapper. This avoids passing arbitrary revision expressions from an
untrusted environment into the tool command.

Both modes record configuration paths and hashes. Findings are tagged with
their scan mode before normalization.

The installer remains on GitLeaks `8.30.1`, but the downloaded archive is now
trusted only after its platform-specific SHA-256 matches. Extraction rejects:

- paths that escape the installation directory;
- tar symbolic links;
- tar hard links;
- platforms or archives without a reviewed hash.

This protects the installation path from a corrupted or replaced release
archive.

### 8. Dynamic deprecated-module handling

Changed files:

- `src/ansibleguard/detectors/deprecated_modules.py`;
- `src/ansibleguard/parser.py`;
- `src/ansibleguard/smells.py`.

For every unique module, the detector reuses the cached `ansible-doc` adapter
already present in the project. Installed deprecation metadata takes
precedence. A conservative fallback remains because modules removed from the
installed Ansible version may no longer have local documentation.

The former mixed list was split:

- true deprecated modules produce `deprecated-modules`;
- legacy redirects or short names produce `redirected-module`.

Parser metrics, smell assessment, finding normalization, and the catalog were
all wired for the new redirected-module result.

### 9. Credential-log detector

Changed file:
`src/ansibleguard/detectors/credentials_leaking_in_log.py`

The former detector focused heavily on loops and broad text matching. The new
logic walks structured tasks and nested values.

For each task it:

1. identifies real module arguments rather than using the task name;
2. finds sensitive argument paths and sensitive Jinja references;
3. checks explicit or inherited `no_log`;
4. treats literal true values as protected;
5. treats false/missing values as exposed;
6. reports dynamic `no_log` as not proven safe;
7. emits variable names and paths, never values.

This extends ansible-lint's useful `no-log-password` idea beyond password
loops. It uses a wider sensitive-name vocabulary, but it does not pretend that
GitLeaks and log exposure are the same problem: GitLeaks detects committed
secret material, while this detector analyzes runtime logging risk.

### 10. Permissions, unsafe writes, and silent failures

Changed file: `src/ansibleguard/detectors/review_checklist.py`

Numeric modes are parsed as octal and evaluated with permission bits.
Symbolic write grants are also checked. The new cases are documented in the
earlier permissions section.

`unsafe_writes: true` became its own rule because it is a reliability and
atomicity issue, not simply another Unix permission mode.

The silent-error rule was kept, but its justification became stronger:

- `ignore_errors: true` is checked;
- `failed_when: false` is checked;
- `register` alone is no longer considered recovery;
- the registered result must be referenced in a later task to avoid the
  finding.

This is deliberately broader than ansible-lint's `ignore-errors` rule while
remaining transparent about its static-analysis limitation.

### 11. File-kind-aware analysis

New file: `src/ansibleguard/detectors/file_kinds.py`

Changed integration files:

- `src/ansibleguard/parser.py`;
- `src/ansibleguard/cli.py`;
- `src/ansibleguard/report/findings.py`.

The detectors use the existing document classifier, so a vars file does not
need to look like a playbook before it can be checked.

Plaintext-sensitive-variable findings record only the variable path. Values
are never copied into reports. Empty values, Jinja expressions, and Vault
content are excluded.

Dependency checks understand list and mapping forms in requirements files.
Role metadata also checks external Galaxy-style dependencies, but a short
local sibling-role name is intentionally not called unpinned.

Role precedence collision analysis compares `defaults/main.yml|yaml` with
`vars/main.yml|yaml`. A collision is reported because role vars have much
higher precedence and can make a normal role default impossible for a caller
to override.

### 12. Pull-request comparator and workflow

New files:

- `src/ansibleguard/report/comparison.py`;
- `scripts/compare_pr_results.py`.

Changed file:

- `.github/workflows/ansibleguard.yml`.

The comparator proceeds conservatively:

1. match identical occurrence IDs;
2. match a unique shared native fingerprint;
3. match a unique semantic identity;
4. classify a unique same-file detector shape as uncertain;
5. leave remaining head findings introduced and base findings fixed.

Hardcoded secrets never use the uncertain detector-shape fallback. A changed
secret must remain introduced unless a stable identity proves otherwise.

The comparison script writes both the classification and policy decision as
JSON, and returns non-zero when the selected policy fails.

For a pull request, the workflow:

1. checks out full history;
2. installs AnsibleGuard and the verified GitLeaks binary;
3. scans the head with the `pr` profile and the base/head SHAs;
4. creates a detached base worktree;
5. scans that base with the same `pr` profile;
6. compares base and head occurrences in `observe` mode;
7. publishes a readable summary;
8. uploads canonical head SARIF when permissions allow;
9. uploads head, base, and decision artifacts;
10. blocks external-tool failures or a failing PR policy.

Push scans retain the existing full error policy through
`technical-full`. The workflow does not give fork PRs a writable SARIF upload
path.

### 13. Dependency contract

Changed file: `pyproject.toml`

Previously unbounded dependencies now use compatible ranges:

```text
PyYAML >=6.0,<7
regex >=2024.11,<2027
pandas >=2.2,<4
spaCy >=3.8,<4
NLTK >=3.9,<4
ansible-lint >=26.4,<27
ansible-compat >=26.3,<27
requests >=2.32,<3
pytest >=8,<10
jsonschema >=4.23,<5
```

`ruamel.yaml==0.19.1` and `ansiblemetrics==0.4.2` remain exact because current
parser/detector behavior is tied more closely to them.

These ranges prevent completely unreviewed future major versions while still
allowing compatible fixes. This session did not invent a universal lock file,
because one generated on a single machine can incorrectly claim portability.
A reviewed constraints/lock process remains the next dependency-reproducibility
step.

### 14. Tests added or expanded

New test files:

- `tests/test_developer_profiles.py`;
- `tests/test_file_kind_checks.py`;
- `tests/test_install_gitleaks.py`;
- `tests/test_occurrences.py`;
- `tests/test_pr_comparison.py`.

Expanded test files:

- `tests/test_ansible_lint.py`;
- `tests/test_cli_statuses.py`;
- `tests/test_credentials_leaking_in_log.py`;
- `tests/test_gitleaks_hardcoded_credentials.py`;
- `tests/test_review_checklist.py`.

The tests cover:

- provider execution and filtering for profiles;
- preservation of native ansible-lint identity;
- canonical grouping without losing either detector;
- occurrence identity changes when secret evidence changes;
- exact, moved, introduced, fixed, and uncertain PR classification;
- observe versus ratchet behavior;
- changed-secret blocking;
- GitLeaks directory/history scan-mode separation;
- validated revision ranges;
- report redaction;
- installer checksum rejection;
- project-root ansible-lint execution;
- credential false-positive reduction and inherited `no_log`;
- expanded permission and unsafe-write cases;
- stronger silent-error behavior;
- vars, Vault, requirements, role meta, and precedence checks.

### 15. Documentation changed in this session

Changed file: `README.md`

The README now lists 65 rules, the operational profiles, raw/canonical output
files, the updated CLI profile choices, and the final test result. It links to
this document.

New file: `DEVELOPER_PROFILES_OVERLAP_PR_IMPLEMENTATION.md`

This is the detailed session record.

The working tree already contained changes to
`ANSIBLE_LINT_GITLEAKS_OVERLAP.md` and the untracked drafts
`ARTICLE_APPROACH_TOOL_BUILD_TESTING_PERFORMANCE.md` and
`PULL_REQUEST_PROFILES_AND_TESTING_PLAN.md` before this implementation work.
They were preserved and are not presented here as changes made by this
session.

## End-to-end data flow

```text
selected profile
      |
      +--> provider decision
      |      +--> internal detectors
      |      +--> ansible-lint
      |      +--> GitLeaks dir/history
      |
      +--> normalized raw findings
             provider + native rule + concept + fingerprint
                        |
                        +--> findings.json / findings.raw.json
                        +--> CSV and text
                        |
                        +--> overlap policy + occurrence grouping
                                      |
                                      +--> occurrences.json
                                      +--> canonical SARIF
                                      +--> base/head PR comparison
```

This separation is intentional:

- raw findings answer, “What did every detector report?”;
- occurrences answer, “How many developer-visible problems are there?”;
- PR comparison answers, “What changed relative to the base branch?”.

## Verification

The implementation is covered by tests for profiles, provider filtering,
overlap grouping, PR matching/policy, GitLeaks redaction/history/checksum,
ansible-lint working-directory behavior, dynamic rule normalization,
credential logging, permission checks, file kinds, and output compatibility.

Run:

```bash
.venv/bin/pytest -q
.venv/bin/python -m compileall -q src scripts
git diff --check
```

Final verification result:

```text
197 passed in the current post-output-v2 suite
Python source and scripts compiled successfully
Profile definitions validated
GitHub workflow YAML parsed successfully
git diff --check passed
```

## Honest limitations

- Canonical grouping is line-based first. A provider that reports a different
  line and supplies no stable fingerprint may remain a separate occurrence.
- The `uncertain` PR category is intentionally non-blocking because guessing
  that two findings are identical is unsafe.
- Static analysis cannot prove runtime values from inventories, secret
  managers, dynamic includes, or extra vars.
- Sensitive-name detection is conservative and still needs calibration on a
  labeled real-repository corpus.
- Installed `ansible-doc` metadata is environment-dependent.
- The initial PR policy must be observed on real pull requests before enabling
  the full error ratchet.
