# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-041

- Repository: `usegalaxy-eu/vgcn`
- Commit: `c65e4ea9febe2bf5eeca04715c93a441d82f7875`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-play`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `ansible/workers.yml` (reported anchor line 2)
- Object: `source_location` `108ba8dc1fe78caff18936412e865ffb3604fc39887bd006384abb5382a69a49`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–159 of 159:

```text
    1 | ---
    2 | - hosts: workers
    3 |   vars_files:
    4 |     - "group_vars/pulsar.yml"
    5 |   pre_tasks:
    6 |     - name: Ensure `gnupg2` is installed
    7 |       # required for repository management,
    8 |       # in this playbook precisely by `geerlingguy.docker`
    9 |       ansible.builtin.package:
   10 |         name:
   11 |           - gnupg2
   12 |         state: present
   13 |       when: ansible_distribution_major_version|int >= 10
   14 |     - name: Debug Kernel version
   15 |       ansible.builtin.shell:
   16 |         cmd: uname -r
   17 |       register: kernel
   18 |     - name: Print kernel version
   19 |       ansible.builtin.debug:
   20 |         msg: "{{ kernel }}"
   21 |     - name: Install Pulsar dependencies
   22 |       ansible.builtin.package:
   23 |         name:
   24 |           - gcc
   25 |           - curl
   26 |           - git
   27 |           - libcurl-devel
   28 |           - python3-devel
   29 |           - python3-setuptools
   30 |         state: present
   31 |       become: true
   32 |       when: ansible_os_family == 'RedHat' and ansible_distribution_major_version | int >= 9
   33 |     - name: Set default version of Python
   34 |       ansible.builtin.alternatives:
   35 |         name: python
   36 |         path: /usr/bin/python3
   37 |         link: /usr/bin/python
   38 |     - name: Put SELinux in permissive mode, logging actions that would be blocked.
   39 |       ansible.builtin.lineinfile:
   40 |         path: /etc/selinux/config
   41 |         regexp: '^SELINUX='
   42 |         line: SELINUX=permissive
   43 |     # CHECK IF THIS IS NEEDED OR EXECUTED
   44 |     - name: "Deploy docker-stop-1M script"
   45 |       ansible.builtin.copy:
   46 |         content: |
   47 |             #!/bin/bash
   48 |             docker ps -f status=running --format '{{ '{{' }}.ID}}: {{ '{{' }}.RunningFor}}' | awk '/months/ && $2 > 1 { print $0 }'|cut -f1 -d':' | xargs docker stop
   49 |         dest: /usr/bin/docker-stop-1M
   50 |         owner: root
   51 |         group: root
   52 |         mode: 0755
   53 |     - name: Ensure the HTCondor configuration directory exists.
   54 |       become: true
   55 |       ansible.builtin.file:
   56 |         path: /etc/condor
   57 |         state: directory
   58 |         owner: root
   59 |         group: root
   60 |         mode: "0755"
   61 |     - name: Condor walltime script
   62 |       ansible.builtin.copy:
   63 |         dest: /etc/condor/meta_walltime.py
   64 |         src: meta_walltime.py
   65 |         mode: "0755"
   66 |     - name: Create Staponpriv user homedir, see issue 23
   67 |       become: true
   68 |       ansible.builtin.file:
   69 |         path: /var/lib/stapunpriv
   70 |         state: directory
   71 |         owner: root
   72 |         group: root
   73 |     - name: Ensure CVMFS scratch directory exists
   74 |       become: true
   75 |       ansible.builtin.file:
   76 |         path: /scratch/cvmfs/
   77 |         state: directory
   78 |         owner: cvmfs
   79 |         group: cvmfs
   80 |         mode: "0755"
   81 |   post_tasks:
   82 |     - name: Add firewall rules for NFS
   83 |       ansible.posix.firewalld:
   84 |         service: "{{ item }}"
   85 |         state: enabled
   86 |         permanent: true
   87 |         immediate: true
   88 |       with_items:
   89 |         - nfs
   90 |         - rpc-bind
   91 |         - mountd
   92 |     - name: Restart Autofs
   93 |       ansible.builtin.service:
   94 |         name: autofs
   95 |         state: restarted
   96 |     - name: Post Task Create User and add galaxy and condor/docker user groups
   97 |       ansible.builtin.user:
   98 |         name: galaxy
   99 |         groups: condor,docker
  100 |         append: yes
  101 |         #  Let's keep this here as a reminder that uninstalling something
  102 |         #  because we think it MAY not be needed, can result in several hours
  103 |         #  debugging. This task removed the nvidia driver and cuda.
  104 |         #  - ansible.builtin.dnf:
  105 |         #      name: "{{ packages }}"
  106 |         #      state: absent
  107 |         #    vars:
  108 |         #      packages:
  109 |         #        - libcurl-devel
  110 |         #        - openssl-devel
  111 |         #    become: yes
  112 |     - name: Ensure Docker directory extists
  113 |       file:
  114 |         state: directory
  115 |         path: /etc/docker
  116 |         mode: '0755'
  117 |     - name: Copy Docker daemon.json
  118 |       ansible.builtin.copy:
  119 |         src: daemon.json
  120 |         dest: /etc/docker/daemon.json
  121 |         mode: '0644'
  122 |     - name: Restart Docker service, in all cases
  123 |       ansible.builtin.service:
  124 |         name: docker
  125 |         state: restarted
  126 |     - name: Deploy a signal emitter for telegraf
  127 |       ansible.builtin.copy:
  128 |         content: |
  129 |           #!/bin/bash
  130 |           echo '{"alive":1}'
  131 |         dest: /bin/iamalive
  132 |         owner: telegraf
  133 |         group: telegraf
  134 |         mode: 0755
  135 |   roles:
  136 |     - role: usegalaxy_eu.handy.os_setup
  137 |       vars:
  138 |         enable_pam_limits: true
  139 |         enable_journald: true
  140 |         enable_ansible_root_cron: true
  141 | 
  142 |     - usegalaxy-eu.autofs
  143 | 
  144 |     - geerlingguy.docker
  145 | 
  146 |     - galaxyproject.cvmfs
  147 |     - galaxyproject.pulsar
  148 |     - usegalaxy_eu.cuda
  149 |     - usegalaxy_eu.nvidia_container
  150 | 
  151 |     - usegalaxy-eu.logrotate
  152 | 
  153 |     # Applies a 250GB soft and 1TB hard limit on the file size for the condor systemd unit
  154 |     - role: usegalaxy-eu.fslimit
  155 |       become: yes
  156 |       vars:
  157 |         ulimit_fsize_unit: "condor.service"
  158 |         ulimit_fsize_soft: 268435456000
  159 |         ulimit_fsize_hard: 1073741824000
```
