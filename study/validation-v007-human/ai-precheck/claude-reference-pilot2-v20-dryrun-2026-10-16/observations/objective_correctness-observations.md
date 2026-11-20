# Observations: objective_correctness (pilot2, 25 items)

## Process / tooling
- check_labels.py fails as shipped on this input: codebook_path is already `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md` and v2_family_file appends `_V2` again (FileNotFoundError for `..._V2_V2.md`). I ran the checker on a temp copy of the input with the v1 path (`codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`): 0 problems.
- Bundle headers say `Codebook: codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md` (v1) while the input list points to the v2 file (all items).

## Codebook gaps (FAMILY_OBJECTIVE_CORRECTNESS_V2.md)
- No operational definition for `silent-error-suppression` (006, 013, 020), `missing-handler` (024) or `overriden-keys` (025). I judged from the rule name; positives for 006/013/020/025 used `other` or `confirmed-defect`.
- `redirected-module` (005, 012, 019): positive reasons are only confirmed-defect / confirmed-deprecation; a redirect is neither. Suggest a `confirmed-redirect` reason. Also the C3 instruction to decide routing from "documentation facts" needs a routing table in the bundle; I relied on memory of ansible-core runtime.yml (sysctl, docker_container, acl -> collection FQCNs), which C1 discourages.
- `non-idempotent-command` (010): unclear whether an unconditional `changed_when: true` counts as a guard. Family text lists changed_when as a guard, but it does not guard anything. Judged negative with low confidence.
- `non-idempotent-command` (017): a `when` on an unrelated precondition (prior-state check of another package) is borderline as a "when on prior state" guard.
- `unpinned-ansible-dependency` (007, 014, 021): role dependencies in meta cannot carry a version, and `meta collections:` is a search path that cannot either; scope text says both are in scope. Siblings are out of scope but the bundle shows no repo tree/galaxy.yml, so sibling status cannot be verified (007, 014 uncertain, other-repo-file).
- `invalid-task-attribute-type` (008, 015): "list where mapping required is positive", but whether ansible-core 2.21 still accepts `vars:` as a list of dicts (older versions did) is not decidable from the bundle. Labelled positive, low confidence; arguably should be uncertain/ansible-version if the codebook author cannot confirm.
- `invalid-numeric-value` (023): `port: 0` is a key in a set_fact dict, not a task/module attribute; the detector seems to match any `port` key.

## Detector false-positive patterns
- 001: bare task `gather_facts:` is the valid ansible.builtin.gather_facts module, flagged as keyword with null value.
- 022: quoted boolean `'yes'` for `become` is accepted by 2.21.
- 023: data-dict `port: 0` in set_fact flagged as invalid numeric value.
- 011: `read-only-command-change` fired on a shell that deletes files (`xargs rm -rf`).

## Bundle notes
- 008: anchor line 189 is the enclosing block, the offending `vars:` list is at line 224 (35 lines later); header says "attribute vars" so it was usable, but the anchor does not sit on the construct.
- 002-004, 006, 009, 010, 011, 013, 016-020, 024: "Asserted subject" is the placeholder `location`, not a real subject.
- 024: handler bundle shows only the play's own imported handlers file; handlers from `import_role` roles (which join the play handler namespace) are not shown, so absence of a handler cannot be established (C7 contract gap).
- 025: header says flagged construct is task `unknown`; the finding is actually the duplicate play-level key.
- 004: redaction markers appear inside the earlier shell heredoc (lines 91, 101, 110-111) but do not affect the flagged task.
- 010: bundle excerpt is complete; head of file needed only to confirm fresh tempdirs.
