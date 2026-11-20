# Frozen source context: V007PILOT2-STYLE_POLICY-022

- Repository: `adoptium/infrastructure`
- Commit: `d31f47293b3a0166a4f9d7b8c51475d548999408`
- Family: style_policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `ansible/playbooks/AdoptOpenJDK_AIX_Playbook/roles/dnf/tasks/main.yml` (reported anchor line 129)
- Flagged construct: task `install cmake 3.14.3 (see https://github.com/adoptopenjdk/openjdk-build/issues/2492)`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–199 of 199:

```text
    1 | ---
    2 | 
    3 | # See https://github.com/adoptium/infrastructure/issues/3142#issuecomment-1658743632
    4 | # Yum is no longer supported on AIX 7.3. Dnf is recommended. Dnf supports AIX 7.1 TL3 and higher
    5 | # Dnf needs python3
    6 | # For more information https://community.ibm.com/community/user/power/blogs/sangamesh-mallayya1/2021/05/28/dnf-is-now-available-on-aix-toolbox?CommunityKey=10c1d831-47ee-4d92-a138-b03f7896f7c9&tab=recentcommunityblogsdashboard
    7 | 
    8 | # Dnf needs python3
    9 | - name: Fail if python3 is not available
   10 |   stat:
   11 |     path: /opt/freeware/bin/python3
   12 |   register: python3_installed
   13 |   failed_when: not python3_installed.stat.exists
   14 | 
   15 | - name: Check if dnf is installed
   16 |   stat:
   17 |     path: /opt/freeware/bin/dnf
   18 |   register: dnf_installed
   19 | 
   20 | - name: Install dnf
   21 |   when: not dnf_installed.stat.exists
   22 |   block:
   23 |     # Installs dnf when yum is not present
   24 |     - name: Set install flag
   25 |       set_fact:
   26 |         install_flag: "-d"
   27 | 
   28 |     - name: Check if yum is installed
   29 |       stat:
   30 |         path: /opt/freeware/bin/yum
   31 |       register: yum_installed
   32 | 
   33 |     # Installs dnf when yum is present, links yum to dnf
   34 |     - name: Set install flag if yum is installed
   35 |       set_fact:
   36 |         install_flag: "-y"
   37 |       when: yum_installed.stat.exists
   38 | 
   39 |     - name: Download dnf script
   40 |       get_url:
   41 |         url: "https://public.dhe.ibm.com/aix/freeSoftware/aixtoolbox/ezinstall/ppc/dnf_aixtoolbox.sh"
   42 |         mode: 0744
   43 |         validate_certs: false
   44 |         dest: /tmp/dnf_aixtoolbox.sh
   45 |         checksum: sha256:7582a79530a30280548bebf6730686ff3c8b4b7259ddf2d1361494be19a193f8
   46 | 
   47 |     - name: Install dnf
   48 |       command: "/tmp/dnf_aixtoolbox.sh {{ install_flag }}"
   49 | 
   50 |     - name: Remove dnf script
   51 |       file:
   52 |         state: absent
   53 |         path: /tmp/dnf_aixtoolbox.sh
   54 | 
   55 | # See https://github.com/adoptium/infrastructure/pull/3271#issuecomment-1836343656
   56 | - name: Dnf module needs /opt/freeware/libexec/python3 as its ansible_python_interpreter
   57 |   vars:
   58 |     ansible_python_interpreter: /opt/freeware/libexec/python3
   59 |   block:
   60 |     # See https://github.com/adoptium/infrastructure/pull/3271#issuecomment-1836227877
   61 |     - name: Remove yum-utils before dnf update
   62 |       dnf:
   63 |         name: yum-utils
   64 |         state: absent
   65 |         use_backend: dnf
   66 | 
   67 |     - name: Update dnf
   68 |       dnf:
   69 |         update_cache: true
   70 |         name: '*'
   71 |         state: latest
   72 |         use_backend: dnf
   73 | 
   74 |     - name: Install packages
   75 |       dnf:
   76 |         state: present
   77 |         use_backend: dnf
   78 |         update_cache: yes
   79 |         disable_excludes: all
   80 |         name:
   81 |           - bash
   82 |           - autoconf-2.69-1
   83 |           - bc
   84 |           - bison
   85 |           - coreutils
   86 |           - cpio
   87 |           - cups-devel
   88 |           - cups-libs
   89 |           - expect
   90 |           - flex
   91 |           - freetype2-devel-2.8-1
   92 |           - fontconfig-devel-2.11.95
   93 |           - gawk
   94 |           - git
   95 |           # - gnupg2-2.0.30
   96 |           - grep
   97 |           - libffi-devel
   98 |           - make
   99 |           - m4
  100 |           - pcre
  101 |           - pkg-config
  102 |           - popt
  103 |           - sed
  104 |           - sudo
  105 |           - tar
  106 |           - tcl
  107 |           - unzip
  108 |           - wget
  109 |           - xz-libs
  110 |           - zip
  111 |           - zsh
  112 | 
  113 |     ##########################################################################
  114 |     # Adoptium builds do not work properly with the latest cmake @AIXToolbox #
  115 |     ##########################################################################
  116 |     # NOTE: Cannot use dnf module here as it will pull in cmake 3.16 which we do not want
  117 |     - name: Install cmake 3.14.3 prerequisites
  118 |       command:
  119 |         cmd: rpm -i "{{ item }}"
  120 |         creates: /opt/freeware/etc/rpm/macros.cmake
  121 |       with_items:
  122 |         - https://public.dhe.ibm.com/aix/freeSoftware/aixtoolbox/RPMS/ppc-7.1/cmake/cmake-filesystem-3.14.3-1.aix7.1.ppc.rpm
  123 |         - https://public.dhe.ibm.com/aix/freeSoftware/aixtoolbox/RPMS/ppc-7.1/cmake/cmake-rpm-macros-3.14.3-1.aix7.1.ppc.rpm
  124 |       tags:
  125 |         - rpm_install
  126 |         - cmake
  127 | 
  128 |     # See https://github.com/AdoptOpenJDK/openjdk-build/issues/2492 for why we are locking this
  129 |     - name: Install cmake 3.14.3 (See https://github.com/AdoptOpenJDK/openjdk-build/issues/2492)
  130 |       dnf:
  131 |         name: cmake-3.14.3
  132 |         state: present
  133 |         update_cache: yes
  134 |         disable_excludes: all
  135 |         use_backend: dnf
  136 |       tags:
  137 |         - rpm_install
  138 |         - cmake
  139 |     ##############################################################################
  140 |     # TASK [yum : Install cmake 3.14.3
  141 |     #   (See https://github.com/AdoptOpenJDK/openjdk-build/issues/2492)]
  142 |     # fatal: [x077]: FAILED! =>
  143 |     #   {"changed": false, "msg": "No package matching 'cmake-3.14.3' found available,
  144 |     #   installed or updated", "rc": 126,
  145 |     #   "results": ["No package matching 'cmake-3.14.3' found available,
  146 |     #   installed or updated"}
  147 |     ## If you get this message - you need to remove 'cmake*' from
  148 |     #   /opt/freeware/etc/yum/yum.conf
  149 |     ##############################################################################
  150 | 
  151 |     - name: Remove packages - in case installed historically, or by accident
  152 |       dnf:
  153 |         state: absent
  154 |         use_backend: dnf
  155 |         name:
  156 |           - libXrender-devel
  157 |           - libXrender
  158 |           - libXft
  159 |           - tk
  160 |           - renderproto
  161 |       tags:
  162 |         - adoptopenjdk
  163 | 
  164 | - name: Ensure perl from /opt/freeware/bin is the default in /usr/bin
  165 |   shell: mv /usr/bin/perl /usr/bin/perl.old && ln -s /opt/freeware/bin/perl /usr/bin/
  166 |   failed_when: false
  167 |   tags:
  168 |     - rpm_install
  169 | 
  170 | # Create zlib.h and zconf.h links - See https://github.com/adoptium/infrastructure/issues/1952
  171 | - name: Copy zlib.h and zconf.h (See https://github.com/adoptium/infrastructure/issues/1952)
  172 |   copy:
  173 |     src: "/opt/freeware/include/{{ item }}"
  174 |     dest: "/usr/include/"
  175 |     force: true
  176 |     remote_src: true
  177 |   with_items:
  178 |     - zconf.h
  179 |     - zlib.h
  180 | 
  181 | ##############################################################################
  182 | # Prevent accidental updates to 'locked' packages
  183 | ##############################################################################
  184 | - name: Exclude packages from dnf (main)
  185 |   lineinfile:
  186 |     dest: /opt/freeware/etc/dnf/dnf.conf
  187 |     firstmatch: true
  188 |     insertafter: 'plugins=1'
  189 |     line: 'exclude=autoconf* cmake* freetype2* fontconfig-devel*'
  190 |   tags:
  191 |     - cmake
  192 |     - freetype2
  193 | 
  194 | - name: Remove, if exists, reference to libXrender-devel include files
  195 |   file:
  196 |     state: absent
  197 |     path: /opt/freeware/include/X11/extensions
  198 |   tags:
  199 |     - adoptopenjdk
```
