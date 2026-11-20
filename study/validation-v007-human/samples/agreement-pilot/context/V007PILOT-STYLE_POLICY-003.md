# Frozen source context: V007PILOT-STYLE_POLICY-003

- Repository: `Linuxfabrik/lfops`
- Commit: `9b51b59db61b87e01cc75adef892e5345a5bf4b1`
- Family: Style/policy
- Rule: `ansibleguard/inconsistent-naming-convention`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/apache_solr/tasks/main.yml` (reported anchor line 110)
- Object: `task` `8fba400d76fc974b5dcc6a02c793e9ea19fcd4518961c4eb08d53ea22540becf`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–218 of 218:

```text
    1 | - block:
    2 | 
    3 |   - name: 'install {{ __apache_solr__java_package[apache_solr__version.split(".")[0]] }}'
    4 |     ansible.builtin.package:
    5 |       name: '{{ __apache_solr__java_package[apache_solr__version.split(".")[0]] }}'
    6 |       state: 'present'
    7 | 
    8 |   - name: 'Download and verify Apache Solr {{ apache_solr__version }} from Solr archive (the full binary package, for all operating systems)'
    9 |     ansible.builtin.get_url:
   10 |       url: 'https://archive.apache.org/dist/solr/solr/{{ apache_solr__version }}/solr-{{ apache_solr__version }}.tgz'
   11 |       dest: '/tmp/solr-{{ apache_solr__version }}.tgz'
   12 |       checksum: '{{ apache_solr__checksum }}'
   13 |     delegate_to: 'localhost'
   14 |     become: false
   15 |     check_mode: false # run task even if `--check` is specified
   16 |     changed_when: false # just gathering info, no actual change
   17 |     when:
   18 |       - 'apache_solr__version is version("9.0.0", ">=")'
   19 | 
   20 |   - name: 'Download and verify Apache Solr {{ apache_solr__version }} from Lucene archive (the full binary package, for all operating systems)'
   21 |     ansible.builtin.get_url:
   22 |       url: 'https://archive.apache.org/dist/lucene/solr/{{ apache_solr__version }}/solr-{{ apache_solr__version }}.tgz'
   23 |       dest: '/tmp/solr-{{ apache_solr__version }}.tgz'
   24 |       checksum: '{{ apache_solr__checksum }}'
   25 |     delegate_to: 'localhost'
   26 |     become: false
   27 |     check_mode: false # run task even if `--check` is specified
   28 |     changed_when: false # just gathering info, no actual change
   29 |     when:
   30 |       - 'apache_solr__version is version("9.0.0", "<")'
   31 | 
   32 |   - name: 'Ensure group "{{ apache_solr__user }}" exists'
   33 |     ansible.builtin.group:
   34 |       name: '{{ apache_solr__user }}'
   35 |       state: 'present'
   36 | 
   37 |   - name: 'Add the user "{{ apache_solr__user }}" with primary group of "{{ apache_solr__user }}"'
   38 |     ansible.builtin.user:
   39 |       comment: 'User for Apache Solr service'
   40 |       create_home: true
   41 |       group: '{{ apache_solr__user }}'
   42 |       home: '{{ apache_solr__var_dir }}'
   43 |       name: '{{ apache_solr__user }}'
   44 |       system: true
   45 | 
   46 |   - name: 'mkdir -p {{ apache_solr__install_dir }}/solr-{{ apache_solr__version }}'
   47 |     ansible.builtin.file:
   48 |       path: '{{ apache_solr__install_dir }}/solr-{{ apache_solr__version }}'
   49 |       state: 'directory'
   50 | 
   51 |   - name: 'mkdir -p {{ apache_solr__data_dir }}'
   52 |     ansible.builtin.file:
   53 |       path: '{{ apache_solr__data_dir }}'
   54 |       state: 'directory'
   55 | 
   56 |   - name: 'mkdir -p {{ apache_solr__logs_dir }}'
   57 |     ansible.builtin.file:
   58 |       path: '{{ apache_solr__logs_dir }}'
   59 |       state: 'directory'
   60 |       owner: '{{ apache_solr__user }}'
   61 |       group: '{{ apache_solr__user }}'
   62 |       mode: 0o750
   63 | 
   64 |   - name: 'tar xvzf /tmp/solr-{{ apache_solr__version }}.tgz'
   65 |     ansible.builtin.unarchive:
   66 |       src: '/tmp/solr-{{ apache_solr__version }}.tgz'
   67 |       dest: '{{ apache_solr__install_dir }}/solr-{{ apache_solr__version }}/'
   68 |       remote_src: false
   69 |       extra_opts:
   70 |         - '--strip-components=1'
   71 | 
   72 |   - name: 'ln -s {{ apache_solr__install_dir }}/solr-{{ apache_solr__version }} {{ apache_solr__install_dir }}/solr'
   73 |     ansible.builtin.file:
   74 |       src: '{{ apache_solr__install_dir }}/solr-{{ apache_solr__version }}'
   75 |       dest: '{{ apache_solr__install_dir }}/solr'
   76 |       state: 'link'
   77 |     ignore_errors: '{{ ansible_check_mode }}' # ignore errors if `--check` is specified
   78 |     notify: 'apache_solr: restart solr.service'
   79 | 
   80 |   - name: 'Deploy {{ apache_solr__install_dir }}/solr/bin/solr.in.sh'
   81 |     ansible.builtin.template:
   82 |       backup: true
   83 |       src: 'opt/solr/bin/solr.in.sh.j2'
   84 |       dest: '{{ apache_solr__install_dir }}/solr/bin/solr.in.sh'
   85 |     notify: 'apache_solr: restart solr.service'
   86 | 
   87 |   - name: 'Deploy {{ apache_solr__log4j_props }}'
   88 |     ansible.builtin.template:
   89 |       backup: true
   90 |       src: 'var/solr/log4j.xml.j2'
   91 |       dest: '{{ apache_solr__log4j_props }}'
   92 |     notify: 'apache_solr: restart solr.service'
   93 | 
   94 |   - name: 'chown -R {{ apache_solr__user }}:{{ apache_solr__user }} {{ apache_solr__install_dir }}/solr'
   95 |     ansible.builtin.file:
   96 |       group: '{{ apache_solr__user }}'
   97 |       owner: '{{ apache_solr__user }}'
   98 |       path: '{{ apache_solr__install_dir }}/solr'
   99 |       recurse: true
  100 |       state: 'directory'
  101 | 
  102 |   - name: 'chown -R {{ apache_solr__user }}:{{ apache_solr__user }} {{ apache_solr__var_dir }}'
  103 |     ansible.builtin.file:
  104 |       group: '{{ apache_solr__user }}'
  105 |       owner: '{{ apache_solr__user }}'
  106 |       path: '{{ apache_solr__var_dir }}'
  107 |       recurse: true
  108 |       state: 'directory'
  109 | 
  110 |   - name: 'find {{ apache_solr__install_dir }}/solr-{{ apache_solr__version }} -type d -exec chmod --changes 0755 {} \;'
  111 |     ansible.builtin.command: 'find {{ apache_solr__install_dir }}/solr-{{ apache_solr__version }} -type d -exec chmod --changes 0755 {} \;'
  112 |     register: 'apache_solr__chmod_dirs_result'
  113 |     changed_when: 'apache_solr__chmod_dirs_result["stdout"] | length > 0'
  114 | 
  115 |   - name: 'find {{ apache_solr__install_dir }}/solr-{{ apache_solr__version }} -type f -exec chmod --changes 0644 {} \;'
  116 |     ansible.builtin.command: 'find {{ apache_solr__install_dir }}/solr-{{ apache_solr__version }} -type f -exec chmod --changes 0644 {} \;'
  117 |     register: 'apache_solr__chmod_files_result'
  118 |     changed_when: 'apache_solr__chmod_files_result["stdout"] | length > 0'
  119 | 
  120 |   - name: 'chmod -R 0755 {{ apache_solr__install_dir }}/solr-{{ apache_solr__version }}/bin'
  121 |     ansible.builtin.file:
  122 |       mode: 0o755
  123 |       path: '{{ apache_solr__install_dir }}/solr-{{ apache_solr__version }}/bin'
  124 |       recurse: true
  125 |       state: 'directory'
  126 | 
  127 |   - name: 'find {{ apache_solr__var_dir }} -type d -exec chmod --changes 0750 {} \;'
  128 |     ansible.builtin.command: 'find {{ apache_solr__var_dir }} -type d -exec chmod --changes 0750 {} \;'
  129 |     register: 'apache_solr__chmod_dirs_result'
  130 |     changed_when: 'apache_solr__chmod_dirs_result["stdout"] | length > 0'
  131 | 
  132 |   - name: 'find {{ apache_solr__var_dir }} -type f -exec chmod --changes 0640 {} \;'
  133 |     ansible.builtin.command: 'find {{ apache_solr__var_dir }} -type f -exec chmod --changes 0640 {} \;'
  134 |     register: 'apache_solr__chmod_files_result'
  135 |     changed_when: 'apache_solr__chmod_files_result["stdout"] | length > 0'
  136 | 
  137 |   tags:
  138 |     - 'apache_solr'
  139 | 
  140 | 
  141 | - block:
  142 | 
  143 |   - name: 'Deploy /etc/systemd/system/solr.service'
  144 |     ansible.builtin.template:
  145 |       backup: true
  146 |       src: 'etc/systemd/system/solr.service.j2'
  147 |       dest: '/etc/systemd/system/solr.service'
  148 |       owner: 'root'
  149 |       group: 'root'
  150 |       mode: 0o644
  151 |     register: 'apache_solr__systemd_service_template_result'
  152 | 
  153 |   - name: 'systemctl daemon-reload'
  154 |     ansible.builtin.systemd:
  155 |       daemon_reload: true
  156 |     when:
  157 |       - 'apache_solr__systemd_service_template_result is changed'
  158 | 
  159 |   tags:
  160 |     - 'apache_solr'
  161 |     - 'apache_solr:state'
  162 | 
  163 | 
  164 | # user management
  165 | - block:
  166 | 
  167 |   - name: 'Combined Users:'
  168 |     ansible.builtin.debug:
  169 |       var: 'apache_solr__users__combined_var'
  170 | 
  171 |   - name: 'Generate hashed passwords'
  172 |     ansible.builtin.shell: |-
  173 |       set -o pipefail
  174 |       PW='{{ item["password"] }}'
  175 |       SALT=$(pwgen 48 -1)
  176 |       echo '{{ item["username"] }}'
  177 |       echo "$(echo -n "$SALT$PW" | sha256sum --binary | xxd -r -p | sha256sum --binary | xxd -r -p | base64 --wrap=1024) $(echo -n "$SALT" | base64 --wrap=1024)"
  178 |       echo '{{ item["role"] }}'
  179 |       echo '{{ item["state"] }}'
  180 |     args:
  181 |       executable: '/bin/bash'
  182 |     loop: '{{ apache_solr__users__combined_var }}'
  183 |     register: 'apache_solr__pwhashes'
  184 |     when:
  185 |       - 'apache_solr__users__combined_var is defined and apache_solr__users__combined_var | length > 0'
  186 | 
  187 |   - name: 'Deploy {{ apache_solr__var_dir }}/security.json'
  188 |     ansible.builtin.template:
  189 |       backup: true
  190 |       src: 'var/solr/security.json.j2'
  191 |       dest: '{{ apache_solr__var_dir }}/security.json'
  192 |     notify: 'apache_solr: restart solr.service'
  193 |     when:
  194 |       - 'apache_solr__users__combined_var is defined and apache_solr__users__combined_var | length > 0'
  195 | 
  196 |   tags:
  197 |     - 'apache_solr'
  198 |     - 'apache_solr:users'
  199 | 
  200 | 
  201 | # runs last, after security.json above, so that a fresh installation starts Solr with the deployed
  202 | # configuration and the restart handler can skip the redundant bounce.
  203 | - block:
  204 | 
  205 |   - name: 'systemctl {{ apache_solr__service_enabled | bool | ternary("enable", "disable") }} solr.service'
  206 |     ansible.builtin.systemd:
  207 |       name: 'solr.service'
  208 |       enabled: '{{ apache_solr__service_enabled }}'
  209 | 
  210 |   - name: 'systemctl {{ apache_solr__service_state | regex_replace("p?ed$", "") }} solr.service'
  211 |     ansible.builtin.systemd:
  212 |       name: 'solr.service'
  213 |       state: '{{ apache_solr__service_state }}'
  214 |     register: '__apache_solr__service_state_result'
  215 | 
  216 |   tags:
  217 |     - 'apache_solr'
  218 |     - 'apache_solr:state'
```
