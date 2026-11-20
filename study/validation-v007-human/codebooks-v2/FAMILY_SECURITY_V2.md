# Family v2: security
Question: is the documented exposure or unsafe configuration present, and is a remediation proportionate here?

Operational definitions:
- **Placeholder vs real credential.** A value is a placeholder when it is a documented example (`changeme`, `example`, `<password>`, `vagrant` in a Vagrant/test fixture) or a Jinja reference. A placeholder in a test/molecule/vagrant fixture: semantic `positive` only if the rule is about the pattern (`default-credentials`); actionability `not-actionable`, reason `test-or-fixture-context`. A real-looking secret in production paths: positive and `actionable`.
- **`no_log`.** Task-level `no_log` counts. Module-level protection (argument-spec `no_log` on the specific parameter, per ansible-doc for 2.21) counts as protection when the bundle shows the module. A dynamic `no_log: "{{ x }}"` is `uncertain` (`runtime-value`).
- `insecure-permissions`: positive when the mode grants world write, or world read on a path holding secrets/keys; judge the protected object.
- `become-scope-too-broad`: positive when a play sets `become: true` at play level and contains at least 5 leaf tasks (the rule's threshold; the rule cannot tell which tasks need root). Semantic label = predicate holds. Actionability: `advisory` normally; `not-actionable` when the play's tasks visibly all need privilege (package, service, system files) or `become_user` is unprivileged; `actionable` when clearly read-only/unprivileged tasks dominate.
- `missing-validate-certs`: positive when `validate_certs` is false for a module that honours it (ansible-doc).
- `unsafe-file-write`: positive when `unsafe_writes: true`.

Positive semantic reasons: `confirmed-broad-privilege`, `confirmed-exposure`, `confirmed-unsafe-permission`, `confirmed-tls-bypass`, `confirmed-unsafe-write`, `confirmed-default-credential`.
Negative: `not-sensitive-or-not-exposed`, `safeguard-present`, `placeholder-or-reference`.
Uncertain: `runtime-value`, `organization-policy`, `redaction-hides-value` (the value block is redacted and no surrounding evidence separates a placeholder from a real secret; also set bundle_issue `redaction-hides`).
