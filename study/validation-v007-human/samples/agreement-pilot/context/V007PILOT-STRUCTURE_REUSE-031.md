# Frozen source context: V007PILOT-STRUCTURE_REUSE-031

- Repository: `TechDufus/dotfiles`
- Commit: `abe3beabdf436c1a7aeeff66b6c2f5903f7b9878`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/npm/tasks/Ubuntu.yml` (reported anchor line 1)
- Object: `source_location` `0e707dad3acf5427e46697093ca572c8ff3f573773f8464a1861ace4b93de4af`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–326 of 326:

```text
    1 | ---
    2 | # NPM/Node.js installation with nvm detection and user-local fallback for Ubuntu/Debian
    3 | 
    4 | - name: "NPM | {{ ansible_facts['distribution'] }} | Check for nvm installation"
    5 |   ansible.builtin.stat:
    6 |     path: "{{ ansible_facts['env']['HOME'] }}/.nvm/nvm.sh"
    7 |   register: nvm_check
    8 | 
    9 | - name: "NPM | {{ ansible_facts['distribution'] }} | Determine Node.js source"
   10 |   ansible.builtin.set_fact:
   11 |     use_nvm: "{{ (npm_node_source == 'nvm') or (npm_node_source == 'auto' and nvm_check.stat.exists) }}"
   12 |     require_nvm: "{{ npm_node_source == 'nvm' }}"
   13 | 
   14 | - name: "NPM | {{ ansible_facts['distribution'] }} | Fail if nvm required but not found"
   15 |   ansible.builtin.fail:
   16 |     msg: "nvm is required but not installed. Please run the nvm role first."
   17 |   when:
   18 |     - require_nvm
   19 |     - not nvm_check.stat.exists
   20 | 
   21 | # NVM-based installation
   22 | - name: "NPM | {{ ansible_facts['distribution'] }} | Configure npm via nvm"
   23 |   when: use_nvm
   24 |   block:
   25 |     - name: "NPM | Check Node.js installation via nvm"
   26 |       ansible.builtin.shell: |
   27 |         export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
   28 |         [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
   29 |         node --version 2>/dev/null || echo "not-installed"
   30 |       args:
   31 |         executable: /bin/bash
   32 |       register: nvm_node_check
   33 |       changed_when: false
   34 | 
   35 |     - name: "NPM | Display nvm Node.js status"
   36 |       ansible.builtin.debug:
   37 |         msg: "Node.js via nvm: {{ nvm_node_check.stdout }}"
   38 | 
   39 |     - name: "NPM | Check current npm version"
   40 |       ansible.builtin.shell: |
   41 |         export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
   42 |         [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
   43 |         npm --version 2>/dev/null || echo "not-installed"
   44 |       args:
   45 |         executable: /bin/bash
   46 |       register: current_npm_version
   47 |       changed_when: false
   48 |       when: nvm_node_check.stdout != 'not-installed'
   49 | 
   50 |     - name: "NPM | Get latest npm version"
   51 |       ansible.builtin.shell: |
   52 |         export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
   53 |         [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
   54 |         npm view npm version 2>/dev/null || echo "unknown"
   55 |       args:
   56 |         executable: /bin/bash
   57 |       register: latest_npm_version
   58 |       changed_when: false
   59 |       when:
   60 |         - npm_update_npm
   61 |         - nvm_node_check.stdout != 'not-installed'
   62 | 
   63 |     - name: "NPM | Update npm to latest version (nvm)"
   64 |       ansible.builtin.shell: |
   65 |         export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
   66 |         [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
   67 |         npm install -g npm@latest
   68 |       args:
   69 |         executable: /bin/bash
   70 |       when:
   71 |         - npm_update_npm
   72 |         - nvm_node_check.stdout != 'not-installed'
   73 |         - current_npm_version.stdout != latest_npm_version.stdout
   74 |       register: npm_update_result
   75 |       changed_when: current_npm_version.stdout != latest_npm_version.stdout
   76 | 
   77 | # System/Direct installation
   78 | - name: "NPM | {{ ansible_facts['distribution'] }} | System/Direct installation"
   79 |   when: not use_nvm
   80 |   block:
   81 |     - name: "NPM | Get latest STABLE NodeJS version"
   82 |       ansible.builtin.shell:
   83 |         cmd: curl -sL https://nodejs.org/dist/index.json | jq -r '.[] | select(.lts) | .version' | head -n 1
   84 |       register: nodejs_latest_version
   85 |       changed_when: false
   86 | 
   87 |     - name: "NPM | Check if NodeJS is installed"
   88 |       ansible.builtin.command: node --version
   89 |       register: nodejs_installed
   90 |       failed_when: false
   91 |       changed_when: false
   92 | 
   93 |     - name: "NPM | Show NodeJS versions"
   94 |       ansible.builtin.debug:
   95 |         msg:
   96 |           - "Current NodeJS: {{ nodejs_installed.stdout if nodejs_installed.rc == 0 else 'Not installed' }}"
   97 |           - "Latest LTS: {{ nodejs_latest_version.stdout }}"
   98 |           - "Installation needed: {{ nodejs_installed.rc != 0 or nodejs_installed.stdout != nodejs_latest_version.stdout }}"
   99 | 
  100 |           - ""
  101 | 
  102 |           - "# System-wide installation with sudo"
  103 |     - name: "NPM | System installation"
  104 |       when:
  105 |         - can_install_packages | default(false)
  106 |         - nodejs_installed.rc != 0 or nodejs_installed.stdout != nodejs_latest_version.stdout
  107 |       become: true
  108 |       block:
  109 |         - name: "NPM | Get System Arch"
  110 |           ansible.builtin.set_fact:
  111 |             nodejs_arch: "{{ ansible_facts['machine'] | replace('x86_64', 'x64') | replace('aarch64', 'arm64') }}"
  112 | 
  113 |         - name: "NPM | Register Package Name"
  114 |           ansible.builtin.set_fact:
  115 |             nodejs_package_name: "node-{{ nodejs_latest_version.stdout }}-{{ ansible_facts['system'] | lower }}-{{ nodejs_arch }}"
  116 | 
  117 |         - name: "NPM | Download NodeJS"
  118 |           ansible.builtin.get_url:
  119 |             url: "https://nodejs.org/dist/{{ nodejs_latest_version.stdout }}/{{ nodejs_package_name }}.tar.xz"
  120 |             dest: /tmp/{{ nodejs_package_name }}.tar.xz
  121 |             mode: "0644"
  122 | 
  123 |         - name: "NPM | Extract and install NodeJS (system-wide)"
  124 |           ansible.builtin.unarchive:
  125 |             src: /tmp/{{ nodejs_package_name }}.tar.xz
  126 |             dest: /usr/local
  127 |             remote_src: true
  128 |             extra_opts: "--strip-components=1"
  129 |           register: npm_system_install
  130 | 
  131 |     # User-local installation without sudo
  132 |     - name: "NPM | User-local installation"
  133 |       when:
  134 |         - not (can_install_packages | default(false))
  135 |         - nodejs_installed.rc != 0 or nodejs_installed.stdout != nodejs_latest_version.stdout
  136 |       block:
  137 |         - name: "NPM | Create local directories"
  138 |           ansible.builtin.file:
  139 |             path: "{{ item }}"
  140 |             state: directory
  141 |             mode: '0755'
  142 |           loop:
  143 |             - "{{ ansible_facts['env']['HOME'] }}/.local"
  144 |             - "{{ ansible_facts['env']['HOME'] }}/.local/bin"
  145 |             - "{{ ansible_facts['env']['HOME'] }}/.local/lib"
  146 |             - "{{ ansible_facts['env']['HOME'] }}/.npm-global"
  147 | 
  148 |         - name: "NPM | Get System Arch"
  149 |           ansible.builtin.set_fact:
  150 |             nodejs_arch: "{{ ansible_facts['machine'] | replace('x86_64', 'x64') | replace('aarch64', 'arm64') }}"
  151 | 
  152 |         - name: "NPM | Register Package Name"
  153 |           ansible.builtin.set_fact:
  154 |             nodejs_package_name: "node-{{ nodejs_latest_version.stdout }}-{{ ansible_facts['system'] | lower }}-{{ nodejs_arch }}"
  155 | 
  156 |         - name: "NPM | Download NodeJS"
  157 |           ansible.builtin.get_url:
  158 |             url: "https://nodejs.org/dist/{{ nodejs_latest_version.stdout }}/{{ nodejs_package_name }}.tar.xz"
  159 |             dest: /tmp/{{ nodejs_package_name }}.tar.xz
  160 |             mode: "0644"
  161 | 
  162 |         - name: "NPM | Extract NodeJS to user directory"
  163 |           ansible.builtin.unarchive:
  164 |             src: /tmp/{{ nodejs_package_name }}.tar.xz
  165 |             dest: "{{ ansible_facts['env']['HOME'] }}/.local"
  166 |             remote_src: true
  167 |             extra_opts: "--strip-components=1"
  168 |           register: npm_user_install
  169 | 
  170 |         - name: "NPM | Configure npm for user-local packages"
  171 |           ansible.builtin.shell: |
  172 |             export PATH="${HOME}/.local/bin:${PATH}"
  173 |             npm config set prefix '{{ ansible_facts['env']['HOME'] }}/.npm-global'
  174 |           args:
  175 |             executable: /bin/bash
  176 |           when: npm_user_install is succeeded
  177 | 
  178 | # Configure NPM (common for all installation methods)
  179 | - name: "NPM | {{ ansible_facts['distribution'] }} | Configure NPM"
  180 |   block:
  181 |     - name: "NPM | Check global package directory setting"
  182 |       ansible.builtin.shell: |
  183 |         {% if use_nvm %}
  184 |         export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
  185 |         [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  186 |         {% endif %}
  187 |         npm config get prefix 2>/dev/null || echo ""
  188 |       args:
  189 |         executable: /bin/bash
  190 |       register: npm_prefix_current
  191 |       changed_when: false
  192 |       when:
  193 |         - not (can_install_packages | default(false))
  194 |         - not use_nvm
  195 | 
  196 |     - name: "NPM | Set global package directory for non-sudo"
  197 |       ansible.builtin.command: npm config set prefix '{{ ansible_facts['env']['HOME'] }}/.npm-global'
  198 |       when: 
  199 |         - not (can_install_packages | default(false))
  200 |         - not use_nvm
  201 |         - npm_prefix_current.stdout != (ansible_facts['env']['HOME'] + '/.npm-global')
  202 |       changed_when: true
  203 | 
  204 |     - name: "NPM | Check and apply npm configuration settings"
  205 |       ansible.builtin.shell: |
  206 |         {% if use_nvm %}
  207 |         export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
  208 |         [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  209 |         {% endif %}
  210 |         current_value=$(npm config get {{ item.key }} 2>/dev/null || echo "undefined")
  211 |         if [ "$current_value" != "{{ item.value }}" ]; then
  212 |           npm config set {{ item.key }} '{{ item.value }}'
  213 |           echo "changed"
  214 |         else
  215 |           echo "unchanged"
  216 |         fi
  217 |       args:
  218 |         executable: /bin/bash
  219 |       register: npm_config_result
  220 |       changed_when: "'changed' in npm_config_result.stdout"
  221 |       loop: "{{ npm_config | dict2items }}"
  222 |       when: npm_config is defined
  223 | 
  224 |     - name: "NPM | Ensure .npmrc file with proper configuration"
  225 |       ansible.builtin.template:
  226 |         src: npmrc.j2
  227 |         dest: "{{ ansible_facts['env']['HOME'] }}/.npmrc"
  228 |         mode: '0644'
  229 |         backup: yes
  230 | 
  231 | # Install global packages
  232 | - name: "NPM | {{ ansible_facts['distribution'] }} | Install global packages"
  233 |   block:
  234 |     - name: "NPM | Combine package lists"
  235 |       ansible.builtin.set_fact:
  236 |         all_npm_packages: "{{ npm_global_packages + (npm_extra_packages | default([])) }}"
  237 | 
  238 |     - name: "NPM | Get list of installed global packages"
  239 |       ansible.builtin.shell: |
  240 |         {% if use_nvm %}
  241 |         export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
  242 |         [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  243 |         {% else %}
  244 |         export PATH="${HOME}/.local/bin:${HOME}/.npm-global/bin:${PATH}"
  245 |         {% endif %}
  246 |         npm list -g --depth=0 --json 2>/dev/null | jq -r '.dependencies | keys[]' 2>/dev/null || echo ""
  247 |       args:
  248 |         executable: /bin/bash
  249 |       register: installed_global_packages
  250 |       changed_when: false
  251 | 
  252 |     - name: "NPM | Install missing global packages (nvm)"
  253 |       ansible.builtin.shell: |
  254 |         export NVM_DIR="{{ ansible_facts['env']['HOME'] }}/.nvm"
  255 |         [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  256 |         if echo "{{ installed_global_packages.stdout_lines | join(' ') }}" | grep -qw "{{ item }}"; then
  257 |           echo "already installed"
  258 |         else
  259 |           npm install -g {{ item }}
  260 |           echo "installed"
  261 |         fi
  262 |       args:
  263 |         executable: /bin/bash
  264 |       loop: "{{ all_npm_packages }}"
  265 |       when: use_nvm
  266 |       register: nvm_install_result
  267 |       changed_when: "'already installed' not in nvm_install_result.stdout"
  268 |       loop_control:
  269 |         label: "{{ item }}"
  270 | 
  271 |     - name: "NPM | Install missing global packages (system with sudo)"
  272 |       ansible.builtin.shell: |
  273 |         if npm list -g --depth=0 {{ item }} >/dev/null 2>&1; then
  274 |           echo "already installed"
  275 |         else
  276 |           npm install -g {{ item }}
  277 |           echo "installed"
  278 |         fi
  279 |       loop: "{{ all_npm_packages }}"
  280 |       when: 
  281 |         - not use_nvm
  282 |         - can_install_packages | default(false)
  283 |       become: true
  284 |       register: system_install_result
  285 |       changed_when: "'already installed' not in system_install_result.stdout"
  286 | 
  287 |     - name: "NPM | Install missing global packages (user-local)"
  288 |       ansible.builtin.shell: |
  289 |         export PATH="${HOME}/.local/bin:${HOME}/.npm-global/bin:${PATH}"
  290 |         if npm list -g --depth=0 {{ item }} >/dev/null 2>&1; then
  291 |           echo "already installed"
  292 |         else
  293 |           npm install -g {{ item }}
  294 |           echo "installed"
  295 |         fi
  296 |       args:
  297 |         executable: /bin/bash
  298 |       loop: "{{ all_npm_packages }}"
  299 |       when: 
  300 |         - not use_nvm
  301 |         - not (can_install_packages | default(false))
  302 |       register: user_install_result
  303 |       changed_when: "'already installed' not in user_install_result.stdout"
  304 | 
  305 | # Report installation status
  306 | - name: "NPM | {{ ansible_facts['distribution'] }} | Report installation status"
  307 |   ansible.builtin.debug:
  308 |     msg: |
  309 |       NPM/Node.js installation status:
  310 |       - Installation method: {{ 'nvm' if use_nvm else ('system-wide' if can_install_packages else 'user-local') }}
  311 |       - Node.js installed: {{ '✓' if (use_nvm and nvm_node_check.stdout != 'not-installed') or (not use_nvm and nodejs_installed.rc == 0) else '✗' }}
  312 |       {% if use_nvm %}
  313 |       - Using nvm for Node.js management
  314 |       - Run 'nvm list' to see installed versions
  315 |       {% else %}
  316 |       - NPM prefix: {{ '~/.npm-global' if not can_install_packages else '/usr/local (system-wide)' }}
  317 |       {% endif %}
  318 |       - Global packages configured: {{ all_npm_packages | join(', ') }}
  319 |       - Global packages installed: {{ installed_global_packages.stdout_lines | join(', ') if installed_global_packages.stdout_lines else 'None' }}
  320 |       
  321 |       {% if not can_install_packages and not use_nvm %}
  322 |       ⚠️  User-local installation notes:
  323 |       1. Add to your PATH: export PATH='${HOME}/.local/bin:${HOME}/.npm-global/bin:${PATH}'
  324 |       2. Global packages will be installed to: ~/.npm-global
  325 |       3. This is already configured in your shell if using the zsh role
  326 |       {% endif %}
```

## Frozen tracked paths in the relevant role/scope

```text
roles/npm/README.md
roles/npm/defaults/main.yml
roles/npm/handlers/main.yml
roles/npm/tasks/Archlinux.yml
roles/npm/tasks/Fedora.yml
roles/npm/tasks/MacOSX.yml
roles/npm/tasks/Ubuntu.yml
roles/npm/tasks/main.yml
roles/npm/tasks/update.yml
roles/npm/templates/npmrc.j2
roles/npm/uninstall.sh
```
