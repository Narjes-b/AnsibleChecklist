# Frozen source context: V007PILOT-STRUCTURE_REUSE-017

- Repository: `Linuxfabrik/lfops`
- Commit: `9b51b59db61b87e01cc75adef892e5345a5bf4b1`
- Family: Structure/reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/chromium_headless/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `aea59ed471f942dc65ae2557c0abb4e565572bc11c1cb04156fa0e7da91e4933`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–157 of 157:

```text
    1 | - block:
    2 | 
    3 |   - name: 'Set platform/version specific variables'
    4 |     ansible.builtin.import_role:
    5 |       name: 'shared'
    6 |       tasks_from: 'platform-variables.yml'
    7 | 
    8 |   tags:
    9 |     - 'always'
   10 | 
   11 | 
   12 | - block:
   13 | 
   14 |   - name: 'groupadd --system chromium'
   15 |     ansible.builtin.group:
   16 |       name: 'chromium'
   17 |       state: 'present'
   18 |       system: true
   19 | 
   20 |   - name: 'useradd --system chromium'
   21 |     ansible.builtin.user:
   22 |       name: 'chromium'
   23 |       comment: 'Headless Chromium'
   24 |       group: 'chromium'
   25 |       home: '{{ chromium_headless__user_data_dir }}'
   26 |       shell: '/sbin/nologin'
   27 |       system: true
   28 |       state: 'present'
   29 | 
   30 |   - name: 'install --directory --owner chromium --group chromium --mode 0750 {{ chromium_headless__user_data_dir }}'
   31 |     ansible.builtin.file:
   32 |       path: '{{ chromium_headless__user_data_dir }}'
   33 |       state: 'directory'
   34 |       owner: 'chromium'
   35 |       group: 'chromium'
   36 |       mode: 0o750
   37 | 
   38 |   - name: 'Install required packages'
   39 |     ansible.builtin.package:
   40 |       name: '{{ __chromium_headless__packages }}'
   41 |       state: 'present'
   42 | 
   43 |   tags:
   44 |     - 'chromium_headless'
   45 | 
   46 | 
   47 | # Chromium itself does not implement the systemd socket-activation protocol (sd_listen_fds() / LISTEN_FDS); it always binds its own --remote-debugging-port. Direct socket activation is therefore not possible, so we deploy a systemd-socket-proxyd in front of Chromium: the .socket unit binds listen_port, the proxy accepts on that activated fd and forwards to backend_port (the port Chromium opens itself). --exit-idle-time on the proxy plus BindsTo= on chromium-headless.service ties Chromium's lifecycle to the proxy, so Chromium stops together with the proxy after the idle timeout.
   48 | # Two SELinux booleans are required: bind_any so the .socket can bind the listen port even when it has an unexpected port type (e.g. on Rocky 9, port 9222 maps to hplip_port_t and would otherwise reject the bind); connect_any so the proxy can connect to Chromium's non-standard backend port, which has no matching SELinux port type.
   49 | - block:
   50 | 
   51 |   - name: 'setsebool -P systemd_socket_proxyd_bind_any on'
   52 |     ansible.posix.seboolean:
   53 |       name: 'systemd_socket_proxyd_bind_any'
   54 |       persistent: true
   55 |       state: true
   56 | 
   57 |   - name: 'setsebool -P systemd_socket_proxyd_connect_any on'
   58 |     ansible.posix.seboolean:
   59 |       name: 'systemd_socket_proxyd_connect_any'
   60 |       persistent: true
   61 |       state: true
   62 | 
   63 |   # block
   64 |   when:
   65 |     - 'ansible_facts["selinux"]["status"] != "disabled"'
   66 |   tags:
   67 |     - 'chromium_headless'
   68 | 
   69 | 
   70 | - block:
   71 | 
   72 |   - name: 'Deploy /etc/systemd/system/chromium-headless-proxy.socket'
   73 |     ansible.builtin.template:
   74 |       backup: true
   75 |       src: 'etc/systemd/system/chromium-headless-proxy.socket.j2'
   76 |       dest: '/etc/systemd/system/chromium-headless-proxy.socket'
   77 |       owner: 'root'
   78 |       group: 'root'
   79 |       mode: 0o644
   80 |     register: '__chromium_headless__deploy_socket_result'
   81 |     notify:
   82 |       - 'chromium_headless: restart chromium-headless-proxy.socket'
   83 | 
   84 |   - name: 'Deploy /etc/systemd/system/chromium-headless-proxy.service'
   85 |     ansible.builtin.template:
   86 |       backup: true
   87 |       src: 'etc/systemd/system/chromium-headless-proxy.service.j2'
   88 |       dest: '/etc/systemd/system/chromium-headless-proxy.service'
   89 |       owner: 'root'
   90 |       group: 'root'
   91 |       mode: 0o644
   92 |     register: '__chromium_headless__deploy_proxy_result'
   93 | 
   94 |   - name: 'Deploy /etc/systemd/system/chromium-headless.service'
   95 |     ansible.builtin.template:
   96 |       backup: true
   97 |       src: 'etc/systemd/system/chromium-headless.service.j2'
   98 |       dest: '/etc/systemd/system/chromium-headless.service'
   99 |       owner: 'root'
  100 |       group: 'root'
  101 |       mode: 0o644
  102 |     register: '__chromium_headless__deploy_service_result'
  103 | 
  104 |   - name: 'Remove rpmnew / rpmsave (and Debian equivalents)'
  105 |     ansible.builtin.include_role:
  106 |       name: 'shared'
  107 |       tasks_from: 'remove-rpmnew-rpmsave.yml'
  108 |     vars:
  109 |       shared__remove_rpmnew_rpmsave_config_file: '{{ item }}'
  110 |     loop:
  111 |       - '/etc/systemd/system/chromium-headless-proxy.socket'
  112 |       - '/etc/systemd/system/chromium-headless-proxy.service'
  113 |       - '/etc/systemd/system/chromium-headless.service'
  114 | 
  115 |   # Run daemon-reload as a regular task (not as a handler), so it runs before the
  116 |   # state block below and so the restart-socket handler can rely on the registered
  117 |   # __chromium_headless__service_state_result to skip redundant restarts.
  118 |   - name: 'systemctl daemon-reload'
  119 |     ansible.builtin.systemd:
  120 |       daemon_reload: true
  121 |     when:
  122 |       - '__chromium_headless__deploy_socket_result is changed or
  123 |          __chromium_headless__deploy_proxy_result is changed or
  124 |          __chromium_headless__deploy_service_result is changed'
  125 | 
  126 |   tags:
  127 |     - 'chromium_headless'
  128 |     - 'chromium_headless:configure'
  129 | 
  130 | 
  131 | - block:
  132 | 
  133 |   - name: 'systemctl {{ chromium_headless__service_enabled | bool | ternary("enable", "disable") }} chromium-headless-proxy.socket'
  134 |     ansible.builtin.service:
  135 |       name: 'chromium-headless-proxy.socket'
  136 |       enabled: '{{ chromium_headless__service_enabled | bool }}'
  137 | 
  138 |   - name: 'systemctl {{ chromium_headless__service_state | regex_replace("p?ed$", "") }} chromium-headless-proxy.socket'
  139 |     ansible.builtin.service:
  140 |       name: 'chromium-headless-proxy.socket'
  141 |       state: '{{ chromium_headless__service_state }}'
  142 |     register: '__chromium_headless__service_state_result'
  143 | 
  144 |   tags:
  145 |     - 'chromium_headless'
  146 |     - 'chromium_headless:state'
  147 | 
  148 | 
  149 | - block:
  150 | 
  151 |   - name: 'Flush handlers so that the service is ready for dependent roles'
  152 |     ansible.builtin.meta: 'flush_handlers'
  153 | 
  154 |   tags:
  155 |     - 'chromium_headless'
  156 |     - 'chromium_headless:configure'
  157 |     - 'chromium_headless:state'
```

## Frozen tracked paths in the relevant role/scope

```text
roles/chromium_headless/README.md
roles/chromium_headless/defaults/main.yml
roles/chromium_headless/handlers/main.yml
roles/chromium_headless/meta/argument_specs.yml
roles/chromium_headless/tasks/main.yml
roles/chromium_headless/templates/etc/systemd/system/chromium-headless-proxy.service.j2
roles/chromium_headless/templates/etc/systemd/system/chromium-headless-proxy.socket.j2
roles/chromium_headless/templates/etc/systemd/system/chromium-headless.service.j2
roles/chromium_headless/vars/Debian.yml
roles/chromium_headless/vars/RedHat.yml
roles/chromium_headless/vars/RedHat8.yml
```
