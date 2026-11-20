# Frozen source context: V007PILOT-STRUCTURE_REUSE-033

- Repository: `adoptium/infrastructure`
- Commit: `d31f47293b3a0166a4f9d7b8c51475d548999408`
- Family: Structure/reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/MacOSX.yml` (reported anchor line 1)
- Object: `source_location` `5d654d3c4159656331a29abd871af0f77cab246610875c207426ba2d56416527`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–276 of 276:

```text
    1 | ---
    2 | 
    3 | #
    4 | # Updates all packages for macos-based distributions
    5 | #
    6 | 
    7 | # Issue https://github.com/adoptium/infrastructure/issues/1902
    8 | - name: Ensure ansible version is greater than 2.11
    9 |   fail:
   10 |     msg: "The version of Ansible you are using needs to be greater than 2.11"
   11 |   when: ansible_version.full is version('2.11', '<=')
   12 | 
   13 | - name: Get macOS version
   14 |   shell: sw_vers -productVersion
   15 |   register: macos_version
   16 |   changed_when: false
   17 | 
   18 | - name: Set macos version
   19 |   set_fact:
   20 |     macos_version_number: "{{ macos_version.stdout.split('.')[0] }}.{{ macos_version.stdout.split('.')[1] }}"
   21 | 
   22 | - name: Display macOS Version
   23 |   debug:
   24 |     var: macos_version_number
   25 | 
   26 | - name: Set homebrew path (x64)
   27 |   set_fact:
   28 |     homebrew_path: /usr/local/bin
   29 |   when: ansible_architecture == "x86_64"
   30 | 
   31 | - name: Set homebrew path (Arm64)
   32 |   set_fact:
   33 |     homebrew_path: /opt/homebrew/bin
   34 |   when: ansible_architecture == "arm64"
   35 | 
   36 | - name: Configure system-wide Bash profile
   37 |   become: true
   38 |   copy:
   39 |     src: files/macos/profile
   40 |     dest: /etc/profile
   41 |     owner: root
   42 |     group: wheel
   43 | 
   44 | - name: Ensure that directory for system-wide profile extensions is present
   45 |   become: true
   46 |   file:
   47 |     path: /etc/profile.d
   48 |     owner: root
   49 |     group: wheel
   50 |     state: directory
   51 | 
   52 | # Skipping linting as no situation where this can't run (lint error 301)
   53 | - name: Check for xcode-tools
   54 |   raw: xcode-select --print-path &> /dev/null
   55 |   register: xcode
   56 |   failed_when: false
   57 |   tags:
   58 |     - skip_ansible_lint
   59 | 
   60 | # Currently required to install packages. This can be removed once it installs on arm64
   61 | - name: Install Rosetta 2
   62 |   command: /usr/sbin/softwareupdate --install-rosetta --agree-to-license
   63 |   when:
   64 |     - ansible_architecture == "arm64"
   65 |   tags:
   66 |     - rosetta
   67 | 
   68 | - name: Check if Homebrew is already installed
   69 |   stat:
   70 |     path: "{{ homebrew_path }}/brew"
   71 |   register: brew
   72 | 
   73 | - name: Install Homebrew
   74 |   become: true
   75 |   become_user: "{{ ansible_user }}"
   76 |   script: scripts/install-homebrew.sh
   77 |   when: not brew.stat.exists
   78 | 
   79 | - name: Switch back to command line tools xcode before proceeding
   80 |   command: sudo xcode-select --switch /
   81 |   tags: adoptopenjdk
   82 | 
   83 | - name: Upgrade installed packages
   84 |   become: true
   85 |   become_user: "{{ ansible_user }}"
   86 |   homebrew:
   87 |     upgrade_all: yes
   88 |     path: "{{ homebrew_path }}"
   89 |   when: "macos_version_number is version('10.15', '>')"
   90 |   tags:
   91 |     - brew_upgrade
   92 | 
   93 | - name: Install brew cu
   94 |   become: true
   95 |   become_user: "{{ ansible_user }}"
   96 |   homebrew_tap:
   97 |     name: buo/cask-upgrade
   98 |     path: "{{ homebrew_path }}"
   99 |   tags:
  100 |     - brew_cu
  101 | 
  102 | # Skipping linting as no situation where this can't run (lint error 301)
  103 | - name: Update Casks
  104 |   become: true
  105 |   become_user: "{{ ansible_user }}"
  106 |   command: "{{ homebrew_path }}/brew cu -y"
  107 |   tags:
  108 |     - brew_cu
  109 |     - skip_ansible_lint
  110 | 
  111 | - name: Install Build Tool Packages
  112 |   become: true
  113 |   become_user: "{{ ansible_user }}"
  114 |   homebrew:
  115 |     name: "{{ Build_Tool_Packages }}"
  116 |     state: present
  117 |     path: "{{ homebrew_path }}"
  118 |   tags: build_tools
  119 | 
  120 | # Install CMAKE Where It Doesn't exist
  121 | - name: Check if cmake is installed in /opt/homebrew/bin
  122 |   stat:
  123 |     path: /opt/homebrew/bin/cmake
  124 |   register: cmake_homebrew
  125 | 
  126 | - name: Check if cmake is installed in /usr/local/bin
  127 |   stat:
  128 |     path: /usr/local/bin/cmake
  129 |   register: cmake_local
  130 | 
  131 | - name: Install Cmake
  132 |   become: true
  133 |   become_user: "{{ ansible_user }}"
  134 |   homebrew:
  135 |     name: "cmake"
  136 |     state: present
  137 |   tags: build_tools
  138 |   when: not (cmake_homebrew.stat.exists or cmake_local.stat.exists)
  139 | 
  140 | - name: Install Build Tool Packages NOT MacOS 14 arm64
  141 |   become: true
  142 |   become_user: "{{ ansible_user }}"
  143 |   homebrew:
  144 |     name: "{{ Build_Tool_Packages_Not_MacOS14_arm64 }}"
  145 |     state: present
  146 |     path: "{{ homebrew_path }}"
  147 |   when: not ((macos_version_number | regex_search("14")) and ansible_architecture == "arm64")
  148 |   tags: build_tools
  149 | 
  150 | - name: Install Build Tool Packages NOT macOS 10.12
  151 |   become: true
  152 |   become_user: "{{ ansible_user }}"
  153 |   homebrew:
  154 |     name: "{{ Build_Tool_Packages_NOT_10_12 }}"
  155 |     state: present
  156 |     path: "{{ homebrew_path }}"
  157 |   when:
  158 |     - not (macos_version_number | regex_search("10.12"))
  159 |   tags: build_tools
  160 | 
  161 | - name: Install Build Tool Casks
  162 |   become: true
  163 |   become_user: "{{ ansible_user }}"
  164 |   homebrew_cask:
  165 |     name: "{{ Build_Tool_Casks }}"
  166 |     state: present
  167 |     path: "{{ homebrew_path }}"
  168 |   tags: build_tools
  169 | 
  170 | - name: Install Test Tool Packages
  171 |   become: true
  172 |   become_user: "{{ ansible_user }}"
  173 |   homebrew:
  174 |     name: "{{ Test_Tool_Packages }}"
  175 |     state: present
  176 |     path: "{{ homebrew_path }}"
  177 |   tags: test_tools
  178 | 
  179 | - name: Install JCK Tool Casks
  180 |   become: true
  181 |   become_user: "{{ ansible_user }}"
  182 |   homebrew_cask:
  183 |     name: "{{ JCK_Tool_Casks }}"
  184 |     state: present
  185 |     path: "{{ homebrew_path }}"
  186 |   tags: jck_tools
  187 | 
  188 | # Used for JCK printer tests
  189 | - name: Check if PDFwriter is installed
  190 |   stat:
  191 |     path: /Users/Shared/PDFwriter
  192 |   register: pdfwriter
  193 |   tags: jck_tools
  194 | 
  195 | - name: Download PDFwriter
  196 |   command: wget https://github.com/rodyager/RWTS-PDFwriter/releases/download/v1.0.1/RWTS-PDFwriter.pkg
  197 |   when: not pdfwriter.stat.exists
  198 |   tags: jck_tools
  199 | 
  200 | - name: Install PDFwriter
  201 |   command: installer -pkg ./RWTS-PDFwriter.pkg -target /
  202 |   when: not pdfwriter.stat.exists
  203 |   tags: jck_tools
  204 | 
  205 | # As per https://github.com/eclipse/openj9/issues/3790
  206 | - name: Creating /etc/sysctl.conf for kernel tunings
  207 |   file:
  208 |     path: /etc/sysctl.conf
  209 |     state: touch
  210 |     mode: 0644
  211 |     owner: root
  212 |     group: wheel
  213 |   tags:
  214 |     - kernel_tuning
  215 | 
  216 | - name: Writing kernel tuning parameters to /etc/sysctl.conf
  217 |   blockinfile:
  218 |     path: /etc/sysctl.conf
  219 |     block: |
  220 |       kern.sysv.shmmax=125839605760
  221 |       kern.sysv.shmall=30722560
  222 |   register: kernel
  223 |   tags:
  224 |     - kernel_tuning
  225 | 
  226 | - name: Allow staff users to generate core dumps
  227 |   file:
  228 |     path: /cores
  229 |     state: directory
  230 |     mode: 0774
  231 |     owner: root
  232 |     group: staff
  233 |   tags:
  234 |     - core_dumps
  235 | 
  236 | - name: Create limit.core.plist file in /Library/LaunchDaemons
  237 |   copy:
  238 |     dest: /Library/LaunchDaemons/limit.core.plist
  239 |     owner: root
  240 |     group: wheel
  241 |     mode: 0644
  242 |     content: |
  243 |       <?xml version="1.0" encoding="UTF-8"?>
  244 |       <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  245 |       "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
  246 |       <plist version="1.0">
  247 |       <dict>
  248 |       <key>Label</key>
  249 |       <string>limit.core</string>
  250 |       <key>ProgramArguments</key>
  251 |       <array>
  252 |       <string>launchctl</string>
  253 |       <string>limit</string>
  254 |       <string>core</string>
  255 |       <string>8388608</string>
  256 |       <string>8388608</string>
  257 |       </array>
  258 |       <key>RunAtLoad</key>
  259 |       <true/>
  260 |       <key>ServiceIPC</key>
  261 |       <false/>
  262 |       </dict>
  263 |       </plist>
  264 |   become: true
  265 | 
  266 | - name: Load limit.core.plist file with launchctl
  267 |   command: sudo launchctl load -w /Library/LaunchDaemons/limit.core.plist
  268 | 
  269 | # Skipping linting as not to introduce handlers into task-only playbooks (lint error 503)
  270 | - name: Reboot macOS after tweaking kernel tuning parameters
  271 |   reboot:
  272 |     reboot_timeout: 3600
  273 |   when: kernel.changed
  274 |   tags:
  275 |     - kernel_tuning
  276 |     - skip_ansible_lint
```

## Frozen tracked paths in the relevant role/scope

```text
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/files/macos/profile
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/scripts/install-homebrew.sh
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/Alpine.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/CentOS.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/Debian.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/Fedora.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/FreeBSD.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/MacOSX.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/RedHat.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/SLES.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/Ubuntu.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/build_packages_and_tools.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/main.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/tasks/openSUSE.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/Alpine.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/CentOS.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/Debian.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/Fedora.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/FreeBSD.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/MacOSX.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/RedHat.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/SLES.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/Ubuntu.yml
ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/Common/vars/openSUSE.yml
```
