# Frozen source context: V007PILOT2-SECURITY-011

- Repository: `scruffaluff/bootware`
- Commit: `f3940d2d3afeead1262403c6087fe598db0d883b`
- Family: security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `ansible_collections/scruffaluff/bootware/roles/font/tasks/unix.yaml` (reported anchor line 31)
- Flagged construct: not named by the finding; the anchor line 31 lies in the task at line 31, name `Set font temporary directory permissions for Unix`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–97 of 97:

```text
    1 | ---
    2 | - name: Install font config for FreeBSD
    3 |   become: true
    4 |   community.general.pkgng:
    5 |     name: fontconfig
    6 |   tags:
    7 |     - install
    8 |   when: ansible_facts.system == "FreeBSD"
    9 | 
   10 | - name: Install font config for Linux
   11 |   ansible.builtin.package:
   12 |     name: fontconfig
   13 |   become: true
   14 |   tags:
   15 |     - install
   16 |   when: ansible_facts.system == "Linux"
   17 | 
   18 | - name: Check if font is installed for Unix
   19 |   ansible.builtin.stat:
   20 |     path: "{{ font_folder[ansible_facts.system] }}/{{ font_family.check }}"
   21 |   register: font_check_unix
   22 | 
   23 | - name: Create font temporary directory for Unix
   24 |   ansible.builtin.tempfile:
   25 |     state: directory
   26 |   register: font_temp
   27 |   tags:
   28 |     - install
   29 |   when: not font_check_unix.stat.exists
   30 | 
   31 | - name: Set font temporary directory permissions for Unix
   32 |   ansible.builtin.file:
   33 |     mode: "777"
   34 |     path: "{{ font_temp.path }}"
   35 |     state: directory
   36 |   tags:
   37 |     - install
   38 |   when: not font_check_unix.stat.exists
   39 | 
   40 | - name: Install fonts for Unix
   41 |   tags:
   42 |     - install
   43 |   when: not font_check_unix.stat.exists
   44 |   block:
   45 |     - name: Create temporary font directory for Unix
   46 |       ansible.builtin.file:
   47 |         mode: "777"
   48 |         path: "{{ font_temp.path }}/{{ font_family.name }}"
   49 |         state: directory
   50 | 
   51 |     - name: Download fonts for Unix
   52 |       ansible.builtin.unarchive:
   53 |         dest: "{{ font_temp.path }}/{{ font_family.name }}"
   54 |         mode: "777"
   55 |         remote_src: true
   56 |         src: "{{ font_family.url }}"
   57 | 
   58 |     - name: Find font files for Unix
   59 |       ansible.builtin.find:
   60 |         paths: "{{ font_temp.path }}/{{ font_family.name }}"
   61 |         patterns: "{{ font_family.patterns }}"
   62 |         recurse: true
   63 |       register: font_paths
   64 | 
   65 |     - name: Create font directory for Unix
   66 |       ansible.builtin.file:
   67 |         mode: "755"
   68 |         path: "{{ font_folder[ansible_facts.system] }}"
   69 |         state: directory
   70 |       become: true
   71 | 
   72 |     - name: Install font files for Unix
   73 |       ansible.builtin.copy:
   74 |         dest: "{{ font_folder[ansible_facts.system] }}"
   75 |         mode: "644"
   76 |         remote_src: true
   77 |         src: "{{ item.path }}"
   78 |       become: true
   79 |       loop: "{{ font_paths.files }}"
   80 | 
   81 | - name: Update font cache for Unix
   82 |   ansible.builtin.command:
   83 |     cmd: fc-cache --verbose
   84 |   become: true
   85 |   changed_when: "'new cache contents' in font_cache_unix.stdout"
   86 |   register: font_cache_unix
   87 |   tags:
   88 |     - install
   89 |   when: ansible_facts.system in ["FreeBSD", "Linux"]
   90 | 
   91 | - name: Remove font temporary directory for Unix
   92 |   ansible.builtin.file:
   93 |     path: "{{ font_temp.path }}"
   94 |     state: absent
   95 |   tags:
   96 |     - install
   97 |   when: not font_check_unix.stat.exists
```
