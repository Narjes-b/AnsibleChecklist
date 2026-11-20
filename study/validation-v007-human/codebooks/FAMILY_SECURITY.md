# Family codebook: security

## Review question

Is the documented security exposure or unsafe configuration actually present in the frozen source, and what concrete remediation is justified in this repository context?

## What to inspect

Inspect the complete cited task/module arguments, relevant variable source or template, nearby `no_log`, permission/mode, TLS, privilege-escalation, and file-operation context. Do not infer secret exposure from a variable name alone. Do not reveal literal credentials in notes.

## Semantic labels

- `positive`: the described exposure or unsafe security condition is supported by the evidence.
- `negative`: a relevant safeguard is present, the value is not sensitive/exposed as claimed, or the security premise is not met.
- `uncertain`: sensitivity, threat model, runtime source, destination, or compensating control cannot be determined from the supplied evidence.
- `unreviewable`: required security-relevant source context is unavailable/corrupt.

## Family-specific cautions

- Separate “credential-like identifier” from an actual sensitive value; do not copy the value into the worksheet.
- `no_log` omissions are evidence about logging protection, not proof that the task contains a secret.
- TLS verification and permissions must be judged for the actual target/resource and deployment context supplied.
- Broad privilege escalation is a scope/risk question; inspect whether every task in scope needs it.
- Inline encrypted values can still create operational, review, or rotation risk, but an organization-specific volume threshold is not itself a security breach.
- `actionability_label` records remediation priority separately from whether the security predicate is true.

## Reason codes

`sensitive-value-supported`, `not-sensitive-or-not-exposed`, `safeguard-present`, `unsafe-permission-or-write`, `privilege-scope`, `tls-validation`, `logging-protection`, `organization-policy`, `runtime-context-needed`, `insufficient-source-context`, `other`.
