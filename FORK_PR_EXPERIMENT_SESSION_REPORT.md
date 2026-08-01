# Fork and pull-request experiment session report

## Purpose

This session answers a practical question: instead of only scanning frozen
repositories, can we fork a real Ansible project, introduce mistakes that we
already understand, open an isolated pull request, and inspect how
AnsibleGuard presents the difference between the base and head revisions?

Yes. The local base/head experiment works and found exactly 17 introduced
canonical occurrences. A real fork-internal GitHub pull request was also
created. Its first workflow run exposed a separate deployment boundary: the
AnsibleGuard source repository is private, so a public fork runner cannot
install it anonymously.

## Safety boundary

The selected project is the small public role:

```text
adfinis/ansible-role-the_bastion
```

The fork and demonstration PR are owned by the authenticated test account:

```text
fork: https://github.com/JedidiAymen/ansible-role-the_bastion
PR:   https://github.com/JedidiAymen/ansible-role-the_bastion/pull/1
```

The PR targets the fork's own `main` branch. Nothing was pushed or proposed to
the upstream Adfinis repository. The PR title and body clearly state that the
mistakes are intentional and that the PR must not be merged.

## Relationship to the preceding session

The preceding session implemented and validated:

- developer/security/lint/quality/PR/research profiles;
- provider provenance for internal, Ansible-Lint, and GitLeaks results;
- raw detector findings and canonical overlap-aware occurrences;
- base/head PR comparison and `observe`/`ratchet` policies;
- dynamic deprecated-module metadata;
- file-kind checks for defaults, vars, group_vars, host_vars, meta, and
  dependency manifests;
- cached, star-stratified GitHub repository discovery;
- PR activity enrichment and post-clone eligibility gates;
- full-SHA screening of four native-GitHub projects;
- a three-project selected GitHub sample;
- Ansible-Lint offline dependency isolation;
- 210 passing tests and valid workflow YAML.

Those changes were pushed to existing AnsibleChecklist PR #1 in commits:

```text
28e20eb feat: add auditable profiles PR ratcheting and GitHub study
c951801 docs: explain profiles GitHub study and PR validation
```

The user explicitly rejected merging or rebasing `main`. The interrupted
merge request made no change: there was no `MERGE_HEAD`, no conflict state,
and no rewritten history.

## GitHub fork creation

Authentication was checked without printing the token value. The active
account was `JedidiAymen` with repository/workflow scopes.

The first command attempted was:

```text
gh repo fork adfinis/ansible-role-the_bastion --clone=false --remote=false
```

It failed safely because this GitHub CLI version does not accept `--remote`
when a repository argument is supplied. No fork was created by that command.

The corrected command was:

```text
gh repo fork adfinis/ansible-role-the_bastion --clone=false
```

The fork was then cloned into a temporary directory, and the branch
`ansibleguard-known-errors-demo` was created.

## Intentional mistakes

The experiment added `tasks/ansibleguard_pr_demo.yml` containing only
synthetic mistakes:

- an unnamed `shell: chmod 777` task;
- `ignore_errors: true` without registered recovery handling;
- a world-writable `mode: "0777"`;
- `validate_certs: false`;
- a deliberately hardcoded demo password passed through `set_fact`;
- a `debug` task that prints the password without `no_log: true`;
- no tags on any demo task.

No realistic provider token, private key, or usable credential was published.
This avoids GitHub push-protection confusion and keeps the sample obviously
synthetic.

The first demo commit was:

```text
e472b95 test: demonstrate AnsibleGuard PR findings
```

## Local base/head validation

Frozen revisions:

```text
base: 6e09f8a18e89ec72e0deefafc4e0068788d3a9bf
head: e472b9559d6f4d320b7300ef6f12f6408d486235
```

The first parallel scan attempt was interrupted by the command execution
window before either output directory finalized. It produced no usable
evidence. Head and base were rerun through persistent terminal sessions.

Final local scan health:

| Revision | Selected YAML | Raw findings | GitLeaks | Ansible-Lint | Diagnostics |
|---|---:|---:|---|---|---:|
| base | 18 | 194 | completed | completed | 0 |
| head | 19 | 213 | completed | completed | 0 |

Canonical comparison:

```json
{
  "mode": "observe",
  "conclusion": "success",
  "blocking_occurrence_ids": [],
  "counts": {
    "introduced": 17,
    "unchanged": 171,
    "fixed": 0,
    "moved": 0,
    "uncertain": 0
  }
}
```

Introduced concepts:

| Concept | Count |
|---|---:|
| `missing-tags` | 4 |
| `ansible-lint-issue` | 4 |
| `unhandled-failure-suppression` | 2 |
| `credential-log-exposure` | 2 |
| `non-idempotent-command` | 1 |
| `shell-module-migration` | 1 |
| `unnamed-task` | 1 |
| `insecure-permissions` | 1 |
| `missing-validate-certs` | 1 |

The result proves that internal and Ansible-Lint output remains distinguishable
inside each canonical occurrence. For example, `ignore_errors` is reported by
both providers as two detector observations of the same broader suppression
concept.

`observe` succeeds even though error-level findings exist because its current
blocking rule is newly introduced `hardcoded-secret`. `ratchet` would also
block any newly introduced error-severity occurrence. This is intentional:
teams can begin with visibility and later enable stricter gating.

## Fork-internal pull request

The verified branch was pushed only to the fork and PR #1 was opened against
the fork's `main`. The PR workflow was designed to:

1. check out the exact PR head with full history;
2. install AnsibleGuard and GitLeaks;
3. scan the head with `base..head` review context;
4. create a detached base worktree and scan it with `base..base` context;
5. compare canonical occurrence documents;
6. show the first head-summary rows and policy JSON in the job summary;
7. upload head, base, and decision artifacts;
8. block provider tool errors or a failing `observe` policy.

## Actual first GitHub Actions result

The AnsibleGuard job failed during installation before any scan ran:

```text
fatal: could not read Username for 'https://github.com': No such device or address
```

The exact cause was verified through repository metadata:

```json
{
  "nameWithOwner": "Narjes-b/AnsibleChecklist",
  "visibility": "PRIVATE",
  "isPrivate": true
}
```

A public repository's default `GITHUB_TOKEN` cannot clone an unrelated private
repository. Because the install failed, no `ansibleguard-head`,
`ansibleguard-base`, or decision artifact existed. The original workflow used
`if: always()` for its summary/artifact steps, so they also failed. Those were
secondary failures, not additional scanner defects.

The workflow was hardened in commit:

```text
3db900c ci: explain private AnsibleGuard installation requirement
```

It now:

- requires an `ANSIBLEGUARD_READ_TOKEN` secret;
- prints a direct error explaining that it must be fine-grained and read-only;
- runs summary/artifact steps only when scanner output exists;
- never embeds or logs a personal token.

Verified workflow runs:

| Run | Commit | Result | Meaning |
|---|---|---|---|
| [30705374033](https://github.com/JedidiAymen/ansible-role-the_bastion/actions/runs/30705374033) | `e472b95` | failure | Anonymous clone of private AnsibleGuard failed; summary and artifact then also failed because outputs did not exist |
| [30705557577](https://github.com/JedidiAymen/ansible-role-the_bastion/actions/runs/30705557577) | `3db900c` | failure | One explicit setup failure requesting a fine-grained read-only secret; no misleading missing-output failures |

The existing broad GitHub CLI token was deliberately not copied into Actions
secrets. A live successful run needs one of these safe deployment choices:

1. publish AnsibleGuard as a versioned public/internal package;
2. make a public read-only source distribution intentionally;
3. create a fine-grained token scoped only to `Narjes-b/AnsibleChecklist` with
   Contents read access, store it as `ANSIBLEGUARD_READ_TOKEN`, and rotate it
   after the experiment;
4. use a read-only deploy key if repository administration permits it.

Option 1 is the best long-term developer experience. Option 3 is suitable for
finishing this temporary private-repository demonstration after explicit
credential approval.

## Other upstream checks

The fork retains the upstream role's own lint and Molecule workflows. Their
failures are expected because this PR intentionally adds invalid/unsafe tasks.
They provide useful independent evidence, but they are not AnsibleGuard's
canonical base/head result.

## Files changed in AnsibleChecklist during this session

- `GITHUB_MULTI_ECOSYSTEM_AND_PR_SESSION.md` — records the no-merge decision;
- `FORK_PR_EXPERIMENT_SESSION_REPORT.md` — this exact execution report;
- `ANSIBLEGUARD_COMMANDS_TESTING_AND_PR_GUIDE.md` — the separate operational
  command and PR guide requested by the user;
- `README.md` — links the two new documents.

No source detector or policy implementation was changed during the fork
experiment. The experiment tested the existing behavior and exposed a private
distribution requirement.
