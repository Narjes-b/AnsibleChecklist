# Family v2: objective correctness
Question: does the frozen source violate the rule's documented correctness, reliability, dependency or compatibility condition in ansible-core 2.21 (COMMON_V2 C1)?

Rule-specific operational definitions:
- `loop-legacy-syntax`: positive when a `with_*` loop keyword is present on the task. This is a **deprecation-style** claim, not a claim of failure; actionability is normally `advisory`.
- `redirected-module`: positive when the module name resolves through ansible-core 2.21 routing to a different FQCN. Name the target in notes. Not decidable from memory: use C1/C3.
- `unpinned-ansible-dependency`: positive when the declared dependency has no version constraint. Scope: `requirements.yml` entries and `meta/main.yml` `dependencies`/`collections`; a sibling role in the same repository is out of scope (negative, `out-of-scope`).
- `non-idempotent-command` / `read-only-command-change`: positive only when the command is not guarded (`creates`, `removes`, `changed_when`, `when` on prior state) / the command is read-only and the task reports change. A read-only probe with `changed_when: false` is negative. `changed_when: true` is not a guard. A bare `gather_facts:` task is the valid `ansible.builtin.gather_facts` module. A key inside a `set_fact` data mapping is data, not a task attribute.
- `invalid-task-attribute-type` / `invalid-numeric-value`: judge against 2.21 attribute types. A quoted boolean string accepted by 2.21 (for example `become: 'yes'`) is negative; a list given where a mapping is required (for example `vars:` as a list of mappings) is positive (checked against ansible-core 2.21 syntax-check).
- `silent-error-suppression`: a task has `ignore_errors: true` or `failed_when: false` and its registered result is never inspected afterwards (no later `when`/`failed_when`/`changed_when`/`until`/`var`/`that` reference, including connected task files shown) and the task is not the target of a `rescue`. No register at all = no recovery. Positive = this holds; a deliberate best-effort probe is positive with `advisory`/`low-value`.
- `missing-handler`: a `notify` names a handler that does not exist in the play, its roles' handlers, or imported handler files visible in the bundle. If handlers from imported roles are not shown: `uncertain` + bundle_issue `missing-file`.
- `overriden-keys`: the same mapping key appears twice in one YAML mapping (the later value silently wins). Positive by parser fact; name the key.
- `deprecated-modules`: positive when the module is marked deprecated in 2.21 routing/metadata.

Positive semantic reasons: `confirmed-defect`, `confirmed-redirect` (the module name routes to a different FQCN in ansible-core 2.21 routing; evidence must be in the bundle's routing facts, else `uncertain` + `collection-docs`), `confirmed-duplicate-key`, `confirmed-silent-suppression`, `confirmed-missing-handler`, `confirmed-removed-syntax` (for example bare `include:`, removed in ansible-core 2.16, so it fails on 2.21),  `confirmed-deprecation`, `confirmed-unconstrained-dependency`, `confirmed-unguarded-command`.
Negative: `condition-absent`, `valid-guard-or-reference`, `accepted-in-2.21`, `out-of-scope`.
Uncertain: `external-dependency`, `dynamic-execution`, `ansible-version`.
