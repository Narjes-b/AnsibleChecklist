# Frozen source context: V007PILOT-SECURITY-050

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: Security
- Rule: `ansibleguard/missing-validate-certs`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `onecloud/roles/common/tasks/master_online.yml` (reported anchor line 37)
- Object: `task` `67cced4706d89e26f43917634fbbf31721204eb5d4ec347d3da5c2b8ef40447d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–65 of 65:

```text
    1 | ---
    2 | - name: assert onecloud_version_abbr
    3 |   fail:
    4 |     msg: "onecloud_version_abbr is not defined."
    5 |   when:
    6 |   -  onecloud_version_abbr |default('') | length == 0
    7 | 
    8 | - name: Online repo
    9 |   shell: |
   10 |     cat > /etc/yum.repos.d/yunion.repo <<EOF_MISC
   11 |     [yunion-repo-base]
   12 |     name=Packages for Yunion Multi-Cloud Platform -
   13 |     baseurl=https://iso.yunion.cn/centos/7/{{onecloud_version_abbr}}/{{ansible_architecture}}
   14 |     sslverify=0
   15 |     failovermethod=priority
   16 |     enabled=1
   17 |     gpgcheck=0
   18 |     priority=1
   19 | 
   20 |     [yunion-repo-updates]
   21 |     name=Yunion Bin Packages for Yunion Multi-Cloud Platform -
   22 |     baseurl=https://iso.yunion.cn/rpm-updates/{{ansible_architecture}}
   23 |     sslverify=0
   24 |     failovermethod=priority
   25 |     enabled=1
   26 |     gpgcheck=0
   27 |     priority=2
   28 |     EOF_MISC
   29 |   become: yes
   30 |   args:
   31 |     executable: /bin/bash
   32 |   when:
   33 |   - online_status | default('') == 'online'
   34 |   - is_centos | default(false) == true
   35 | 
   36 | - name: Add cloud rpm repository for Kylin
   37 |   get_url:
   38 |     url: https://iso.yunion.cn/kylin/v10-{{ansible_distribution_release|lower}}/3.10/{{ansible_architecture}}/kylin-yunion.repo
   39 |     dest: /etc/yum.repos.d/kylin-yunion.repo
   40 |     validate_certs: no
   41 |   become: yes
   42 |   when:
   43 |   - is_kylin_based|default(false)|bool == true
   44 | 
   45 | - name: Add cloud rpm repository for OpenEuler
   46 |   get_url:
   47 |     url: https://iso.yunion.cn/openeuler/{{ansible_distribution_major_version |lower}}/3.10/{{ansible_architecture}}/yunion.repo
   48 |     dest: /etc/yum.repos.d/yunion-openeuler.repo
   49 |     validate_certs: no
   50 |   become: yes
   51 |   when:
   52 |   - is_openeuler_based|default(false)|bool == true
   53 | 
   54 | - name: make cache
   55 |   shell: |
   56 |     yum clean all
   57 |     yum -y --disablerepo='*' --enablerepo='yunion*' makecache
   58 |   when:
   59 |   - is_centos_based is defined
   60 | 
   61 | - name: install libselinux-python for arm64 centos
   62 |   yum:
   63 |     name: libselinux-python
   64 |   when:
   65 |   - is_centos_aarch64 is defined
```
