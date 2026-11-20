# Frozen source context: V007PILOT-STYLE_POLICY-017

- Repository: `scruffaluff/bootware`
- Commit: `f3940d2d3afeead1262403c6087fe598db0d883b`
- Family: Style/policy
- Rule: `ansibleguard/missing-file-extension`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `ansible_collections/scruffaluff/bootware/roles/handy/tasks/config.yaml` (reported anchor line 1)
- Object: `source_location` `e36aa95bd5e2dcc6d938fb4a7155559e0e381e61acd18c697334842364babfe6`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–96 of 96:

```text
    1 | ---
    2 | - name: Check if Handy settings file exists for Unix
    3 |   ansible.builtin.stat:
    4 |     path: "{{ handy_settings_path }}"
    5 |   register: handy_settings_check_unix
    6 |   tags:
    7 |     - config
    8 |   when: ansible_facts.system != "Win32NT"
    9 | 
   10 | - name: Check if Handy settings file exists for Windows
   11 |   ansible.windows.win_stat:
   12 |     path: "{{ handy_settings_path }}"
   13 |   register: handy_settings_check_windows
   14 |   tags:
   15 |     - config
   16 |   when: ansible_facts.system == "Win32NT"
   17 | 
   18 | - name: Set Handy settings check
   19 |   ansible.builtin.set_fact:
   20 |     handy_settings_check: >-
   21 |       {{ handy_settings_check_unix if not 'skipped' in handy_settings_check_unix
   22 |       else handy_settings_check_windows }}
   23 |   tags:
   24 |     - config
   25 | 
   26 | - name: Read contents of current Handy settings file
   27 |   ansible.builtin.slurp:
   28 |     src: "{{ handy_settings_path }}"
   29 |   register: handy_settings_file
   30 |   tags:
   31 |     - config
   32 |   when: handy_settings_check.stat.exists
   33 | 
   34 | - name: Parse current Handy settings
   35 |   ansible.builtin.set_fact:
   36 |     handy_settings_dest: >-
   37 |       {{ {} if 'skipped' in handy_settings_file else
   38 |       handy_settings_file['content'] | b64decode | from_json }}
   39 |   tags:
   40 |     - config
   41 | 
   42 | - name: Load Handy settings overrides
   43 |   ansible.builtin.include_vars:
   44 |     file: settings.json
   45 |     name: handy_settings_src
   46 |   tags:
   47 |     - config
   48 | 
   49 | - name: Set Handy settings
   50 |   ansible.builtin.set_fact:
   51 |     handy_settings: >-
   52 |       {{ handy_settings_dest | combine(handy_settings_src, recursive=True) }}
   53 |   tags:
   54 |     - config
   55 | 
   56 | - name: Create Handy settings directory for Unix
   57 |   ansible.builtin.file:
   58 |     group: "{{ group_id }}"
   59 |     mode: "755"
   60 |     owner: "{{ user_id }}"
   61 |     path: "{{ handy_settings_path | dirname }}"
   62 |     state: directory
   63 |   become: true
   64 |   tags:
   65 |     - config
   66 |   when: ansible_facts.system != "Win32NT"
   67 | 
   68 | - name: Copy Handy settings for Unix
   69 |   ansible.builtin.copy:
   70 |     content: "{{ handy_settings | to_nice_json(indent=2) }}"
   71 |     dest: "{{ handy_settings_path }}"
   72 |     force: true
   73 |     group: "{{ group_id }}"
   74 |     mode: "644"
   75 |     owner: "{{ user_id }}"
   76 |   become: true
   77 |   tags:
   78 |     - config
   79 |   when: ansible_facts.system != "Win32NT"
   80 | 
   81 | - name: Create Handy settings directory for Windows
   82 |   ansible.windows.win_file:
   83 |     path: "{{ handy_settings_path | dirname }}"
   84 |     state: directory
   85 |   tags:
   86 |     - config
   87 |   when: ansible_facts.system == "Win32NT"
   88 | 
   89 | - name: Copy Handy settings for Windows
   90 |   ansible.windows.win_copy:
   91 |     content: "{{ handy_settings | to_nice_json(indent=2) }}"
   92 |     dest: "{{ handy_settings_path }}"
   93 |     force: true
   94 |   tags:
   95 |     - config
   96 |   when: ansible_facts.system == "Win32NT"
```
