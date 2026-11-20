# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-044

- Repository: `grycap/im`
- Commit: `5e54aa6e02108a615abf2670abaa4aa1c56add02`
- Family: Maintainability/complexity
- Rule: `ansibleguard/shell-instead-of-module`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `contextualization/conf-ansible.yml` (reported anchor line 137)
- Object: `task` `409e9a88f3e20c4952e91c5af69526d01e4bb1e3d820b84f49ab2f561a1927f2`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–205 of 205:

```text
    1 | ---
    2 | - hosts: "{{IM_HOST}}"
    3 |   become: yes
    4 |   become_method: sudo
    5 |   gather_facts: false
    6 |   vars:
    7 |     MICROMAMBA_PATH: /var/tmp/.mamba
    8 |     DEFAULT_ANSIBLE_VERSION: "9.5.1"  # Latest Ansible 9.X version in the conda channels
    9 |     ANSIBLE_PYTHON_VERSION: "3.12"
   10 |   tasks:
   11 |   ############## To avoid some issues with cloud-init and unattended upgrades ###############
   12 |     - name: Avoid unattended upgrades
   13 |       raw: |
   14 |         sudo touch /var/lib/apt/periodic/upgrade-stamp; \
   15 |         sudo touch /var/lib/apt/periodic/update-stamp; \
   16 |         sudo touch /var/lib/apt/periodic/download-upgradeable-stamp;
   17 |       ignore_errors: yes
   18 |       changed_when: false
   19 | 
   20 |     - name: Wait for the VM to boot
   21 |       raw: systemctl is-system-running --wait
   22 |       ignore_errors: yes
   23 |       changed_when: false
   24 | 
   25 |   ################### Some OSs does not have python by default #########################
   26 |     - name: Check Python is installed
   27 |       raw: python3 -c 'import sys; print(sys.version_info[1])'
   28 |       ignore_errors: yes
   29 |       register: python3_version
   30 |       changed_when: false
   31 | 
   32 |     - name: Bootstrap with python Debian/Ubuntu
   33 |       raw: command -v apt && sudo apt update && sudo apt install -y python3
   34 |       ignore_errors: yes
   35 |       register: python_install
   36 |       changed_when: python_install.stdout_lines|length > 1
   37 |       when: python3_version is failed or python3_version.stdout|int < 5
   38 | 
   39 |     - name: Bootstrap with python RedHat/CentOS
   40 |       raw: command -v yum && sudo yum install -y python3
   41 |       ignore_errors: yes
   42 |       register: python_install
   43 |       changed_when: python_install.stdout_lines|length > 1
   44 |       when: python3_version is failed
   45 | 
   46 |     - name: Bootstrap with python SUSE
   47 |       raw: command -v zypper && sudo zypper -n install python3 python3-xml
   48 |       ignore_errors: yes
   49 |       register: python_install
   50 |       changed_when: python_install.stdout_lines|length > 1
   51 |       when: python3_version is failed
   52 | 
   53 |      # In some cases python link is not created
   54 |     - name: Link python 3 in case is needed
   55 |       raw: ls /usr/bin/python || { ls /usr/bin/python3 && ln -s /usr/bin/python3 /usr/bin/python; }
   56 |       ignore_errors: yes
   57 | 
   58 |     # In case of redhat systems libselinux-python3 is needed
   59 |     - name: Install libselinux-python3 on RH systems
   60 |       raw: command -v yum && yum -y install libselinux-python3
   61 |       register: selinux_install
   62 |       changed_when: selinux_install.stdout_lines|length > 1
   63 |       ignore_errors: yes
   64 | 
   65 |   ################### Some basic OSs operations #########################
   66 |     - name: Get Facts
   67 |       setup:
   68 | 
   69 |     - name: Install EPEL
   70 |       command: yum install -y epel-release
   71 |       args:
   72 |         creates: /etc/yum.repos.d/epel.repo
   73 |       when: ansible_os_family == "RedHat" and ansible_distribution != "Fedora"
   74 | 
   75 |     - name: Fix EPEL
   76 |       lineinfile:
   77 |         path: /etc/yum.repos.d/epel.repo
   78 |         regexp: '^metalink=https:\/\/mirrors\.fedoraproject\.org\/metalink\?repo=epel-\$releasever&arch=\$basearch&infra=\$infra&content=\$contentdir'
   79 |         insertafter: '^#baseurl '
   80 |         line: 'baseurl=https://dl.fedoraproject.org/pub/archive/epel/8.5.2022-05-10/Everything/x86_64/'
   81 |       when: ansible_os_family == "RedHat" and ansible_distribution != "Fedora" and ansible_distribution_major_version|int < 9
   82 | 
   83 |     - name: Ensure to Enable EPEL repo
   84 |       ini_file:
   85 |         dest: /etc/yum.repos.d/epel.repo
   86 |         section: epel
   87 |         option: enabled
   88 |         value: "1"
   89 |       when: ansible_os_family == "RedHat" and ansible_distribution != "Fedora" and ansible_distribution_major_version|int < 9
   90 |       ignore_errors: yes
   91 | 
   92 |     - name: Ubuntu/Debian apt update
   93 |       apt:
   94 |         update_cache: yes
   95 |         cache_valid_time: 3600
   96 |       when: ansible_os_family == "Debian"
   97 |       ignore_errors: yes
   98 |       register: apt_update
   99 | 
  100 |     - name: Ubuntu/Debian force apt update (avoid apt lock)
  101 |       command: apt update
  102 |       when: ansible_os_family == "Debian" and apt_update is failed
  103 | 
  104 |   ################### Install Ansible/micromamba requisites #########################
  105 | 
  106 |     - name: Debian/Ubuntu install requisites with apt
  107 |       apt:
  108 |         name:
  109 |         - wget
  110 |         - sshpass
  111 |         - openssh-client
  112 |         - unzip
  113 |         install_recommends: no
  114 |       when: ansible_os_family == "Debian"
  115 | 
  116 |     - name: Yum install requisites RH 7/8 or Fedora
  117 |       command: yum install -y wget sshpass openssh-clients unzip
  118 |       when: ansible_os_family == "RedHat"
  119 | 
  120 |     - name: Zypper install requirements Suse
  121 |       zypper:
  122 |         name:
  123 |         - wget
  124 |         - sshpass
  125 |         - openssh
  126 |         - unzip
  127 |       when: ansible_os_family == "Suse"
  128 | 
  129 |   ################# Use micromamba to install Ansible ##################################
  130 | 
  131 |     - name: Create micromamba directory
  132 |       file:
  133 |         path: "{{ MICROMAMBA_PATH }}/bin"
  134 |         state: directory
  135 |         mode: '0755'
  136 | 
  137 |     - name: Download micromamba
  138 |       command: wget https://github.com/mamba-org/micromamba-releases/releases/latest/download/micromamba-linux-64 -O {{ MICROMAMBA_PATH }}/bin/micromamba
  139 |       args:
  140 |         creates: "{{ MICROMAMBA_PATH }}/bin/micromamba"
  141 | 
  142 |     - name: Make executable
  143 |       file:
  144 |         path: "{{ MICROMAMBA_PATH }}/bin/micromamba"
  145 |         mode: '0755'
  146 | 
  147 |     - name: Set Ansible version from playbook var if defined
  148 |       set_fact:
  149 |         ANSIBLE_VERSION: "{{ im_ansible_version }}"
  150 |       when: im_ansible_version is defined and im_ansible_version | length > 0
  151 | 
  152 |     - name: Set Ansible version from env if defined
  153 |       set_fact: ANSIBLE_VERSION={{ lookup('env','ANSIBLE_VERSION') }}
  154 |       when:
  155 |         - lookup('env','ANSIBLE_VERSION') != ""
  156 |         - ANSIBLE_VERSION is not defined or ANSIBLE_VERSION | length == 0
  157 | 
  158 |     - name: Set default ANSIBLE_VERSION
  159 |       set_fact:
  160 |         ANSIBLE_VERSION: "{{ DEFAULT_ANSIBLE_VERSION }}"
  161 |       when: ANSIBLE_VERSION is not defined or ANSIBLE_VERSION | length == 0
  162 | 
  163 |     - name: Create base Ansible environment with micromamba
  164 |       command: "{{ MICROMAMBA_PATH }}/bin/micromamba create -y -n ansible -r {{ MICROMAMBA_PATH }} python={{ ANSIBLE_PYTHON_VERSION }} paramiko psutil pyyaml jmespath scp pywinrm requests urllib3"
  165 |       args:
  166 |         creates: "{{ MICROMAMBA_PATH }}/envs/ansible"
  167 | 
  168 |     - name: Install Ansible from conda channel
  169 |       command: "{{ MICROMAMBA_PATH }}/bin/micromamba install -y -n ansible -r {{ MICROMAMBA_PATH }} ansible={{ ANSIBLE_VERSION }}"
  170 | 
  171 | ######################### Configure Ansible  ######################################
  172 | 
  173 |     - name: Create Ansible config file
  174 |       copy:
  175 |         dest: /var/tmp/ansible.cfg
  176 |         content: |
  177 |           [defaults]
  178 |           transport  = ssh
  179 |           timeout = 30
  180 |           host_key_checking = False
  181 |           nocolor = 1
  182 |           become_user = root
  183 |           become_method = sudo
  184 |           fact_caching = jsonfile
  185 |           fact_caching_connection = /var/tmp/facts_cache
  186 |           fact_caching_timeout = 86400
  187 |           interpreter_python = /usr/bin/python3
  188 |           gathering = smart
  189 |           roles_path = /var/tmp/ansible/roles
  190 |           collections_path = /var/tmp/ansible
  191 |           jinja2_extensions = jinja2.ext.do
  192 |           allow_world_readable_tmpfiles = True
  193 |           ansible_python_interpreter = auto
  194 |           [paramiko_connection]
  195 |           record_host_keys=False
  196 |           [ssh_connection]
  197 |           pipelining = True
  198 |           ssh_args = -o ControlMaster=auto -o ControlPersist=900s -o UserKnownHostsFile=/dev/null
  199 |           [galaxy]
  200 |           server_list = galaxy, oldgalaxy
  201 |           [galaxy_server.galaxy]
  202 |           url = https://galaxy.ansible.com/api/
  203 |           [galaxy_server.oldgalaxy]
  204 |           url = https://old-galaxy.ansible.com/api/
  205 |         mode: '0644'
```
