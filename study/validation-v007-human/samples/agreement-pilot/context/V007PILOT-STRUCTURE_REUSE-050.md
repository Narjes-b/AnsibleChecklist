# Frozen source context: V007PILOT-STRUCTURE_REUSE-050

- Repository: `scruffaluff/bootware`
- Commit: `f3940d2d3afeead1262403c6087fe598db0d883b`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible_collections/scruffaluff/bootware/roles/just/tasks/main.yaml` (reported anchor line 1)
- Object: `source_location` `255a57a6c22b72915428e38a4f08ac6d045e1ed591a1e379b251c6f8f56eb281`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–132 of 132:

```text
    1 | ---
    2 | - name: Create Just temporary directory for Unix
    3 |   ansible.builtin.tempfile:
    4 |     state: directory
    5 |   register: just_temp
    6 |   tags:
    7 |     - install
    8 |   when: ansible_facts.system != "Win32NT"
    9 | 
   10 | - name: Install Just for Alpine
   11 |   become: true
   12 |   community.general.apk:
   13 |     name: just
   14 |     repository: http://dl-cdn.alpinelinux.org/alpine/edge/community
   15 |     state: latest
   16 |     update_cache: true
   17 |   tags:
   18 |     - install
   19 |   when: system_pkg_mgr == "apk"
   20 | 
   21 | - name: Install Just for FreeBSD
   22 |   become: true
   23 |   community.general.pkgng:
   24 |     name: just
   25 |   tags:
   26 |     - install
   27 |   when: ansible_facts.system == "FreeBSD"
   28 | 
   29 | # TODO: Renable when Just package in most distributions reaches version 1.38.
   30 | # - name: Install Just for Linux
   31 | #   ansible.builtin.package:
   32 | #     name: just
   33 | #   become: true
   34 | #   ignore_errors: true
   35 | #   register: just_linux
   36 | #   tags:
   37 | #     - install
   38 | #   when: ansible_facts.system == "Linux" and system_pkg_mgr != "apk"
   39 | 
   40 | - name: Get latest Just version for Linux
   41 |   ansible.builtin.uri:
   42 |     method: GET
   43 |     return_content: true
   44 |     url: https://formulae.brew.sh/api/formula/just.json
   45 |   register: just_formula
   46 |   tags:
   47 |     - install
   48 |   when: ansible_facts.system == "Linux" and system_pkg_mgr != "apk"
   49 | 
   50 | - name: Download Just for Linux
   51 |   ansible.builtin.unarchive:
   52 |     dest: "{{ just_temp.path }}"
   53 |     mode: "777"
   54 |     remote_src: true
   55 |     src: >-
   56 |       https://github.com/casey/just/releases/download/{{
   57 |       just_formula.json.versions.stable }}/just-{{
   58 |       just_formula.json.versions.stable }}-{{ just_arch
   59 |       }}-unknown-linux-musl.tar.gz
   60 |   tags:
   61 |     - install
   62 |   when: ansible_facts.system == "Linux" and system_pkg_mgr != "apk"
   63 | 
   64 | - name: Install Just for Linux
   65 |   ansible.builtin.copy:
   66 |     dest: /usr/local/bin/just
   67 |     force: true
   68 |     mode: "755"
   69 |     remote_src: true
   70 |     src: "{{ just_temp.path }}/just"
   71 |   become: true
   72 |   tags:
   73 |     - install
   74 |   when: ansible_facts.system == "Linux" and system_pkg_mgr != "apk"
   75 | 
   76 | - name: Install Just for MacOS
   77 |   become: true
   78 |   become_user: "{{ brew_user }}"
   79 |   community.general.homebrew:
   80 |     name: just
   81 |   tags:
   82 |     - install
   83 |   when: ansible_facts.system == "Darwin"
   84 | 
   85 | - name: Install Just for Windows
   86 |   community.windows.win_scoop:
   87 |     global: true
   88 |     name: just
   89 |   tags:
   90 |     - install
   91 |   when: ansible_facts.system == "Win32NT"
   92 | 
   93 | - name: Create Just shell completions for Unix
   94 |   ansible.builtin.shell: >-
   95 |     just --completions {{ item }} > {{ just_temp.path }}/just.{{ item }}
   96 |   become: true
   97 |   changed_when: true
   98 |   environment:
   99 |     PATH: /opt/homebrew/bin:/usr/local/bin:{{ ansible_facts.env.PATH }}
  100 |   loop:
  101 |     - bash
  102 |     - fish
  103 |   tags:
  104 |     - completion
  105 |     - install
  106 |   when: ansible_facts.system != "Win32NT"
  107 | 
  108 | - name: Install Just shell completions for Unix
  109 |   ansible.builtin.copy:
  110 |     dest: "{{ item.dest }}"
  111 |     force: true
  112 |     mode: "644"
  113 |     remote_src: true
  114 |     src: "{{ just_temp.path }}/just.{{ item.shell }}"
  115 |   become: true
  116 |   loop:
  117 |     - dest: "{{ bash_completion }}/just"
  118 |       shell: bash
  119 |     - dest: "{{ fish_completion }}/just.fish"
  120 |       shell: fish
  121 |   tags:
  122 |     - completion
  123 |     - install
  124 |   when: ansible_facts.system != "Win32NT"
  125 | 
  126 | - name: Remove Just temporary directory for Unix
  127 |   ansible.builtin.file:
  128 |     path: "{{ just_temp.path }}"
  129 |     state: absent
  130 |   tags:
  131 |     - install
  132 |   when: ansible_facts.system != "Win32NT"
```

## Frozen tracked paths in the relevant role/scope

```text
ansible_collections/scruffaluff/bootware/roles/just/README.md
ansible_collections/scruffaluff/bootware/roles/just/defaults/main.yaml
ansible_collections/scruffaluff/bootware/roles/just/meta/main.yaml
ansible_collections/scruffaluff/bootware/roles/just/tasks/main.yaml
```
