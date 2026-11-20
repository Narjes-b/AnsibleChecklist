# Frozen source context: V007PILOT-STYLE_POLICY-037

- Repository: `Checkmk/ansible-collection-checkmk.general`
- Commit: `50be8bde935f94e4702f40c9a549f86ffe773db1`
- Family: Style/policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/server/tasks/RedHat.yml` (reported anchor line 36)
- Object: `task` `a06d848f5f415fc97a17d315ff9fbc9a4286c14e49c27c676fd449b14d27f69d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–110 of 110:

```text
    1 | ---
    2 | - name: "{{ ansible_facts['os_family'] }} Derivatives: Enable repositories on CentOS & RHEL 8."
    3 |   when: |
    4 |     (ansible_facts['distribution'] == "RedHat" or ansible_facts['distribution'] == "CentOS" or ansible_facts['distribution'] == "OracleLinux")
    5 |     and ansible_facts['distribution_major_version'] == "8"
    6 |   block:
    7 |     - name: "{{ ansible_facts['os_family'] }} Derivatives: Download EPEL GPG Key on CentOS & RHEL 8."
    8 |       ansible.builtin.get_url:
    9 |         url: "{{ __checkmk_server_epel_gpg_key }}"
   10 |         dest: "{{ __checkmk_server_tmp_dir }}/EPEL-pubkey.gpg"
   11 |         mode: "0640"
   12 |       when: checkmk_server_verify_setup | bool
   13 |       tags:
   14 |         - download-gpg-key
   15 |         - enable-repos
   16 | 
   17 |     - name: "{{ ansible_facts['os_family'] }} Derivatives: Import EPEL GPG Key on CentOS & RHEL 8."
   18 |       become: true
   19 |       ansible.builtin.rpm_key:
   20 |         key: "{{ __checkmk_server_tmp_dir }}/EPEL-pubkey.gpg"
   21 |         state: present
   22 |       when: checkmk_server_epel_gpg_check | bool
   23 |       tags:
   24 |         - import-gpg-key
   25 |         - enable-repos
   26 | 
   27 |     - name: "{{ ansible_facts['os_family'] }} Derivatives: Install epel-release from URL on CentOS & RHEL 8."
   28 |       become: true
   29 |       ansible.builtin.package:
   30 |         name: "{{ __checkmk_server_epel_url }}"
   31 |         state: present
   32 |         disable_gpg_check: "{{ not checkmk_server_epel_gpg_check | bool }}"
   33 |       tags:
   34 |         - enable-repos
   35 | 
   36 | - name: "{{ ansible_facts['os_family'] }} Derivatives: Enable CodeReady Linux Builder repo on RHEL 8."
   37 |   become: true
   38 |   community.general.rhsm_repository:
   39 |     name: "codeready-builder-for-rhel-{{ ansible_facts['distribution_major_version'] }}-x86_64-rpms"
   40 |     state: enabled
   41 |   tags:
   42 |     - enable-repos
   43 |   when: |
   44 |     ansible_facts['distribution'] == "RedHat"
   45 |     and ansible_facts['distribution_major_version'] == "8"
   46 | 
   47 | - name: "{{ ansible_facts['os_family'] }} Derivatives: Enable powertools repository on CentOS 8."  # noqa no-changed-when
   48 |   become: true
   49 |   ansible.builtin.shell: dnf config-manager --set-enabled powertools  # noqa command-instead-of-shell
   50 |   when: | # RHEL needs epel and a package URL
   51 |     (ansible_facts['distribution'] != "RedHat" and ansible_facts['distribution'] != "OracleLinux")
   52 |     and ansible_facts['distribution_major_version'] == "8"
   53 |   tags:
   54 |     - enable-repos
   55 | 
   56 | - name: "{{ ansible_facts['os_family'] }} Derivatives: Enable codeready builder repository on OracleLinux 8."  # noqa no-changed-when
   57 |   become: true
   58 |   ansible.builtin.shell: dnf config-manager --set-enabled ol8_codeready_builder  # noqa command-instead-of-shell
   59 |   when: | # RHEL needs epel and a package URL
   60 |     ansible_facts['distribution'] == "OracleLinux"
   61 |     and ansible_facts['distribution_major_version'] == "8"
   62 |   tags:
   63 |     - enable-repos
   64 | 
   65 | - name: "{{ ansible_facts['os_family'] }} Derivatives: Enable powertools repository on RHEL 7."
   66 |   become: true
   67 |   community.general.rhsm_repository:
   68 |     name: "{{ item }}"
   69 |     state: enabled
   70 |   loop:
   71 |     - "rhel-7-server-optional-rpms"
   72 |     - "rhel-7-server-extras-rpms"
   73 |   when: |
   74 |     ansible_facts['distribution'] == "RedHat"
   75 |     and ansible_facts['distribution_major_version'] == "7"
   76 |   tags:
   77 |     - enable-repos
   78 | 
   79 | - name: "{{ ansible_facts['os_family'] }} Derivatives: Install Checkmk Server."
   80 |   when: not 'check-mk-' + __checkmk_server_edition_mapping[checkmk_server_edition] + '-' +checkmk_server_version in ansible_facts['packages']
   81 |   become: true
   82 |   ansible.builtin.package:
   83 |     name: "{{ __checkmk_server_tmp_dir }}/{{ __checkmk_server_setup_file }}"
   84 |     state: present
   85 |     disable_gpg_check: '{{ not checkmk_server_verify_setup | bool }}'
   86 |   notify: Start httpd
   87 |   tags:
   88 |     - install-package
   89 | 
   90 | - name: "{{ ansible_facts['os_family'] }} Derivatives: Enable httpd can network connect selinux boolean."
   91 |   become: true
   92 |   ansible.posix.seboolean:
   93 |     name: httpd_can_network_connect
   94 |     state: true
   95 |     persistent: true
   96 |   when: ansible_facts['selinux']['status'] == 'enabled'
   97 |   tags:
   98 |     - set-selinux-boolean
   99 | 
  100 | - name: "{{ ansible_facts['os_family'] }} Derivatives: Open Firewall Ports for the Checkmk Server."
  101 |   when: checkmk_server_configure_firewall | bool and "firewalld.service" in ansible_facts['services']
  102 |   ansible.posix.firewalld:
  103 |     permanent: true
  104 |     immediate: "{% if ansible_facts['services']['firewalld.service']['state'] == 'running' %}true{% else %}false{% endif %}"
  105 |     port: "{{ item }}/tcp"
  106 |     state: "enabled"
  107 |   become: true
  108 |   loop: "{{ checkmk_server_ports }}"
  109 |   tags:
  110 |     - configure-firewall
```
