# Frozen source context: V007PILOT-SECURITY-004

- Repository: `scruffaluff/bootware`
- Commit: `f3940d2d3afeead1262403c6087fe598db0d883b`
- Family: Security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `ansible_collections/scruffaluff/bootware/roles/typst/tasks/main.yaml` (reported anchor line 99)
- Object: `source_location` `ebdcd04de5ffcaa440940c8f6f1603afa9d3099d18407e102b8ed3079ac2ca29`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–155 of 155:

```text
    1 | ---
    2 | - name: Install Typst for FreeBSD
    3 |   become: true
    4 |   community.general.pkgng:
    5 |     name:
    6 |       - typst
    7 |       - typstyle
    8 |   tags:
    9 |     - install
   10 |   when: ansible_facts.system == "FreeBSD"
   11 | 
   12 | - name: Get latest Typst version for Linux
   13 |   ansible.builtin.uri:
   14 |     method: GET
   15 |     return_content: true
   16 |     url: https://formulae.brew.sh/api/formula/typst.json
   17 |   register: typst_formula
   18 |   tags:
   19 |     - install
   20 |   when: ansible_facts.system == "Linux"
   21 | 
   22 | - name: Get latest Typstyle version for Linux
   23 |   ansible.builtin.uri:
   24 |     method: GET
   25 |     return_content: true
   26 |     url: https://formulae.brew.sh/api/formula/typstyle.json
   27 |   register: typstyle_formula
   28 |   tags:
   29 |     - install
   30 |   when: ansible_facts.system == "Linux"
   31 | 
   32 | - name: Get latest Tinymist version for Linux
   33 |   ansible.builtin.uri:
   34 |     method: GET
   35 |     return_content: true
   36 |     url: https://formulae.brew.sh/api/formula/tinymist.json
   37 |   register: tinymist_formula
   38 |   tags:
   39 |     - install
   40 |   when: ansible_facts.system == "Linux"
   41 | 
   42 | - name: Create Typst temporary directory for Linux
   43 |   ansible.builtin.tempfile:
   44 |     state: directory
   45 |   register: typst_temp
   46 |   tags:
   47 |     - install
   48 |   when: ansible_facts.system == "Linux"
   49 | 
   50 | - name: Set Typst temporary directory permissions for Linux
   51 |   ansible.builtin.file:
   52 |     mode: "755"
   53 |     path: "{{ typst_temp.path }}"
   54 |     state: directory
   55 |   tags:
   56 |     - install
   57 |   when: ansible_facts.system == "Linux"
   58 | 
   59 | - name: Download Typst for Linux
   60 |   ansible.builtin.unarchive:
   61 |     dest: "{{ typst_temp.path }}"
   62 |     mode: "777"
   63 |     remote_src: true
   64 |     src: >-
   65 |       https://github.com/typst/typst/releases/download/v{{
   66 |       typst_formula.json.versions.stable }}/typst-{{ typst_arch
   67 |       }}-unknown-linux-musl.tar.xz
   68 |   tags:
   69 |     - install
   70 |   when: ansible_facts.system == "Linux"
   71 | 
   72 | - name: Install Typst for Linux
   73 |   ansible.builtin.copy:
   74 |     dest: /usr/local/bin/typst
   75 |     force: true
   76 |     mode: "755"
   77 |     remote_src: true
   78 |     src: >-
   79 |       {{ typst_temp.path }}/typst-{{ typst_arch }}-unknown-linux-musl/typst
   80 |   become: true
   81 |   tags:
   82 |     - install
   83 |   when: ansible_facts.system == "Linux"
   84 | 
   85 | - name: Install Typstyle for Linux
   86 |   ansible.builtin.get_url:
   87 |     dest: /usr/local/bin/typstyle
   88 |     force: true
   89 |     mode: "755"
   90 |     url: >-
   91 |       https://github.com/typstyle-rs/typstyle/releases/download/v{{
   92 |       typstyle_formula.json.versions.stable }}/typstyle-{{ typst_arch
   93 |       }}-unknown-linux-{{ system_libc }}
   94 |   become: true
   95 |   tags:
   96 |     - install
   97 |   when: ansible_facts.system == "Linux"
   98 | 
   99 | - name: Download Tinymist for Linux
  100 |   ansible.builtin.unarchive:
  101 |     dest: "{{ typst_temp.path }}"
  102 |     mode: "777"
  103 |     remote_src: true
  104 |     src: >-
  105 |       https://github.com/Myriad-Dreamin/tinymist/releases/download/v{{
  106 |       tinymist_formula.json.versions.stable }}/tinymist-{{ typst_arch
  107 |       }}-unknown-linux-{{ system_libc }}.tar.gz
  108 |   tags:
  109 |     - install
  110 |   when: ansible_facts.system == "Linux"
  111 | 
  112 | - name: Install Tinymist for Linux
  113 |   ansible.builtin.copy:
  114 |     dest: /usr/local/bin/tinymist
  115 |     force: true
  116 |     mode: "755"
  117 |     remote_src: true
  118 |     src: >-
  119 |       {{ typst_temp.path }}/tinymist-{{ typst_arch }}-unknown-linux-{{
  120 |       system_libc }}/tinymist
  121 |   become: true
  122 |   tags:
  123 |     - install
  124 |   when: ansible_facts.system == "Linux"
  125 | 
  126 | - name: Install Typst for MacOS
  127 |   become: true
  128 |   become_user: "{{ brew_user }}"
  129 |   community.general.homebrew:
  130 |     name:
  131 |       - tinymist
  132 |       - typst
  133 |       - typstyle
  134 |   tags:
  135 |     - install
  136 |   when: ansible_facts.system == "Darwin"
  137 | 
  138 | - name: Install Typst for Windows
  139 |   community.windows.win_scoop:
  140 |     global: true
  141 |     name:
  142 |       - tinymist
  143 |       - typst
  144 |       - typstyle
  145 |   tags:
  146 |     - install
  147 |   when: ansible_facts.system == "Win32NT"
  148 | 
  149 | - name: Remove Typst temporary directory for Linux
  150 |   ansible.builtin.file:
  151 |     path: "{{ typst_temp.path }}"
  152 |     state: absent
  153 |   tags:
  154 |     - install
  155 |   when: ansible_facts.system == "Linux"
```
