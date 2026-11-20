# Frozen source context: V007PILOT-STRUCTURE_REUSE-039

- Repository: `compscidr/iac`
- Commit: `350e7b8162778ad7beab8e2da8be53ea24a1127a`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible/roles/fnm/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `10c9f116f297afd691dd65507ea2ad1c5cf1dd96c1e4f5010688e1cc1d4f6113`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–172 of 172:

```text
    1 | ---
    2 | # fnm - Fast Node Manager
    3 | # https://github.com/Schniz/fnm
    4 | 
    5 | - name: Remove apt nodejs/npm packages (cleanup old installs)
    6 |   become: true
    7 |   tags:
    8 |     - fnm
    9 |     - node
   10 |     - cleanup
   11 |   ansible.builtin.apt:
   12 |     pkg:
   13 |       - nodejs
   14 |       - npm
   15 |     state: absent
   16 |     autoremove: true
   17 |   when:
   18 |     - fnm_cleanup_apt | default(true)
   19 |     - ansible_os_family == "Debian"
   20 | 
   21 | - name: Install fnm dependencies (unzip, curl)
   22 |   become: true
   23 |   tags:
   24 |     - fnm
   25 |     - node
   26 |   ansible.builtin.apt:
   27 |     pkg:
   28 |       - unzip
   29 |       - curl
   30 |     state: present
   31 |     update_cache: true
   32 |   when: ansible_os_family == "Debian"
   33 | 
   34 | - name: Check if fnm is installed
   35 |   become: true
   36 |   become_user: "{{ username }}"
   37 |   ansible.builtin.shell: which fnm || echo "not found"
   38 |   register: fnm_check
   39 |   changed_when: false
   40 |   tags:
   41 |     - fnm
   42 |     - node
   43 | 
   44 | # Uses the vendor's official install script rather than get_url/uri, since the
   45 | # script itself handles the download, extraction, and directory layout.
   46 | - name: Install fnm via install script (Linux)
   47 |   become: true
   48 |   become_user: "{{ username }}"
   49 |   ansible.builtin.shell: |  # noqa: command-instead-of-module
   50 |     set -o pipefail
   51 |     curl -fsSL https://fnm.vercel.app/install | bash -s -- --skip-shell
   52 |   args:
   53 |     creates: "/home/{{ username }}/.local/share/fnm/fnm"
   54 |     executable: /bin/bash
   55 |   when:
   56 |     - ansible_system == "Linux"
   57 |     - "'not found' in fnm_check.stdout"
   58 |   tags:
   59 |     - fnm
   60 |     - node
   61 | 
   62 | - name: Install fnm via Homebrew (macOS)
   63 |   community.general.homebrew:
   64 |     name: fnm
   65 |     state: present
   66 |   when:
   67 |     - ansible_os_family == "Darwin"
   68 |     - "'not found' in fnm_check.stdout"
   69 |   tags:
   70 |     - fnm
   71 |     - node
   72 | 
   73 | - name: Add fnm to bashrc (Linux)
   74 |   become: true
   75 |   become_user: "{{ username }}"
   76 |   ansible.builtin.blockinfile:
   77 |     path: "/home/{{ username }}/.bashrc"
   78 |     marker: "# {mark} ANSIBLE MANAGED - fnm"
   79 |     block: |
   80 |       # fnm (Fast Node Manager)
   81 |       FNM_PATH="$HOME/.local/share/fnm"
   82 |       if [ -d "$FNM_PATH" ]; then
   83 |         export PATH="$FNM_PATH:$PATH"
   84 |         eval "$(fnm env --use-on-cd --shell bash)"
   85 |       fi
   86 |     create: true
   87 |     mode: '0644'
   88 |   when:
   89 |     - ansible_system == "Linux"
   90 |     - fnm_configure_shell | default(true)
   91 |   tags:
   92 |     - fnm
   93 |     - node
   94 | 
   95 | - name: Add fnm to zshrc (Linux)
   96 |   become: true
   97 |   become_user: "{{ username }}"
   98 |   ansible.builtin.blockinfile:
   99 |     path: "/home/{{ username }}/.zshrc"
  100 |     marker: "# {mark} ANSIBLE MANAGED - fnm"
  101 |     block: |
  102 |       # fnm (Fast Node Manager)
  103 |       FNM_PATH="$HOME/.local/share/fnm"
  104 |       if [ -d "$FNM_PATH" ]; then
  105 |         export PATH="$FNM_PATH:$PATH"
  106 |         eval "$(fnm env --use-on-cd --shell zsh)"
  107 |       fi
  108 |     create: true
  109 |     mode: '0644'
  110 |   when:
  111 |     - ansible_system == "Linux"
  112 |     - fnm_configure_shell | default(true)
  113 |   tags:
  114 |     - fnm
  115 |     - node
  116 | 
  117 | - name: Add fnm to zshrc (macOS)
  118 |   ansible.builtin.blockinfile:
  119 |     path: "/home/{{ username }}/.zshrc"
  120 |     marker: "# {mark} ANSIBLE MANAGED - fnm"
  121 |     block: |
  122 |       # fnm (Fast Node Manager) - installed via Homebrew
  123 |       eval "$(fnm env --use-on-cd --shell zsh)"
  124 |     create: true
  125 |     mode: '0644'
  126 |   when:
  127 |     - ansible_os_family == "Darwin"
  128 |     - fnm_configure_shell | default(true)
  129 |   tags:
  130 |     - fnm
  131 |     - node
  132 | 
  133 | - name: Check installed Node versions
  134 |   become: true
  135 |   become_user: "{{ username }}"
  136 |   ansible.builtin.shell: |
  137 |     set -o pipefail
  138 |     export PATH="$HOME/.local/share/fnm:/opt/homebrew/bin:$PATH"
  139 |     fnm list 2>/dev/null | grep -q "{{ fnm_node_version }}" && echo "installed" || echo "not installed"
  140 |   args:
  141 |     executable: /bin/bash
  142 |   register: fnm_node_version_check
  143 |   changed_when: false
  144 |   tags:
  145 |     - fnm
  146 |     - node
  147 | 
  148 | - name: Install Node.js version via fnm
  149 |   become: true
  150 |   become_user: "{{ username }}"
  151 |   ansible.builtin.shell: |
  152 |     export PATH="$HOME/.local/share/fnm:/opt/homebrew/bin:$PATH"
  153 |     eval "$(fnm env)"
  154 |     fnm install {{ fnm_node_version }}
  155 |   changed_when: true
  156 |   when: "'not installed' in fnm_node_version_check.stdout"
  157 |   tags:
  158 |     - fnm
  159 |     - node
  160 | 
  161 | - name: Set default Node.js version
  162 |   become: true
  163 |   become_user: "{{ username }}"
  164 |   ansible.builtin.shell: |
  165 |     export PATH="$HOME/.local/share/fnm:/opt/homebrew/bin:$PATH"
  166 |     eval "$(fnm env)"
  167 |     fnm default {{ fnm_node_version }}
  168 |   when: fnm_set_default | default(true)
  169 |   changed_when: false
  170 |   tags:
  171 |     - fnm
  172 |     - node
```

## Frozen tracked paths in the relevant role/scope

```text
ansible/roles/fnm/defaults/main.yml
ansible/roles/fnm/tasks/main.yml
```
