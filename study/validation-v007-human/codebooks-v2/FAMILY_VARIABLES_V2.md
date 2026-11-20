# Family v2: variables and references
Question: what is the strongest conclusion the frozen evidence supports about the variable condition? The bundle names the variable or attribute (COMMON_V2 C7); if it does not, `unreviewable` / `bundle-defect`.

Operational definitions:
- A variable is **defined** if it appears in a `vars`, `defaults`, `set_fact`, `register`, loop variable, or an included vars file visible in the bundle.
- A variable is a **declared input** if the role's defaults, meta argument specs or README list it. An undeclared input used without a guard is `positive` for `unguarded-variable` but `actionability` normally `advisory`.
- Same-valued duplicate definitions: `redundant-default-value` positive; `role-variable-precedence-collision` positive only when values differ or both layers exist.
- A prior `set_fact`/`register` on the same path makes a later use guarded (negative).
- `overriding-facts`: a `set_fact` assigns the same fact more than once on the same execution path with a different value, losing the earlier one. Repeating it in mutually exclusive `when` branches or as an intentional accumulator/reset is negative (`condition-absent`).
- `unscoped-shell-variable`: inside a quoted heredoc or `command` module (no shell expansion) the finding is negative; evaluate in the task's actual shell.

Positive semantic reasons: `confirmed-unresolved-reference`, `confirmed-order-conflict`, `confirmed-unused-value`, `confirmed-redundant-value`, `confirmed-precedence-collision`.
Negative: `condition-absent`, `module-parameter-not-variable` (a module parameter key such as `nics:` read as a variable), `non-ansible-yaml`, `visible-definition`, `visible-guard`, `valid-precedence`, `scope-mismatch`.
Uncertain: `runtime-input-possible`, `dynamic-reference`, `inventory-or-caller`.
