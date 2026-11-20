# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-003

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: objective_correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `src/commcare_cloud/ansible/roles/bootstrap-users/tasks/remove_users.yml` (reported anchor line 35)
- Flagged construct: not named by the finding; the anchor line 35 lies in the task at line 35, name `Force kill stuck processes`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–59 of 59:

```text
    1 | ---
    2 | 
    3 | - name: Find users to remove
    4 |   getent:
    5 |     database: passwd
    6 |     key: "{{ item }}"
    7 |     fail_key: no
    8 |   loop: "{{ dev_users.absent }}"
    9 |   register: user_check
   10 | 
   11 | - name: Build list of users to remove
   12 |   set_fact:
   13 |     users_to_remove: "{{ user_check.results|selectattr('msg', 'undefined')|map(attribute='item')|list }}"
   14 | 
   15 | - name: Get running processes
   16 |   command: "ps -o pid= -u \"{{ users_to_remove|join(',') }}\""
   17 |   register: running_processes
   18 |   changed_when: no
   19 |   failed_when: no
   20 | 
   21 | - name: Kill running processes
   22 |   become: yes
   23 |   command: "kill {{ item }}"
   24 |   with_items: "{{ running_processes.stdout_lines|default([]) }}"
   25 | 
   26 | - name: Wait for killed processes to exit
   27 |   wait_for:
   28 |     path: "/proc/{{ item }}/status"
   29 |     state: absent
   30 |     timeout: 15
   31 |   with_items: "{{ running_processes.stdout_lines|default([]) }}"
   32 |   ignore_errors: yes
   33 |   register: killed_processes
   34 | 
   35 | - name: Force kill stuck processes
   36 |   become: yes
   37 |   command: "kill -9 {{ item }}"
   38 |   with_items: "{{ killed_processes.results|default([]) | select('failed') | map(attribute='item') | list }}"
   39 | 
   40 | - name: Remove users of former devs
   41 |   become: yes
   42 |   user: name="{{ item }}" state=absent
   43 |   with_items: '{{ users_to_remove }}'
   44 | 
   45 | - name: check if key files exist
   46 |   become: false
   47 |   delegate_to: localhost
   48 |   stat:
   49 |     path: "{{ authorized_keys_dir ~ item ~ '.pub' }}"
   50 |   register: absent_user_keys
   51 |   with_items: '{{ dev_users.absent }}'
   52 | 
   53 | - name: Revoke former devs ability to login as ansible
   54 |   become: yes
   55 |   authorized_key: user=ansible state=absent key="{{ lookup('file', authorized_keys_dir ~ item.0 ~ '.pub') }}"
   56 |   when: item.1.stat.exists
   57 |   with_together:
   58 |     - "{{ dev_users.absent }}"
   59 |     - "{{ absent_user_keys.results|default({}) }}"
```
