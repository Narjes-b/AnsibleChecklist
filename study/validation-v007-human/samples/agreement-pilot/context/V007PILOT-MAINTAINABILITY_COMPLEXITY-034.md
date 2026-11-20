# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-034

- Repository: `adoptium/infrastructure`
- Commit: `d31f47293b3a0166a4f9d7b8c51475d548999408`
- Family: Maintainability/complexity
- Rule: `ansibleguard/undocumented-complex-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Python2.7/tasks/main.yml` (reported anchor line 19)
- Object: `source_location` `86321584c72a5d189096716b6015b67b8f62aa767cc26f7bff0b60dc7088b85f`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–33 of 33:

```text
    1 | ---
    2 | ####################
    3 | # Python Bootstrap #
    4 | ####################
    5 | 
    6 | # Check if Python is installed, and its version. If Python isn't installed, or it's at a version below 2.7.18, install Python 2.7.18.
    7 | # Currently only for CentOS6. See: https://github.com/adoptium/infrastructure/issues/1877
    8 | 
    9 | - name: Check for Python 2's version
   10 |   shell: python -V 2>&1 | grep -Po '(?<=Python )(.+)'
   11 |   register: python_version
   12 |   changed_when: false
   13 |   failed_when: false
   14 |   when:
   15 |     - (ansible_distribution == "CentOS" or ansible_distribution == "RedHat") and (ansible_distribution_major_version == "6")
   16 |   tags:
   17 |     - python2.7
   18 | 
   19 | - name: Install Python2.7 to /usr/local/python2
   20 |   unarchive:
   21 |     src: https://ci.adoptium.net/userContent/usrlocalPython27.tar.xz
   22 |     dest: /usr/local/
   23 |     remote_src: yes
   24 |     mode: 0755
   25 |   retries: 3
   26 |   delay: 5
   27 |   register: python_download
   28 |   until: python_download is not failed
   29 |   when:
   30 |     - (ansible_distribution == "CentOS" or ansible_distribution == "RedHat") and (ansible_distribution_major_version == "6")
   31 |     - (python_version.rc != 0) or (python_version.rc == 0 and python_version.stdout is version_compare('2.7.18', operator='lt'))
   32 |   tags:
   33 |     - python2.7
```
