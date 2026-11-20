# Frozen source context: V007PILOT2-STRUCTURE_REUSE-001

- Repository: `autobase-tech/autobase`
- Commit: `f24ff3d316e688901a1118a9f769798f40dd42e7`
- Family: structure_reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `automation/roles/patroni/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`automation/roles/patroni/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–101 of 1161:

```text
    1 | ---
    2 | - name: Make sure handlers are flushed immediately
    3 |   ansible.builtin.meta: flush_handlers
    4 |   when: not point_in_time_recovery | default(false) | bool
    5 | 
    6 | # pip install
    7 | - ansible.builtin.import_tasks: pip.yml
    8 |   when:
    9 |     - patroni_installation_method == "pip"
   10 |     - pip_package not in system_packages
   11 |     - not point_in_time_recovery | default(false) | bool
   12 |   vars:
   13 |     pip_package: "python{{ python_version | default('3') }}-pip"
   14 |   tags: patroni, patroni_install, pip
   15 | 
   16 | # Patroni install
   17 | - block: # installation_method: "packages" and patroni_installation_method: "pip"
   18 |     - name: Install setuptools
   19 |       ansible.builtin.pip:
   20 |         name: setuptools<66.0.0 # https://github.com/pypa/setuptools/issues/3772
   21 |         state: latest
   22 |         executable: pip3
   23 |         extra_args: "--trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org"
   24 |         umask: "0022"
   25 |       environment:
   26 |         PATH: "{{ ansible_env.PATH }}:/usr/local/bin:/usr/bin"
   27 |         PIP_BREAK_SYSTEM_PACKAGES: "1"
   28 |       when: patroni_pip_requirements_repo | length < 1
   29 | 
   30 |     # Use master requirements if patroni_install_version is 'latest' or explicitly forced via patroni_latest_requirements
   31 |     - name: Download Patroni requirements.txt
   32 |       ansible.builtin.get_url:
   33 |         url: >-
   34 |           https://raw.githubusercontent.com/patroni/patroni/{{
   35 |             'refs/heads/master' if patroni_install_version == 'latest' or patroni_latest_requirements | default(false)
   36 |             else 'refs/tags/v' ~ (patroni_install_version | regex_replace('^v', ''))
   37 |           }}/requirements.txt
   38 |         dest: /tmp/requirements.txt
   39 |         timeout: 60
   40 |         validate_certs: false
   41 |       when: patroni_pip_requirements_repo | length < 1
   42 | 
   43 |     - name: Install requirements
   44 |       ansible.builtin.pip:
   45 |         requirements: /tmp/requirements.txt
   46 |         executable: pip3
   47 |         extra_args: "--trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org"
   48 |         umask: "0022"
   49 |       environment:
   50 |         PATH: "{{ ansible_env.PATH }}:{{ postgresql_bin_dir }}:/usr/local/bin:/usr/bin"
   51 |         PIP_BREAK_SYSTEM_PACKAGES: "1"
   52 |       when: patroni_pip_requirements_repo | length < 1
   53 | 
   54 |     - name: Install patroni
   55 |       ansible.builtin.pip:
   56 |         name: patroni
   57 |         state: latest
   58 |         executable: pip3
   59 |         extra_args: "--trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org"
   60 |         umask: "0022"
   61 |       environment:
   62 |         PATH: "{{ ansible_env.PATH }}:/usr/local/bin:/usr/bin"
   63 |         PIP_BREAK_SYSTEM_PACKAGES: "1"
   64 |       when: patroni_pip_package_repo | length < 1 and patroni_install_version == "latest"
   65 | 
   66 |     - name: "Install patroni {{ patroni_install_version | default('') }}"
   67 |       ansible.builtin.pip:
   68 |         name: "patroni=={{ patroni_install_version }}"
   69 |         executable: pip3
   70 |         extra_args: "--trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org"
   71 |         umask: "0022"
   72 |       environment:
   73 |         PATH: "{{ ansible_env.PATH }}:/usr/local/bin:/usr/bin"
   74 |         PIP_BREAK_SYSTEM_PACKAGES: "1"
   75 |       when: patroni_pip_package_repo | length < 1 and patroni_install_version != "latest"
   76 |   when:
   77 |     - installation_method == "packages"
   78 |     - patroni_installation_method == "pip"
   79 |     - not point_in_time_recovery | default(false) | bool
   80 |   environment: "{{ proxy_env | default({}) }}"
   81 |   tags: patroni, patroni_install
   82 | 
   83 | - block: # when "patroni_pip_requirements_repo" and "patroni_pip_package_repo" is defined
   84 |     - name: Download patroni requirements
   85 |       ansible.builtin.get_url:
   86 |         url: "{{ item }}"
   87 |         dest: /tmp/
   88 |         timeout: 120
   89 |         validate_certs: false
   90 |       loop: "{{ patroni_pip_requirements_repo }}"
   91 |       when: patroni_pip_requirements_repo | length > 0
   92 | 
   93 |     - name: Download patroni package
   94 |       ansible.builtin.get_url:
   95 |         url: "{{ item }}"
   96 |         dest: /tmp/
   97 |         timeout: 60
   98 |         validate_certs: false
   99 |       loop: "{{ patroni_pip_package_repo | list }}"
  100 |       when: patroni_pip_package_repo | length > 0
  101 | 
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `automation/roles/patroni`; 15 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: yes
- molecule/ directory: no

automation/roles/patroni/README.md
automation/roles/patroni/handlers/main.yml
automation/roles/patroni/meta/main.yml
automation/roles/patroni/tasks/config.yml
automation/roles/patroni/tasks/custom_wal_dir.yml
automation/roles/patroni/tasks/failover.yml
automation/roles/patroni/tasks/main.yml
automation/roles/patroni/tasks/patroni.yml
automation/roles/patroni/tasks/pg_hba.yml
automation/roles/patroni/tasks/pip.yml
automation/roles/patroni/tasks/reinit.yml
automation/roles/patroni/tasks/switchover.yml
automation/roles/patroni/templates/patroni.service.j2
automation/roles/patroni/templates/patroni.yml.j2
automation/roles/patroni/templates/pg_hba.conf.j2
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).
