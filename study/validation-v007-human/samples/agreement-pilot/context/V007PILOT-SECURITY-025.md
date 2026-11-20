# Frozen source context: V007PILOT-SECURITY-025

- Repository: `ricsanfre/pi-cluster`
- Commit: `f55c4ba0659fd1409389f39026d91441bb0cf6d0`
- Family: Security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `ansible/roles/k3s/master/tasks/k3s_install.yml` (reported anchor line 3)
- Object: `source_location` `2c55fc05e6ad938b73ddcff3fae64289759932e40d570dd7958d73dfc880c14e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–28 of 28:

```text
    1 | ---
    2 | 
    3 | - name: Get K3s installation script
    4 |   ansible.builtin.get_url:
    5 |     url: https://get.k3s.io
    6 |     dest: /tmp/k3s_install.sh
    7 |     mode: '0766'
    8 | 
    9 | - name: Install K3s
   10 |   ansible.builtin.command: "/tmp/k3s_install.sh server"
   11 |   environment:
   12 |     INSTALL_K3S_VERSION: "{{ k3s_version }}"
   13 |   changed_when: true
   14 | 
   15 | - name: Create directory .kube
   16 |   ansible.builtin.file:
   17 |     path: ~{{ ansible_user }}/.kube
   18 |     state: directory
   19 |     owner: "{{ ansible_user }}"
   20 |     mode: "u=rwx,g=rx,o="
   21 | 
   22 | - name: Copy config file to user home directory
   23 |   ansible.builtin.copy:
   24 |     src: /etc/rancher/k3s/k3s.yaml
   25 |     dest: ~{{ ansible_user }}/.kube/config
   26 |     remote_src: true
   27 |     owner: "{{ ansible_user }}"
   28 |     mode: "u=rw,g=,o="
```
