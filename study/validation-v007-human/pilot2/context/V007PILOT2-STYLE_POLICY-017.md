# Frozen source context: V007PILOT2-STYLE_POLICY-017

- Repository: `cfpb/aurora`
- Commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Family: style_policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `deploy/deploy_research_environment.yml` (reported anchor line 110)
- Flagged construct: not named by the finding; the anchor line 110 lies in the task at line 110, name `{{ item }}`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–187 of 187:

```text
    1 | ---
    2 | - hosts: research_environment
    3 |   become: yes
    4 |   become_method: sudo
    5 |   roles:
    6 |     - {role: iptables, when: "iptables_config"}
    7 |     - common
    8 |     - {role: epel, when: "use_epel and not 'production' in group_names"}
    9 |     - emacs
   10 |     - jdk
   11 |     - odbc
   12 |     - postgresql-client
   13 |   post_tasks:
   14 |     - name: research eod symlinks
   15 |       file:
   16 |          src: "{{ item.src }}"
   17 |          dest: "{{ item.dest }}"
   18 |       with_items: "{{ eod_symlinks }}"
   19 | 
   20 |     - name: Install xauth dependency
   21 |       yum:
   22 |         name: xorg-x11-xauth
   23 |         state: present
   24 | 
   25 |     - name: Ensure X11 Forwarding is present
   26 |       lineinfile:
   27 |         dest: /etc/ssh/sshd_config
   28 |         regexp: ^\s*X11Forwarding\s*no
   29 |         line: X11Forwarding yes
   30 |       when: not custom_repo
   31 | 
   32 |     - name: Ensure ClientAliveCountMax is set to correct value
   33 |       lineinfile:
   34 |         dest: /etc/ssh/sshd_config
   35 |         regexp: ^\s*ClientAliveCountMax\s*[0-9]+
   36 |         line: ClientAliveCountMax 384
   37 |       when: not custom_repo
   38 | 
   39 |     - name: Ensure run level 5
   40 |       lineinfile:
   41 |         dest: /etc/inittab
   42 |         regexp: initdefault
   43 |         line: "id:5:initdefault:"
   44 | 
   45 |     - name: research printers symlinks
   46 |       file:
   47 |         state: link
   48 |         src: "{{ item.src }}"
   49 |         dest: "{{ item.dest }}"
   50 |       with_items: "{{ printers_symlinks }}"
   51 | 
   52 |     - name: Install git
   53 |       yum:
   54 |         name: git
   55 |         state: present
   56 | 
   57 | - hosts: research_ancillary_services
   58 |   become: yes
   59 |   become_method: sudo
   60 |   roles:
   61 |     - umask
   62 |     - devtools
   63 |     - open_office
   64 |     - evince
   65 |     - stattransfer
   66 |     - sublime
   67 |     - ultra-edit
   68 |   post_tasks:
   69 |     - name: Install texlive
   70 |       yum:
   71 |         name: texlive
   72 |         state: present
   73 | 
   74 | - hosts: research_eod
   75 |   become: yes
   76 |   become_method: sudo
   77 |   pre_tasks:
   78 |     - name: Stop EOD
   79 |       service:
   80 |         name: "otecs_13.8"
   81 |         state: stopped
   82 |       when: eod_upgrade is defined and eod_upgrade
   83 | 
   84 | - hosts: research_eod
   85 |   become: yes
   86 |   become_method: sudo
   87 |   serial: 1
   88 |   roles:
   89 |     - eod
   90 | 
   91 | - hosts: research_gauss
   92 |   become: yes
   93 |   become_method: sudo
   94 |   roles:
   95 |     # - gauss
   96 |     - stata
   97 |     - gocd
   98 |     - stattransfer
   99 |     - math_lm
  100 |     - r
  101 | 
  102 | - hosts: research_stata
  103 |   become: yes
  104 |   become_method: sudo
  105 |   roles:
  106 |     - stata
  107 |     - stattransfer
  108 |     - r
  109 | 
  110 | - hosts: research_python
  111 |   become: yes
  112 |   become_method: sudo
  113 |   roles:
  114 |     - devtools
  115 |     - devtools6
  116 |     - {role: python, when: "custom_repo"}
  117 |     #- {role: python-build, when: "not custom_repo"}
  118 |     - {role: python27-scl, when: "not custom_repo"}
  119 |     - python36-scl
  120 |     - python-libs
  121 |     - postgresql-client
  122 |     - r-core
  123 |     - r-libs
  124 |     - r-studio-desktop
  125 |     - r-studio-server
  126 |     - r-studio-server-config
  127 |     - pycharm
  128 |     - gocd
  129 |     - stattransfer
  130 | 
  131 |   post_tasks:
  132 |     - name: Install Gnome-Terminal package
  133 |       yum:
  134 |         name: "{{ item }}"
  135 |         state: present
  136 |         disable_gpg_check: yes
  137 |       with_items:
  138 |         - gnome-terminal
  139 | 
  140 |     - name: Install texlive
  141 |       yum:
  142 |         name: texlive
  143 |         state: present
  144 | 
  145 | - hosts: research_sas
  146 |   become: yes
  147 |   become_method: sudo
  148 |   roles:
  149 |     - sas
  150 |     - gocd
  151 |     - stattransfer
  152 |     - r
  153 | 
  154 | - hosts: research_spss
  155 |   become: yes
  156 |   become_method: sudo
  157 |   roles:
  158 |     # - spss
  159 |     - gocd
  160 |     - stattransfer
  161 | 
  162 | - hosts: research_matlab
  163 |   become: yes
  164 |   become_method: sudo
  165 |   roles:
  166 |     - matlab
  167 |     - gocd
  168 |     - stattransfer
  169 | 
  170 |   tasks:
  171 |   - name: Install libselinux-python and libicu package
  172 |     yum:
  173 |       name: "{{ item }}"
  174 |       state: present
  175 |       disable_gpg_check: yes
  176 |     with_items:
  177 |       - libicu
  178 |       - libselinux-python
  179 | 
  180 |   - name: Install git
  181 |     yum:
  182 |       name: "{{ item }}"
  183 |       state: present
  184 |       disable_gpg_check: yes
  185 |     with_items:
  186 |       - libicu
  187 |       - libselinux-python
```
