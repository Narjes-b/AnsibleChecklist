# Frozen source context: V007PILOT2-SECURITY-024

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `onecloud/roles/common/tasks/v3_9_online.yml` (reported anchor line 12)
- Flagged construct: task `add cloud rpm repository for kylin`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–32 of 32:

```text
    1 | ---
    2 | - name: Add cloud rpm repository
    3 |   get_url:
    4 |     url: https://iso.yunion.cn/centos/7/3.9/{{ansible_architecture}}/yunion.repo
    5 |     dest: /etc/yum.repos.d/yunion.repo
    6 |     validate_certs: no
    7 |   become: yes
    8 |   when:
    9 |   - is_centos_based is defined
   10 | 
   11 | - name: Add cloud rpm repository for Kylin
   12 |   get_url:
   13 |     url: https://iso.yunion.cn/kylin/v10-{{ansible_distribution_release|lower}}/3.9/{{ansible_architecture}}/kylin-yunion.repo
   14 |     dest: /etc/yum.repos.d/kylin-yunion.repo
   15 |     validate_certs: no
   16 |   become: yes
   17 |   when:
   18 |   - is_kylin_based|default(false)|bool == true
   19 | 
   20 | - name: make cache
   21 |   shell: |
   22 |     yum clean all
   23 |     yum -y --disablerepo='*' --enablerepo='yunion*' makecache
   24 |   when:
   25 |   - is_centos_based is defined
   26 | 
   27 | - name: install libselinux-python for arm64 centos
   28 |   yum:
   29 |     name: libselinux-python
   30 |   when:
   31 |   - is_centos_aarch64 is defined
   32 | 
```
