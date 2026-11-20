# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-014

- Repository: `osism/ansible-collection-services`
- Commit: `131734f2c007d0009a7fc218849f4ede66c7c899`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/containerd/tasks/install-Debian-family.yml` (reported anchor line 32)
- Object: `variable` `7290a60e5894e433a60c0a3b593327728dace3b5b86de95ed50cf5a232167fd9`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–71 of 71:

```text
    1 | ---
    2 | - name: Remove old architecture-dependent repository
    3 |   become: true
    4 |   ansible.builtin.apt_repository:
    5 |     repo: "deb [ arch=amd64 ] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
    6 |     state: absent
    7 |     filename: docker
    8 |   when: containerd_configure_repository|bool
    9 | 
   10 | - name: Gather the apt package facts
   11 |   ansible.builtin.package_facts:
   12 |     manager: auto
   13 | 
   14 | - name: Check whether packages are installed that should not be installed
   15 |   ansible.builtin.fail:
   16 |     msg: "{{ ansible_facts.packages[item] | length }} versions of {{ item }} are installed!"
   17 |   when: "item in ansible_facts.packages"
   18 |   loop: "{{ containerd_packages_fail }}"
   19 | 
   20 | - name: Install apt-transport-https package
   21 |   become: true
   22 |   ansible.builtin.apt:
   23 |     name: apt-transport-https
   24 |     state: present
   25 |     lock_timeout: "{{ apt_lock_timeout | default(300) }}"
   26 |   when: containerd_configure_repository|bool
   27 |   changed_when: false
   28 | 
   29 | - name: Add repository gpg key
   30 |   become: true
   31 |   ansible.builtin.get_url:
   32 |     url: "{{ docker_repository_key }}"
   33 |     dest: /etc/apt/trusted.gpg.d/docker.asc
   34 |     mode: 0644
   35 |     owner: root
   36 |     group: root
   37 |   when:
   38 |     - containerd_configure_repository|bool
   39 | 
   40 | - name: Add repository
   41 |   become: true
   42 |   ansible.builtin.apt_repository:
   43 |     repo: "{{ docker_repository }}"
   44 |     state: present
   45 |     filename: docker
   46 |     update_cache: true
   47 |     mode: 0644
   48 |   when: containerd_configure_repository|bool
   49 | 
   50 | - name: Unlock containerd package
   51 |   become: true
   52 |   ansible.builtin.dpkg_selections:
   53 |     name: "{{ containerd_package_name }}"
   54 |     selection: install
   55 |   when: containerd_package_name in ansible_facts.packages
   56 |   tags: molecule-idempotence-notest
   57 | 
   58 | # NOTE: At this point the last available version of containerd should be installed
   59 | - name: Install containerd package
   60 |   become: true
   61 |   ansible.builtin.apt:
   62 |     name: "{{ containerd_package_name }}"
   63 |     state: latest
   64 |     lock_timeout: "{{ apt_lock_timeout | default(300) }}"
   65 | 
   66 | - name: Lock containerd package
   67 |   become: true
   68 |   ansible.builtin.dpkg_selections:
   69 |     name: "{{ containerd_package_name }}"
   70 |     selection: hold
   71 |   tags: molecule-idempotence-notest
```

## Visible variable references

```text
131734f2c007d0009a7fc218849f4ede66c7c899:roles/containerd/tasks/install-Debian-family.yml:32:    url: "{{ docker_repository_key }}"
131734f2c007d0009a7fc218849f4ede66c7c899:roles/containerd/tasks/install-RedHat-family.yml:21:    key: "{{ docker_repository_key }}"
131734f2c007d0009a7fc218849f4ede66c7c899:roles/containerd/tasks/main.yml:10:- name: Set docker_repository_key variable to default value
131734f2c007d0009a7fc218849f4ede66c7c899:roles/containerd/tasks/main.yml:12:    docker_repository_key: "{{ __docker_repository_key }}"
131734f2c007d0009a7fc218849f4ede66c7c899:roles/containerd/tasks/main.yml:13:  when: docker_repository_key|default(None) == None
131734f2c007d0009a7fc218849f4ede66c7c899:roles/containerd/vars/CentOS-dist.yml:2:__docker_repository_key: https://download.docker.com/linux/centos/gpg
131734f2c007d0009a7fc218849f4ede66c7c899:roles/containerd/vars/Debian-dist.yml:2:__docker_repository_key: https://download.docker.com/linux/debian/gpg
131734f2c007d0009a7fc218849f4ede66c7c899:roles/containerd/vars/Ubuntu-dist.yml:2:__docker_repository_key: https://download.docker.com/linux/ubuntu/gpg
```
