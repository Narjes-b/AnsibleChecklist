# Stratified sample, built on the fixed v0.0.7.1 detector

This is the same impact-weighted stratified-sampling methodology as
`stratified-sample/` (see its `DESIGN.md`), re-run against a corpus scanned
with the fixed detector (tool commit `4a3f73f`, includes the merged
`fix/v007-audit-2026-10-15` detector fixes plus two additional fixes made
while reproducing this run — see below) instead of the original pre-fix
v0.0.7 corpus.

## Run provenance

- **Population**: 191 of the original 207-repository frozen manifest
  (`study/manifests/github-v0071-191.csv`). 16 repositories excluded:
  - 15 with a frozen commit SHA no longer shallow-fetchable from GitHub
    (`git fetch --depth=1 origin <sha>` exits 128 — the SHA is unreachable
    from any current remote ref). Documented in
    `study/runs/v0071-final-2026/status/acquisition-excluded.json` on the
    `v0071-rerun` branch of the WSL reproduction checkout.
  - 1 (`fgci-org/fgci-ansible`) crashed the detector itself: `PermissionError`
    on `/root/pull_variables.yml`, an absolute `include_vars` target outside
    the repository that `expand_include_vars_target()`
    (`src/ansibleguard/include_vars_semantics.py`) attempts to `.is_dir()`
    without catching `PermissionError`/`OSError`. **This is a real,
    previously unknown detector robustness bug**, worth fixing separately —
    not fixed here, just excluded so it doesn't block this run.
- **Validation**: passed cleanly — 0 failed, single tool commit, single rule
  hash, 163 complete + 28 partial (partial = some files within a repo didn't
  fully analyze, not excluded from results). See
  `study/runs/v0071-final-2026/status/validation-report.json`.
- **Detector state**: built on the WSL reproduction checkout, which carries
  the merged `fix/v007-audit-2026-10-15` detector fixes (shallow-clone
  diff-tree bug, CHANGELOG/fragments recognition, ansible-lint workspace
  guard, handler cross-file resolution, bug-reference/bot-author/file-
  extension precision) plus three fixes made while reproducing this run: an
  acquisition-failure tolerance flag, a fix for `repository_path` being read
  from a stale manifest column instead of derived from `checkout_root`, and
  a matching preflight tolerance for already-documented acquisition
  exclusions. **All three are now merged onto `feat/v0071-detector-fixes-and-llm-merge`**,
  alongside a fix for the `include_vars_semantics.py` `PermissionError` bug
  that excluded `fgci-org/fgci-ansible` above (fixed and tested, not just
  documented, as of this branch).

## Result

352 of 355 target rows populated (120 occurrences skipped for unreadable
file context — consistent with the original run's experience).
`stratified-sample.csv` / `stratified-sample-manifest.json` have the same
schema as `../stratified-sample/stratified-sample.csv`.

## Labeling

`stratified-sample-completed.csv` has an independent AI-shadow labeling pass
(Reviewer A, same identity as `../stratified-sample/`'s Reviewer A, protocol
version `stratified-v0071-352`) over all 352 rows — split into 8 per-family
chunks (`families/*-completed.csv`, merged with no deduplication or
reconciliation; sample_id sets verified to match exactly, zero blank
labels). Headline: 188 positive, 101 uncertain, 62 negative, 1 unreviewable;
confidence 195 high / 107 medium / 50 low — note this confidence
distribution genuinely varies with case difficulty, unlike the flat
"always high confidence" pattern found in the local-LLM evaluation
(`local-llm/eval/EVAL_RESULTS.md`).

**No second reviewer (AI or human) has labeled this sample yet.** Several
labeling passes surfaced real, concrete detector issues worth separate
attention:
- Non-Ansible files being scanned and misclassified as Ansible task YAML:
  a Kustomize JSON6902 patch, KRD host-definition data, a go-task
  `Taskfile.yaml` matched by multiple different rules, and a Notifiarr/Radarr
  webhook config (`hooks.yaml`) matched by `unnamed-task`.
- A line-attribution error on `complex-expression`: one flagged line was a
  plain YAML comment with no expression on it at all.
- `duplicate-task-names` findings reporting `count=1`, which is logically
  invalid for a rule that by definition needs at least 2 occurrences.
- Go-task's own built-in template syntax (`{{end}}`, `{{if eq .STATE ...}}`,
  `OS`/`ARCH`) misparsed as undeclared Ansible Jinja2 variables.
- A `listen:` handler-trigger attribute present on a regular (non-handler)
  task, which is silently inert — a genuine functional defect, not just a
  style nit.

## Not yet done

- No second reviewer has labeled this sample — everything above is a single
  AI pass, not an agreement comparison.
- The detector issues listed above under "Labeling" are documented here
  only; none has its own tracked issue or fix yet.
