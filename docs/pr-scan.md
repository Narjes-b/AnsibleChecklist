# How the pull-request scan works

A PR scan answers one question: **what did this change introduce, and what did
it fix?** It does not re-report problems that already existed on the base
branch. AnsibleGuard scans the base and the head revision separately, compares
the two sets of canonical findings, and applies a policy to the findings that
are new.

## 1. Run it

Locally, from any Git checkout:

```bash
# Compare a feature branch with main (both are committed revisions)
ansibleguard diff . --base main --head feature --profile pr --policy ratchet -o pr-out

# Compare main with the current working tree (uncommitted edits included)
ansibleguard diff . --base main --profile pr -o pr-out

# Compare HEAD with what is staged for the next commit
ansibleguard diff . --staged --profile pr -o pr-out

# Also evaluate the Git review rules over the PR range
ansibleguard diff . --base main --head feature --profile review-range --policy observe -o pr-review
```

`--parallel-base-head` scans base and head concurrently; the result is
identical to the sequential run.

In GitHub Actions, `.github/workflows/ansibleguard.yml` does the same thing
for every pull request (section 6).

## 2. What happens, step by step

```text
  repository ──► git worktree add --detach <tmp>/base <base>
             └─► git worktree add --detach <tmp>/head <head>   (or the working tree / staged index)
                      │
   analyze base  ◄────┴────►  analyze head        (same profile, same providers)
   review range = empty       review range = base..head
                      │
        canonical occurrences of each side
                      │
   compare_occurrences:  exact ─► native fingerprint ─► semantic ─► semantic rename ─► renamed file
                      │
   unchanged · moved · introduced · fixed · uncertain
                      │
   changed-line mapping (git diff base..head)  ─►  "direct" / "context" / "-"
                      │
   policy (observe | ratchet | strict)  ─►  diff/summary.md, SARIF, annotations, exit code
```

1. **Isolated snapshots.** Base and head are checked out as temporary detached
   worktrees, so the scan never touches your branch or working tree. They are
   removed afterwards.
2. **Two ordinary scans.** Each side is analyzed with the selected profile,
   exactly like `ansibleguard <path>`. With `pr` that is 69 rules plus
   ansible-lint and GitLeaks.
3. **Review rules see the PR range.** Git review rules (`review-range`
   profile) evaluate the head scan over `base..head`: every commit message in
   the range and the full set of changed files. The base scan gets an empty
   range, so history findings are never reported as "fixed" just because the
   base is older. CI sets the same ranges with `ANSIBLEGUARD_BASE_SHA` and
   `ANSIBLEGUARD_HEAD_SHA`.
4. **Matching.** Occurrences are paired in order of strength: identical
   occurrence ID; shared provider fingerprint; same semantic key; same content
   in a renamed task; same finding in a renamed file. Every base line is also
   mapped through the `git diff -U0` hunks to the head line it became (lines
   inside deleted or rewritten hunks have no image):
   - an identical ID is accepted as *unchanged* only if the diff maps the base
     line onto the same head line — otherwise a different task merely
     occupies that line number now;
   - when several identical findings compete (for example many
     `yaml[truthy]` lines in one file), the one whose base line maps exactly
     onto the head line is chosen (`…-line-mapped`).
   Anything left over on the head side is **introduced**; on the base side,
   **fixed**. A pair whose identity is still ambiguous is reported as
   **uncertain** rather than guessed.
5. **Changed lines.** `git diff base..head` decides whether an introduced
   finding sits on a changed line (`direct`), in a changed task or file
   (`context`), or outside the change (`-`).
6. **Policy.**
   - `observe` — report only; never fails.
   - `ratchet` — fails on any introduced `error`, or any introduced hardcoded
     secret.
   - `strict` — also fails on introduced `warning`s.
   Optional style-policy findings (for example `missing-tags`) are listed
   separately and never block.

## 3. What you get

`pr-out/` contains `base/` and `head/` (complete scan outputs) and `diff/`:

| File | Content |
|---|---|
| `diff/summary.md` | Human-readable PR report: status, blocking finding, counts, introduced findings by category, fixed findings |
| `diff/introduced.json`, `diff/fixed.json` | Introduced and fixed canonical occurrences |
| `diff/introduced-actionable.json` | Introduced findings without optional style policy |
| `diff/introduced.sarif`, `diff/introduced-actionable.sarif` | SARIF 2.1.0 for GitHub code scanning; only introduced findings |
| `diff/comparison.json` | Full classification including unchanged, moved, and uncertain pairs |
| `diff/playbooks.json` | Playbooks affected through changed roles |

The process exit code follows the policy: `1` when the policy fails.

## 4. Reading a result

Example from the controlled test repository (a PR that removes
`validate_certs: false`, adds a `shell: systemctl restart nginx` task and a
`mode: "0777"` file task):

```text
Status: Failed
> Blocking finding: insecure-permissions at roles/web/tasks/main.yml:15
- 7 finding(s) introduced (6 from AnsibleGuard, 1 from ansible-lint)
- 1 finding(s) fixed            ← missing-validate-certs on the removed option
```

`insecure-permissions` is an `error`, so `ratchet` fails the PR. The shell task
(line 12) is reported once per concept: non-idempotent command, shell-module
migration, and ansible-lint's command-instead-of-shell.

## 5. Correctness safeguards

- **The scanned tree is never modified.** ansible-lint applies a project
  config's `write_list` (and can rewrite its own config) even without
  `--fix`. AnsibleGuard snapshots YAML before ansible-lint runs, restores any
  rewrite, removes `.ansible/`, `__pycache__/`, and `*.tmp.yml` artifacts, and
  records the intervention as `workspace_guard` in the provider metadata.
- **ansible-lint lines point at the right task.** ansible-lint 26.x reports a
  task-level match at the line after the task ends — the start of the next
  task. AnsibleGuard moves such matches back to the start of the task they
  describe (the provider's original line is kept as
  `provider_reported_line`); `yaml[...]` findings keep their exact line.
  Without this, a finding on one task was shown on the next one and the
  changed-line mapping could mark it `direct` on the wrong change.
- **No guessed history.** If the head commit records a parent that the
  checkout does not have (a shallow clone), diff-dependent review rules are
  not evaluated and a `not-evaluated` diagnostic says so; they never treat the
  whole repository as the change. Fetch enough history in CI
  (`actions/checkout` with `fetch-depth: 0`, as the workflow does).
- **Incompatible snapshots are refused.** Base and head must use the same
  profile, rule set, and provider configuration;
  `--allow-incompatible-snapshots` overrides this and is recorded in the
  output.
- **Unparseable files are set aside, not guessed.** A file that fails to
  parse on either side (often a non-Ansible YAML such as `mkdocs.yml` with a
  Python tag) is excluded from both sides and listed under "Not compared". If
  the PR itself makes a file it changes unparseable, the policy fails with a
  parse regression.
- **Missing provider evidence is excluded, not zero.** If ansible-lint is
  partial on a side (for example `ansible-playbook --syntax-check` fails
  offline), its findings are excluded from both sides and the report says so;
  AnsibleGuard and GitLeaks are still compared.
- **Incomplete internal analysis is not compared.** If AnsibleGuard's own
  analysis did not complete on a side, or a fault other than a provider fault
  or a per-file parse failure occurred (for example an internal detector
  exception), `ansibleguard diff` stops with an error instead of reporting
  missing findings as fixed or introduced.

## 6. GitHub Actions

The workflow (`.github/workflows/ansibleguard.yml`) runs, for every pull
request: checkout with full history → install → scan head (`--profile pr`,
review range `base..head`) → scan base in a detached worktree (empty review
range) → `ansibleguard diff --base-results … --head-results … --policy
ratchet` → introduced-finding annotations → job summary → actionable SARIF
upload (when `vars.ANSIBLEGUARD_UPLOAD_SARIF` is `true` or the repository has
code scanning) → upload reports → enforce the policy last, so every report is
published even when the PR fails.

## 7. Validation of PR mode

See [study/v007-audit-2026-10-15.md](study/v007-audit-2026-10-15.md) section 4
for the controlled test, the replay of real merged pull requests, and the
manual review of sampled findings.
