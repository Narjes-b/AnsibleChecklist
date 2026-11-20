# Single-repository demonstration scan (2026-10-24)

Status: one illustrative `technical-full` scan of one corpus repository. It is a demonstration of the tool on real input, not a study result, a sample, or validated evidence. Nothing here is added to the 207-repository denominators.

## Run

| Item | Value |
|---|---|
| Repository | `NSLS2/nsls2.ioc_deploy`, commit `10518de6b2fbd124ce01d7b67512558f3bcf7b8e` (local corpus clone, clean worktree, left unchanged) |
| Selection | random pick from `study/repositories/` |
| Tool | AnsibleGuard 0.0.7.1 at `eb15545e`, ansible-lint 26.4.0, GitLeaks 8.30.1 |
| Profile | `technical-full`, `--fail-on never` |
| Duration | 33 seconds, exit 0 |

```sh
.venv/bin/ansibleguard study/repositories/NSLS2/nsls2.ioc_deploy \
  --profile technical-full --fail-on never \
  -o study/single-repo-scan-2026-10-24/full-output
```

## Health

448 files selected and processed, 97 structurally analyzed. ansible-lint and GitLeaks completed. Run status `completed_with_diagnostics`: the local clone is shallow, so the diff-dependent review rules (`missing-release-note`, `missing-test-update`, `untested-override-change`, `removed-copyright-notice`) were **not evaluated**, not passed.

## Results (unvalidated tool output)

| Breakdown | Values |
|---|---|
| Raw / canonical | 1,447 / 1,436 |
| Canonical provider | AnsibleGuard 1,324 · ansible-lint 112 · GitLeaks 0 |
| Severity | 2 error · 184 warning · 1,250 note |
| Policy | 100 required · 1,336 optional |
| Semantic status | 738 CONFIRMED · 695 UNCERTAIN · 3 ORDERED_CONFLICT |

Most findings are optional signals: 683 unresolved-variable classifications, 417 `missing-tags`, 202 `variable-naming-convention`. Required findings concentrate in `roles/deploy_ioc/tasks/deploy-ioc.yml` (legacy `with_items`, complex expressions, size thresholds, shell-to-module, non-idempotent commands).

**Observed likely false positive.** Both errors are `insecure-permissions` on `roles/device_roles/adaravis/tasks/autogen_files.yml:3` and `:9`: `mode: "02775"` with `state: directory`. Setgid on a shared directory is a standard group-inheritance pattern, yet under `ratchet` it would block a PR. Candidate codebook/detector case for the experimental rule.

## Files

| Path | Tracked | Contents |
|---|---|---|
| `summary/run-summary.md` | yes | Trust summary |
| `summary/report.json` | yes | Run summary report |
| `summary/diagnostics.json` | yes | Not-evaluated review rules |
| `summary/occurrences.csv` | yes | All 1,436 canonical occurrences |
| `summary/findings.sarif` | yes | Canonical SARIF 2.1.0 |
| `summary/run.json` | yes | Run metadata and provenance (contains local absolute paths) |
| `full-output/` | no (48 MB, 4,256 files) | Complete scan output, regenerate with the command above |
| `scan-console.log` | no | Console output |
