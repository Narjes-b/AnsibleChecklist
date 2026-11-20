# Frozen source context: V007PILOT-SECURITY-041

- Repository: `freeipa/ansible-freeipa`
- Commit: `5ba9b59d5b614abdb0af70fc9f2d336e5479e833`
- Family: Security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `playbooks/vault/ensure-vault-member-user-is-absent.yml` (reported anchor line 8)
- Object: `task` `f76140620889f94c87df30cd90e88f67b537c4850dd10a16ec89556e1f438cd7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–17 of 17:

```text
    1 | ---
    2 | - name: Tests
    3 |   hosts: ipaserver
    4 |   become: true
    5 |   gather_facts: false
    6 | 
    7 |   tasks:
    8 |   - name: Ensure vault member "user" is absent.
    9 |     ipavault:
   10 |       ipaadmin_password: [REDACTED_LITERAL]
   11 |       name: keychain
   12 |       username: admin
   13 |       state: absent
   14 |       action: member
   15 |       users:
   16 |       - user01
   17 |       - user02
```
