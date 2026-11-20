# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-025

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: objective_correctness
- Rule: `ansibleguard/overriden-keys`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `playbooks/utils/journal_ctl.yml` (reported anchor line 10)
- Flagged construct: task `unknown`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–37 of 37:

```text
    1 | ---
    2 | # by default this playbook runs in the staging environment
    3 | # to run in qa, pass '-e runtime_env=qa'
    4 | # to run in production, pass '-e runtime_env=production'
    5 | # and will need to be manually updated
    6 | - name: modify journalctl logging
    7 |   hosts: "{{ runtime_env | default('staging') }}"
    8 |   remote_user: pulsys
    9 |   serial: 2
   10 |   remote_user: pulsys
   11 |   become: true
   12 |   vars_files:
   13 |     - ../group_vars/all/vault.yml
   14 | 
   15 |   tasks:
   16 |     - name: update cap size to 100MB
   17 |       ansible.builtin.lineinfile:
   18 |         dest: /etc/systemd/journald.conf
   19 |         line: "SystemMaxUse=100M"
   20 |         regexp: "^#SystemMaxUse"
   21 |         state: present
   22 | 
   23 |     - name: update cap size of logs to 7
   24 |       ansible.builtin.lineinfile:
   25 |         dest: /etc/systemd/journald.conf
   26 |         line: "SystemMaxFiles=7"
   27 |         regexp: "^#SystemMaxFiles=100"
   28 |         state: present
   29 | 
   30 |     - name: apply new settings
   31 |       ansible.builtin.command: journalctl --rotate
   32 | 
   33 |     - name: tell everyone on slack you ran an ansible playbook
   34 |       community.general.slack:
   35 |         token: "{{ vault_pul_slack_token }}"
   36 |         msg: "Ansible ran `{{ ansible_play_name }}` on {{ inventory_hostname }}"
   37 |         channel: "{{ slack_alerts_channel }}"
```
