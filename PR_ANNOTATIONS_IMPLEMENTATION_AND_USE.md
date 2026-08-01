# Pull-request annotations: implementation and use

Date: 2026-08-01  
Branch: `sarif-validation-support`  
Merge status: not merged into `main`

## 1. Problem and result

The PR workflow produced JSON, CSV, SARIF, and artifacts, but a developer had
to open the Actions run to discover them. SARIF alone is not sufficient because
code scanning can be unavailable, disabled, or rejected by token permissions.

The workflow now gives developers four views:

1. file-and-line annotations for newly introduced findings;
2. an introduced-findings table in the job summary;
3. optional SARIF code-scanning presentation;
4. complete base, head, and comparison artifacts.

## 2. Implementation

The installed command `ansibleguard-pr-annotations` reads
`ansibleguard-pr-decision.json` and publishes only
`comparison.introduced`. It deliberately excludes unchanged baseline debt,
moved findings, fixed findings, and uncertain matches.

Example output sent to GitHub:

```text
::warning file=tasks/main.yml,line=12,title=AnsibleGuard%3A shell-instead-of-module::Prefer a purpose-built module
```

Severity is preserved as follows:

| AnsibleGuard | GitHub |
|---|---|
| `error` | `error` |
| `warning` | `warning` |
| `note` | `notice` |
| unknown | `warning` |

The command can also append a Markdown table containing severity, canonical
rule, `file:line`, and message to `$GITHUB_STEP_SUMMARY`. It publishes at most
50 annotations by default and reports truncation; the artifact remains
complete.

## 3. Safety and correctness

Finding text is escaped before it becomes a workflow command. Percent signs
and line breaks are escaped in messages; colons and commas are additionally
escaped in properties. This prevents detector-controlled text from injecting a
second command.

Paths must be repository-relative. Absolute paths and paths containing `..`
are rejected. Lines must be positive integers. A malformed or wrong decision
document returns exit code 2 rather than silently publishing misleading output.

Annotations are presentation, not policy. The later enforcement step remains
the authoritative pass/fail decision. In `observe` mode an introduced
hardcoded secret blocks the run; other introduced findings remain visible.

## 4. Workflow configuration

The product and demonstration workflows run this after base/head comparison:

```yaml
- name: Publish introduced PR annotations
  if: >-
    always() &&
    github.event_name == 'pull_request' &&
    hashFiles('ansibleguard-pr-decision.json') != ''
  run: >-
    ansibleguard-pr-annotations ansibleguard-pr-decision.json
    --limit 50
    --summary "$GITHUB_STEP_SUMMARY"
```

The demonstration also grants `security-events: write` and uploads
`ansibleguard-head/canonical/findings.sarif` using
`github/codeql-action/upload-sarif@v4`. The upload runs only for a PR whose head
belongs to the same repository and is `continue-on-error: true`.

The outputs have different scopes:

- workflow annotations: introduced canonical occurrences only;
- head SARIF: all canonical findings in the PR head tree;
- decision JSON: complete base/head classification;
- enforcement step: policy conclusion;
- artifact: all raw and canonical evidence.

## 5. Where developers see results

On the pull request:

1. **Checks** shows the complete workflow annotation list.
2. **Files changed** shows annotations inline when the file and reported line
   belong to the PR diff.
3. The Actions job summary shows the compact introduced-findings table and
   policy counts.
4. The artifact contains the full reports.
5. When code scanning is enabled, the PR security view also renders SARIF.

## 6. Commands

Focused tests:

```bash
.venv/bin/python -m pytest -q \
  tests/test_pr_annotations.py \
  tests/test_pr_workflow_contract.py
```

Complete tests:

```bash
.venv/bin/python -m pytest -q
```

Preview a real decision locally:

```bash
ansibleguard-pr-annotations \
  ansibleguard-pr-decision.json \
  --limit 50 \
  --summary /tmp/ansibleguard-pr-summary.md
```

Tests cover severity and location, command escaping, introduced-only
selection, truncation, Markdown output, invalid documents, unsafe paths, and
the workflow contract. The complete local suite passed: **224 tests**.

The first editable-install check attempted isolated build dependency resolution
and could not reach PyPI from the restricted local environment. Re-running with
`--no-build-isolation` used the already installed build tools and succeeded:

```bash
.venv/bin/pip install -e . --no-deps --no-build-isolation
```

The installed `ansibleguard-pr-annotations --help` command was then verified.

## 7. Live validation

The code is committed only to the original feature branch and copied to the
approved private package. The demonstration workflow pins that private commit
and updates only the existing demo branch. After GitHub completes the run, this
section records the run URL and annotations returned by GitHub's check API.

No work in this session merges or pushes to `main`.
