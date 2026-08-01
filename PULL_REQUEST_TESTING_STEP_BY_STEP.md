# Pull-request testing: step by step

## What the PR test proves

A pull-request test should answer four separate questions:

1. Did every required provider execute successfully?
2. Which canonical occurrences already existed at the base commit?
3. Which occurrences were introduced, moved, fixed, or uncertain?
4. Does the selected policy allow the PR?

The `pr` profile is used for base/head comparison. It runs source rules,
ansible-lint, and GitLeaks, but excludes Git review-metadata findings that
would make the two source snapshots difficult to compare. Review-range checks
can be run separately.

## Automated GitHub test

The repository already contains:

```text
.github/workflows/ansibleguard.yml
```

To test it:

1. Push the implementation branch to GitHub.
2. Open a pull request against `main` or `master`.
3. Open the PR's **Checks** tab.
4. Select **AnsibleGuard PR scan**.
5. Confirm the head and base scan steps completed.
6. Read the job summary.
7. Download the `ansibleguard-results` artifact.
8. Inspect `ansibleguard-pr-decision.json`.
9. Inspect `ansibleguard-head/summary/report.json`.
10. Inspect Code Scanning/SARIF annotations when the PR token has permission.

The workflow:

- checks out full Git history;
- scans the PR head;
- creates a detached worktree at the base SHA;
- scans the base with the same `pr` profile;
- scans GitLeaks history over validated `base..head`;
- compares canonical occurrences;
- enriches head summary rows with introduced counts;
- uploads organized outputs;
- blocks external-tool failures;
- applies the `observe` policy.

Fork PRs still produce downloadable artifacts. SARIF upload is skipped when a
fork token cannot safely write security events.

## Local reproduction of a PR

Run from the AnsibleGuard repository with the development environment active.
The target repository can be another local Git repository.

Set explicit full SHAs:

```bash
TARGET=/absolute/path/to/ansible-project
BASE_SHA=$(git -C "$TARGET" rev-parse origin/main)
HEAD_SHA=$(git -C "$TARGET" rev-parse HEAD)
BASE_TREE=$(mktemp -d)
```

Create a detached base worktree:

```bash
git -C "$TARGET" worktree add --detach "$BASE_TREE" "$BASE_SHA"
```

Scan the base:

```bash
ansibleguard "$BASE_TREE" \
  --profile pr \
  --fail-on never \
  --output pr-results/base
```

Scan the head and its introduced Git history:

```bash
ANSIBLEGUARD_BASE_SHA="$BASE_SHA" \
ANSIBLEGUARD_HEAD_SHA="$HEAD_SHA" \
ansibleguard "$TARGET" \
  --profile pr \
  --fail-on never \
  --output pr-results/head
```

Compare:

```bash
python scripts/compare_pr_results.py \
  pr-results/base/canonical/occurrences.json \
  pr-results/head/canonical/occurrences.json \
  --policy observe \
  --head-output pr-results/head \
  --output pr-results/decision.json
```

The comparison command intentionally returns non-zero when policy fails.

Remove the temporary worktree after testing:

```bash
git -C "$TARGET" worktree remove "$BASE_TREE"
```

## What to inspect

Start with:

```text
pr-results/decision.json
pr-results/head/summary/report.json
pr-results/head/summary/summary.csv
pr-results/head/canonical/occurrences.txt
pr-results/head/summary/diagnostics.json
```

The decision contains:

- `introduced`;
- `unchanged`;
- `fixed`;
- `moved`;
- `uncertain`;
- policy mode and conclusion;
- blocking occurrence IDs.

After comparison, every head summary row contains:

- `new_pr_findings`;
- `pr_comparison_status=compared`.

## Policies

### Observe

```bash
--policy observe
```

Blocks only introduced hardcoded-secret occurrences and external-tool
failures. Other introduced problems are measured but do not block.

Use this first while calibrating real repositories.

### Ratchet

```bash
--policy ratchet
```

Also blocks introduced error-severity occurrences. Existing debt does not
block merely because it still exists.

Enable this only after reviewing baseline noise, uncertain matches, and rule
severity.

## Recommended PR test cases

### 1. Clean documentation-only PR

Expected:

- tools complete;
- no introduced Ansible occurrences;
- policy succeeds.

### 2. Add a hardcoded secret canary

Add a clearly synthetic test token to a temporary branch.

Expected:

- GitLeaks detects it;
- the occurrence has `concept_id=hardcoded-secret`;
- it is introduced;
- observe and ratchet both fail;
- the secret value does not appear in reports or logs.

Remove the canary immediately after the test.

### 3. Add duplicate YAML keys

Expected:

- raw output can retain AnsibleGuard and ansible-lint evidence;
- canonical output groups matching evidence;
- the PR receives one developer-facing occurrence.

### 4. Add a credential task without `no_log`

Expected:

- AnsibleGuard reports `credential-log-exposure`;
- ansible-lint evidence is retained if its native rule applies;
- no credential value is copied to output.

### 5. Move an existing finding

Move a task without changing its meaning.

Expected:

- native fingerprint or semantic matching classifies it as `moved`;
- it is not incorrectly classified as newly introduced.

### 6. Change an existing secret

Expected:

- a changed GitLeaks fingerprint is not downgraded to uncertain;
- the new secret remains introduced and blocking.

### 7. Fix an existing problem

Expected:

- the base occurrence appears in `fixed`;
- it does not appear in introduced.

### 8. Simulate an unavailable external tool

Expected:

- diagnostics contain `tool-error`;
- the workflow fails independently of finding severity.

## Secret-safety check

Use a unique synthetic value, then verify it is absent from persisted output:

```bash
rg -n 'UNIQUE-SECRET-CANARY' pr-results
```

Expected: no match.

GitLeaks is invoked with full redaction, and the legacy writer excludes raw
`Secret` and `Match` fields.

## Final PR acceptance checklist

- [ ] Base and head SHAs are full immutable hashes.
- [ ] Both scans used `profile=pr`.
- [ ] GitLeaks and ansible-lint statuses are `completed`.
- [ ] Diagnostics contain no `tool-error`.
- [ ] Base/head occurrence schemas validate.
- [ ] `pr_comparison_status` is `compared`.
- [ ] Policy mode is documented.
- [ ] Blocking IDs are understood.
- [ ] Secret canaries are absent from artifacts.
- [ ] SARIF uploaded or the artifact fallback is available.
- [ ] Existing debt was not mistaken for introduced debt.
