# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-003

- Repository: `Sunbird-Obsrv/sunbird-data-pipeline`
- Commit: `eb1e1a1c3533c549693dda32cd92c667754aaea9`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/redundant-default-value`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `ansible/roles/secor-deploy/tasks/main.yml` (reported anchor line 4)
- Object: `variable` `cad8206f5015d1aff2470c724c6175b270024b712400ee98afbf9e2945585268`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–28 of 28:

```text
    1 | - name: Create secor service
    2 |   vars:
    3 |     description: Secor service
    4 |     script_dir: "{{ sbin_path }}"
    5 |   template: src=secor-service.j2 dest={{ sbin_path }}/secor mode=755 owner={{ analytics_user }} group={{ analytics_group }}
    6 | 
    7 | - name: Copy monitoring script
    8 |   template: src=monitor-secor.j2 dest={{ sbin_path }}/monitor-secor.sh mode=755 owner={{ analytics_user }} group={{ analytics_group }}
    9 | 
   10 | - name: Finding the old artifact name 
   11 |   find:
   12 |     paths: "{{ analytics_user_home }}"
   13 |     patterns: secor-*-SNAPSHOT-bin.tar.gz
   14 |   register: file_name
   15 | 
   16 | - name: Remove the old artifacts
   17 |   file: name="{{ item }}" state=absent
   18 |   with_items: "{{ file_name.files[0].path }}"
   19 |   when: file_name.files | length > 0
   20 | 
   21 | - name: Copy secor libraries
   22 |   copy:
   23 |     src: "{{ item }}"
   24 |     dest: "{{ analytics_user_home }}" 
   25 |     owner: "{{ analytics_user }}"
   26 |     group: "{{ analytics_user }}"
   27 |   with_fileglob:
   28 |     - "artifacts/target/secor-{{ secor.artifact_ver }}-bin.tar.gz"
```

## Visible variable references

```text
eb1e1a1c3533c549693dda32cd92c667754aaea9:ansible/roles/secor-deploy/defaults/main.yml:8:script_dir: "{{ sbin_path }}"
eb1e1a1c3533c549693dda32cd92c667754aaea9:ansible/roles/secor-deploy/tasks/main.yml:4:    script_dir: "{{ sbin_path }}"
```
