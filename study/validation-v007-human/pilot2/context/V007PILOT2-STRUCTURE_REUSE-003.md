# Frozen source context: V007PILOT2-STRUCTURE_REUSE-003

- Repository: `Linuxfabrik/lfops`
- Commit: `9b51b59db61b87e01cc75adef892e5345a5bf4b1`
- Family: structure_reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/blocky/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/blocky/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–173 of 173:

```text
    1 | - block:
    2 | 
    3 |   - name: 'Install bind-utils'
    4 |     ansible.builtin.package:
    5 |       name:
    6 |         - 'bind-utils'
    7 |       state: 'present'
    8 | 
    9 |   tags:
   10 |     - 'blocky'
   11 | 
   12 | 
   13 | # inspiration:
   14 | # * https://0xerr0r.github.io/blocky/latest/installation/
   15 | # * https://0xerr0r.github.io/blocky/latest/configuration/
   16 | # * https://github.com/m0zgen/blocky-installer/blob/master/install.sh
   17 | 
   18 | - block:
   19 | 
   20 |   - name: 'Store the github release version'
   21 |     ansible.builtin.set_fact:
   22 |       blocky__github_version: '{{ blocky__version }}'
   23 |     when: 'blocky__version != "latest"'
   24 | 
   25 |   - block:
   26 | 
   27 |     - name: 'Get latest blocky release version'
   28 |       ansible.builtin.uri:
   29 |         url: 'https://api.github.com/repos/0xERR0R/blocky/releases/latest'
   30 |       register: 'blocky__github_release'
   31 |       check_mode: false # run task even if `--check` is specified
   32 |       delegate_to: 'localhost'
   33 |       become: false
   34 |       run_once: true
   35 | 
   36 |     - name: 'Store the latest release version'
   37 |       ansible.builtin.set_fact:
   38 |         blocky__github_version: '{{ blocky__github_release["json"]["tag_name"] }}'
   39 | 
   40 |     # block
   41 |     when: 'blocky__version == "latest"'
   42 | 
   43 |   - name: 'curl --location https://github.com/0xERR0R/blocky/releases/download/{{ blocky__github_version }}/blocky_{{ blocky__github_version }}_Linux_x86_64.tar.gz --output /tmp/ansible.blocky_{{ blocky__github_version }}_Linux_x86_64.tar.gz'
   44 |     ansible.builtin.get_url:
   45 |       url: 'https://github.com/0xERR0R/blocky/releases/download/{{ blocky__github_version }}/blocky_{{ blocky__github_version }}_Linux_x86_64.tar.gz'
   46 |       dest: '/tmp/ansible.blocky_{{ blocky__github_version }}_Linux_x86_64.tar.gz'
   47 |       mode: 0o644
   48 |     delegate_to: 'localhost'
   49 |     become: false
   50 |     changed_when: false # not an actual config change on the server
   51 |     check_mode: false # run task even if `--check` is specified
   52 | 
   53 |   - name: 'tar xzvf /tmp/ansible.blocky_{{ blocky__github_version }}_Linux_x86_64.tar.gz'
   54 |     ansible.builtin.unarchive:
   55 |       src: '/tmp/ansible.blocky_{{ blocky__github_version }}_Linux_x86_64.tar.gz'
   56 |       dest: '/tmp'
   57 |     delegate_to: 'localhost'
   58 |     become: false
   59 |     ignore_errors: '{{ ansible_check_mode }}' # ignore errors if `--check` is specified
   60 | 
   61 |   - name: 'scp /tmp/blocky {{ inventory_hostname }}:/usr/local/sbin/blocky'
   62 |     ansible.builtin.copy:
   63 |       src: '/tmp/blocky'
   64 |       dest: '/usr/local/sbin/blocky'
   65 |       owner: 'root'
   66 |       group: 'root'
   67 |       mode: 0o755
   68 |     notify: 'blocky: validate config & restart blocky.service'
   69 | 
   70 |   # if you want to use port 53 or 953 on Linux you should add CAP_NET_BIND_SERVICE capability to
   71 |   # the binary
   72 |   - name: 'setcap cap_net_bind_service=ep /usr/local/sbin/blocky'
   73 |     community.general.capabilities:
   74 |       path: '/usr/local/sbin/blocky'
   75 |       capability: 'cap_net_bind_service=ep'
   76 |       state: 'present'
   77 | 
   78 |   - name: 'useradd --system --shell /bin/false blocky'
   79 |     ansible.builtin.user:
   80 |       comment: 'blocky Service User'
   81 |       name: 'blocky'
   82 |       create_home: false
   83 |       shell: '/bin/false'
   84 |       state: 'present'
   85 |       system: true
   86 | 
   87 |   - name: 'mkdir -p /etc/blocky'
   88 |     ansible.builtin.file:
   89 |       path: '/etc/blocky'
   90 |       state: 'directory'
   91 |       owner: 'blocky'
   92 |       group: 'blocky'
   93 |       mode: 0o755
   94 | 
   95 |   - name: 'Check if /etc/blocky/config.yml exists'
   96 |     ansible.builtin.stat:
   97 |       path: '/etc/blocky/config.yml'
   98 |     changed_when: false
   99 |     register: 'blocky__remote_config'
  100 | 
  101 |   # copy the sample configuration file
  102 |   - name: 'scp etc/blocky/config.yml {{ inventory_hostname }}:/usr/local/sbin/blocky (the sample config)'
  103 |     ansible.builtin.copy:
  104 |       src: 'etc/blocky/config.yml'
  105 |       dest: '/etc/blocky/config.yml'
  106 |       owner: 'blocky'
  107 |       group: 'blocky'
  108 |       mode: 0o440
  109 |     when: 'not blocky__remote_config.stat.exists'
  110 | 
  111 |   tags:
  112 |     - 'blocky'
  113 | 
  114 | 
  115 | - block:
  116 | 
  117 |   - name: 'Deploy /etc/systemd/system/blocky.service'
  118 |     ansible.builtin.template:
  119 |       backup: true
  120 |       src: 'etc/systemd/system/blocky.service.j2'
  121 |       dest: '/etc/systemd/system/blocky.service'
  122 |       owner: 'root'
  123 |       group: 'root'
  124 |       mode: 0o644
  125 |     register: 'blocky__systemd_service_template_result'
  126 | 
  127 |   - name: 'systemctl daemon-reload'
  128 |     ansible.builtin.systemd:
  129 |       daemon_reload: true
  130 |     when:
  131 |       - 'blocky__systemd_service_template_result is changed'
  132 | 
  133 |   tags:
  134 |     - 'blocky'
  135 |     - 'blocky:state'
  136 | 
  137 | 
  138 | - block:
  139 | 
  140 |   # copy the user's configuration file
  141 |   - name: "scp user's blocky/config.yml to /etc/blocky/config.yml"
  142 |     ansible.builtin.copy:
  143 |       content: '{{ blocky__config_yml }}'
  144 |       dest: '/etc/blocky/config.yml'
  145 |       owner: 'blocky'
  146 |       group: 'blocky'
  147 |       mode: 0o440
  148 |       backup: true
  149 |     notify: 'blocky: validate config & restart blocky.service'
  150 | 
  151 |   tags:
  152 |     - 'blocky'
  153 |     - 'blocky:configure'
  154 | 
  155 | 
  156 | # runs last, after /etc/blocky/config.yml above, so that a fresh installation starts blocky with
  157 | # the deployed configuration and the restart handler can skip the redundant bounce.
  158 | - block:
  159 | 
  160 |   - name: 'systemctl {{ blocky__service_enabled | bool | ternary("enable", "disable") }} blocky.service'
  161 |     ansible.builtin.systemd:
  162 |       name: 'blocky.service'
  163 |       enabled: '{{ blocky__service_enabled }}'
  164 | 
  165 |   - name: 'systemctl {{ blocky__service_state | regex_replace("p?ed$", "") }} blocky.service'
  166 |     ansible.builtin.systemd:
  167 |       name: 'blocky.service'
  168 |       state: '{{ blocky__service_state }}'
  169 |     register: '__blocky__service_state_result'
  170 | 
  171 |   tags:
  172 |     - 'blocky'
  173 |     - 'blocky:state'
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/blocky`; 6 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

roles/blocky/README.md
roles/blocky/defaults/main.yml
roles/blocky/files/etc/blocky/config.yml
roles/blocky/handlers/main.yml
roles/blocky/tasks/main.yml
roles/blocky/templates/etc/systemd/system/blocky.service.j2
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- leaf tasks (not counting block containers): 17 (the rule needs more than 10)
- include/import task or role, or play-level roles, present: no
```
