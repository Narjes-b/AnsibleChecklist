# AnsibleGuard commands, testing, outputs, and pull requests

## 1. Install the project for development

Run from the AnsibleChecklist repository root:

```bash
python -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/ansibleguard install-tools
```

What these commands do:

- create an isolated Python environment;
- install AnsibleGuard plus its declared test dependencies;
- install the validated GitLeaks binary used by security and full profiles.

Ansible-Lint runs with `--offline`. It does not install dependencies from a
scanned repository and records `dependency_mode=offline-no-auto-install` in
`run_metadata.json`.

## 2. Run all tests

```bash
.venv/bin/python -m pytest -q
```

Current verified result:

```text
210 passed in 26.23s
```

Useful focused suites:

```bash
# Profiles and provider boundaries
.venv/bin/python -m pytest -q tests/test_developer_profiles.py tests/test_profiles.py

# Raw/canonical overlap and output v2
.venv/bin/python -m pytest -q tests/test_occurrences.py tests/test_output_contract.py

# PR comparison and workflow contract
.venv/bin/python -m pytest -q tests/test_pr_comparison.py tests/test_pr_workflow_contract.py

# GitHub discovery and reproducible repository collection
.venv/bin/python -m pytest -q tests/test_github_discovery.py tests/test_study_scripts.py

# Security providers and dependency isolation
.venv/bin/python -m pytest -q tests/test_ansible_lint.py tests/test_gitleaks_hardcoded_credentials.py tests/test_install_gitleaks.py
```

Validate workflow YAML and whitespace:

```bash
.venv/bin/python -c 'import pathlib,yaml; [yaml.safe_load(p.read_text()) for p in pathlib.Path(".github/workflows").glob("*.yml")]; print("workflow YAML parsed")'
git diff --check
```

## 3. Run AnsibleGuard

General form:

```bash
.venv/bin/ansibleguard TARGET \
  --profile PROFILE \
  --output OUTPUT_DIRECTORY \
  --fail-on POLICY
```

Scan one playbook:

```bash
.venv/bin/ansibleguard playbook.yml \
  --profile developer-fast \
  --output results/developer-fast \
  --fail-on error
```

Scan a whole role or repository:

```bash
.venv/bin/ansibleguard ./my-ansible-project \
  --profile technical-full \
  --output results/technical-full \
  --fail-on never
```

Use `--fail-on never` when collecting/calibrating evidence. Use
`--fail-on error`, `warning`, `tool-error`, or `parse-error` when the command
should act as a local/CI gate.

## 4. Choose the right profile

| Profile | Providers | Main use |
|---|---|---|
| `developer-fast` | internal | Fast local security/correctness/reliability feedback; no external tools or Git review |
| `security` | internal + GitLeaks + security Ansible-Lint | Secret, credential, TLS, permissions, and security review |
| `lint` | Ansible-Lint | Native Ansible-Lint results only |
| `quality` | internal | Correctness, maintainability, structure, style, documentation, reliability, tests |
| `technical-full` | all | Everything: internal, Ansible-Lint, GitLeaks, and Git review |
| `pr` | all source providers | Base/head PR comparison input |
| `snapshot-source` | internal | One immutable source snapshot without review-range/external aggregates |
| `research-core` | internal | Conservative paper-derived primary research stratum |
| `extended-ansible` | internal | Ansible-specific secondary research stratum, disjoint from research core |
| `review-range` | internal Git checks | Commit/release/test/review metadata for one base-to-head range |

Examples:

```bash
.venv/bin/ansibleguard . -o results/security --profile security --fail-on error
.venv/bin/ansibleguard . -o results/lint --profile lint --fail-on never
.venv/bin/ansibleguard . -o results/quality --profile quality --fail-on warning
.venv/bin/ansibleguard . -o results/all --profile technical-full --fail-on never
```

## 5. Understand the output

Important top-level files:

| File | Meaning |
|---|---|
| `findings.raw.json` | Every native detector/provider observation before overlap merging |
| `occurrences.json` | Canonical concepts after exact/substantial overlap grouping |
| `findings.json` | Canonical compatibility output |
| `summary.csv` | Per-file errors, warnings, notes, total, and PR enrichment columns |
| `findings.sarif` | Code-scanning upload format |
| `diagnostics.json` | Parser/provider/tool failures; never confuse these with findings |
| `run_metadata.json` | Profile, rule hash, provider status, tool versions/configuration |
| `file_selection.json` | Which YAML population was selected and its manifest hash |
| `review_metrics.json` | Git range/review evidence |

Organized v2 directories contain the same contract in clearer groups:

```text
raw/          detector-native findings
canonical/    overlap-aware occurrences and SARIF
summary/      summary CSV, diagnostics, report JSON
metadata/     run, file-selection, review metadata
legacy/       compatibility layout information
```

Check provider health before interpreting results:

```bash
.venv/bin/python -c 'import json; print(json.dumps(json.load(open("results/all/run_metadata.json"))["tools"], indent=2))'
.venv/bin/python -c 'import json; print(json.dumps(json.load(open("results/all/diagnostics.json")), indent=2))'
```

Do not say “zero findings” when a provider has `tool-error`. Say that the scan
is partial and name the failed provider.

## 6. Use a file-classification manifest

For research and large repositories, the scanner should not mistake CI,
documentation, test, generated, or arbitrary data YAML for production Ansible.

Generate row-level classification from a frozen repository manifest:

```bash
.venv/bin/python scripts/classify_study_files.py \
  study/manifests/github-selected-frozen.csv \
  --output-dir study/manifests/file-classification
```

Then scan only rows with `included=true`:

```bash
.venv/bin/ansibleguard /path/to/frozen/repository \
  --profile technical-full \
  --file-manifest study/manifests/file-classification/OWNER__REPO__SHA.csv \
  --output results/frozen-scan \
  --fail-on never
```

The manifest must cover every YAML candidate, use safe repository-relative
paths, and match the frozen repository. Missing, duplicate, stale, or escaping
paths are rejected.

## 7. Discover native GitHub candidates

Create a cached, star-stratified candidate snapshot:

```bash
.venv/bin/python scripts/discover_github_ansible.py \
  --pages 1 \
  --per-page 30 \
  --as-of 2026-08-01T00:00:00+00:00
```

The default queries cover all four star bands plus `ansible-role` and
`ansible-collection` topics. Stars are sampling context, not a correctness
gate.

Enrich PR counts only for an explicit shortlist:

```bash
.venv/bin/python scripts/discover_github_ansible.py \
  --pages 1 \
  --per-page 30 \
  --as-of 2026-08-01T00:00:00+00:00 \
  --enrich-prs \
  --enrich-project kubernetes-sigs/kubespray \
  --enrich-project Linuxfabrik/lfops
```

Useful modes:

```bash
# Reuse cache and guarantee no network
.venv/bin/python scripts/discover_github_ansible.py --offline

# Deliberately retrieve fresh API data
.venv/bin/python scripts/discover_github_ansible.py --refresh-cache
```

If `GITHUB_TOKEN` is present in the environment, the script uses it only in
request headers. It never writes the token to cache or CSV.

## 8. Screen and freeze selected repositories

Discovery begins with both states false:

```text
collect_for_screening=false
selected=false
```

Set `collect_for_screening=true` to permit clone/measurement without claiming
final inclusion. After all gates and manual scope review pass, set
`selected=true` and record the full revision SHA.

Clone/freeze:

```bash
.venv/bin/python scripts/clone_study_repositories.py \
  study/manifests/github-screening-pilot.csv \
  --output study/manifests/github-screening-frozen.csv
```

Run the frozen sample:

```bash
.venv/bin/python scripts/run_study_pilot.py \
  study/manifests/github-selected-frozen.csv \
  --file-manifests-dir study/manifests/file-classification \
  --profile technical-full
```

The collector records SHA/date, commits, contributors, recent contributors,
YAML/production counts and LOC, Ansible percentage, Ansible-touching commits,
PR evidence, eligibility state, and explicit rejection reasons.

## 9. Test a pull request locally

Fetch full history and identify exact SHAs:

```bash
git fetch origin --prune
git rev-parse origin/main
git rev-parse HEAD
```

Assume:

```text
BASE_SHA=<full base SHA>
HEAD_SHA=<full head SHA>
```

Create a detached base worktree:

```bash
git worktree add --detach /tmp/ansibleguard-base "$BASE_SHA"
```

Scan head with its real review range:

```bash
ANSIBLEGUARD_BASE_SHA="$BASE_SHA" \
ANSIBLEGUARD_HEAD_SHA="$HEAD_SHA" \
.venv/bin/ansibleguard . \
  --output ansibleguard-head \
  --profile pr \
  --fail-on never
```

Scan base with an empty review range:

```bash
ANSIBLEGUARD_BASE_SHA="$BASE_SHA" \
ANSIBLEGUARD_HEAD_SHA="$BASE_SHA" \
.venv/bin/ansibleguard /tmp/ansibleguard-base \
  --output ansibleguard-base \
  --profile pr \
  --fail-on never
```

Compare canonical occurrences:

```bash
.venv/bin/python scripts/compare_pr_results.py \
  ansibleguard-base/canonical/occurrences.json \
  ansibleguard-head/canonical/occurrences.json \
  --policy observe \
  --head-output ansibleguard-head \
  --output ansibleguard-pr-decision.json
```

Use `--policy ratchet` when all new error-severity occurrences should block.

Inspect the decision:

```bash
.venv/bin/python -c 'import json; p=json.load(open("ansibleguard-pr-decision.json")); print(json.dumps(p["policy"], indent=2))'
```

## 10. How PR comparison works

```text
base checkout ──scan──> base canonical occurrences ─┐
                                                    ├─ compare ─> decision
head checkout ──scan──> head canonical occurrences ─┘
```

Comparison categories:

- `unchanged`: exact same occurrence ID;
- `moved`: stable native fingerprint or semantic identity at a new location;
- `fixed`: exists only in base;
- `introduced`: exists only in head;
- `uncertain`: looks like the same detector shape, but identity is not strong
  enough to call it moved.

Policy behavior:

| Policy | Blocks |
|---|---|
| `observe` | introduced `hardcoded-secret` concepts; provider tool errors are enforced separately |
| `ratchet` | introduced hardcoded secrets and introduced error-severity occurrences |

Provider failures always come from `diagnostics.json`, not the occurrence
policy. A comparator crash must also block: on PRs, absence of
`ansibleguard-pr-decision.json` is a failure.

## 11. What developers see in GitHub Actions

The workflow should present three layers:

1. **Job summary** — first per-file summary rows plus policy counts.
2. **Checks** — success/failure from provider health and policy enforcement.
3. **Artifact** — complete base/head output and decision JSON for investigation.

For trusted same-repository PRs, SARIF may be uploaded to Code Scanning. Fork
PRs should use artifacts when the security-events token is not trusted.

Expected artifact structure:

```text
ansibleguard-head/
ansibleguard-base/
ansibleguard-pr-decision.json
```

The summary must distinguish:

- raw detector count;
- canonical occurrence count;
- introduced/fixed/moved/uncertain counts;
- provider statuses;
- diagnostics/tool errors;
- policy mode and conclusion.

## 12. Reproduce the known-errors demo

Fork without altering the current repository's remotes:

```bash
gh repo fork adfinis/ansible-role-the_bastion --clone=false
git clone https://github.com/YOUR_ACCOUNT/ansible-role-the_bastion.git
cd ansible-role-the_bastion
git switch -c ansibleguard-known-errors-demo
```

Add an intentionally bad test task file, run the local base/head procedure
above, then push only after the expected introduced findings are confirmed:

```bash
git push -u origin ansibleguard-known-errors-demo
gh pr create \
  --repo YOUR_ACCOUNT/ansible-role-the_bastion \
  --base main \
  --head ansibleguard-known-errors-demo \
  --title 'test: isolated AnsibleGuard known-errors PR demo'
```

Never open the intentional-error PR against upstream.

Actual local demo result:

```text
17 introduced canonical occurrences
171 unchanged
0 fixed
0 moved
0 uncertain
observe conclusion: success
GitLeaks: completed
Ansible-Lint: completed
diagnostics: 0
```

## 13. Private AnsibleGuard repository in downstream CI

The real fork experiment showed that this command fails on a public runner
while AnsibleChecklist is private:

```bash
pip install 'git+https://github.com/Narjes-b/AnsibleChecklist.git@sarif-validation-support'
```

Recommended long-term fix: publish a versioned package or reusable action.

Temporary private-repository option: have an authorized repository owner
create a short-lived credential scoped only to `Narjes-b/AnsibleChecklist`
with Contents read access, then store it interactively—never as a command-line
value:

```bash
gh secret set ANSIBLEGUARD_READ_TOKEN \
  --repo YOUR_ACCOUNT/ansible-role-the_bastion
```

The workflow can then install with the masked secret. Do not reuse or upload a
broad personal `repo` token. Rotate/delete the temporary read token after the
experiment.

If the active account is only a collaborator, verify permissions before
choosing a deploy key:

```bash
gh api repos/Narjes-b/AnsibleChecklist \
  --jq '{visibility, permissions, default_branch}'
```

`admin: false` means that account cannot add a deploy key even when
`push: true`. Ask a repository administrator to configure the read-only key or
GitHub App. Do not weaken the source repository's visibility merely to make a
test workflow pass.

## 14. Pull-request acceptance checklist

- full history is available;
- exact base/head SHAs are recorded;
- base scan uses `base..base`, not an unrelated preceding commit;
- head and base use the same profile/tool versions;
- Ansible-Lint is offline and does not mutate dependencies;
- GitLeaks history range is validated;
- raw and canonical results are both preserved;
- diagnostics contain no provider `tool-error`;
- the comparison decision exists;
- summary and artifacts are uploaded;
- fork SARIF permissions are handled safely;
- intentional demo PRs never target upstream;
- secrets are fine-grained, read-only, masked, and temporary.
