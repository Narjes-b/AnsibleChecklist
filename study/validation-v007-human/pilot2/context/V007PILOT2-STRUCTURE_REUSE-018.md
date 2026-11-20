# Frozen source context: V007PILOT2-STRUCTURE_REUSE-018

- Repository: `ethpandaops/ansible-collection-general`
- Commit: `15a1f3490258357c4652b96b80f0a92636fa4135`
- Family: structure_reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/bootstrap/tasks/prepare/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/bootstrap/tasks/prepare/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–77 of 77:

```text
    1 | - name: Try connection
    2 |   block:
    3 |     - name: Test connection
    4 |       ansible.builtin.wait_for_connection:
    5 |         timeout: "{{ bootstrap_timeout }}"
    6 |       register: bootstrap_connect
    7 |       changed_when: false
    8 |   rescue:
    9 |     - name: Gather facts about the system
   10 |       ansible.builtin.include_tasks:
   11 |         file: gather_facts.yml
   12 |     - name: Install minmal bootstrap packages
   13 |       ansible.builtin.raw: "{{ bootstrap_install.raw }}"
   14 |       register: bootstrap_install_packages
   15 |       changed_when:
   16 |         - (bootstrap_install.stdout_regex in bootstrap_install_packages.stdout and
   17 |            bootstrap_os_family in [ "Alpine", "Archlinux", "Gentoo" ]) or
   18 |           (bootstrap_install.stdout_regex not in bootstrap_install_packages.stdout and
   19 |            bootstrap_os_family in [ "Debian", "RedHat", "Rocky", "Suse" ])
   20 |       vars:
   21 |         ansible_user: "{{ bootstrap_user }}"
   22 |   always:
   23 |     - name: Set bootstrap_ansible_user connected
   24 |       ansible.builtin.set_fact:
   25 |         bootstrap_ansible_user: "{{ ansible_user }}"
   26 |       when:
   27 |         - bootstrap_connect is succeeded
   28 |         - ansible_user is defined
   29 | 
   30 |     - name: Set bootstrap_ansible_user not connected
   31 |       ansible.builtin.set_fact:
   32 |         bootstrap_ansible_user: "{{ bootstrap_user }}"
   33 |       when:
   34 |         - bootstrap_connect is failed
   35 | 
   36 | - name: Ensure system is prepared
   37 |   vars:
   38 |     ansible_user: "{{ bootstrap_ansible_user | default(omit) }}"
   39 |   block:
   40 |     - name: Gather ansible facts
   41 |       ansible.builtin.setup:
   42 | 
   43 |     - name: Install bootstrap packages
   44 |       ansible.builtin.package:
   45 |         name: "{{ item }}"
   46 |         state: present
   47 |       loop: "{{ bootstrap_facts_packages.split() }}"
   48 | 
   49 |     - name: Get my IP address
   50 |       ansible.builtin.set_fact:
   51 |         _bootstrap_my_ip: "{{ lookup('ansible.builtin.url', 'https://ifconfig.me/ip', split_lines=False) }}"
   52 |       when: bootstrap_connect is failed
   53 | 
   54 |     - name: Check if auth log exists
   55 |       ansible.builtin.stat:
   56 |         path: /var/log/auth.log
   57 |       register: _bootstrap_auth_log_reg
   58 |       when: bootstrap_connect is failed
   59 | 
   60 |     - name: Auth log - Cleanup failed SSH attempts from auth log to avoid getting banned by systems like fail2ban
   61 |       ansible.builtin.replace:
   62 |         path: /var/log/auth.log
   63 |         regexp: "{{ item }}"
   64 |         replace: ''
   65 |       when: bootstrap_connect is failed and _bootstrap_auth_log_reg.stat.exists
   66 |       loop:
   67 |         - .* Invalid user .* {{ _bootstrap_my_ip | replace('.', '\.') }} .*
   68 |         - .* Connection closed by invalid user .* {{ _bootstrap_my_ip | replace('.', '\.') }} .*
   69 | 
   70 |     - name: No auth log - Probably we need to clean journalctl. Not ideal, but this should be just called once per bootstrap
   71 |       ansible.builtin.command: "{{ item }}"
   72 |       failed_when: false
   73 |       changed_when: true
   74 |       loop:
   75 |         - journalctl --rotate
   76 |         - journalctl --vacuum-time=1s
   77 |       when: bootstrap_connect is failed and not _bootstrap_auth_log_reg.stat.exists
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/bootstrap`; 15 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: yes
- molecule/ directory: yes

roles/bootstrap/README.md
roles/bootstrap/defaults/main.yml
roles/bootstrap/handlers/main.yml
roles/bootstrap/meta/main.yml
roles/bootstrap/meta/requirements.yml
roles/bootstrap/molecule/default/converge.yml
roles/bootstrap/molecule/default/inventory/group_vars/molecule.yml
roles/bootstrap/molecule/default/inventory/hosts.yml
roles/bootstrap/molecule/default/molecule.yml
roles/bootstrap/molecule/default/verify.yml
roles/bootstrap/tasks/main.yml
roles/bootstrap/tasks/prepare/gather_facts.yml
roles/bootstrap/tasks/prepare/main.yml
roles/bootstrap/templates/docker-config.json.j2
roles/bootstrap/vars/main.yml
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- blocks in file: 2; blocks containing exactly one task: 1
  - block at line 1: block-level keys ['always', 'name', 'rescue']; justifying keys ['always', 'rescue']
```
