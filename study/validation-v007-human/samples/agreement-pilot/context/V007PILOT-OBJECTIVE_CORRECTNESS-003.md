# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-003

- Repository: `cradle8810/ansible_hayaworld`
- Commit: `d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597`
- Family: Objective correctness
- Rule: `ansibleguard/missing-handler`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `skylark.yml` (reported anchor line 55)
- Object: `source_location` `1691d6099c23092f699c0f06e0ee972ae4a8acc411b241329128e1e11da7d4b8`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–55 of 55:

```text
    1 | ---
    2 | - name: Play for skylark Datastore
    3 |   hosts: skylark
    4 |   remote_user: hayato
    5 |   gather_facts: true
    6 |   become: true
    7 | 
    8 |   vars_files:
    9 |     - host_vars/networks.yml
   10 | 
   11 |   handlers:
   12 |     - name: Restart handler tasks
   13 |       ansible.builtin.import_tasks:
   14 |         file: handlers/main.yml
   15 | 
   16 |   tasks:
   17 |     - name: "Common / Set Hostinfo"
   18 |       ansible.builtin.set_fact:
   19 |         common_hostinfo: "{{ network | selectattr('ipv4', 'eq', mgmt_ipv4) | first }}"
   20 |       vars:
   21 |         mgmt_ipv4: "{{ ansible_all_ipv4_addresses | select('match', '192.168.88.') | first }}"
   22 |       tags:
   23 |         - always
   24 | 
   25 |     - name: Scrutiny collector setting
   26 |       ansible.builtin.import_role:
   27 |         name: scrutiny_collector
   28 |       vars:
   29 |         scrutiny_collector_server_id: "{{ common_hostinfo.shortname }}"
   30 |         scrutiny_collector_cron: true
   31 |         scrutiny_collector_install_bin: "/usr/local/bin"
   32 |         scrutiny_collector_install_etc: "/usr/local/etc"
   33 |         scrutiny_collector_smartctl: "/opt/sbin/smartctl"
   34 |         scrutiny_collector_device:
   35 |           - device: /dev/sda
   36 |             type: 'sat,auto'
   37 |           - device: /dev/sdb
   38 |             type: 'sat,auto'
   39 |           - device: /dev/sdc
   40 |             type: 'sat,auto'
   41 |           - device: /dev/sdd
   42 |             type: 'sat,auto'
   43 |           - device: /dev/sde
   44 |             type: 'sat,auto'
   45 |           - device: /dev/sdf
   46 |             type: 'sat,auto'
   47 |       tags:
   48 |         - scrutiny
   49 | 
   50 |     - name: "Install Locales"
   51 |       ansible.builtin.apt:
   52 |         name: locales
   53 |         state: present
   54 |         update_cache: true
   55 |       notify: "locale gen for skylark"
```
