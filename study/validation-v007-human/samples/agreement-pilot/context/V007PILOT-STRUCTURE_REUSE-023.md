# Frozen source context: V007PILOT-STRUCTURE_REUSE-023

- Repository: `manala/ansible-roles`
- Commit: `1ae6394d7b780665788234418ace2a060903f5f1`
- Family: Structure/reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/gomplate/tasks/install.yaml` (reported anchor line 1)
- Object: `source_location` `6b007409302ccd171e332fd6cad2c92eb1979002ada0918b2344388d8e7f42e6`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–41 of 41:

```text
    1 | ---
    2 | 
    3 | - name: Install > Stat bin
    4 |   ansible.builtin.stat:
    5 |     path: "{{ manala_gomplate_bin }}"
    6 |   register: __manala_gomplate_bin_stat_result
    7 | 
    8 | - name: Install > Get latest version
    9 |   ansible.builtin.uri:
   10 |     url: https://api.github.com/repos/hairyhenderson/gomplate/releases/latest
   11 |   check_mode: false
   12 |   register: __manala_gomplate_version_latest
   13 |   when:
   14 |     - not __manala_gomplate_bin_stat_result.stat.exists
   15 |     - manala_gomplate_version is none
   16 | 
   17 | - name: Install > Install
   18 |   when: not __manala_gomplate_bin_stat_result.stat.exists
   19 |   vars:
   20 |     __manala_gomplate_version: |-
   21 |       {{
   22 |         manala_gomplate_version
   23 |           if (manala_gomplate_version) else
   24 |         __manala_gomplate_version_latest.json.tag_name | regex_replace('v(.+)$', '\1')
   25 |       }}
   26 |     __manala_gomplate_url: |-
   27 |       {{
   28 |         'https://github.com/hairyhenderson/gomplate/releases/download/v%(version)s/gomplate_linux-%(architecture)s' | format(
   29 |           version=__manala_gomplate_version,
   30 |           architecture=ansible_facts.architecture | manala.roles.gomplate_architecture,
   31 |         )
   32 |       }}
   33 |   block:
   34 | 
   35 |     - name: Install > Download binary
   36 |       ansible.builtin.get_url:
   37 |         url: "{{ __manala_gomplate_url }}"
   38 |         dest: "{{ manala_gomplate_bin }}"
   39 |         owner: root
   40 |         group: root
   41 |         mode: "0755"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/gomplate/README.md
roles/gomplate/defaults/main.yaml
roles/gomplate/meta/main.yaml
roles/gomplate/tasks/install.yaml
roles/gomplate/tasks/main.yaml
```
