# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-017

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: maintainability_complexity
- Rule: `ansibleguard/high-coupling`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `student_cli/2_configure.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`student_cli/2_configure.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–19 of 19:

```text
    1 | ---
    2 | 
    3 | # This playbook uses "workshop_prefix" AWS Tag to 
    4 | # configure the instances. Found in group_vars/all.
    5 | - name: AWS | Install & Configure Instances
    6 |   remote_user: ec2-user
    7 |   hosts: tag_Workshop_student_cli       # AWS: workshop_prefix: 
    8 |   become: yes
    9 |   roles:
   10 |     - subscription_manager
   11 |     - jq
   12 |     - skopeo
   13 |     - epel
   14 |     - vaulttec.zsh
   15 |     - nodejs
   16 |     - LetsEncrypt      # Does not work with Vagrant, must be a public ip for Let'sEncrypt to work. 
   17 |     - wetty            # Not needed for Vagrant, use vagrant ssh
   18 |     # - sendgrid       # I send mail if you don't turn me off!
   19 |     - student_cli 
```
