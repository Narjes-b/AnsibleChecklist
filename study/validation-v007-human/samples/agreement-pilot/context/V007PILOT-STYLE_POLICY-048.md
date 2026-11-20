# Frozen source context: V007PILOT-STYLE_POLICY-048

- Repository: `usegalaxy-eu/infrastructure-playbook`
- Commit: `13681d4e758b42aeeb7e12aac62243e76a5c04fb`
- Family: Style/policy
- Rule: `ansibleguard/missing-tags`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/denbi.osiris/tasks/main.yml` (reported anchor line 28)
- Object: `task` `8470529813021b209215feefec7ffd131f6e1542bb48f6ad1578a8fb4408c208`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–48 of 48:

```text
    1 | ---
    2 | - name: "Install dependencies for OSIRIS or system use"
    3 |   ansible.builtin.dnf:
    4 |     name: "{{ item }}"
    5 |     state: present
    6 |   loop: "{{ osiris_dependencies }}"
    7 | 
    8 | - name: "Configure restic backups"
    9 |   ansible.builtin.include_tasks: configure_restic.yml
   10 | 
   11 | - name: "Check if we should restore the latest backup"
   12 |   ansible.builtin.stat:
   13 |     path: "{{ restore_backup_semaphore_path }}"
   14 |   register: backup_status_register
   15 | 
   16 | - name: "Invert conditional logic for readability"
   17 |   ansible.builtin.set_fact:
   18 |     restore_backup: "{{ not backup_status_register.stat.exists }}"
   19 | 
   20 | - name: "Perform backup before changes/updates if not restoring"
   21 |   ansible.builtin.include_tasks: perform_backup.yml
   22 |   when: not restore_backup
   23 | 
   24 | - name: "Restore backup from restic"
   25 |   ansible.builtin.include_tasks: restore_from_restic.yml
   26 |   when: restore_backup
   27 | 
   28 | - name: "Use restored backup"
   29 |   ansible.builtin.include_tasks: apply_backup_files.yml
   30 |   when: restore_backup
   31 | 
   32 | - name: "Ensure OSIRIS configuration and permissions"
   33 |   ansible.builtin.include_tasks: osiris_configuration.yml
   34 | 
   35 | - name: "Ensure OSIRIS version matches configuration"
   36 |   ansible.builtin.include_tasks: osiris_version.yml
   37 | 
   38 | - name: "Configure SELinux for OSIRIS"
   39 |   ansible.builtin.include_tasks: selinux.yml
   40 | 
   41 | - name: "Delete/Cleanup backup directories"
   42 |   ansible.builtin.include_tasks: delete_backup_dir.yml
   43 | 
   44 | - name: "Configure certbot and SSL certs"
   45 |   ansible.builtin.include_tasks: certbot_ssl.yml
   46 | 
   47 | - name: "Configure firewall restrictions"
   48 |   ansible.builtin.include_tasks: firewall.yml
```
