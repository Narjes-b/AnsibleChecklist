# Frozen source context: V007PILOT-SECURITY-022

- Repository: `gantsign/development-environment`
- Commit: `eeffd50b7a2a5b2a6c218bc1ff9ecb93789968d4`
- Family: Security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `provisioning/playbook.yml` (reported anchor line 2)
- Object: `source_location` `07ba59a7cf89c6673a1ab88deb4527ef11143a26b9fd74f49f3b521ddc09f873`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–37 of 687:

```text
    1 | ---
    2 | - hosts: all
    3 |   become: true
    4 | 
    5 |   vars:
    6 |     x_ansible_download_dir: /usr/local/src/ansible/data
    7 |     intellij_edition: community
    8 |     my_user: dev
    9 | 
   10 |   pre_tasks:
   11 |     - name: Update apt cache
   12 |       ansible.builtin.apt: update_cache=true cache_valid_time=86400
   13 | 
   14 |     - name: Update all packages to the latest version
   15 |       ansible.builtin.apt:
   16 |         upgrade: dist
   17 | 
   18 |     # zram shouldn't be used with Zswap
   19 |     - name: Ensure zram-config absent
   20 |       ansible.builtin.apt:
   21 |         name: zram-config
   22 |         state: absent
   23 | 
   24 |     # Workaround https://docs.ansible.com/ansible-core/2.15/playbook_guide/playbooks_privilege_escalation.html#risks-of-becoming-an-unprivileged-user
   25 |     - name: Enable access control lists
   26 |       apt:
   27 |         name: acl
   28 |         state: present
   29 | 
   30 |   roles:
   31 |     # Preserve the apt cache
   32 |     - role: gantsign.apt
   33 |       apt_preserve_cache: true
   34 | 
   35 |     # Set system timezone
   36 |     - role: gantsign.timezone
   37 |       timezone: Europe/London
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.
