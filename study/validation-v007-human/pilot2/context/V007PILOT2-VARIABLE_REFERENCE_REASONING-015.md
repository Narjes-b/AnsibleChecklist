# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-015

- Repository: `Kubeinit/kubeinit`
- Commit: `da6fec314d5594b6bd97ef2e4e71f9098a85e63c`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/overriding-facts`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `kubeinit/roles/kubeinit_libvirt/tasks/gather_host_facts.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`kubeinit/roles/kubeinit_libvirt/tasks/gather_host_facts.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–187 of 187:

```text
    1 | ---
    2 | # Copyright kubeinit contributors
    3 | # All Rights Reserved.
    4 | #
    5 | # Licensed under the Apache License, Version 2.0 (the "License"); you may
    6 | # not use this file except in compliance with the License. You may obtain
    7 | # a copy of the License at
    8 | #
    9 | #     http://www.apache.org/licenses/LICENSE-2.0
   10 | #
   11 | # Unless required by applicable law or agreed to in writing, software
   12 | # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
   13 | # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
   14 | # License for the specific language governing permissions and limitations
   15 | # under the License.
   16 | 
   17 | - name: Delegate to _param_gather_host
   18 |   block:
   19 | 
   20 |     - name: Confirm that we have ansible host connectivity
   21 |       ansible.builtin.ping:
   22 | 
   23 |     - name: Gather network facts
   24 |       ansible.builtin.gather_facts:
   25 |         gather_subset: "!all,network"
   26 |       register: _result_facts
   27 | 
   28 |     - name: Set distribution_family for CentOS
   29 |       ansible.builtin.set_fact:
   30 |         distribution_family: "CentOS"
   31 |         libvirt_qemu_user: "qemu"
   32 |         host_os: "centos"
   33 |         package_manager: auto
   34 |       when: _result_facts.ansible_facts.ansible_distribution == 'CentOS'
   35 | 
   36 |     - name: Set distribution_family for RedHat
   37 |       ansible.builtin.set_fact:
   38 |         distribution_family: "CentOS"
   39 |         libvirt_qemu_user: "qemu"
   40 |         host_os: "redhat"
   41 |         package_manager: auto
   42 |       when: _result_facts.ansible_facts.ansible_distribution == 'RedHat'
   43 | 
   44 |     - name: Set distribution_family for Fedora
   45 |       ansible.builtin.set_fact:
   46 |         distribution_family: "Fedora"
   47 |         libvirt_qemu_user: "qemu"
   48 |         host_os: "fedora"
   49 |         package_manager: auto
   50 |       when: _result_facts.ansible_facts.ansible_distribution == 'Fedora'
   51 | 
   52 |     - name: Set distribution_family for Debian
   53 |       ansible.builtin.set_fact:
   54 |         distribution_family: "Debian"
   55 |         libvirt_qemu_user: "libvirt-qemu"
   56 |         host_os: "debian"
   57 |         package_manager: apt
   58 |       when: _result_facts.ansible_facts.ansible_distribution == 'Debian'
   59 | 
   60 |     - name: Set distribution_family for Ubuntu
   61 |       ansible.builtin.set_fact:
   62 |         distribution_family: "Debian"
   63 |         libvirt_qemu_user: "libvirt-qemu"
   64 |         host_os: "ubuntu"
   65 |         package_manager: apt
   66 |       when: _result_facts.ansible_facts.ansible_distribution == 'Ubuntu'
   67 | 
   68 |     - name: Fails if OS is not supported
   69 |       ansible.builtin.assert:
   70 |         msg: "The host \"{{ _param_gather_host }}\" needs to be CentOS/RHEL, Fedora, or Debian/Ubuntu"
   71 |         that: hostvars[_param_gather_host]['distribution_family'] is defined
   72 | 
   73 |     - name: Set ssh_host_key_ecdsa
   74 |       ansible.builtin.set_fact:
   75 |         ssh_host_key_ecdsa: "{{ _result_facts.ansible_facts.ansible_ssh_host_key_ecdsa_public_keytype }} {{ _result_facts.ansible_facts.ansible_ssh_host_key_ecdsa_public }}"
   76 |       when: >
   77 |         _result_facts.ansible_facts.ansible_ssh_host_key_ecdsa_public_keytype is defined and
   78 |         _result_facts.ansible_facts.ansible_ssh_host_key_ecdsa_public is defined
   79 | 
   80 |     - name: Gather the package facts
   81 |       ansible.builtin.package_facts:
   82 |         manager: "{{ hostvars[_param_gather_host].package_manager }}"
   83 |       register: _result_packages
   84 |       no_log: "{{ not ((lookup('env', 'KUBEINIT_SHOW_PACKAGE_FACTS') | bool) or false) }}"
   85 | 
   86 |     - name: Set podman_is_installed
   87 |       ansible.builtin.set_fact:
   88 |         podman_is_installed: "{{ true if ('podman' in _result_packages.ansible_facts.packages) else false }}"
   89 | 
   90 |     - name: Gather the services facts
   91 |       ansible.builtin.service_facts:
   92 |       register: _result_services
   93 |       no_log: "{{ not ((lookup('env', 'KUBEINIT_SHOW_SERVICE_FACTS') | bool) or false) }}"
   94 | 
   95 |     - name: Set _service_state to unknown
   96 |       ansible.builtin.set_fact:
   97 |         _service_state: 'unknown'
   98 |       delegate_to: "{{ inventory_hostname }}"
   99 | 
  100 |     - name: Set _service_state when firewalld is defined
  101 |       ansible.builtin.set_fact:
  102 |         _service_state: "{{ _result_services.ansible_facts.services['firewalld'].state }}"
  103 |       delegate_to: "{{ inventory_hostname }}"
  104 |       when: _result_services.ansible_facts.services['firewalld'] is defined
  105 | 
  106 |     - name: Set _service_state when firewalld.service is defined
  107 |       ansible.builtin.set_fact:
  108 |         _service_state: "{{ _result_services.ansible_facts.services['firewalld.service'].state }}"
  109 |       delegate_to: "{{ inventory_hostname }}"
  110 |       when: _result_services.ansible_facts.services['firewalld.service'] is defined
  111 | 
  112 |     - name: Set firewalld_is_active
  113 |       ansible.builtin.set_fact:
  114 |         firewalld_is_active: "{{ true if _service_state == 'running' else false }}"
  115 | 
  116 |     - name: Clear _service_state
  117 |       ansible.builtin.set_fact:
  118 |         _service_state: ''
  119 |       delegate_to: "{{ inventory_hostname }}"
  120 | 
  121 |     - name: Set _service_state when podman is defined
  122 |       ansible.builtin.set_fact:
  123 |         _service_state: "{{ _result_services.ansible_facts.services['podman'].state }}"
  124 |       delegate_to: "{{ inventory_hostname }}"
  125 |       when: _result_services.ansible_facts.services['podman'] is defined
  126 | 
  127 |     - name: Set _service_state when podman.service is defined
  128 |       ansible.builtin.set_fact:
  129 |         _service_state: "{{ _result_services.ansible_facts.services['podman.service'].state }}"
  130 |       delegate_to: "{{ inventory_hostname }}"
  131 |       when: _result_services.ansible_facts.services['podman.service'] is defined
  132 | 
  133 |     - name: Set podman_is_active
  134 |       ansible.builtin.set_fact:
  135 |         podman_is_active: "{{ true if _service_state == 'running' else false }}"
  136 | 
  137 |     - name: Set _service_state to unknown
  138 |       ansible.builtin.set_fact:
  139 |         _service_state: 'unknown'
  140 |       delegate_to: "{{ inventory_hostname }}"
  141 | 
  142 |     - name: Set _service_state when ovs-vswitchd is defined
  143 |       ansible.builtin.set_fact:
  144 |         _service_state: "{{ _result_services.ansible_facts.services['ovs-vswitchd'].state }}"
  145 |       delegate_to: "{{ inventory_hostname }}"
  146 |       when: _result_services.ansible_facts.services['ovs-vswitchd'] is defined
  147 | 
  148 |     - name: Set _service_state when ovs-vswitchd.service is defined
  149 |       ansible.builtin.set_fact:
  150 |         _service_state: "{{ _result_services.ansible_facts.services['ovs-vswitchd.service'].state }}"
  151 |       delegate_to: "{{ inventory_hostname }}"
  152 |       when: _result_services.ansible_facts.services['ovs-vswitchd.service'] is defined
  153 | 
  154 |     - name: Set ovs_is_active
  155 |       ansible.builtin.set_fact:
  156 |         ovs_is_active: "{{ true if _service_state == 'running' else false }}"
  157 | 
  158 |     - name: Add more facts to hostvars
  159 |       ansible.builtin.set_fact:
  160 |         ansible_default_ipv4_address: "{{ _result_facts.ansible_facts.ansible_default_ipv4.address }}"
  161 |       when: _result_facts.ansible_facts.ansible_default_ipv4.address is defined
  162 | 
  163 |     - name: Add more facts to hostvars
  164 |       ansible.builtin.set_fact:
  165 |         ssh_connection_address: "{{ _result_facts.ansible_facts.ansible_env['SSH_CONNECTION'].split(' ')[2] }}"
  166 |       when: _result_facts.ansible_facts.ansible_env['SSH_CONNECTION'] is defined
  167 | 
  168 |     - name: Add more facts to hostvars
  169 |       ansible.builtin.set_fact:
  170 |         os: "{{ hostvars[_param_gather_host].os if (hostvars[_param_gather_host].os is defined) else hostvars[_param_gather_host].host_os }}"
  171 |         remote_path: "{{ _result_facts.ansible_facts.ansible_env['PATH'] }}"
  172 |         remote_home: "{{ _result_facts.ansible_facts.ansible_env['HOME'] }}"
  173 |         runtime_path: "{{ _result_facts.ansible_facts.ansible_env['XDG_RUNTIME_DIR'] | default('') | string }}"
  174 | 
  175 |     - name: Clear results
  176 |       ansible.builtin.set_fact:
  177 |         ansible_facts:
  178 |           pkg_mgr: "{{ _result_facts.ansible_facts.ansible_pkg_mgr }}"
  179 |         packages: {}
  180 |         services: {}
  181 |         _result_facts: {}
  182 |         _result_packages: {}
  183 |         _result_services: {}
  184 |         _service_state: ''
  185 | 
  186 |   delegate_to: "{{ _param_gather_host }}"
  187 |   delegate_facts: true
```
