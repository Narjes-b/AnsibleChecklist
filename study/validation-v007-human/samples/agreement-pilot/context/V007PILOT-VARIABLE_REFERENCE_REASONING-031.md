# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-031

- Repository: `scruffaluff/bootware`
- Commit: `f3940d2d3afeead1262403c6087fe598db0d883b`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `ansible_collections/scruffaluff/bootware/roles/bat/tasks/main.yaml` (reported anchor line 178)
- Object: `variable` `07d09d62528e89a60ecd2b130d1fcfb835b1f35a6b5d13c07b71f8c5770057a4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–267 of 267:

```text
    1 | ---
    2 | - name: Check if Less is installed for Linux
    3 |   ansible.builtin.shell:
    4 |     cmd: command -v less
    5 |     executable: "{{ bash_executable }}"
    6 |   become: true
    7 |   changed_when: false
    8 |   ignore_errors: true
    9 |   register: bat_less_linux
   10 |   tags:
   11 |     - install
   12 |   when: ansible_facts.system == "Linux"
   13 | 
   14 | - name: Install Less for Linux
   15 |   ansible.builtin.package:
   16 |     name: less
   17 |   become: true
   18 |   tags:
   19 |     - install
   20 |   when: ansible_facts.system == "Linux" and bat_less_linux is failed
   21 | 
   22 | - name: Install Bat for FreeBSD
   23 |   become: true
   24 |   community.general.pkgng:
   25 |     name:
   26 |       - bat
   27 |       - less
   28 |   tags:
   29 |     - install
   30 |   when: ansible_facts.system == "FreeBSD"
   31 | 
   32 | - name: Install Bat for Linux
   33 |   ansible.builtin.package:
   34 |     name: bat
   35 |   become: true
   36 |   ignore_errors: true
   37 |   register: bat_linux
   38 |   tags:
   39 |     - install
   40 |   when: ansible_facts.system == "Linux"
   41 | 
   42 | - name: Get latest Bat version for Linux
   43 |   ansible.builtin.uri:
   44 |     method: GET
   45 |     return_content: true
   46 |     url: https://formulae.brew.sh/api/formula/bat.json
   47 |   register: bat_formula
   48 |   tags:
   49 |     - install
   50 |   when: >-
   51 |     ansible_facts.system == "Linux" and (system_libc == "gnu" or
   52 |     system_architecture == 'amd64') and bat_linux is failed
   53 | 
   54 | - name: Create Bat temporary directory for Linux
   55 |   ansible.builtin.tempfile:
   56 |     state: directory
   57 |   register: bat_temp
   58 |   tags:
   59 |     - install
   60 |   when: >-
   61 |     ansible_facts.system == "Linux" and (system_libc == "gnu" or
   62 |     system_architecture == 'amd64') and bat_linux is failed
   63 | 
   64 | - name: Download Bat for Linux
   65 |   ansible.builtin.unarchive:
   66 |     dest: "{{ bat_temp.path }}"
   67 |     mode: "777"
   68 |     remote_src: true
   69 |     src: >-
   70 |       https://github.com/sharkdp/bat/releases/download/v{{
   71 |       bat_formula.json.versions.stable }}/bat-v{{
   72 |       bat_formula.json.versions.stable }}-{{ bat_arch }}-unknown-linux-{{
   73 |       system_libc }}.tar.gz
   74 |   tags:
   75 |     - install
   76 |   when: >-
   77 |     ansible_facts.system == "Linux" and (system_libc == "gnu" or
   78 |     system_architecture == 'amd64') and bat_linux is failed
   79 | 
   80 | - name: Install Bat for Linux
   81 |   ansible.builtin.copy:
   82 |     dest: /usr/local/bin/bat
   83 |     force: true
   84 |     mode: "755"
   85 |     remote_src: true
   86 |     src: >-
   87 |       {{ bat_temp.path }}/bat-v{{ bat_formula.json.versions.stable }}-{{
   88 |       bat_arch }}-unknown-linux-{{ system_libc }}/bat
   89 |   become: true
   90 |   tags:
   91 |     - install
   92 |   when: >-
   93 |     ansible_facts.system == "Linux" and (system_libc == "gnu" or
   94 |     system_architecture == 'amd64') and bat_linux is failed
   95 | 
   96 | - name: Install Bat shell completions for Linux
   97 |   ansible.builtin.copy:
   98 |     dest: "{{ item.dest }}"
   99 |     force: true
  100 |     mode: "644"
  101 |     remote_src: true
  102 |     src: >-
  103 |       {{ bat_temp.path }}/bat-v{{ bat_formula.json.versions.stable }}-{{
  104 |       bat_arch }}-unknown-linux-{{ system_libc }}/autocomplete/bat.{{ item.shell
  105 |       }}
  106 |   become: true
  107 |   loop:
  108 |     - dest: "{{ bash_completion }}/bat"
  109 |       shell: bash
  110 |     - dest: "{{ fish_completion }}/bat.fish"
  111 |       shell: fish
  112 |   tags:
  113 |     - completion
  114 |     - install
  115 |   when: >-
  116 |     ansible_facts.system == "Linux" and (system_libc == "gnu" or
  117 |     system_architecture == 'amd64') and bat_linux is failed
  118 | 
  119 | # Debian Bat package installs Bat as command "batcat" since another package
  120 | # installs the command "bat".
  121 | - name: Make Bat symlink for Debian
  122 |   ansible.builtin.file:
  123 |     src: /usr/bin/batcat
  124 |     dest: /usr/local/bin/bat
  125 |     force: true
  126 |     mode: "755"
  127 |     state: link
  128 |   become: true
  129 |   tags:
  130 |     - install
  131 |   when: system_pkg_mgr == "apt"
  132 | 
  133 | # Bat uses Less configuration for keybindings. MacOS default version of Less is
  134 | # too old to support keybindings.
  135 | - name: Install Bat for MacOS
  136 |   become: true
  137 |   become_user: "{{ brew_user }}"
  138 |   community.general.homebrew:
  139 |     name:
  140 |       - bat
  141 |       - less
  142 |   tags:
  143 |     - install
  144 |   when: ansible_facts.system == "Darwin"
  145 | 
  146 | - name: Install Bat for Windows
  147 |   community.windows.win_scoop:
  148 |     global: true
  149 |     name:
  150 |       - bat
  151 |       - less
  152 |   tags:
  153 |     - install
  154 |   when: ansible_facts.system == "Win32NT"
  155 | 
  156 | # VSCode remote terminals for MacOS automatically prepend folders to the system
  157 | # path, which makes the /usr/bin/less appear before the /opt/homebrew/bin/less.
  158 | # Luckily /usr/local/bin still appears before /usr/bin.
  159 | - name: Make less symlink for MacOS
  160 |   ansible.builtin.file:
  161 |     src: /opt/homebrew/bin/less
  162 |     dest: /usr/local/bin/less
  163 |     force: true
  164 |     mode: "755"
  165 |     state: link
  166 |   become: true
  167 |   tags:
  168 |     - install
  169 |   when: >-
  170 |     ansible_facts.system == "Darwin" and ansible_facts.architecture == "arm64"
  171 | 
  172 | - name: Copy Less settings file for Unix
  173 |   ansible.builtin.copy:
  174 |     dest: "{{ user_home }}/.lesskey"
  175 |     force: true
  176 |     group: "{{ group_id }}"
  177 |     mode: "640"
  178 |     owner: "{{ user_id }}"
  179 |     src: lesskey
  180 |   become: true
  181 |   tags:
  182 |     - config
  183 |   when: ansible_facts.system != "Win32NT"
  184 | 
  185 | # On Windows Less configuration files start with "_" instead of ".". For more
  186 | # information, visit https://linux.die.net/man/1/less.
  187 | - name: Copy Less settings file for Windows
  188 |   ansible.windows.win_copy:
  189 |     dest: "{{ user_home }}\\_lesskey"
  190 |     force: true
  191 |     src: lesskey
  192 |   tags:
  193 |     - config
  194 |   when: ansible_facts.system == "Win32NT"
  195 | 
  196 | - name: Create Bat settings directory for Unix
  197 |   ansible.builtin.file:
  198 |     dest: "{{ user_home }}/.config/bat"
  199 |     group: "{{ group_id }}"
  200 |     mode: "755"
  201 |     owner: "{{ user_id }}"
  202 |     state: directory
  203 |   become: true
  204 |   tags:
  205 |     - config
  206 |   when: ansible_facts.system != "Win32NT"
  207 | 
  208 | - name: Copy Bat settings file for Unix
  209 |   ansible.builtin.copy:
  210 |     dest: "{{ user_home }}/.config/bat/config"
  211 |     force: true
  212 |     group: "{{ group_id }}"
  213 |     mode: "644"
  214 |     owner: "{{ user_id }}"
  215 |     src: config
  216 |   become: true
  217 |   tags:
  218 |     - config
  219 |   when: ansible_facts.system != "Win32NT"
  220 | 
  221 | - name: Create Bat settings directory for Windows
  222 |   ansible.windows.win_file:
  223 |     path: "{{ user_home }}\\AppData\\Roaming\\bat"
  224 |     state: directory
  225 |   tags:
  226 |     - config
  227 |   when: ansible_facts.system == "Win32NT"
  228 | 
  229 | - name: Copy Bat settings file for Windows
  230 |   ansible.windows.win_copy:
  231 |     dest: "{{ user_home }}\\AppData\\Roaming\\bat\\config"
  232 |     force: true
  233 |     src: config
  234 |   tags:
  235 |     - config
  236 |   when: ansible_facts.system == "Win32NT"
  237 | 
  238 | - name: Override Scoop custom Bat configuration path for Windows
  239 |   ansible.windows.win_environment:
  240 |     level: user
  241 |     name: BAT_CONFIG_PATH
  242 |     value: "{{ user_home }}\\AppData\\Roaming\\bat\\config"
  243 |   tags:
  244 |     - config
  245 |   when: ansible_facts.system == "Win32NT"
  246 | 
  247 | - name: Set owner of Bat files for Windows
  248 |   ansible.windows.win_owner:
  249 |     path: "{{ user_home }}\\{{ item }}"
  250 |     recurse: true
  251 |     user: "{{ user_id }}"
  252 |   loop:
  253 |     - _lesskey
  254 |     - AppData\Roaming\bat
  255 |   tags:
  256 |     - config
  257 |   when: ansible_facts.system == "Win32NT"
  258 | 
  259 | - name: Remove Bat temporary directory for Linux
  260 |   ansible.builtin.file:
  261 |     path: "{{ bat_temp.path }}"
  262 |     state: absent
  263 |   tags:
  264 |     - install
  265 |   when: >-
  266 |     ansible_facts.system == "Linux" and (system_libc == "gnu" or
  267 |     system_architecture == 'amd64') and bat_linux is failed
```

## Visible variable references

```text
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/alacritty/tasks/main.yaml:30:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/alacritty/tasks/main.yaml:52:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/alacritty/tasks/main.yaml:72:    user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bash/tasks/main.yaml:74:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bash/tasks/main.yaml:88:    cmd: chsh -s {{ bash_executable }} {{ user_id }}
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bash/tasks/main.yaml:98:    name: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bat/tasks/main.yaml:178:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bat/tasks/main.yaml:201:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bat/tasks/main.yaml:214:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bat/tasks/main.yaml:251:    user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bottom/tasks/main.yaml:98:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bottom/tasks/main.yaml:111:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/bottom/tasks/main.yaml:139:    user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/caffeine/tasks/main.yaml:8:      become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/caffeine/tasks/main.yaml:56:      become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/caffeine/tasks/main.yaml:87:  become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/chrome/tasks/main.yaml:79:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/chrome/tasks/main.yaml:117:  become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/desktop_environment/tasks/gnome_extension.yaml:7:      become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/desktop_environment/tasks/gnome_extension.yaml:57:      become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/desktop_environment/tasks/main.yaml:52:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/desktop_environment/tasks/main.yaml:69:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/desktop_environment/tasks/main.yaml:89:  become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/desktop_environment/tasks/main.yaml:99:  become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/desktop_environment/tasks/main.yaml:134:    user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/docker/tasks/main.yaml:211:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/docker/tasks/main.yaml:236:    name: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/docker/tasks/main.yaml:247:    name: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/essential/tasks/main.yaml:209:#     user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/firefox/tasks/main.yaml:51:  become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/firefox/tasks/main.yaml:53:    user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/firefox/tasks/main.yaml:57:  when: ansible_facts.system != "Win32NT" and user_id != "root"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/firefox/tasks/main.yaml:61:    user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/firefox/tasks/main.yaml:71:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/firefox/tasks/main.yaml:78:  when: ansible_facts.system != "Win32NT" and user_id != "root"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/firefox/tasks/main.yaml:95:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/firefox/tasks/main.yaml:101:  when: ansible_facts.system != "Win32NT" and user_id != "root"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/fish/tasks/main.yaml:50:  become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/fish/tasks/main.yaml:64:  become_user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/fish/tasks/main.yaml:76:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/fish/tasks/main.yaml:93:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/fish/tasks/main.yaml:115:    cmd: chsh -s {{ fish_executable }} {{ user_id }}
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/fish/tasks/main.yaml:125:    name: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/gdb/tasks/main.yaml:30:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/gdb/tasks/main.yaml:52:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/gdb/tasks/main.yaml:82:    user: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/git/tasks/main.yaml:125:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/gitui/tasks/main.yaml:97:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/gitui/tasks/main.yaml:111:    owner: "{{ user_id }}"
f3940d2d3afeead1262403c6087fe598db0d883b:ansible_collections/scruffaluff/bootware/roles/gitui/tasks/main.yaml:139:    user: "{{ user_id }}"
[reference search truncated after 50 matches]
```
