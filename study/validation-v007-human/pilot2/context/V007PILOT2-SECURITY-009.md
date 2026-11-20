# Frozen source context: V007PILOT2-SECURITY-009

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `openshift4_aws/roles/deploy_ansible_automation/tasks/deploy.yml` (reported anchor line 54)
- Flagged construct: task `update ansible tower installation inventory file (set secret_key)`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–151 of 151:

```text
    1 | ---
    2 | # tasks file for deploy_ansible_automation
    3 | ### Download and stage Ansible archive
    4 | - name: create temporary build directory
    5 |   tempfile:
    6 |     state: directory
    7 |     suffix: ansible-archive
    8 |   register: download_dir_ansible
    9 | - name: Echo download directory
   10 |   debug:
   11 |     msg: "{{ download_dir_ansible.path }}"
   12 | - name: Download Ansible Archive
   13 |   get_url: 
   14 |     url: "{{ ansible_archive_url_base }}/{{ ansible_archive_filename }}"
   15 |     dest: "{{ download_dir_ansible.path }}/{{ ansible_archive_filename }}"
   16 | - name: Unzip Ansible archive
   17 |   unarchive:
   18 |     src: "{{ download_dir_ansible.path }}/{{ ansible_archive_filename }}"
   19 |     dest: "{{ download_dir_ansible.path }}"
   20 |     extra_opts:
   21 |     - -P
   22 |     - --transform
   23 |     - s/^a.*-[0-9]\//ansible-openshift\//
   24 | 
   25 | ### Update Ansible Inventory file with installation settings
   26 | - name: Setting Ansible Automation installer location fact
   27 |   set_fact:
   28 |     ansible_installer_inventory: "{{ download_dir_ansible.path }}/ansible-openshift/inventory"
   29 | - name: Update Ansible Tower installation inventory file (set openshift_host)
   30 |   lineinfile:
   31 |     dest: "{{ ansible_installer_inventory }}"
   32 |     regexp: '^openshift_host=.*'
   33 |     line: "openshift_host={{ ansible_openshift_host }}"
   34 | - name: Update Ansible Tower installation inventory file (set skip_tls_verify)
   35 |   lineinfile:
   36 |     dest: "{{ ansible_installer_inventory }}"
   37 |     regexp: '^openshift_skip_tls_verify=.*'
   38 |     line: "openshift_skip_tls_verify={{ ansible_openshift_skip_tls_verify }}"
   39 | - name: Update Ansible Tower installation inventory file (set openshift_project)
   40 |   lineinfile:
   41 |     dest: "{{ ansible_installer_inventory }}"
   42 |     regexp: '^openshift_project=.*'
   43 |     line: "openshift_project={{ ansible_openshift_project }}"
   44 | - name: Update Ansible Tower installation inventory file (set openshift_user)
   45 |   lineinfile:
   46 |     dest: "{{ ansible_installer_inventory }}"
   47 |     regexp: '^openshift_user=.*'
   48 |     line: "openshift_user={{ ansible_openshift_user }}"
   49 | - name: Update Ansible Tower installation inventory file (set openshift_password)
   50 |   lineinfile:
   51 |     dest: "{{ ansible_installer_inventory }}"
   52 |     regexp: '^openshift_password=[REDACTED_LITERAL]
   53 |     line: "openshift_password={{ ansible_openshift_password }}"
   54 | - name: Update Ansible Tower installation inventory file (set secret_key)
   55 |   lineinfile:
   56 |     dest: "{{ ansible_installer_inventory }}"
   57 |     regexp: '^secret_key=[REDACTED_LITERAL]
   58 |     line: "secret_key={{ ansible_secret_key }}"
   59 | - name: Update Ansible Tower installation inventory file (set admin_user)
   60 |   lineinfile:
   61 |     dest: "{{ ansible_installer_inventory }}"
   62 |     regexp: '^admin_user=.*'
   63 |     line: "admin_user={{ ansible_openshift_user }}"
   64 | - name: Update Ansible Tower installation inventory file (set admin_password)
   65 |   lineinfile:
   66 |     dest: "{{ ansible_installer_inventory }}"
   67 |     regexp: '^admin_password=[REDACTED_LITERAL]
   68 |     line: "admin_password={{ ansible_openshift_password }}"
   69 | - name: Update Ansible Tower installation inventory file (set pg_username)
   70 |   lineinfile:
   71 |     dest: "{{ ansible_installer_inventory }}"
   72 |     regexp: '^pg_username=.*'
   73 |     line: "pg_username={{ ansible_pg_username }}"
   74 | - name: Update Ansible Tower installation inventory file (set pg_password)
   75 |   lineinfile:
   76 |     dest: "{{ ansible_installer_inventory }}"
   77 |     regexp: '^pg_password=[REDACTED_LITERAL]
   78 |     line: "pg_password={{ ansible_pg_password }}"
   79 | - name: Update Ansible Tower installation inventory file (set openshift_pg_emptydir)
   80 |   lineinfile:
   81 |     dest: "{{ ansible_installer_inventory }}"
   82 |     regexp: '^openshift_pg_emptydir=.*'
   83 |     line: "openshift_pg_emptydir={{ ansible_openshift_pg_emptydir }}"
   84 | 
   85 | ## Update resource reservation settings
   86 | - name: Update memory reservation for Ansible Tower deployment (web)"
   87 |   lineinfile:
   88 |     path: "{{ download_dir_ansible.path }}/ansible-openshift/roles/kubernetes/defaults/main.yml"
   89 |     regexp: '^web_mem_request:'
   90 |     line: 'web_mem_request: 4'
   91 | 
   92 | - name: Update cpu reservation for Ansible Tower deployment (web)"
   93 |   lineinfile:
   94 |     path: "{{ download_dir_ansible.path }}/ansible-openshift/roles/kubernetes/defaults/main.yml"
   95 |     regexp: '^web_cpu_request:'
   96 |     line: 'web_cpu_request: 1500'
   97 | 
   98 | - name: Update memory reservation for Ansible Tower deployment (tasks)"
   99 |   lineinfile:
  100 |     path: "{{ download_dir_ansible.path }}/ansible-openshift/roles/kubernetes/defaults/main.yml"
  101 |     regexp: '^task_mem_request:'
  102 |     line: 'task_mem_request: 10'
  103 | 
  104 | - name: Update cpu reservation for Ansible Tower deployment (tasks)"
  105 |   lineinfile:
  106 |     path: "{{ download_dir_ansible.path }}/ansible-openshift/roles/kubernetes/defaults/main.yml"
  107 |     regexp: '^task_cpu_request:'
  108 |     line: 'task_cpu_request: 2500'
  109 | 
  110 | - name: Update memory reservation for Ansible Tower deployment (redis)"
  111 |   lineinfile:
  112 |     path: "{{ download_dir_ansible.path }}/ansible-openshift/roles/kubernetes/defaults/main.yml"
  113 |     regexp: '^redis_mem_request:'
  114 |     line: 'redis_mem_request: 2'
  115 | 
  116 | - name: Update cpu reservation for Ansible Tower deployment (redis)"
  117 |   lineinfile:
  118 |     path: "{{ download_dir_ansible.path }}/ansible-openshift/roles/kubernetes/defaults/main.yml"
  119 |     regexp: '^redis_cpu_request:'
  120 |     line: 'redis_cpu_request: 1500'
  121 | 
  122 | #### Create namespace for Ansible Automation
  123 | - name: Create tower namespace
  124 |   k8s:
  125 |     name: tower
  126 |     kind: Namespace
  127 |     state: present
  128 |     api_key: "{{ k8s_auth_results.k8s_auth.api_key }}"
  129 | 
  130 | #### Run installer
  131 | - name: Run Ansible on OpenShift installation (runtime ~15 minutes)
  132 |   shell: "PATH={{ openshift_build_path }}:$PATH ./setup_openshift.sh -i {{ ansible_installer_inventory }} 2>&1 | tee {{ openshift_build_path }}/ansible-tower-install.log && touch {{ download_dir_ansible.path }}/ansible-openshift/.ansible-openshift-complete"
  133 |   args:
  134 |     chdir: "{{ download_dir_ansible.path }}/ansible-openshift/"
  135 |     creates: "{{ download_dir_ansible.path }}/ansible-openshift/.ansible-openshift-complete"
  136 |   async: 10800
  137 |   poll: 0
  138 |   register: ansible_install_status
  139 | - name: 'Check on Ansible Tower on OpenShift install ...'
  140 |   async_status: jid={{ ansible_install_status.ansible_job_id }}
  141 |   register: job_result
  142 |   until: job_result.finished
  143 |   delay: 30
  144 |   retries: 350
  145 | 
  146 | #### Clean up
  147 | - name: Remove ansible download directory
  148 |   file:
  149 |     path: "{{ download_dir_ansible.path }}"
  150 |     state: absent
  151 |   when: download_dir_ansible.path is defined
```
