# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-015

- Repository: `jr0dd/home-ops`
- Commit: `0e76c37818159bea648890d4ee132616f6ed6499`
- Family: maintainability_complexity
- Rule: `ansibleguard/deprecated-modules`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `infrastructure/ansible/roles/ubuntu/tasks/main.yml` (reported anchor line 31)
- Flagged construct: task `unnamed task`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–45 of 45:

```text
    1 | ---
    2 | - include: locale.yml
    3 |   tags:
    4 |     - locale
    5 | 
    6 | - include: packages.yml
    7 |   tags:
    8 |     - packages
    9 | 
   10 | - include: kernel.yml
   11 |   tags:
   12 |     - kernel
   13 | 
   14 | - include: network.yml
   15 |   tags:
   16 |     - network
   17 | 
   18 | - include: filesystem.yml
   19 |   tags:
   20 |     - filesystem
   21 | 
   22 | - include: disks.yml
   23 |   when: inventory_hostname not in groups['storage-nodes']
   24 |   tags:
   25 |     - disks
   26 | 
   27 | - include: power.yml
   28 |   tags:
   29 |     - power
   30 | 
   31 | - include: grub.yml
   32 |   tags:
   33 |     - grub
   34 | 
   35 | - include: unattended-upgrades.yml
   36 |   tags:
   37 |     - unattended-upgrades
   38 | 
   39 | - include: group.yml
   40 |   tags:
   41 |     - group
   42 | 
   43 | - include: user.yml
   44 |   tags:
   45 |     - user
```
