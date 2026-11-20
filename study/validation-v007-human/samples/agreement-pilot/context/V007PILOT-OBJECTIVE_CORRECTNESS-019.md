# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-019

- Repository: `kubernetes-sigs/kubespray`
- Commit: `9ee6f9b27981b251d77302fd6cf631f330e0ec39`
- Family: Objective correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/bootstrap_os/tasks/openEuler.yml` (reported anchor line 57)
- Object: `source_location` `324650d30b6dbc0a3abacda8ed598028c98979aa8f6559320c61ef082ffb6d65`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–62 of 62:

```text
    1 | ---
    2 | - name: Import CentOS bootstrap for openEuler
    3 |   ansible.builtin.import_tasks: centos.yml
    4 | 
    5 | - name: Read openEuler release string
    6 |   ansible.builtin.command: cat /etc/openEuler-release
    7 |   register: _openeuler_release_raw
    8 |   changed_when: false
    9 |   check_mode: false
   10 |   become: true
   11 |   when: openeuler_metalink_enabled
   12 | 
   13 | # /etc/openEuler-release contains e.g. "openEuler release 24.03 (LTS)"
   14 | # The metalink server expects "24.03LTS" (no spaces/parens/dashes),
   15 | # but DNF's $releasever resolves to just "24.03", causing "invalid repo or arch".
   16 | - name: Set openEuler metalink releasever
   17 |   ansible.builtin.set_fact:
   18 |     _openeuler_releasever: >-
   19 |       {{ _openeuler_release_raw.stdout
   20 |          | regex_replace('.*release\s+', '')
   21 |          | regex_replace('[() -]', '') }}
   22 |   when: openeuler_metalink_enabled
   23 | 
   24 | - name: Get existing openEuler repo sections
   25 |   ansible.builtin.shell:
   26 |     cmd: "set -o pipefail && grep '^\\[' /etc/yum.repos.d/openEuler.repo | tr -d '[]'"
   27 |     executable: /bin/bash
   28 |   register: _openeuler_repo_sections
   29 |   changed_when: false
   30 |   failed_when: false
   31 |   check_mode: false
   32 |   become: true
   33 |   when: openeuler_metalink_enabled
   34 | 
   35 | - name: Enable metalink for openEuler repos
   36 |   community.general.ini_file:
   37 |     path: /etc/yum.repos.d/openEuler.repo
   38 |     section: "{{ item.key }}"
   39 |     option: metalink
   40 |     value: "{{ item.value }}"
   41 |     no_extra_spaces: true
   42 |     mode: "0644"
   43 |   loop: "{{ _openeuler_metalink_repos | dict2items | selectattr('key', 'in', _openeuler_repo_sections.stdout_lines | default([])) }}"
   44 |   become: true
   45 |   when: openeuler_metalink_enabled
   46 |   register: _openeuler_metalink_result
   47 |   vars:
   48 |     _openeuler_metalink_repos:
   49 |       OS: "https://mirrors.openeuler.org/metalink?repo={{ _openeuler_releasever }}/OS&arch=$basearch"
   50 |       everything: "https://mirrors.openeuler.org/metalink?repo={{ _openeuler_releasever }}/everything&arch=$basearch"
   51 |       EPOL: "https://mirrors.openeuler.org/metalink?repo={{ _openeuler_releasever }}/EPOL/main&arch=$basearch"
   52 |       debuginfo: "https://mirrors.openeuler.org/metalink?repo={{ _openeuler_releasever }}/debuginfo&arch=$basearch"
   53 |       source: "https://mirrors.openeuler.org/metalink?repo={{ _openeuler_releasever }}&arch=source"
   54 |       update: "https://mirrors.openeuler.org/metalink?repo={{ _openeuler_releasever }}/update&arch=$basearch"
   55 |       update-source: "https://mirrors.openeuler.org/metalink?repo={{ _openeuler_releasever }}/update&arch=source"
   56 | 
   57 | - name: Clean dnf metadata cache to apply metalink mirror selection
   58 |   ansible.builtin.command: dnf clean metadata
   59 |   become: true
   60 |   when:
   61 |     - openeuler_metalink_enabled
   62 |     - _openeuler_metalink_result.changed
```
