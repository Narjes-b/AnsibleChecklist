# Observations: variable_reference_reasoning (50 rows)

## (a) Counts and hardest items
Semantic: negative 22, positive 16, uncertain 11, unreviewable 1. Confidence: high 20, medium 22, low 8. bundle_issue != none: 20 (other:variable-not-named 14, truncated-evidence 5, codebook-ambiguous 1).

Five hardest items:
1. 002 (overriding-facts): default-then-overwrite initialisation. Visible, harmless, never read. Codebook does not say whether a dead initialisation counts. Labelled positive, low confidence.
2. 029 (overriding-facts): k3s_postinstall false then true around a re-rendered template. The template (config.j2) is not in the bundle. Labelled negative on inference, medium confidence.
3. 021 (redundant-default-value): the value is passed to a different role's include_role. The comparison default belongs to the caller role. Labelled uncertain.
4. 048 (use-before-definition): checkpoints_match is read before it is set, saved by `or` short-circuit and by a caller-owned retry_count. Labelled uncertain.
5. 023 (unguarded-variable): edpm_ovs_external_ids is set only inside a block whose guard default is not shown. Labelled uncertain. 036 (negative, low) is a close sixth, because a bare list in `when` depends on the ansible-core version.

## (b) Bundle defects
- No bundle shows the detector's message, so none names WHICH variable or expression is asserted. This matters most where several candidates share a line or file: 009, 018, 035, 043, 049 (loop var vs certbot_cert_path), 031, 039, 008 (anchor is a task header; the register is 36 lines lower). 14 rows are flagged other:variable-not-named.
- missing-bool-filters (001, 010, 019, 028, 036) and overriding-facts (002, 011, 020, 029, 037) are anchored at line 1 (comment, `---`, or an import). The excerpt does not locate the finding.
- 011: only lines 1-36 of 546 are shown, with no assignment visible. Labelled unreviewable.
- 034, 047: source shown as a window only (180-250 of 550; 377-447 of 991). The repo search compensated.
- 031: reference search truncated after 50 hits, none a definition.
- 039: the search returned 50 CircleCI lines (probably the token `app`), so it was useless. The truncation hid the relevant hits.
- 006: search truncated at 50. Several searches are exact-name only and miss dynamic access.
- Redaction swallows following script lines (041, 046, 009, 010, 045, 012). Decisive evidence survived in every case. 046's heredoc looks unbalanced because of it.
- 049: the search covers only certbot_cert_path, not `account` or certbot_accounts.

## (c) Codebook and override ambiguities
- Reason codes are all negative- or uncertainty-oriented (`visible-definition`, `valid-precedence`, `visible-guard`, ...). Only `unused-value-supported` suits a positive. Positives for precedence collision and overriding then need `visible-definition` or `other`. I used `other` 10 times, notably for "value is used elsewhere" (006, 008, 026, 032, 040, 045) and "command module does no shell expansion" (033). Fix: add `value-consumed`, `no-shell-expansion`, `duplicate-definition`, `dead-overwrite`.
- Codebook: "`positive`: ... no relevant visible definition, guard, ordering, or contract resolves it." This does not say what the positive condition is for rules whose defect is the duplication or redundancy itself (003, 004, 013, 022, 030). Fix: state per rule what constitutes positive.
- Same-valued duplicates in defaults and vars (004, 013, 022, 030): harmless today but the override contract is broken. Humans may split between positive and negative. Fix: say whether identical values count.
- "unguarded-variable ... Separate visible missing definitions from undeclared input contracts": 031 and 049 are pervasive unguarded inputs with no visible definition. Positive or uncertain is a coin toss. Fix: define when an undocumented required input is positive.
- missing-bool-filters: "A quoted Boolean string ... must be judged by actual expression/expansion semantics". It does not say how to treat comparison with a string literal `== "true"` when the variable type is unknown. I used uncertain for 001, 010, 019, 028.
- RULE_OVERRIDES describes unnecessary-set-fact as "whether the fact is truly unused in scope". Is a value consumed only by another role or by caller code (006, 024) in scope? Fix: define the search scope.
- No guidance on how literally to treat the actionability label for example or documentation files (047, not-actionable) or harmless dead initialisation (002).

## (d) Detector patterns
False positives (mechanism):
- unused-registered-variable: 008 and 026 are read cross-file (hostvars, role vars).
- unnecessary-set-fact: 006, 032, 040, 045 are read downstream or cross-role.
- unscoped-shell-variable: 007, 025, 033, 041, 046 are defined in the same script, are inside a quoted heredoc, or sit in the `command` module with no shell.
- unguarded-variable: 005, 014, 044 have an earlier set_fact or import.
- overriding-facts: 037 (each value consumed before reassignment) and 029.
- variable-use-before-definition: 009, 018, 027 (string literal in `not in hostvars`), 035, 043.

True positives:
- Unused registers: 017, 034, 042, 047.
- Dead set_fact: 015, 024, 050.
- Genuine precedence conflicts: 004, 013, 038 (different values, a real bug), 022, 030.
- 020 is the clearest overriding-facts true positive. The `when:` is mis-indented under set_fact, so both set_facts run unconditionally and the custom PEM is always overridden.

## (e) Sampling and evidence-generation concerns
- The reference search is literal-name only and truncates at 50 hits, so noisy substrings (039) or common names (031) defeat it. It should drop non-YAML noise and rank definitions first.
- The pilot rule mix is one per rule per round, with many rows anchored at line 1 for rules the detector cannot locate. It is a small, rule-stratified sample.
- Some roles appear multiple times in search hits (050 and 022 copies across sibling roles). Repo clones inflate evidence.
- Bundles contain no rule definition, so a reviewer must infer the predicate from the rule name. The task forbids using the rule name as evidence, which is in tension with this.

## (f) Rule definition vs codebook
- I never saw the rule definitions, so I could not compare them to the codebook directly.
- The override table says role-variable-precedence-collision "Requires the Ansible role-variable precedence model", yet the codebook has no precedence reason code for a positive.
- overriding-facts "Requires comparing effective values and execution order", but the codebook has no guidance on intentional re-assignment (002, 029, 037).
- redundant-default-value "Requires comparing assignments with role defaults and the effective input contract": 012 and 021 depend on caller or callee scope the bundle lacks.

CSV was not changed after this write-up; I found no actual errors on re-reading.
