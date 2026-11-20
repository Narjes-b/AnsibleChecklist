# Observations: objective_correctness reference labels (50 rows)

## (a) Counts and hardest items
- semantic_label: positive 28, negative 12, uncertain 10, unreviewable 0.
- actionability: advisory 18, actionable 7, uncertain 3 (positive rows 008, 023, 030), not-applicable 12 (negatives), uncertain 10 (uncertain rows).
- reason_code: condition-present 26, condition-absent 7, valid-guard-or-reference 5, version-compatibility 7, insufficient-source-context 5.
- bundle_issue != none: 14 (001, 003, 006, 009, 011, 016, 017, 021, 024, 028, 034, 036, 040, 048).
- Five hardest items:
  1. 002 (and the whole loop-legacy-syntax group 010/018/025/031/037/043/049): with_items is not deprecated or removed. I labelled positive because the legacy construct is present and `loop` is available, but "compatibility/deprecation" could justify negative. Largest source of likely disagreement (8 rows).
  2. 016/036/048: meta `collections:` only, `dependencies: []`. Is a meta collections search-path list a "declared dependency"? Labelled uncertain (low confidence).
  3. 008/023/030: bare role dependency, possibly a sibling role (local), so pinning may not apply. Labelled positive (literal reading) with actionability uncertain; low/medium confidence.
  4. 006/021/028/034/040 vs 014/046: redirected-module with no Ansible version in the bundle. I inferred >=2.10 only from FQCN conventions (014) or the `truthy` test (046); the rest uncertain. Inference-based, fragile.
  5. 001/009/017/024: invalid-task-attribute-type where the flagged attribute is not named. I judged list-of-dict `vars:` and quoted 'yes' booleans as valid from my own Ansible knowledge (Base._load_vars merges lists; bool coercion). If a reviewer thinks otherwise, they would call these positive.

## (b) Bundle defects
- 003, 011 (missing-handler): notify target may be defined in handlers/main.yml, pulled in via import_tasks in `handlers:`. The file is not in the bundle, so the decisive evidence is absent (labelled uncertain).
- 001: anchor is line 1 (`---`); no attribute is identified. 009, 017, 024 also do not name the flagged attribute (anchor is the task start).
- 008, 016, 023, 030, 036, 042, 048: anchor line 1 although the dependency is at line 42/45/15/2 etc.; line 1 is not the subject.
- 006, 021, 028, 034, 040: no Ansible/collection version context, which the override says is needed ("frozen version/context").
- Anchors point to the task start rather than the `ignore_errors` line (007, 015, 022, 029, 035, 041): minor.
- 010: window excerpt (1685-1755 of 4812) is adequate but note the bundle is partial by design.
- Redaction side effects: `[REDACTED_LITERAL]` swallows the rest of the line and breaks quoting (027 L103, 038 L136, 040 L38/59/70, 031 Authorization headers). Did not hide decisive evidence but can confuse. No residual secrets noticed. 028 shows an SSH public key (not secret).
- 011: unrelated bug visible: changed_when string 'Set dropbear...' vs echoed 'Set Dropbear...' (case mismatch). 035 L86 is a syntax error (`when: ... "raspbian" Swap_Val`). Out of scope.

## (c) Codebook / override ambiguities
- Codebook positive definition: "the rule's concrete condition is present and the stated behavior/compatibility issue follows from the source." For legacy loops the "issue" may not follow. Fix: add per-rule predicate lines (e.g. "loop-legacy-syntax: positive when any with_* is used and no evidence of Ansible <2.5; deprecation is not required").
- Override for loop-legacy-syntax: "Evaluate actual compatibility/deprecation for the supported Ansible context." Contradicts a purely syntactic condition; state which.
- Redirected-module override: "Verify module identity and redirect target in the frozen version/context." Bundles carry no version; fix: either supply min_ansible_version/collections requirements in bundle or define default assumption (e.g. assume current ansible-core unless evidence of <2.10).
- Unpinned dependency: "inspect the declared source and constraint" does not say whether meta `collections:`, sibling local roles, or same-collection FQCN roles count as dependencies. Fix: define in-scope declaration forms.
- Codebook "positive validates only the rule's semantic condition" vs "stated behavior issue follows": for silent-error-suppression, deliberate best-effort `ignore_errors` (007, 015, 022, 047) is still positive in my labelling; the codebook should say whether intent matters (I handled intent via actionability).
- Read-only-command-change vs non-idempotent-command boundary (044, 050, 005): `changed_when: rc==0` on a read-only probe is a false-change report, yet I labelled non-idempotent negative. Rules overlap; state which applies.
- Vars list-of-dicts: codebook says "do not assume a parser warning proves a runtime defect" but gives no policy for type checks relying on Ansible internals.
- actionability for uncertain semantic rows: instructions allow `uncertain`; positive rows with unknown pin applicability (008/023/030) used `uncertain`: guidance needed.

## (d) Detector patterns
- invalid-task-attribute-type (001, 009, 017, 024): all four judged false positive. Mechanisms: list-of-dict `vars:` (accepted by Ansible), quoted 'yes'/'no' booleans (coerced).
- non-idempotent-command: 004 (changed_when false), 012 (found==0 guard), 019 (changed-guarded), 038, 044, 050 (read-only probes with changed_when/when guards): false positives; true positives 026, 032 (unguarded download/append scripts).
- read-only-command-change: true positives 013, 020, 033, 039, 045 (read-only shell/command with no changed_when); false positives 005 (pipeline ends in umount), 027 (publish script mutates).
- silent-error-suppression: all 7 true positives by the condition (ignore_errors with no result check), mostly benign best-effort cleanup (015, 022, 047, 041); heavier risk in 007, 029, 035.
- loop-legacy-syntax: 8/8 true positives for presence of with_*; low practical severity.
- redirected-module: 1 positive (014), 1 positive (046), five uncertain; module redirect itself is real for >=2.10.
- missing-handler: both uncertain; detector likely does not follow import_tasks in handlers.
- unpinned-ansible-dependency: mostly literal positives for bare role deps; collections-only meta uncertain.

## (e) Sampling / evidence generation concerns
- Rule mix (8/8/7/7/7/7/4/2) with only two missing-handler rows, both unresolvable from the bundle: the family has a bundle-design weakness there.
- Near-duplicate rows: 036 and 048 (ansible-lockdown twins), 009/017 (same vars mechanism); repeated patterns inflate agreement or disagreement on one decision.
- Bundles for dependency rules lack galaxy.yml/requirements.yml/role tree; handler bundles lack imported handler files; module-redirect bundles lack version. Bundle generator should include files referenced by import_tasks/include and project metadata.
- Anchor lines are inconsistent (task start, line 1, or dependency line missing), obscuring the detector's actual subject.
- Detector claim is not stated in bundles, so for attribute-type rows the subject must be guessed.

## (f) Rule definition vs codebook
- loop-legacy-syntax: rule is syntactic (legacy with_*), codebook/override asks for actual compatibility or deprecation; these disagree for supported with_items.
- unpinned-ansible-dependency: rule treats missing version as the flaw; codebook says reproducibility impact is actionability, not proof, which was applied literally for bare role deps.
- non-idempotent-command / read-only-command-change: overlapping scopes (see c).
- redirected-module: rule is catalog-based (name matches redirect table); codebook requires frozen version context that bundles do not supply.
