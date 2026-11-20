# Frozen source context: V007PILOT2-STYLE_POLICY-019

- Repository: `easzlab/kubeasz`
- Commit: `fcb46a47a7fcd3bbc97498ea4aefdd564e16b383`
- Family: style_policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/prepare/tasks/offline.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/prepare/tasks/offline.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–36 of 36:

```text
    1 | # 离线安装基础系统包
    2 | # 仅当机器无法从本地yum/apt源安装时使用
    3 | # 执行前需要预先运行类似 ./ezdown -P debian_10 下载离线安装包
    4 | 
    5 | - name: 检查是否已下载离线软件包{{ SYS_PKG_NAME }}
    6 |   stat:
    7 |     path: "{{ base_dir }}/down/packages/{{ SYS_PKG_NAME }}"
    8 |   register: pkg
    9 |   connection: local
   10 |   run_once: true
   11 | 
   12 | - name: 准备离线安装包目录
   13 |   file: name=/opt/kube/packages/basic state=directory
   14 | 
   15 | - block:
   16 |   - name: 分发离线软件包{{ SYS_PKG_NAME }}
   17 |     copy:
   18 |       src: "{{ base_dir }}/down/packages/{{ SYS_PKG_NAME }}"
   19 |       dest: "/opt/kube/packages/basic/{{ SYS_PKG_NAME }}"
   20 | 
   21 |   # 离线安装包可能需要安装多次才能成功
   22 |   - name: 安装离线软件包{{ SYS_PKG_NAME }}
   23 |     shell: 'cd /opt/kube/packages/basic && tar zxf {{ SYS_PKG_NAME }} && \
   24 |            dpkg -i *.deb > /tmp/install_basic.log 2>&1'
   25 |     register: install_info
   26 |     until: not install_info.failed
   27 |     retries: 3
   28 |     delay: 1
   29 |     when: 'ansible_distribution_file_variety in ["Debian"]'
   30 | 
   31 |   - name: 安装离线软件包{{ SYS_PKG_NAME }}
   32 |     shell: 'cd /opt/kube/packages/basic && tar zxf {{ SYS_PKG_NAME }} && \
   33 |            rpm -Uvh --force --nodeps *.rpm > /tmp/install_basic.log 2>&1'
   34 |     when: 'ansible_distribution_file_variety in ["RedHat", "SUSE"]'
   35 |   when: 'pkg.stat.exists|bool'
   36 |   ignore_errors: true
```
