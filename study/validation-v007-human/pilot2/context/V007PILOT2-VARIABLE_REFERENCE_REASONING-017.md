# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-017

- Repository: `TechDufus/dotfiles`
- Commit: `abe3beabdf436c1a7aeeff66b6c2f5903f7b9878`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unscoped-shell-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `roles/nvm/tasks/main.yml` (reported anchor line 111)
- Flagged construct: not named by the finding; the anchor line 111 lies in the task at line 111, name `NVM | Check current default Node.js version`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–158 of 158:

```text
    1 | ---
    2 | - name: "NVM | Download Latest Version JSON"
    3 |   ansible.builtin.uri:
    4 |     url: https://api.github.com/repos/nvm-sh/nvm/releases/latest
    5 |     headers:
    6 |       Accept: application/vnd.github.v3+json
    7 |   register: nvm_latest_version_json
    8 |   changed_when: false
    9 |   failed_when: false
   10 |   check_mode: false  # Always run this task even in check mode
   11 | 
   12 | - name: "NVM | Check if API request succeeded"
   13 |   ansible.builtin.fail:
   14 |     msg: "Failed to fetch NVM latest version from GitHub API. Status: {{ nvm_latest_version_json.status | default('unknown') }}. You may be rate limited or have network issues."
   15 |   when: 
   16 |     - nvm_latest_version_json.json is not defined or nvm_latest_version_json.status != 200
   17 |     - not (nvm_latest_version_json.skipped | default(false))  # Don't fail if task was skipped
   18 | 
   19 | - name: "NVM | Set fallback version if in check mode and API call was skipped"
   20 |   ansible.builtin.set_fact:
   21 |     nvm_latest_release: "{{ nvm_fallback_version }}"
   22 |   when: 
   23 |     - nvm_latest_version_json.skipped | default(false)
   24 |     - ansible_check_mode
   25 | 
   26 | - name: "NVM | Registering NVM Latest Release from API"
   27 |   ansible.builtin.set_fact:
   28 |     nvm_latest_release: "{{ nvm_latest_version_json.json.tag_name }}"
   29 |   when: 
   30 |     - nvm_latest_version_json.json is defined
   31 |     - nvm_latest_version_json.status == 200
   32 | 
   33 | - name: NVM | Show nvm_latest_release debug
   34 |   ansible.builtin.debug:
   35 |     var: nvm_latest_release
   36 | 
   37 | - name: "NVM | Check current nvm version"
   38 |   ansible.builtin.shell: |
   39 |     if [ -f "{{ ansible_facts['env']['HOME'] }}/.nvm/nvm.sh" ]; then
   40 |       cd "{{ ansible_facts['env']['HOME'] }}/.nvm" && git describe --tags 2>/dev/null || echo "none"
   41 |     else
   42 |       echo "not-installed"
   43 |     fi
   44 |   register: current_nvm_version
   45 |   changed_when: false
   46 |   check_mode: false
   47 | 
   48 | - name: "NVM | Ensure nvm directory exists"
   49 |   ansible.builtin.file:
   50 |     path: "{{ ansible_facts['env']['HOME'] }}/.nvm"
   51 |     state: directory
   52 |     mode: "0755"
   53 |   when:
   54 |     - nvm_latest_release is defined
   55 |     - current_nvm_version.stdout == "not-installed" or current_nvm_version.stdout != nvm_latest_release
   56 | 
   57 | - name: "NVM | Install or update nvm"
   58 |   ansible.builtin.shell: |
   59 |     set -o pipefail
   60 |     export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
   61 |     curl -fsSL "https://raw.githubusercontent.com/nvm-sh/nvm/{{ nvm_latest_release }}/install.sh" | bash
   62 |   args:
   63 |     executable: /bin/bash
   64 |   when: 
   65 |     - nvm_latest_release is defined
   66 |     - current_nvm_version.stdout == "not-installed" or current_nvm_version.stdout != nvm_latest_release
   67 |   register: nvm_install_result
   68 | 
   69 | - name: "NVM | Resolve installed Node.js version"
   70 |   ansible.builtin.shell: |
   71 |     export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
   72 |     [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
   73 |     remote_version="$(nvm version-remote "{{ nvm_node_version }}" 2>/dev/null || true)"
   74 |     if [ -n "$remote_version" ] && [ "$remote_version" != "N/A" ]; then
   75 |       printf '%s\n' "$remote_version"
   76 |     else
   77 |       local_version="$(nvm version "{{ nvm_node_version }}" 2>/dev/null || true)"
   78 |       if [ -n "$local_version" ] && [ "$local_version" != "N/A" ]; then
   79 |         printf '%s\n' "$local_version"
   80 |       else
   81 |         echo "not-installed"
   82 |       fi
   83 |     fi
   84 |   args:
   85 |     executable: /bin/bash
   86 |   register: node_version_normalized
   87 |   changed_when: false
   88 |   when:
   89 |     - nvm_latest_release is defined
   90 |     - current_nvm_version.stdout != "not-installed" or nvm_install_result is changed
   91 | 
   92 | - name: "NVM | Check if Node.js version is already installed"
   93 |   ansible.builtin.stat:
   94 |     path: "{{ ansible_facts['env']['HOME'] }}/.nvm/versions/node/{{ node_version_normalized.stdout }}"
   95 |   register: node_version_installed
   96 |   when: node_version_normalized is not skipped
   97 | 
   98 | - name: "NVM | Install Node.js version"
   99 |   ansible.builtin.shell: |
  100 |     export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
  101 |     [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  102 |     nvm install {{ nvm_node_version }}
  103 |   args:
  104 |     executable: /bin/bash
  105 |   when: 
  106 |     - node_version_normalized is not skipped
  107 |     - not (node_version_installed.stat.exists | default(false))
  108 |   register: node_install_result
  109 |   changed_when: "'is already installed' not in node_install_result.stdout"
  110 | 
  111 | - name: "NVM | Check current default Node.js version"
  112 |   ansible.builtin.shell: |
  113 |     export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
  114 |     if [ -r "$NVM_DIR/alias/default" ]; then
  115 |       IFS= read -r default_alias < "$NVM_DIR/alias/default"
  116 |       printf '%s\n' "$default_alias"
  117 |     else
  118 |       echo "none"
  119 |     fi
  120 |   args:
  121 |     executable: /bin/bash
  122 |   register: current_default_node
  123 |   changed_when: false
  124 |   when: nvm_set_default | bool
  125 | 
  126 | - name: "NVM | Set default Node.js version"
  127 |   ansible.builtin.shell: |
  128 |     export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
  129 |     [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  130 |     nvm alias default {{ nvm_node_version }}
  131 |   args:
  132 |     executable: /bin/bash
  133 |   when: 
  134 |     - nvm_set_default | bool
  135 |     - current_default_node is not skipped
  136 |     - current_default_node.stdout != nvm_node_version
  137 |   register: set_default_result
  138 |   changed_when: true
  139 | 
  140 | - name: "NVM | Verify Node.js installation"
  141 |   ansible.builtin.shell: |
  142 |     export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
  143 |     [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  144 |     echo "Node: $(node --version 2>/dev/null || echo 'not found')"
  145 |     echo "npm: $(npm --version 2>/dev/null || echo 'not found')"
  146 |     echo "nvm: $(nvm --version 2>/dev/null || echo 'not found')"
  147 |   args:
  148 |     executable: /bin/bash
  149 |   register: version_check
  150 |   changed_when: false
  151 |   check_mode: false
  152 | 
  153 | - name: "NVM | Display installation info"
  154 |   ansible.builtin.debug:
  155 |     msg: |
  156 |       NVM installation complete:
  157 |       {{ version_check.stdout }}
  158 |       Changes made: {{ (nvm_install_result is changed) or (node_install_result is changed) or (set_default_result is changed) }}
```
