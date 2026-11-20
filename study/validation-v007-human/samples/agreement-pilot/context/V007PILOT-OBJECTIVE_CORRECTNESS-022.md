# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-022

- Repository: `silogen/cluster-bloom`
- Commit: `6122fdec7e1e0feed6081e46be0e44cd45d08809`
- Family: Objective correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `pkg/ansible/runtime/playbooks/tasks/prepare_node/ntp.yaml` (reported anchor line 35)
- Object: `source_location` `c9f328d2f6488ff7b3fc94b12b36609d04ef8aef1762d9af4d5bf1f5513b868c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–54 of 54:

```text
    1 | ---
    2 | # Purpose: Configure chrony NTP service for time synchronization
    3 | # Dependencies: FIRST_NODE, SERVER_IP variables
    4 | # Usage: Imported by prepare_node/main.yaml
    5 | # Tags: [ntp, prep_node]
    6 | # Handlers: Restart chronyd
    7 | 
    8 | - name: Create Chrony Config (First Node)
    9 |   when: FIRST_NODE | default(true) | bool
   10 |   block:
   11 |     - name: Backup original chrony.conf
   12 |       copy:
   13 |         src: /etc/chrony/chrony.conf
   14 |         dest: /etc/chrony/chrony.conf.bak
   15 |         remote_src: yes
   16 |       ignore_errors: yes
   17 | 
   18 |     - name: Create chrony.conf for first node
   19 |       copy:
   20 |         content: |
   21 |           pool 0.pool.ntp.org iburst maxsources 2
   22 |           server time.google.com iburst
   23 |           server time.cloudflare.com iburst
   24 | 
   25 |           pool pool.ntp.org iburst maxsources 4
   26 | 
   27 |           allow 10.0.0.0/8
   28 |         dest: /etc/chrony/chrony.conf
   29 |         mode: "0644"
   30 |       notify: Restart chronyd
   31 | 
   32 | - name: Create Chrony Config (Additional Node)
   33 |   when: not (FIRST_NODE | default(true) | bool) and SERVER_IP != ""
   34 |   block:
   35 |     - name: Backup original chrony.conf
   36 |       copy:
   37 |         src: /etc/chrony/chrony.conf
   38 |         dest: /etc/chrony/chrony.conf.bak
   39 |         remote_src: yes
   40 |       ignore_errors: yes
   41 | 
   42 |     - name: Create chrony.conf for additional node
   43 |       copy:
   44 |         content: |
   45 |           pool pool.ntp.org iburst maxsources 4
   46 |           server time.google.com iburst
   47 |           server time.cloudflare.com iburst
   48 | 
   49 |           server {{ SERVER_IP }} iburst prefer
   50 | 
   51 |           pool 0.pool.ntp.org iburst maxsources 2
   52 |         dest: /etc/chrony/chrony.conf
   53 |         mode: "0644"
   54 |       notify: Restart chronyd
```
