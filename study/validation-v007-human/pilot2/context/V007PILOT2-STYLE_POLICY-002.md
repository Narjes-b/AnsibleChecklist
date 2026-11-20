# Frozen source context: V007PILOT2-STYLE_POLICY-002

- Repository: `redhat-cop/aap_configuration_extended`
- Commit: `b58344f735518744459c0501cf8971c0541f0caa`
- Family: style_policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `playbooks/upgrade_config.yaml` (reported anchor line 10)
- Flagged construct: task `call upgrade_config role`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–17 of 17:

```text
    1 | ---
    2 | #
    3 | # ansible-playbook -i localhost, playbooks/upgrade_config.yaml -e '{sanitize: true}'
    4 | #
    5 | - name: "Playbook to upgrade CaC from AAP <= 2.4 to AAP >= 2.5 format"
    6 |   hosts: localhost
    7 |   connection: local
    8 |   gather_facts: false
    9 |   tasks:
   10 |     - name: "Call upgrade_config role"
   11 |       ansible.builtin.include_role:
   12 |         name: infra.aap_configuration_extended.upgrade_config
   13 |       vars:
   14 |         aap24_configs_dir: "/tmp/aap24"
   15 |         aap25_configs_dir: "/tmp/aap25"
   16 |         input_authenticator_name: "IDM LDAP"
   17 | ...
```
