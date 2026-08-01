# Private repository and live pull-request final report

## Result

The isolated fork PR now runs AnsibleGuard successfully from a private source
repository owned by `JedidiAymen`. Nothing was merged into either repository's
`main` branch.

- private source: `JedidiAymen/ansibleguard-private`
- visibility: private, verified through the GitHub API
- installed source commit: `9a9392ec067cf4ad90f43137c7274f8e8e0bca29`
- demonstration PR: `JedidiAymen/ansible-role-the_bastion#1`
- demonstration head: `99dbd3d04a56b2f632508bfcbc80f3d3c0d3cd04`
- successful run: [30710629864](https://github.com/JedidiAymen/ansible-role-the_bastion/actions/runs/30710629864)
- policy: `observe`, conclusion `success`
- comparison: 17 introduced, 173 unchanged, 0 fixed, 0 moved, 0 uncertain
- provider diagnostics: 0 in the head scan and 0 in the base scan
- tests after the implementation fixes: 215 passed

## Authorization and repository boundary

The user confirmed that the owner of `Narjes-b/AnsibleChecklist` approved a
private copy in the `JedidiAymen` account. The destination was created only
after that confirmation.

The copy is a clean development/install snapshot rather than a Git mirror. It
contains package source, tests, CI, scripts, packaging metadata, and Markdown
documentation. It deliberately excludes the original Git history, other
branches, research PDFs/images, downloaded third-party corpora, generated study
manifests, scanner outputs, environments, caches, secrets, and every untracked
file. In particular, the unrelated local
`ARTICLE_APPROACH_TOOL_BUILD_TESTING_PERFORMANCE.md` was not copied or staged.

The initial snapshot was scanned and validated before publication:

- GitLeaks: zero findings after one exact-path allowlist for the visibly
  synthetic `tests/fixtures/credentials_in_block.yml` detector fixture;
- tests: 210 passed at snapshot time;
- package build: both `ansibleguard-0.1.0.tar.gz` and
  `ansibleguard-0.1.0-py3-none-any.whl` built successfully;
- initial private commit: `a86184d89055245df8bb288b59d8cf7c0ccaa702`.

The private repository contains `SNAPSHOT_PROVENANCE.md`, which records the
approval, source branch/commit, included content, and exclusions.

## Authentication design

A broad personal access token was not used. A new ED25519 deploy key was
created specifically for `JedidiAymen/ansibleguard-private` and registered by
GitHub as verified and read-only:

- deploy-key title: `ansibleguard-pr-demo-readonly-2026-08-01`;
- deploy-key database ID: `159001120`;
- write access: disabled;
- fork Actions secret: `ANSIBLEGUARD_DEPLOY_KEY`.

The private key value was piped directly into GitHub Actions secret storage and
was never printed or committed. After a successful `git ls-remote` read test,
both temporary local key files were deleted. The deploy key and encrypted
repository secret remain configured so future internal PR runs can install the
tool. Delete both when this integration is retired.

The workflow writes the key to a mode-`0600` file under `RUNNER_TEMP`, removes
it with an exit trap, and installs an exact commit over SSH:

```text
git+ssh://git@github.com/JedidiAymen/ansibleguard-private.git@9a9392ec067cf4ad90f43137c7274f8e8e0bca29
```

An exact commit is used instead of `main`, so an unrelated future push cannot
silently change the scanner used for an already-defined PR check.

## Runtime dependency correction

The private Git installation succeeded in run `30709742322`, proving the
deploy-key design. The head scan then failed because semantic-cohesion modules
load spaCy's `en_core_web_lg` model, which is intentionally documented as a
separate runtime asset rather than a `pyproject.toml` dependency.

The workflow now runs the two setup commands documented by AnsibleGuard:

```bash
python -m spacy download en_core_web_lg
python -c "import nltk; nltk.download('wordnet', quiet=True)"
```

This keeps the Python package contract unchanged while making the full `pr`
profile reproducible on a clean runner.

## Source defects exposed by Python 3.12 and separate worktrees

### Python minimum-version compatibility

Run `30709844747` passed installation and NLP setup but exposed this syntax in
`paper_candidates.py`:

```python
except OSError, yaml.YAMLError:
```

Python 3.14 accepts this newer optional-parentheses form, which is why the local
environment did not reject it. Python 3.12—and the project's declared minimum
Python 3.10 grammar—requires:

```python
except (OSError, yaml.YAMLError):
```

The fix adds `tests/test_python_compatibility.py`, which parses every package
source file with `feature_version=(3, 10)`. This prevents a newer development
interpreter from accidentally accepting syntax that supported releases cannot
import. Private source commit: `040b788`.

### GitLeaks fingerprints

Run `30709956801` completed both scans but falsely treated six existing Molecule
fixture keys as introduced. GitLeaks returned repository-relative fingerprints
for the head checkout and absolute `/home/runner/work/_temp/ansibleguard-base`
fingerprints for the base worktree.

`external/gitleaks.py` now normalizes result paths and fingerprints relative to
the scan root for both directory and Git-range modes. The regression test feeds
an absolute finding from a separate worktree and verifies the stable result
`vars.yml:generic-api-key:1`. Private source commit: `81fe1e7`.

### Canonical contributor ordering

After GitLeaks normalization, unchanged same-line internal findings could still
select different primary messages. The contributor tie-breaker used
`finding_id`, and raw finding IDs include each checkout's absolute source path.

`report/occurrences.py` now orders equal-provider/rule contributors by their
message before the raw ID and removes the repository-root prefix from the
message used for canonical identity. Tests use different base/head roots and
opposite raw-ID ordering to prove identical occurrence IDs. Private source
commit: `8132e59`.

### Ansible-Lint paths and fingerprints

Run `30710439571` produced the expected 17 introduced findings but retained two
`uncertain` role-load occurrences because Ansible-Lint embedded the absolute
checkout directory in its message and native fingerprint.

`external/ansible_lint.py` now makes issue paths repository-relative, replaces
the scan-root portion of messages with `<repo>`, and derives a stable SHA-256
fingerprint from native rule, relative path, line, and normalized message. The
final run consequently has zero uncertain occurrences. Private source commit:
`9a9392e`.

## Definitive PR result

Run [30710629864](https://github.com/JedidiAymen/ansible-role-the_bastion/actions/runs/30710629864)
completed in 1 minute 47 seconds. Every operational step passed:

1. exact PR-head checkout with full history;
2. Python setup;
3. pinned private AnsibleGuard installation through the read-only deploy key;
4. GitLeaks installation;
5. head scan;
6. exact base worktree scan;
7. canonical base/head comparison;
8. readable GitHub job summary;
9. complete artifact upload;
10. provider-health and observe-policy enforcement.

The 17 intentional introductions are:

| Concept | Count |
|---|---:|
| `ansible-lint-issue` | 4 |
| `credential-log-exposure` | 2 |
| `insecure-permissions` | 1 |
| `missing-tags` | 4 |
| `missing-validate-certs` | 1 |
| `non-idempotent-command` | 1 |
| `shell-module-migration` | 1 |
| `unhandled-failure-suppression` | 2 |
| `unnamed-task` | 1 |

The six pre-existing Molecule keys remain visible as unchanged GitLeaks
occurrences. They are not hidden, but they no longer appear as newly introduced
by this PR. This is the intended base/head behavior.

## Run history and what each run proved

| Run | Result | Evidence obtained |
|---|---|---|
| `30705374033` | failed | Anonymous install cannot read the original private repository; secondary artifact handling was also hardened |
| `30705557577` | failed | Clear missing-credential failure with no cascading missing-output errors |
| `30709742322` | failed | Read-only deploy-key installation works; clean runner lacked the separate spaCy model |
| `30709844747` | failed | NLP setup works; Python 3.12 found unsupported exception syntax |
| `30709956801` | failed at enforcement | Both scans and artifacts work; absolute GitLeaks fingerprints caused false secret introductions |
| `30710186060` | success, noisy comparison | GitLeaks false secrets fixed; canonical raw-ID path noise remained |
| `30710439571` | success, two uncertain | Correct 17 introductions; only Ansible-Lint absolute-path identity remained |
| `30710629864` | success | Final deterministic result: 17 introduced, 173 unchanged, no fixed/moved/uncertain, zero diagnostics |

## Current branch and cleanup state

- `Narjes-b/AnsibleChecklist`: changes remain on `sarif-validation-support`;
- `JedidiAymen/ansibleguard-private`: private `main` contains the authorized
  package snapshot and four validated fixes;
- `JedidiAymen/ansible-role-the_bastion`: PR #1 remains isolated inside the
  fork; it does not target `adfinis`;
- no branch was merged into `main` during this work;
- the unrelated local article remains untracked and untouched;
- local temporary deploy-key files were removed;
- the read-only deploy key and encrypted fork secret remain active for future
  internal PR scans.

The only non-blocking workflow annotation is GitHub's Node runtime deprecation
notice for the pinned major versions of `actions/checkout`,
`actions/setup-python`, and `actions/upload-artifact`. GitHub forced them onto
Node 24 and the workflow succeeded. Their next major upgrades should be handled
as a separate dependency update with changelog review and another PR run.
