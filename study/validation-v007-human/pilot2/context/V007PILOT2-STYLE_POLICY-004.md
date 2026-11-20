# Frozen source context: V007PILOT2-STYLE_POLICY-004

- Repository: `Linuxfabrik/lfops`
- Commit: `9b51b59db61b87e01cc75adef892e5345a5bf4b1`
- Family: style_policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/podman_containers/tasks/main.yml` (reported anchor line 202)
- Flagged construct: task `systemctl {{ (item[`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–297 of 297:

```text
    1 | - block:
    2 | 
    3 |   - name: 'Install podman systemd-container'
    4 |     ansible.builtin.package:
    5 |       name:
    6 |         - 'podman'
    7 |         - 'systemd-container'
    8 |       state: 'present'
    9 | 
   10 |   tags:
   11 |     - 'podman_containers'
   12 | 
   13 | 
   14 | - block:
   15 | 
   16 |   - name: 'mkdir -p /etc/containers/systemd/'
   17 |     ansible.builtin.file:
   18 |       path: '/etc/containers/systemd/'
   19 |       state: 'directory'
   20 |       owner: 'root'
   21 |       group: 'root'
   22 |       mode: 0o755
   23 | 
   24 |   - name: 'Get user UIDs'
   25 |     ansible.builtin.getent:
   26 |       database: 'passwd'
   27 | 
   28 |   - name: 'mkdir -p /etc/containers/systemd/users/$UID'
   29 |     ansible.builtin.file:
   30 |       path: '/etc/containers/systemd/users/{{ ansible_facts["getent_passwd"][item["user"]][1] }}'
   31 |       state: 'directory'
   32 |       owner: 'root'
   33 |       group: 'root'
   34 |       mode: 0o755
   35 |     loop: '{{
   36 |           (podman_containers__containers__combined_var +
   37 |           podman_containers__networks__combined_var +
   38 |           podman_containers__volumes__combined_var)
   39 |           | selectattr("user", "defined")
   40 |       }}'
   41 |     loop_control:
   42 |       label: '{{ item["name"] }} - user: {{ item["user"] }})'
   43 | 
   44 |   tags:
   45 |     - 'podman_containers'
   46 |     - 'podman_containers:containers'
   47 | 
   48 | 
   49 | - block:
   50 |   # Note about the handling of the suffixes:
   51 |   # `.volume` & `.network` quadlets always get a `-volume` or `-network` suffix during the conversion to `.service` files.
   52 |   # the name of `.container` quadlets is used as is for the `.service` files.
   53 |   # so for consistency, we always add a `-container` suffix to the `.container` quadlets, so that the unit is `-container.service`
   54 | 
   55 |   - name: 'Remove container units'
   56 |     ansible.builtin.file:
   57 |       path: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary(
   58 |         "/etc/containers/systemd/users/" ~ ansible_facts["getent_passwd"][item["user"]][1] ~ "/",
   59 |         "/etc/containers/systemd"
   60 |         ) }}/{{ item["name"] }}-container.container'
   61 |       state: 'absent'
   62 |     when:
   63 |       - 'item["state"] | d("started") == "absent"'
   64 |     loop: '{{ podman_containers__containers__combined_var }}'
   65 |     loop_control:
   66 |       label: '{{ item["name"] }}'
   67 |     notify: 'podman_containers: systemctl daemon-reload'
   68 | 
   69 |   - name: 'Deploy container units'
   70 |     ansible.builtin.template:
   71 |       backup: true
   72 |       src: 'etc/containers/systemd/container.j2'
   73 |       dest: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary(
   74 |         "/etc/containers/systemd/users/" ~ ansible_facts["getent_passwd"][item["user"]][1],
   75 |         "/etc/containers/systemd"
   76 |         ) }}/{{ item["name"] }}-container.container'
   77 |       owner: '{{ item["user"] | d("root") }}'
   78 |       group: '{{ item["user"] | d("root") }}'
   79 |       mode: 0o600 # could contain secrets
   80 |     when:
   81 |       - 'item["state"] | d("started") != "absent"'
   82 |     loop: '{{ podman_containers__containers__combined_var }}'
   83 |     loop_control:
   84 |       label: '{{ item["name"] }}'
   85 |     notify: 'podman_containers: systemctl daemon-reload'
   86 | 
   87 |   tags:
   88 |     - 'podman_containers'
   89 |     - 'podman_containers:containers'
   90 | 
   91 | 
   92 | - block:
   93 | 
   94 |   - name: 'Remove network units'
   95 |     ansible.builtin.file:
   96 |       path: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary(
   97 |         "/etc/containers/systemd/users/" ~ ansible_facts["getent_passwd"][item["user"]][1],
   98 |         "/etc/containers/systemd"
   99 |         ) }}/{{ item["name"] }}.network'
  100 |       state: 'absent'
  101 |     when:
  102 |       - 'item["state"] | d("started") == "absent"'
  103 |     loop: '{{ podman_containers__networks__combined_var }}'
  104 |     loop_control:
  105 |       label: '{{ item["name"] }}'
  106 |     notify: 'podman_containers: systemctl daemon-reload'
  107 | 
  108 |   - name: 'Deploy network units'
  109 |     ansible.builtin.template:
  110 |       backup: true
  111 |       src: 'etc/containers/systemd/network.j2'
  112 |       dest: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary(
  113 |         "/etc/containers/systemd/users/" ~ ansible_facts["getent_passwd"][item["user"]][1],
  114 |         "/etc/containers/systemd"
  115 |         ) }}/{{ item["name"] }}.network'
  116 |       owner: '{{ item["user"] | d("root") }}'
  117 |       group: '{{ item["user"] | d("root") }}'
  118 |       mode: 0o600 # could contain secrets
  119 |     when:
  120 |       - 'item["state"] | d("started") != "absent"'
  121 |     loop: '{{ podman_containers__networks__combined_var }}'
  122 |     loop_control:
  123 |       label: '{{ item["name"] }}'
  124 |     notify: 'podman_containers: systemctl daemon-reload'
  125 | 
  126 |   tags:
  127 |     - 'podman_containers'
  128 |     - 'podman_containers:networks'
  129 | 
  130 | 
  131 | - block:
  132 | 
  133 |   - name: 'Remove volume units'
  134 |     ansible.builtin.file:
  135 |       path: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary(
  136 |         "/etc/containers/systemd/users/" ~ ansible_facts["getent_passwd"][item["user"]][1],
  137 |         "/etc/containers/systemd"
  138 |         ) }}/{{ item["name"] }}.volume'
  139 |       state: 'absent'
  140 |     when:
  141 |       - 'item["state"] | d("started") == "absent"'
  142 |     loop: '{{ podman_containers__volumes__combined_var }}'
  143 |     loop_control:
  144 |       label: '{{ item["name"] }}'
  145 |     notify: 'podman_containers: systemctl daemon-reload'
  146 | 
  147 |   - name: 'Deploy volume units'
  148 |     ansible.builtin.template:
  149 |       backup: true
  150 |       src: 'etc/containers/systemd/volume.j2'
  151 |       dest: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary(
  152 |         "/etc/containers/systemd/users/" ~ ansible_facts["getent_passwd"][item["user"]][1],
  153 |         "/etc/containers/systemd"
  154 |         ) }}/{{ item["name"] }}.volume'
  155 |       owner: '{{ item["user"] | d("root") }}'
  156 |       group: '{{ item["user"] | d("root") }}'
  157 |       mode: 0o600 # could contain secrets
  158 |     when:
  159 |       - 'item["state"] | d("started") != "absent"'
  160 |     loop: '{{ podman_containers__volumes__combined_var }}'
  161 |     loop_control:
  162 |       label: '{{ item["name"] }}'
  163 |     notify: 'podman_containers: systemctl daemon-reload'
  164 | 
  165 |   tags:
  166 |     - 'podman_containers'
  167 |     - 'podman_containers:volumes'
  168 | 
  169 | 
  170 | - block:
  171 |   # Note about enabling / disabling units todo
  172 |   # also, we always do a `daemon_reload`. this is easier here than via a handler, as the daemon needs to be reloaded for the correct users.
  173 | 
  174 |   - name: 'systemctl {{ (item["state"] | d("started")) | regex_replace("p?ed$", "") }} {{ item["name"] }}-network.service'
  175 |     ansible.builtin.systemd:
  176 |       name: '{{ item["name"] }}-network.service'
  177 |       scope: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary("user", omit) }}'
  178 |       state: '{{ item["state"] | d("started") }}'
  179 |       daemon_reload: true
  180 |     become: true
  181 |     become_user: '{{ item["user"] | d(omit) }}'
  182 |     when:
  183 |       - 'item["state"] | d("started") not in ["present", "absent"]'
  184 |     loop: '{{ podman_containers__networks__combined_var }}'
  185 |     loop_control:
  186 |       label: '{{ item["name"] }}'
  187 | 
  188 |   - name: 'systemctl {{ (item["state"] | d("started")) | regex_replace("p?ed$", "") }} {{ item["name"] }}-volume.service'
  189 |     ansible.builtin.systemd:
  190 |       name: '{{ item["name"] }}-volume.service'
  191 |       scope: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary("user", omit) }}'
  192 |       state: '{{ item["state"] | d("started") }}'
  193 |       daemon_reload: true
  194 |     become: true
  195 |     become_user: '{{ item["user"] | d(omit) }}'
  196 |     when:
  197 |       - 'item["state"] | d("started") not in ["present", "absent"]'
  198 |     loop: '{{ podman_containers__volumes__combined_var }}'
  199 |     loop_control:
  200 |       label: '{{ item["name"] }}'
  201 | 
  202 |   - name: 'systemctl {{ (item["state"] | d("started")) | regex_replace("p?ed$", "") }} {{ item["name"] }}-container.service'
  203 |     ansible.builtin.systemd:
  204 |       name: '{{ item["name"] }}-container.service'
  205 |       scope: '{{ (item["user"] is defined and item["user"] | length > 0) | ternary("user", omit) }}'
  206 |       state: '{{ item["state"] | d("started") }}'
  207 |       daemon_reload: true
  208 |     become: true
  209 |     become_user: '{{ item["user"] | d(omit) }}'
  210 |     when:
  211 |       - 'item["state"] | d("started") not in ["present", "absent"]'
  212 |     loop: '{{ podman_containers__containers__combined_var }}'
  213 |     loop_control:
  214 |       label: '{{ item["name"] }} - state: {{ item["state"] | d("started") }}'
  215 | 
  216 |   tags:
  217 |     - 'podman_containers'
  218 |     - 'podman_containers:state'
  219 | 
  220 | 
  221 | - block:
  222 | 
  223 |   - name: 'mkdir -p /etc/systemd/system/podman-auto-update.timer.d/ # system'
  224 |     ansible.builtin.file:
  225 |       path: '/etc/systemd/system/podman-auto-update.timer.d/'
  226 |       state: 'directory'
  227 |       owner: 'root'
  228 |       group: 'root'
  229 |       mode: 0o755
  230 |     when:
  231 |       - 'podman_containers__auto_update__combined_var | selectattr("user", "equalto", "root") | selectattr("on_calendar", "defined") | length > 0'
  232 | 
  233 |   - name: 'mkdir -p ~/.config/systemd/user/podman-auto-update.timer.d/ # user'
  234 |     ansible.builtin.file:
  235 |       path: '~{{ item["user"] }}/.config/systemd/user/podman-auto-update.timer.d/'
  236 |       state: 'directory'
  237 |       owner: '{{ item["user"] }}'
  238 |       group: '{{ item["user"] }}'
  239 |       mode: 0o755
  240 |     become: true
  241 |     become_user: '{{ item["user"] }}'
  242 |     when:
  243 |       - 'item["user"] != "root"'
  244 |       - 'item["on_calendar"] is defined'
  245 |     loop: '{{ podman_containers__auto_update__combined_var }}'
  246 |     loop_control:
  247 |       label: '{{ item["user"] }}'
  248 | 
  249 |   - name: 'Deploy podman-auto-update.timer.d/z00-linuxfabrik.conf # system'
  250 |     ansible.builtin.template:
  251 |       backup: true
  252 |       src: 'etc/systemd/system/podman-auto-update.timer.d/z00-linuxfabrik.conf.j2'
  253 |       dest: '/etc/systemd/system/podman-auto-update.timer.d/z00-linuxfabrik.conf'
  254 |       owner: 'root'
  255 |       group: 'root'
  256 |       mode: 0o644
  257 |     vars:
  258 |       __podman_containers__auto_update_on_calendar: '{{ (podman_containers__auto_update__combined_var | selectattr("user", "equalto", "root") | first)["on_calendar"] }}'
  259 |     when:
  260 |       - 'podman_containers__auto_update__combined_var | selectattr("user", "equalto", "root") | selectattr("on_calendar", "defined") | length > 0'
  261 |     notify: 'podman_containers: systemctl daemon-reload'
  262 | 
  263 |   - name: 'Deploy podman-auto-update.timer.d/z00-linuxfabrik.conf # user'
  264 |     ansible.builtin.template:
  265 |       backup: true
  266 |       src: 'etc/systemd/system/podman-auto-update.timer.d/z00-linuxfabrik.conf.j2'
  267 |       dest: '~{{ item["user"] }}/.config/systemd/user/podman-auto-update.timer.d/z00-linuxfabrik.conf'
  268 |       owner: '{{ item["user"] }}'
  269 |       group: '{{ item["user"] }}'
  270 |       mode: 0o644
  271 |     vars:
  272 |       __podman_containers__auto_update_on_calendar: '{{ item["on_calendar"] }}'
  273 |     become: true
  274 |     become_user: '{{ item["user"] }}'
  275 |     when:
  276 |       - 'item["user"] != "root"'
  277 |       - 'item["on_calendar"] is defined'
  278 |     loop: '{{ podman_containers__auto_update__combined_var }}'
  279 |     loop_control:
  280 |       label: '{{ item["user"] }}'
  281 | 
  282 |   - name: 'systemctl enable/disable (--user) --now podman-auto-update.timer'
  283 |     ansible.builtin.systemd:
  284 |       name: 'podman-auto-update.timer'
  285 |       scope: '{{ (item["user"] == "root") | ternary(omit, "user") }}'
  286 |       enabled: '{{ item["state"] | d("present") == "present" }}'
  287 |       state: '{{ (item["state"] | d("present") == "present") | ternary("started", "stopped") }}'
  288 |       daemon_reload: true
  289 |     become: '{{ item["user"] != "root" }}'
  290 |     become_user: '{{ (item["user"] != "root") | ternary(item["user"], omit) }}'
  291 |     loop: '{{ podman_containers__auto_update__combined_var }}'
  292 |     loop_control:
  293 |       label: '{{ item["user"] }} - state: {{ item["state"] | d("present") }}'
  294 | 
  295 |   tags:
  296 |     - 'podman_containers'
  297 |     - 'podman_containers:auto_update'
```
