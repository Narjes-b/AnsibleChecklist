# Frozen source context: V007PILOT2-STYLE_POLICY-011

- Repository: `opendevshop/devshop`
- Commit: `98f107b4c7146af38074b9b1e8e78a69a766f10a`
- Family: style_policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `devmaster/modules/devshop/aegir_ansible/playbook.yml` (reported anchor line 6)
- Flagged construct: not named by the finding; the anchor line 6 lies in the task at line 6, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–16 of 16:

```text
    1 | ---
    2 | - hosts: ansible_mysql
    3 |   roles:
    4 |   - aegir.user
    5 |   - geerlingguy.mysql
    6 | - hosts: ansible_apache
    7 |   roles:
    8 |   - aegir.apache
    9 |   - geerlingguy.php
   10 |   - geerlingguy.php-mysql
   11 |   - geerlingguy.composer
   12 | - hosts: nginx
   13 |   roles:
   14 |   - aegir.nginx
   15 |   - geerlingguy.php
   16 |   - geerlingguy.php-mysql
```
