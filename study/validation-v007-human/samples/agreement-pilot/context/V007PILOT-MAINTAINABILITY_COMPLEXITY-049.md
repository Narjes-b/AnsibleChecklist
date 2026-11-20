# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-049

- Repository: `opendevshop/devshop`
- Commit: `98f107b4c7146af38074b9b1e8e78a69a766f10a`
- Family: Maintainability/complexity
- Rule: `ansibleguard/deprecated-modules`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/geerlingguy.supervisor/tasks/main.yml` (reported anchor line 32)
- Object: `task` `aa4b1733672c5ba3fc49954b71262baaa46b171b0627d62adb080cbd6fe4a18f`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–45 of 45:

```text
    1 | ---
    2 | - name: Include OS-specific variables.
    3 |   include_vars: "{{ ansible_os_family }}.yml"
    4 | 
    5 | - name: "Include variables for Amazon Linux."
    6 |   include_vars: "AmazonLinux.yml"
    7 |   when:
    8 |     - ansible_distribution == "Amazon"
    9 |     - ansible_distribution_major_version == "NA" or ansible_distribution_major_version == "2018" or ansible_distribution_major_version == "6"
   10 | 
   11 | - name: Ensure Supervisor is installed (specific version).
   12 |   pip:
   13 |     name: supervisor
   14 |     state: present
   15 |     version: "{{ supervisor_version }}"
   16 |   when: supervisor_version != 'latest'
   17 | 
   18 | - name: Ensure Supervisor is installed (latest version).
   19 |   pip:
   20 |     name: supervisor
   21 |     state: present
   22 |   when: supervisor_version == 'latest'
   23 | 
   24 | - name: Ensure Supervisor log dir exists.
   25 |   file:
   26 |     path: "{{ supervisor_log_dir }}"
   27 |     state: directory
   28 |     mode: 0755
   29 | 
   30 | - include: config.yml
   31 | 
   32 | - include: init-setup.yml
   33 |   when: supervisor_started or supervisor_enabled
   34 | 
   35 | - name: Ensure Supervisor is started (if configured).
   36 |   service:
   37 |     name: supervisord
   38 |     state: started
   39 |   when: supervisor_started
   40 | 
   41 | - name: Ensure Supervisor is enabled at boot (if configured).
   42 |   service:
   43 |     name: supervisord
   44 |     enabled: true
   45 |   when: supervisor_enabled
```
