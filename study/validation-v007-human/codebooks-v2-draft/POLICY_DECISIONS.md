# Codebook v2: policy decisions needed (DRAFT, not frozen)

Frozen codebooks under `../codebooks/` are untouched. Each row lists a term the pilot showed to be
undefined, the proposed default, and why. **Status (2026-10-16): all 16 proposed defaults CONFIRMED by the study owner ("confirm confirm"). They are the codebook v2 policy; the frozen family codebooks must be revised to match before pilot 2.**

| # | Topic | Proposed default | Why / evidence |
|---|---|---|---|
| 1 | Ansible version for judgments | Judge against one stated ansible-core (the version used in the run, 2.21), unless the bundle shows a pinned version | OC-017 (list-valued `vars` rejected by 2.21), OC-028 (`authorized_key` redirect) |
| 2 | `loop-legacy-syntax` | Positive = deprecated-style usage present; separate from "breaks execution" | ansible-core accepts `with_*`; wording is policy; 8/8 positive |
| 3 | Dependency findings | Evidence must be in the bundle; outside knowledge → uncertain | SEC-041 |
| 4 | Placeholder credentials in test/vagrant fixtures | Define "documented example" vs "real default"; decide positive/negative | security disagreements |
| 5 | Module-level `no_log` | State whether the module's own argument-spec `no_log` counts | credentials-leaking-in-log (74 % of security) |
| 6 | Bug reference | Define accepted forms (issue id, URL, `Fixes #n`); is a PR number one? | RH-026, missing-bug-reference misses |
| 7 | Commit subject length | Use the rule's own predicate: subject ≤ 50, blank line after subject, body lines ≤ 72 (checked against the detector source) | style/review disagreements |
| 8 | Bot and merge commits | Not applicable for message rules | about 20 of 42 message rows |
| 9 | Size/complexity terms (long name, long statement, large, coupling, nesting) | Anchor to the rule's configured threshold; the question is only "is the construct correctly measured", plus a separate threshold panel | STYLE-047, STRUCTURE-030 |
| 10 | Structure findings | Bundle must name the construct; otherwise `unreviewable` with reason `bundle-defect` | every structure row is anchored at line 1 |
| 11 | Positive reason codes | Add positive codes per family (e.g. `confirmed-defect`, `confirmed-policy-violation`) | codes lean negative/uncertain |
| 12 | Reason-code semantics | Split into `semantic_reason` and `actionability_reason` | single code mixes both |
| 13 | `external_context_type` | Controlled list (e.g. none, ansible-version, collection-docs, other-repo-file, runtime-value) | free text today |
| 14 | `uncertain` vs `unreviewable` | `unreviewable` = bundle defect or missing evidence; `uncertain` = evidence complete, judgment open | e.g. 36 of 654 lines shown |
| 15 | Overlapping rules | Label each item on its own rule; record overlap in notes | non-idempotent vs read-only |
| 16 | Vendored third-party roles | Out of the sampling frame | konstruktoid.hardening in frame |
