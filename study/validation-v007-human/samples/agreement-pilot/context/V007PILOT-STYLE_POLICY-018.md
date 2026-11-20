# Frozen source context: V007PILOT-STYLE_POLICY-018

- Repository: `FreiFunkMuenster/Ansible-Freifunk-Gateway`
- Commit: `b04e8f81b2b010eaccd13a63271c7ce7eb6fb4b3`
- Family: Style/policy
- Rule: `ansibleguard/missing-tags`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `py_respondd/tasks/main.yml` (reported anchor line 37)
- Object: `task` `0eb6f8cabb66510b93c4c34bfa3bdd0ab0cbe3cba7b6ae06c010dd23d5b30503`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–46 of 46:

```text
    1 | ---
    2 | - name: Install dependencies
    3 |   apt:
    4 |     name: ['python3-pip']
    5 |   when: (ansible_distribution == 'Ubuntu' and ansible_distribution_version == '16.04') or
    6 |         (ansible_distribution == 'Debian' and ansible_distribution_version == '9')
    7 | 
    8 | - name: Install python dependencies
    9 |   pip:
   10 |     name: ['psutil', 'netifaces']
   11 |     executable: pip3
   12 |   when: (ansible_distribution == 'Ubuntu' and ansible_distribution_version == '16.04') or
   13 |         (ansible_distribution == 'Debian' and ansible_distribution_version == '9')
   14 | 
   15 | - name: Install dependencies
   16 |   apt:
   17 |     name: ['python3-distutils', 'python3-setuptools', 'python3-dev', 'python3-psutil', 'python3-netifaces']
   18 |   when: (ansible_distribution == 'Ubuntu' and ansible_distribution_version == '18.04') or
   19 |         (ansible_distribution == 'Debian' and ansible_distribution_version == '10')
   20 | 
   21 | - name: create systemd files
   22 |   template:
   23 |     src: py-respondd.service.j2
   24 |     dest: /etc/systemd/system/py-respondd.service
   25 |   notify: systemctl reload
   26 | 
   27 | - name: Clone py-respondd repo
   28 |   git:
   29 |     repo: https://github.com/FreiFunkMuenster/py-respondd.git
   30 |     dest: /opt/py-respondd/
   31 |     clone: yes
   32 |     update: yes
   33 |   notify: restart respondd
   34 |   tags:
   35 |     - skip_ansible_lint
   36 | 
   37 | - name: create config.json files
   38 |   template:
   39 |     src: config.json.j2
   40 |     dest: /opt/py-respondd/config.json
   41 |   notify: restart respondd
   42 | 
   43 | - name: enable py-respondd service
   44 |   systemd:
   45 |     name: py-respondd.service
   46 |     enabled: yes
```
