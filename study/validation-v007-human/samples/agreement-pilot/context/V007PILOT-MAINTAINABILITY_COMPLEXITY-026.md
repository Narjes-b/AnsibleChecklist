# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-026

- Repository: `scruffaluff/bootware`
- Commit: `f3940d2d3afeead1262403c6087fe598db0d883b`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-playbook`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `ansible_collections/scruffaluff/bootware/roles/lsd/tasks/main.yaml` (reported anchor line 1)
- Object: `source_location` `b385d177b1a35863c60e29feb34512cc56e467455d30af6363ca9a43d356ba6b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–182 of 182:

```text
    1 | ---
    2 | - name: Get latest Lsd version for Unix
    3 |   ansible.builtin.uri:
    4 |     method: GET
    5 |     return_content: true
    6 |     url: https://formulae.brew.sh/api/formula/lsd.json
    7 |   register: lsd_formula
    8 |   tags:
    9 |     - install
   10 |   when: ansible_facts.system != "Win32NT"
   11 | 
   12 | - name: Install Lsd for FreeBSD
   13 |   become: true
   14 |   community.general.pkgng:
   15 |     name: lsd
   16 |   tags:
   17 |     - install
   18 |   when: ansible_facts.system == "FreeBSD"
   19 | 
   20 | - name: Create Lsd temporary directory for Unix
   21 |   ansible.builtin.tempfile:
   22 |     state: directory
   23 |   register: lsd_temp
   24 |   tags:
   25 |     - install
   26 |   when: ansible_facts.system != "Win32NT"
   27 | 
   28 | - name: Download Lsd for Unix
   29 |   ansible.builtin.unarchive:
   30 |     dest: "{{ lsd_temp.path }}"
   31 |     mode: "777"
   32 |     remote_src: true
   33 |     src: >-
   34 |       https://github.com/lsd-rs/lsd/releases/download/v{{
   35 |       lsd_formula.json.versions.stable }}/lsd-v{{
   36 |       lsd_formula.json.versions.stable }}-{{ lsd_arch }}-unknown-linux-{{
   37 |       lsd_libc }}.tar.gz
   38 |   tags:
   39 |     - install
   40 |   when: ansible_facts.system != "Win32NT"
   41 | 
   42 | - name: Install Lsd for Linux
   43 |   ansible.builtin.copy:
   44 |     dest: /usr/local/bin/lsd
   45 |     force: true
   46 |     mode: "755"
   47 |     remote_src: true
   48 |     src: >-
   49 |       {{ lsd_temp.path }}/lsd-v{{ lsd_formula.json.versions.stable }}-{{
   50 |       lsd_arch }}-unknown-linux-{{ lsd_libc }}/lsd
   51 |   become: true
   52 |   tags:
   53 |     - install
   54 |   when: ansible_facts.system == "Linux"
   55 | 
   56 | - name: Install Lsd for MacOS
   57 |   become: true
   58 |   become_user: "{{ brew_user }}"
   59 |   community.general.homebrew:
   60 |     name: lsd
   61 |   tags:
   62 |     - install
   63 |   when: ansible_facts.system == "Darwin"
   64 | 
   65 | - name: Install Lsd for Windows
   66 |   community.windows.win_scoop:
   67 |     global: true
   68 |     name: lsd
   69 |   tags:
   70 |     - install
   71 |   when: ansible_facts.system == "Win32NT"
   72 | 
   73 | - name: Install Lsd shell completions for Unix
   74 |   ansible.builtin.copy:
   75 |     dest: "{{ item.dest }}"
   76 |     force: true
   77 |     mode: "644"
   78 |     remote_src: true
   79 |     src: >-
   80 |       {{ lsd_temp.path }}/lsd-v{{ lsd_formula.json.versions.stable }}-{{
   81 |       lsd_arch }}-unknown-linux-{{ lsd_libc }}/autocomplete/lsd.{{
   82 |       item.extension }}
   83 |   become: true
   84 |   loop:
   85 |     - dest: "{{ bash_completion }}/lsd"
   86 |       extension: bash-completion
   87 |     - dest: "{{ fish_completion }}/lsd.fish"
   88 |       extension: fish
   89 |   tags:
   90 |     - completion
   91 |     - install
   92 |   when: ansible_facts.system != "Win32NT"
   93 | 
   94 | - name: Copy Ls colors file for Unix
   95 |   ansible.builtin.copy:
   96 |     dest: "{{ user_home }}/.ls_colors"
   97 |     force: true
   98 |     group: "{{ group_id }}"
   99 |     mode: "640"
  100 |     owner: "{{ user_id }}"
  101 |     src: ls_colors
  102 |   become: true
  103 |   tags:
  104 |     - config
  105 |   when: ansible_facts.system != "Win32NT"
  106 | 
  107 | - name: Copy Ls colors file for Windows
  108 |   ansible.windows.win_copy:
  109 |     dest: "{{ user_home }}\\.ls_colors"
  110 |     force: true
  111 |     src: ls_colors
  112 |   tags:
  113 |     - config
  114 |   when: ansible_facts.system == "Win32NT"
  115 | 
  116 | - name: Create Lsd configuration directory for Unix
  117 |   ansible.builtin.file:
  118 |     group: "{{ group_id }}"
  119 |     mode: "755"
  120 |     owner: "{{ user_id }}"
  121 |     path: "{{ user_home }}/.config/lsd"
  122 |     state: directory
  123 |   become: true
  124 |   tags:
  125 |     - config
  126 |   when: ansible_facts.system != "Win32NT"
  127 | 
  128 | - name: Copy Lsd configuration files for Unix
  129 |   ansible.builtin.copy:
  130 |     dest: "{{ user_home }}/.config/lsd/{{ item }}"
  131 |     force: true
  132 |     group: "{{ group_id }}"
  133 |     mode: "644"
  134 |     owner: "{{ user_id }}"
  135 |     src: "{{ item }}"
  136 |   become: true
  137 |   loop:
  138 |     - colors.yaml
  139 |     - config.yaml
  140 |   tags:
  141 |     - config
  142 |   when: ansible_facts.system != "Win32NT"
  143 | 
  144 | - name: Create Lsd configuration directory for Windows
  145 |   ansible.windows.win_file:
  146 |     path: "{{ user_home }}\\AppData\\Roaming\\lsd"
  147 |     state: directory
  148 |   tags:
  149 |     - config
  150 |   when: ansible_facts.system == "Win32NT"
  151 | 
  152 | - name: Copy Lsd configuration files for Windows
  153 |   ansible.windows.win_copy:
  154 |     dest: "{{ user_home }}\\AppData\\Roaming\\lsd\\{{ item }}"
  155 |     force: true
  156 |     src: "{{ item }}"
  157 |   loop:
  158 |     - colors.yaml
  159 |     - config.yaml
  160 |   tags:
  161 |     - config
  162 |   when: ansible_facts.system == "Win32NT"
  163 | 
  164 | - name: Set owner of Lsd files for Windows
  165 |   ansible.windows.win_owner:
  166 |     path: "{{ user_home }}\\{{ item }}"
  167 |     recurse: true
  168 |     user: "{{ user_id }}"
  169 |   loop:
  170 |     - .ls_colors
  171 |     - AppData\Roaming\lsd
  172 |   tags:
  173 |     - config
  174 |   when: ansible_facts.system == "Win32NT"
  175 | 
  176 | - name: Remove Lsd temporary directory for Unix
  177 |   ansible.builtin.file:
  178 |     path: "{{ lsd_temp.path }}"
  179 |     state: absent
  180 |   tags:
  181 |     - install
  182 |   when: ansible_facts.system != "Win32NT"
```
