# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-030

- Repository: `mageops/ansible-infrastructure`
- Commit: `5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8`
- Family: Objective correctness
- Rule: `ansibleguard/unpinned-ansible-dependency`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/cs.aws-lambda-varnish/meta/main.yml` (reported anchor line 1)
- Object: `source_location` `f5cd1fd507e7de770cee83de2cd5a64b435d3ad4bd184bc159bd4ea27b842540`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–2 of 2:

```text
    1 | dependencies:
    2 |   - role: cs.ansible-plugins
```
