# Everything noticed while producing the reference labels

Sources: the seven agents' observation files (`observations/`), my 21-item QC, and checks I ran
afterwards. Item ids refer to the agreement pilot.

## 1. Codebook gaps (labels depend on undefined terms)
- No operational predicates or thresholds for: style (long-task-name, long-statement, naming),
  review/history (subject length limit, what counts as a bug reference, release-note/test
  convention, merge and bot commits), maintainability/structure (large, complex, coupling,
  unstructured-module, unnecessary or missing abstraction, duplicated code).
- Security: placeholder credentials in test/vagrant fixtures; whether module-level `no_log` counts.
- Objective: loop-legacy-syntax is accepted by ansible-core, so "deprecated" wording is policy;
  redirected-module needs an Ansible version; unpinned-dependency scope (meta `collections:`,
  sibling roles); non-idempotent vs read-only-command overlap; invalid-task-attribute depends on version.
- Variables: no positive reason codes; same-valued duplicates; undeclared role inputs.
- Reason codes lean to negative/uncertain; one reason code mixes semantic and actionability;
  `external_context_type` has no controlled list; `uncertain` vs `unreviewable` is unclear
  (for example 36 of 654 lines shown).
- No Ansible-version policy (OC-017, OC-028).

## 2. Bundle and evidence defects
- Every structure row is anchored at line 1 and never names the flagged construct.
- 14 variable rows do not name WHICH variable or attribute the finding is about.
- Review/history diffs omit non-YAML files (item 007: 10 of 103 paths; 008: 2 of 9; 015 omits the CHANGELOG.md diff).
- Structure listings truncated at 120 paths (18 rows; decisive in 046, 007, 013, 049).
- Windowed bundles: maintainability 020 shows lines 1-36 of 4812; five molecule-test-absent style
  bundles have no tree, so they cannot be decided.
- Handler bundles lack imported handler files; reference search is literal-name only, capped at 50 hits, noisy (039).
- Redaction over-redacts (booleans, operators), mangles syntax (042), and uses inconsistent markers
  ([REDACTED VALUE BLOCK] vs [REDACTED_LITERAL]).
- Under-redaction: see README warning (tokens, emails, key bodies).

## 3. Detector false-positive patterns seen
- Non-Ansible YAML analysed as Ansible: Kustomize JSON6902 patches (3 of 4 unnamed-task rows), mkdocs, Taskfile.
- missing-file-extension fires on references that have an extension.
- become-scope-too-broad fires on any play-level become (0/8 clearly positive).
- large-task flags 11-24 line tasks; large-play flags a 24-line play; complex-playbook and
  large-playbook anchor on a role task or data file (wrong unit).
- incomplete-task matches "hack" in a font name and a URL path (my regex fix handles `containerd-hack`; standalone "Hack" / `hack/` still match).
- unused-handler/missing-handler are cross-file and mis-resolve.
- non-idempotent-command fires on guarded or read-only probes; read-only-command-change fires when a pipeline ends in `umount`.
- invalid-task-attribute-type: list-valued vars are version-dependent; quoted 'yes' booleans.
- unguarded-variable ignores an earlier set_fact; unscoped-shell-variable fires inside a quoted heredoc or command module.
- missing-bug-reference misses explicit references (018, 040, 042).
- loop-legacy-syntax 8/8 positive, but low severity. role-readme-absent is a true positive when the listing is complete.

## 4. Sampling frame concerns
- Rule-stratified round-robin over-represents bot and merge commits (about 20 of 42 message rows).
- Near-duplicate twin rows from the same repository.
- A vendored third-party role (konstruktoid.hardening) is inside the sampling frame.

## 5. Process notes
- A shared `/tmp` helper was overwritten between parallel agents; labels were re-read and no contamination found.
- Rate limits stopped four agents; resumed via SendMessage with no loss.
- Labels were written family by family and validated only at assembly (0 violations).
