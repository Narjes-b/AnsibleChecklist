# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-013

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: Objective correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `automation/roles/consul/tasks/install.yml` (reported anchor line 56)
- Object: `source_location` `07b14de3223ece77c37099be496e055b21f41fbd1eb0800b8c5d833035ecf3a3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–146 of 146:

```text
    1 | ---
    2 | # File: install.yml - package installation tasks for Consul
    3 | - name: Install OS packages
    4 |   ansible.builtin.package:
    5 |     name: "{{ item }}"
    6 |     state: present
    7 |   register: package_status
    8 |   until: package_status is success
    9 |   delay: 5
   10 |   retries: 3
   11 |   loop: "{{ consul_os_packages | default([]) }}"
   12 |   tags: installation
   13 |   when:
   14 |     - not ansible_facts['os_family'] == "VMware Photon OS"
   15 |     - consul_os_packages | length > 0
   16 |     - item not in ansible_facts.packages
   17 | 
   18 | - name: Install OS packages
   19 |   ansible.builtin.command: "tdnf install -y {{ package_item }}"
   20 |   loop: "{{ consul_os_packages }}"
   21 |   loop_control:
   22 |     loop_var: package_item
   23 |   tags: installation
   24 |   when: ansible_facts['os_family'] == "VMware Photon OS"
   25 | 
   26 | - name: Update Alpine Package Manager (APK)
   27 |   community.general.apk:
   28 |     update_cache: true
   29 |   run_once: true
   30 |   when: ansible_os_family == "Alpine"
   31 |   delegate_to: 127.0.0.1
   32 | 
   33 | - name: Read package checksum file
   34 |   ansible.builtin.stat:
   35 |     path: "{{ role_path }}/files/consul_{{ consul_version }}_SHA256SUMS"
   36 |   become: false
   37 |   vars:
   38 |     ansible_become: false
   39 |   run_once: true
   40 |   register: consul_checksum
   41 |   tags: installation
   42 |   delegate_to: 127.0.0.1
   43 | 
   44 | - name: Download package checksum file
   45 |   ansible.builtin.get_url:
   46 |     url: "{{ consul_checksum_file_url }}"
   47 |     dest: "{{ role_path }}/files/consul_{{ consul_version }}_SHA256SUMS"
   48 |   become: false
   49 |   vars:
   50 |     ansible_become: false
   51 |   run_once: true
   52 |   tags: installation
   53 |   when: not consul_checksum.stat.exists | bool
   54 |   delegate_to: 127.0.0.1
   55 | 
   56 | - name: Read package checksum
   57 |   ansible.builtin.shell: grep "{{ consul_pkg }}" "{{ role_path }}/files/consul_{{ consul_version }}_SHA256SUMS" | awk '{print $1}'
   58 |   become: false
   59 |   vars:
   60 |     ansible_become: false
   61 |   register: consul_sha256
   62 |   tags:
   63 |     - installation
   64 |     - skip_ansible_lint
   65 |   run_once: true
   66 |   delegate_to: 127.0.0.1
   67 | 
   68 | - name: Check Consul package file
   69 |   ansible.builtin.stat:
   70 |     path: "{{ role_path }}/files/{{ consul_pkg }}"
   71 |   become: false
   72 |   vars:
   73 |     ansible_become: false
   74 |   register: consul_package
   75 |   tags: installation
   76 |   run_once: true
   77 |   delegate_to: 127.0.0.1
   78 | 
   79 | - name: Download Consul package
   80 |   ansible.builtin.get_url:
   81 |     url: "{{ consul_zip_url }}"
   82 |     dest: "{{ role_path }}/files/{{ consul_pkg }}"
   83 |     checksum: "sha256:{{ consul_sha256.stdout }}"
   84 |     timeout: "42"
   85 |   become: false
   86 |   vars:
   87 |     ansible_become: false
   88 |   tags: installation
   89 |   when: not consul_package.stat.exists | bool
   90 |   run_once: true
   91 |   delegate_to: 127.0.0.1
   92 |   ignore_errors: "{{ ansible_check_mode }}"
   93 | 
   94 | - name: Create Temporary Directory for Extraction
   95 |   ansible.builtin.tempfile:
   96 |     state: directory
   97 |     prefix: ansible-consul.
   98 |   become: false
   99 |   vars:
  100 |     ansible_become: false
  101 |   register: install_temp
  102 |   tags: installation
  103 |   run_once: true
  104 |   delegate_to: 127.0.0.1
  105 | 
  106 | - name: Unarchive and install Consul
  107 |   block:
  108 |     - name: Unarchive Consul package
  109 |       ansible.builtin.unarchive:
  110 |         src: "{{ role_path }}/files/{{ consul_pkg }}"
  111 |         dest: "{{ install_temp.path }}/"
  112 |         creates: "{{ install_temp.path }}/consul"
  113 |       become: false
  114 |       vars:
  115 |         ansible_become: false
  116 |       tags:
  117 |         - installation
  118 |         - skip_ansible_lint
  119 |       run_once: true
  120 |       delegate_to: 127.0.0.1
  121 |       ignore_errors: "{{ ansible_check_mode }}"
  122 | 
  123 |     - name: Install Consul
  124 |       ansible.builtin.copy:
  125 |         src: "{{ install_temp.path }}/consul"
  126 |         dest: "{{ consul_bin_path }}/consul"
  127 |         owner: "{{ consul_user }}"
  128 |         group: "{{ consul_group }}"
  129 |         mode: "0755"
  130 |       notify:
  131 |         - restart consul
  132 |         - reload systemd daemon
  133 |       tags: installation
  134 |       ignore_errors: "{{ ansible_check_mode }}"
  135 |   always:
  136 |     - name: Cleanup
  137 |       ansible.builtin.file:
  138 |         path: "{{ install_temp.path }}"
  139 |         state: "absent"
  140 |       become: false
  141 |       vars:
  142 |         ansible_become: false
  143 |       tags: installation
  144 |       run_once: true
  145 |       delegate_to: 127.0.0.1
  146 |       ignore_errors: "{{ ansible_check_mode }}"
```
