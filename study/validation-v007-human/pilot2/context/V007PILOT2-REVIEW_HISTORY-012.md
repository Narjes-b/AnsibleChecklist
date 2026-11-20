# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-012

- Repository: `redhat-cop/infra.aap_configuration`
- Target commit: `f84d6a61e4b18aa135d707fe539371587bc92931`
- Actual first parent: unavailable (not required for message-only rules)
- Evidence type: exact target commit message only
- Family: review_history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
Default aap_request_timeout to 10 for blank AAP credential injection (#1434)

* Fix empty aap_request_timeout from AAP credentials in hub roles

Hub roles used default(omit) without the true flag, so credential-injected
empty strings were passed to ansible.hub modules and failed float validation.
Align hub roles with controller/gateway/eda by using default(omit, true).

Co-authored-by: Cursor <[REDACTED_EMAIL]>

* Remove unintended aap_request_timeout dispatch argument spec

The hub role default(omit, true) fix does not require dispatch argument
spec changes.

Co-authored-by: Cursor <[REDACTED_EMAIL]>

* Default aap_request_timeout to 10 for credential-injected empty values

Use default(10, true) across all roles and set aap_request_timeout: 10 in
global_vars so GitOps jobs with blank request_timeout on the AAP credential
always pass a valid float instead of an empty string.

Co-authored-by: Cursor <[REDACTED_EMAIL]>

* Update main.yml

---------

Co-authored-by: Cursor <[REDACTED_EMAIL]>
```

## Changed paths (not required for message-only evidence)


The rule is evaluated only on the exact target commit message above.
