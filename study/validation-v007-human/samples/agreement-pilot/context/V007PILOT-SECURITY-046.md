# Frozen source context: V007PILOT-SECURITY-046

- Repository: `theforeman/forklift`
- Commit: `ee24dec347fc0a785d22989fd1a183393fa4e054`
- Family: Security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `playbooks/collect_debug.yml` (reported anchor line 2)
- Object: `source_location` `d3ec7e3ee74dd4f185b9a73c342316417d4ef04c7bd5e990fd0a61f0169579e7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–51 of 51:

```text
    1 | ---
    2 | - hosts: all
    3 |   become: true
    4 |   vars:
    5 |     bats_output_dir: '/root/bats_results'
    6 |     remote_dir: "/tmp/debug-{{ pipeline_type | default('foreman') }}-{{ pipeline_version | default('nightly') }}-{{ pipeline_os | default('el7') }}-{{ pipeline_action | default('install') }}"
    7 |     smoker_output_dir: '/home/vagrant/smoker'
    8 |     backup_output_dir: '/var/tmp/foreman-backup'
    9 |   roles:
   10 |     - role: foreman_maintain_packages
   11 |     - role: sos_report
   12 |   tasks:
   13 |     - name: "Find bats files"
   14 |       find:
   15 |         paths: "{{ bats_output_dir }}"
   16 |         patterns: "*.tap"
   17 |       register: bats_results
   18 | 
   19 |     - name: "Copy bats results"
   20 |       fetch:
   21 |         src: "{{ item.path }}"
   22 |         dest: "{{ remote_dir }}"
   23 |       with_items: "{{ bats_results.files }}"
   24 | 
   25 |     - name: "Find smoker files"
   26 |       find:
   27 |         paths: "{{ smoker_output_dir }}"
   28 |         patterns:
   29 |           - "junit.xml"
   30 |           - "report.tar*"
   31 |         recurse: False
   32 |       register: smoker_results
   33 | 
   34 |     - name: "Copy smoker results"
   35 |       fetch:
   36 |         src: "{{ item.path }}"
   37 |         dest: "{{ remote_dir }}"
   38 |       with_items: "{{ smoker_results.files }}"
   39 | 
   40 |     - name: "Find backup files"
   41 |       find:
   42 |         paths: "{{ backup_output_dir }}"
   43 |         recurse: True
   44 |         hidden: True
   45 |       register: backup_results
   46 | 
   47 |     - name: "Copy backup results"
   48 |       fetch:
   49 |         src: "{{ item.path }}"
   50 |         dest: "{{ remote_dir }}"
   51 |       with_items: "{{ backup_results.files }}"
```
