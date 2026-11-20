# Frozen source context: V007PILOT2-SECURITY-017

- Repository: `ricsanfre/pi-cluster`
- Commit: `f55c4ba0659fd1409389f39026d91441bb0cf6d0`
- Family: security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `ansible/tasks/install_velero_cli.yml` (reported anchor line 13)
- Flagged construct: not named by the finding; the anchor line 13 lies in the task at line 13, name `Download Velero CLI`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–33 of 33:

```text
    1 | ---
    2 | 
    3 | - name: Gather architecture facts
    4 |   ansible.builtin.setup:
    5 |     gather_subset:
    6 |       - min
    7 |   when: ansible_facts.architecture is not defined
    8 | 
    9 | - name: Set Velero CLI architecture
   10 |   ansible.builtin.set_fact:
   11 |     velero_cli_arch: "{{ {'x86_64': 'amd64', 'aarch64': 'arm64', 'arm64': 'arm64'}.get(ansible_facts.architecture, ansible_facts.architecture) }}"
   12 | 
   13 | - name: Download Velero CLI
   14 |   become: true
   15 |   ansible.builtin.get_url:
   16 |     url: "https://github.com/vmware-tanzu/velero/releases/download/{{ velero_version }}/velero-{{ velero_version }}-linux-{{ velero_cli_arch }}.tar.gz"
   17 |     dest: "/tmp/velero-{{ velero_version }}-linux-{{ velero_cli_arch }}.tar.gz"
   18 |     mode: '0766'
   19 | 
   20 | - name: Extract archives
   21 |   become: true
   22 |   ansible.builtin.unarchive:
   23 |     src: "/tmp/velero-{{ velero_version }}-linux-{{ velero_cli_arch }}.tar.gz"
   24 |     dest: /tmp
   25 |     remote_src: true
   26 | 
   27 | - name: Copy binary to /usr/local/bin
   28 |   become: true
   29 |   ansible.builtin.copy:
   30 |     src: "/tmp/velero-{{ velero_version }}-linux-{{ velero_cli_arch }}/velero"
   31 |     dest: /usr/local/bin/velero
   32 |     mode: '0755'
   33 |     remote_src: true
```
