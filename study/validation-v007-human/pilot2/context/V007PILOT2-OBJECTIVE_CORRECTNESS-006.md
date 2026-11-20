# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-006

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: objective_correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/core_install/tasks/install_nodeid.yml` (reported anchor line 40)
- Flagged construct: not named by the finding; the anchor line 40 lies in the task at line 40, name `cluster | Restart scaleadmd ( workaround)`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–64 of 64:

```text
    1 | ---
    2 | # Updated for Ansible 2.19 compatibility
    3 | #
    4 | # Copy ssh key package
    5 | #
    6 | 
    7 | - block:
    8 |     - name: install| Creates default directory
    9 |       file:
   10 |         path: "{{ hostvars[inventory_hostname].cert_dir_location }}"
   11 |         state: directory
   12 |         mode: '0600'
   13 |         recurse: yes
   14 |       when: hostvars[inventory_hostname].cert_dir_location is defined | bool
   15 | 
   16 |     - name: install | Copy installation package to node
   17 |       copy:
   18 |         src: "{{ hostvars[inventory_hostname].node_cert }}"
   19 |         dest: "{{ hostvars[inventory_hostname].node_cert }}"
   20 |         mode: '0600'
   21 | 
   22 |     - name: install | Copy installation package to node
   23 |       copy:
   24 |         src: "{{ hostvars[inventory_hostname].node_cert_key }}"
   25 |         dest: "{{ hostvars[inventory_hostname].node_cert_key }}"
   26 |         mode: '0600'
   27 | 
   28 |     - name: install | Copy installation package to node
   29 |       copy:
   30 |         src: "{{ hostvars[inventory_hostname].node_cert_chain }}"
   31 |         dest: "{{ hostvars[inventory_hostname].node_cert_chain }}"
   32 |         mode: '0600'
   33 | 
   34 |     - name: cluster | Node identity
   35 |       command: /usr/lpp/mmfs/bin/scalectl node config get
   36 |       register: nodeidentity_exist_results
   37 |       ignore_errors: yes
   38 |       failed_when: false
   39 | 
   40 |     - name: cluster | Restart scaleadmd ( workaround)
   41 |       command: systemctl restart scaleadmd
   42 |       ignore_errors: yes
   43 |       failed_when: false
   44 |       when: 
   45 |           - nodeidentity_exist_results.stderr is defined
   46 |           - "'/var/mmfs/run/grpc.admin.sock' in nodeidentity_exist_results.stderr
   47 |              or '/var/mmfs/run/scaleadmd.grpc.sock' in nodeidentity_exist_results.stderr"
   48 |     - debug:
   49 |             msg: "{{nodeidentity_exist_results}}"
   50 | 
   51 |     - name: cluster | Node identity
   52 |       command: /usr/lpp/mmfs/bin/scalectl node config set --cert {{ hostvars[inventory_hostname].node_cert }} --key {{ hostvars[inventory_hostname].node_cert_key }} --chain {{ hostvars[inventory_hostname].node_cert_chain }}
   53 |       register: nodeidentity_results
   54 |       retries: 5
   55 |       delay: 30
   56 |       #when: nodeidentity_exist_results.stdout_lines | length < 1
   57 |   when:
   58 |     - hostvars[inventory_hostname].node_cert is defined | bool
   59 |     - hostvars[inventory_hostname].node_cert_key is defined | bool
   60 |     - hostvars[inventory_hostname].node_cert_chain is defined | bool
   61 | 
   62 | - debug:
   63 |      msg: "{{ nodeidentity_results.cmd }}"
   64 |   when: nodeidentity_results.cmd is defined | bool
```
