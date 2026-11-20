# Frozen source context: V007PILOT-STYLE_POLICY-043

- Repository: `ansible-lockdown/RHEL8-CIS`
- Commit: `97a6a9aa80506900009129aa389759d6884d5ec5`
- Family: Style/policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `tasks/fetch_audit_output.yml` (reported anchor line 1)
- Object: `source_location` `ba91488363c9ec7b513df84727fa0b28cd33a5db5ca378a70693cf6e1909c8a9`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–45 of 45:

```text
    1 | ---
    2 | 
    3 | # Stage to copy audit output to a centralised location
    4 | 
    5 | - name: "POST | FETCH | Fetch files and copy to controller"
    6 |   when: audit_output_collection_method == "fetch"
    7 |   ansible.builtin.fetch:
    8 |     src: "{{ item }}"
    9 |     dest: "{{ audit_output_destination }}"
   10 |     flat: true
   11 |   changed_when: true
   12 |   failed_when: false
   13 |   register: discovered_audit_fetch_state
   14 |   loop:
   15 |     - "{{ pre_audit_outfile }}"
   16 |     - "{{ post_audit_outfile }}"
   17 |   become: false
   18 | 
   19 | # Added this option for continuity but could be changed by adjusting the variable audit_conf_dest
   20 | # Allowing backup to one location
   21 | - name: "POST | FETCH | Copy files to location available to managed node"
   22 |   when: audit_output_collection_method == "copy"
   23 |   ansible.builtin.copy:
   24 |     src: "{{ item }}"
   25 |     dest: "{{ audit_output_destination }}"
   26 |     mode: 'u-x,go-wx'
   27 |     flat: true
   28 |   failed_when: false
   29 |   register: discovered_audit_copy_state
   30 |   loop:
   31 |     - "{{ pre_audit_outfile }}"
   32 |     - "{{ post_audit_outfile }}"
   33 | 
   34 | - name: "POST | FETCH | Fetch files and copy to controller | Warning if issues with fetch_audit_files"
   35 |   when: (audit_output_collection_method == "fetch" and not discovered_audit_fetch_state.changed) or (audit_output_collection_method == "copy" and not discovered_audit_copy_state.changed)
   36 |   block:
   37 |     - name: "POST | FETCH | Fetch files and copy to controller | Warning if issues with fetch_audit_files"
   38 |       ansible.builtin.debug:
   39 |         msg: "Warning!! Unable to write to localhost {{ audit_output_destination }} for audit file copy"
   40 | 
   41 |     - name: "POST | FETCH | Fetch files and copy to controller | Warning if issues with fetch_audit_files"
   42 |       vars:
   43 |         warn_control_id: "FETCH_AUDIT_FILES"
   44 |       ansible.builtin.import_tasks:
   45 |         file: warning_facts.yml
```
