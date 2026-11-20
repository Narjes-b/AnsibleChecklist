# Frozen source context: V007PILOT-STYLE_POLICY-030

- Repository: `ansible/zuul-config`
- Commit: `82f3415452ef899524f4257b3cdae20b13692c87`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `playbooks/ansible-integration-config/pre.yaml` (reported anchor line 2)
- Object: `source_location` `7a3eac7bd623f91d177fc1e54da9cc2683dede4c0046de28a832e5ca469ff341`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–9 of 9:

```text
    1 | ---
    2 | - hosts: controller
    3 |   tasks:
    4 |     - name: Generate integration_config.yml with Github PAT
    5 |       ansible.builtin.copy:
    6 |         dest: /tmp/integration_config.yml
    7 |         content: |
    8 |           ---
    9 |           github_mcp_pat: "{{ ansible_mcp_github_pat.token }}"
```
