# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-011

- Repository: `Checkmk/ansible-collection-checkmk.general`
- Commit: `50be8bde935f94e4702f40c9a549f86ffe773db1`
- Family: maintainability_complexity
- Rule: `ansibleguard/undocumented-complex-task`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `roles/agent/tasks/Linux.yml` (reported anchor line 136)
- Flagged construct: not named by the finding; the anchor line 136 lies in the task at line 136, name `{{ ansible_facts['system'] }}: Register Agent for automatic Updates using User Password.`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–287 of 287:

```text
    1 | ---
    2 | - name: "{{ ansible_facts['system'] }}: Get RPM or APT package facts."
    3 |   ansible.builtin.package_facts:
    4 |     manager: "auto"
    5 |   tags:
    6 |     - get-package-facts
    7 | 
    8 | - name: "{{ ansible_facts['system'] }}: Populate service facts."
    9 |   ansible.builtin.service_facts:
   10 |   tags:
   11 |     - configure-firewall
   12 | 
   13 | - name: "{{ ansible_facts['system'] }}: Prepare legacy agent support."
   14 |   when: |
   15 |     checkmk_agent_prep_legacy | bool
   16 |     and ansible_facts['packages']['systemd'][0]['version'] | regex_search('\d{1,}') | int < 220
   17 |   block:
   18 |     - name: "{{ ansible_facts['system'] }}: Install xinetd."
   19 |       become: true
   20 |       ansible.builtin.package:
   21 |         name: xinetd
   22 |         state: present
   23 |       tags:
   24 |         - install-package
   25 |         - install-prerequisites
   26 | 
   27 |     - name: "{{ ansible_facts['system'] }}: Enable xinetd."
   28 |       become: true
   29 |       ansible.builtin.service:
   30 |         name: xinetd
   31 |         state: started
   32 |         enabled: true
   33 |       tags:
   34 |         - enable-xinetd
   35 | 
   36 | - name: "{{ ansible_facts['os_family'] }}: Run OS Family specific tasks."
   37 |   ansible.builtin.include_tasks: "{{ ansible_facts['os_family'] }}.yml"
   38 |   tags:
   39 |     - always
   40 | 
   41 | - name: "{{ ansible_facts['system'] }}: Ensure Host Folder is present."
   42 |   checkmk.general.folder:
   43 |     server_url: "{{ checkmk_agent_server_protocol }}://{{ checkmk_agent_server }}:{{ checkmk_agent_server_port }}/"
   44 |     site: "{{ checkmk_agent_site }}"
   45 |     validate_certs: "{{ checkmk_agent_server_validate_certs | bool }}"
   46 |     api_user: "{{ checkmk_agent_user }}"
   47 |     api_secret: "{{ __checkmk_agent_auth }}"
   48 |     path: "{{ checkmk_agent_folder }}"
   49 |     state: "present"
   50 |   become: false
   51 |   delegate_to: "{{ checkmk_agent_delegate_api_calls }}"
   52 |   when: checkmk_agent_folder_create | bool and checkmk_agent_add_host | bool
   53 |   notify: "Activate changes"
   54 |   tags:
   55 |     - manage-host
   56 | 
   57 | - name: "{{ ansible_facts['system'] }}: Ensure Host is present in the correct Folder."
   58 |   checkmk.general.host:
   59 |     server_url: "{{ checkmk_agent_server_protocol }}://{{ checkmk_agent_server }}:{{ checkmk_agent_server_port }}/"
   60 |     site: "{{ checkmk_agent_site }}"
   61 |     validate_certs: "{{ checkmk_agent_server_validate_certs | bool }}"
   62 |     api_user: "{{ checkmk_agent_user }}"
   63 |     api_secret: "{{ __checkmk_agent_auth }}"
   64 |     folder: "{{ checkmk_agent_folder }}"
   65 |     name: "{{ checkmk_agent_host_name }}"
   66 |     state: "present"
   67 |   become: false
   68 |   register: __checkmk_agent_create_result
   69 |   delegate_to: "{{ checkmk_agent_delegate_api_calls }}"
   70 |   when: checkmk_agent_add_host | bool
   71 |   notify: "Activate changes"
   72 |   tags:
   73 |     - manage-host
   74 | 
   75 | - name: "{{ ansible_facts['system'] }}: Update Host Attributes."
   76 |   checkmk.general.host:
   77 |     server_url: "{{ checkmk_agent_server_protocol }}://{{ checkmk_agent_server }}:{{ checkmk_agent_server_port }}/"
   78 |     site: "{{ checkmk_agent_site }}"
   79 |     validate_certs: "{{ checkmk_agent_server_validate_certs | bool }}"
   80 |     api_user: "{{ checkmk_agent_user }}"
   81 |     api_secret: "{{ __checkmk_agent_auth }}"
   82 |     name: "{{ checkmk_agent_host_name }}"
   83 |     attributes: "{{ checkmk_agent_host_attributes }}"
   84 |     state: "present"
   85 |   become: false
   86 |   register: __checkmk_agent_update_attributes_result
   87 |   delegate_to: "{{ checkmk_agent_delegate_api_calls }}"
   88 |   when: checkmk_agent_add_host | bool
   89 |   notify: "Activate changes"
   90 |   tags:
   91 |     - manage-host
   92 | 
   93 | - name: "Ensure registration readiness."  # noqa no-handler
   94 |   tags:
   95 |     - always
   96 |   block:
   97 |     - name: "Trigger activation of changes."
   98 |       ansible.builtin.meta: flush_handlers
   99 | 
  100 | - name: "{{ ansible_facts['system'] }}: Check for Agent Updater Binary."
  101 |   ansible.builtin.stat:
  102 |     path: /usr/bin/cmk-update-agent
  103 |   register: __checkmk_agent_updater_binary
  104 |   tags:
  105 |     - register-agent
  106 | 
  107 | - name: "{{ ansible_facts['system'] }}: Check for Agent Controller Binary."
  108 |   ansible.builtin.stat:
  109 |     path: /usr/bin/cmk-agent-ctl
  110 |   register: __checkmk_agent_controller_binary
  111 |   tags:
  112 |     - register-agent
  113 | 
  114 | - name: "{{ ansible_facts['system'] }}: Read Updater State."
  115 |   become: true
  116 |   ansible.builtin.command: cat /var/lib/check_mk_agent/cache/plugins_cmk-update-agent.cache
  117 |   register: __checkmk_agent_updater_state
  118 |   changed_when: false
  119 |   failed_when: |
  120 |     not __checkmk_agent_updater_state.rc == 0
  121 |     and not __checkmk_agent_updater_state.rc == 1
  122 |   tags:
  123 |     - register-agent
  124 | 
  125 | - name: "{{ ansible_facts['system'] }}: Read Agent Controller State."
  126 |   become: true
  127 |   ansible.builtin.command: cat /var/lib/cmk-agent/registered_connections.json
  128 |   register: __checkmk_agent_registered_connections
  129 |   changed_when: false
  130 |   failed_when: |
  131 |     not __checkmk_agent_registered_connections.rc == 0
  132 |     and not __checkmk_agent_registered_connections.rc == 1
  133 |   tags:
  134 |     - register-agent
  135 | 
  136 | - name: "{{ ansible_facts['system'] }}: Register Agent for automatic Updates using User Password."
  137 |   become: true
  138 |   ansible.builtin.shell: |
  139 |     cmk-update-agent register -H {{ checkmk_agent_host_name }} \
  140 |     -s {{ checkmk_agent_registration_server }} -i {{ checkmk_agent_registration_site }} -p {{ checkmk_agent_registration_server_protocol }} \
  141 |     -U {{ checkmk_agent_user }} -P {{ __checkmk_agent_auth | ansible.builtin.quote }}
  142 |   no_log: "{{ checkmk_agent_no_log | bool }}"
  143 |   register: __checkmk_agent_update_state
  144 |   when: |
  145 |     checkmk_agent_edition | lower != "community"
  146 |     and __checkmk_agent_updater_binary.stat.exists | bool
  147 |     and checkmk_agent_update | bool
  148 |     and (checkmk_agent_pass is defined and checkmk_agent_pass | length > 0)
  149 |     and (checkmk_agent_secret is not defined)
  150 |     and not ((checkmk_agent_registration_server + '/' + checkmk_agent_registration_site in __checkmk_agent_updater_state.stdout)
  151 |     and ('"error": null' in __checkmk_agent_updater_state.stdout) )
  152 |   changed_when: "'Successfully registered agent of host' in __checkmk_agent_update_state.stderr"
  153 |   tags:
  154 |     - register-agent
  155 | 
  156 | - name: "{{ ansible_facts['system'] }}: Register Agent for automatic Updates using Automation Secret."
  157 |   become: true
  158 |   ansible.builtin.shell: |
  159 |     cmk-update-agent register -H {{ checkmk_agent_host_name }} \
  160 |     -s {{ checkmk_agent_registration_server }} -i {{ checkmk_agent_registration_site }} -p {{ checkmk_agent_registration_server_protocol }} \
  161 |     -U {{ checkmk_agent_user }} -S {{ __checkmk_agent_auth | ansible.builtin.quote }}
  162 |   no_log: "{{ checkmk_agent_no_log | bool }}"
  163 |   register: __checkmk_agent_update_state
  164 |   when: |
  165 |     checkmk_agent_edition | lower != "community"
  166 |     and __checkmk_agent_updater_binary.stat.exists | bool
  167 |     and checkmk_agent_update | bool
  168 |     and (checkmk_agent_secret is defined and checkmk_agent_secret | length > 0)
  169 |     and not ((checkmk_agent_registration_server + '/' + checkmk_agent_registration_site in __checkmk_agent_updater_state.stdout)
  170 |     and ('"error": null' in __checkmk_agent_updater_state.stdout) )
  171 |   changed_when: "'Successfully registered agent of host' in __checkmk_agent_update_state.stderr"
  172 |   tags:
  173 |     - register-agent
  174 | 
  175 | - name: "{{ ansible_facts['system'] }}: Register Agent for TLS directly."
  176 |   become: true
  177 |   ansible.builtin.shell: |
  178 |     cmk-agent-ctl register -H {{ checkmk_agent_host_name }} \
  179 |     -s {{ checkmk_agent_registration_server }} -i {{ checkmk_agent_registration_site }} \
  180 |     -U {{ checkmk_agent_user }} -P {{ __checkmk_agent_auth | ansible.builtin.quote }} --trust-cert
  181 |   no_log: "{{ checkmk_agent_no_log | bool }}"
  182 |   register: __checkmk_agent_tls_state
  183 |   when: |
  184 |     __checkmk_agent_controller_binary.stat.exists | bool
  185 |     and checkmk_agent_tls | bool
  186 |     and not checkmk_agent_delegate_registration | bool
  187 |     and (__checkmk_agent_auth is defined and __checkmk_agent_auth | length > 0)
  188 |     and not checkmk_agent_registration_server + '/' + checkmk_agent_registration_site in __checkmk_agent_registered_connections.stdout
  189 |   changed_when: "'Registration complete' in __checkmk_agent_tls_state.stdout"
  190 |   tags:
  191 |     - register-agent
  192 | 
  193 | - name: "{{ ansible_facts['system'] }}: Register Agent for TLS with proxy-register."
  194 |   become: true
  195 |   ansible.builtin.shell: |
  196 |     cmk-agent-ctl proxy-register -H {{ checkmk_agent_host_name }} \
  197 |     -s {{ checkmk_agent_registration_server }} -i {{ checkmk_agent_registration_site }} \
  198 |     -U {{ checkmk_agent_user }} -P {{ __checkmk_agent_auth | ansible.builtin.quote }} --trust-cert
  199 |   no_log: "{{ checkmk_agent_no_log | bool }}"
  200 |   register: __checkmk_agent_proxy_registration_state
  201 |   when: |
  202 |     __checkmk_agent_controller_binary.stat.exists | bool
  203 |     and checkmk_agent_tls | bool
  204 |     and checkmk_agent_delegate_registration | bool
  205 |     and (__checkmk_agent_auth is defined and __checkmk_agent_auth | length > 0)
  206 |     and not checkmk_agent_registration_server + '/' + checkmk_agent_registration_site in __checkmk_agent_registered_connections.stdout
  207 |   delegate_to: "{{ checkmk_agent_delegate_registration_target }}"
  208 | [REDACTED PRIVATE KEY BLOCK]
  209 | [REDACTED PRIVATE KEY CONTENT]
      [... 78 further identical redacted lines, through 287]
```
