# What to clean before the next runs (v0.0.7 → v0.0.7.1)

Status as of 2026-10-16. Items need the owner's approval where marked (A).

## 1. Data and storage
- **Immutable run archive.** `study/runs/` was found deleted on 2026-10-14 (cause unknown). Keep the
  frozen run and the re-execution (`v007-full-repro-2026-reexecution-2026-10-16.tar.gz`, sha256 481cc97d…)
  on a second disk or external storage, with checksums recorded in git.
- **`observations.csv.gz` (164 MB)** is hidden by the global `*.gz` ignore; store externally and record its hash.
- **Stale `study/` directories** (validation-v5 … v8, analysis, comparisons, retired 149-repo sets,
  repositories-207, results, labels, history): index and archive (A).
- **Main checkout** (`study/v007-human-validation`) still has duplicated staged doc moves/deletions and the
  owner's untracked old fetch-script/audit files (A): unstage or commit once the fix branch is merged.
- **Worktrees/venvs** after merge: `AnsibleChecklist-v007-repro`, `AnsibleChecklist-fixes`, `.venv-repro`.
- **Residual secrets/PII in context bundles**: regenerate (see 4) before any packet leaves the machine.

## 2. Tool fixes before a v0.0.7.1 freeze
- File-level findings must name the construct (structure rows currently anchor at line 1).
- Detector false positives listed in `study/validation-v007-human/ai-precheck/claude-reference-2026-10-16/FINDINGS.md` §3:
  non-Ansible YAML exclusion, missing-file-extension, become-scope-too-broad, large-task/large-play/
  complex-playbook units, "hack" matching, handler cross-file resolution, command idempotence guards,
  invalid-task-attribute-type version handling, unguarded-variable with prior set_fact, heredoc scope.
- credentials-leaking-in-log: make it module argument-spec aware; document the dynamic-`no_log` downgrade.
- Document the catalog `policy` field (per-occurrence required/optional).
- Re-run the full run, determinism and sanity gates; handle the one timeout repo (`encapsulate-xyz/cosmos-ansible`).

## 3. Codebook fixes (before humans label)
Define predicates and thresholds (style, review/history, maintainability, structure), an Ansible-version
policy, placeholder-credential policy, module-level `no_log` policy, bug-reference definition, applicability
for bot/merge commits, positive reason codes, a controlled `external_context_type`, and separate
semantic from actionability reason codes. Clarify `uncertain` vs `unreviewable`.

## 4. Bundle generator
Complete tree listing (no 120-path cap), include non-YAML diffs, imported handler files, name the asserted
variable/attribute, better reference search (not literal-only, no silent 50-hit cap), consistent redaction
markers, stronger redaction plus an independent secret/email/key-body scan (the idempotence check cannot find misses).

## 5. Sampling
Exclude or separately stratify vendored third-party roles, bot and merge commits; dedupe sibling files and
twin rows from the same repository.

## 6. Not done yet
Pre-registration sign-off, fix-tracing study, heldout samples (need the frozen v0.0.7.1 run), overall-interval calibration.

## 7. Update 2026-10-16 (plan v2)
Done: marker regex no longer matches `hack/` paths (standalone "Hack" such as a font name still matches; mixed-case "[Hack - …]" is a real marker).
Not changed on purpose: `become-scope-too-broad` follows its documented threshold (5 tasks); whether that is meaningful is a mode-B threshold-panel question and a codebook decision, not a bug fix.
Still open: the other tool false positives, which need owner priorities. See [validation-plan-v2](v007-validation-plan-v2.md).

## 8. Residual-secret gate (added)
`scripts/v007_bundle_secret_scan.py <context dir>` is an independent scanner (emails, token prefixes,
long base64 lines, high-entropy words; prints no values, exits 1 on any finding). On the 350 pilot bundles it reports
57 findings in 18 files. Run it as a build gate and before every packet export; the generator's idempotence check cannot find misses.
Fix path for the generator: redact author/committer emails and names in review/history bundles, redact base64 key bodies
regardless of the header, then re-run the scan until it reports 0.

## 9. Second-pass redactor (added)
`scripts/v007_bundle_redact_v2.py <context dir> <new dir>` writes redacted copies (emails, token prefixes, base64 blocks,
high-entropy words) without touching the frozen bundles. On the 350 pilot bundles it changed 18 files and the scanner then reports 0 findings.
Frozen bundle hashes are unchanged; use the redacted copy for any packet that leaves the machine, and record its checksums.

## 10. Detector changes made for v0.0.7.1 (2026-10-16)
Done (see CHANGELOG): bug-reference forms and bot authors, missing-file-extension (collection playbooks, .json, directories,
free-form arguments), quoted-heredoc scope, read-only classification with mutating pipeline tails, `hack/` path.
Deliberately not changed: become-scope-too-broad (documented threshold), large-task/large-play thresholds (mode-B panels),
non-idempotent-command guards (needs the label evidence from pilot 2 first).
