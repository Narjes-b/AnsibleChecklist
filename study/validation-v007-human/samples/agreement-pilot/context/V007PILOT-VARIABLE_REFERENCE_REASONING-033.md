# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-033

- Repository: `manala/ansible-roles`
- Commit: `1ae6394d7b780665788234418ace2a060903f5f1`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unscoped-shell-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/php/tasks/install.yaml` (reported anchor line 77)
- Object: `source_location` `3c5a45d6fdc4d2fe7bf792a2f98af061bcd891f76cc9b866666acb06b2a99838`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–162 of 162:

```text
    1 | ---
    2 | 
    3 | - name: Install > Packages
    4 |   ansible.builtin.apt:
    5 |     name: "{{ item.packages }}"
    6 |     state: "{{ item.state }}"
    7 |     # Present
    8 |     install_recommends: false
    9 |     update_cache: true
   10 |     cache_valid_time: 3600
   11 |     # Absent
   12 |     purge: true
   13 |     autoremove: true
   14 |   when: item.packages | length
   15 |   loop:
   16 |     # Presents
   17 |     # + Debfoster if one of exclusive mode is set
   18 |     - state: present
   19 |       packages: |
   20 |         {{
   21 |           query(
   22 |             'manala.roles.php_packages',
   23 |             (
   24 |               query(
   25 |                 'manala.roles.php_sapis',
   26 |                 manala_php_sapis | default(manala_php_sapis_default, True),
   27 |                 manala_php_sapis_available,
   28 |                 wantstate='present',
   29 |                 wantmap=true
   30 |               )
   31 |               + query(
   32 |                 'manala.roles.php_extensions',
   33 |                 manala_php_extensions,
   34 |                 manala_php_extensions_available,
   35 |                 manala_php_sapis_available,
   36 |                 wantstate='present',
   37 |                 wantmap=true
   38 |               )
   39 |             ),
   40 |             manala_php_version | string | escape
   41 |           )
   42 |           + (manala_php_sapis_exclusive or manala_php_extensions_exclusive) | ternary(['debfoster'], [])
   43 |         }}
   44 |     # Absents
   45 |     - state: absent
   46 |       packages: |
   47 |         {{
   48 |           query(
   49 |             'manala.roles.php_packages',
   50 |             (
   51 |               query(
   52 |                 'manala.roles.php_sapis',
   53 |                 manala_php_sapis | default(manala_php_sapis_default, True),
   54 |                 manala_php_sapis_available,
   55 |                 wantstate='absent',
   56 |                 wantmap=true
   57 |               )
   58 |               + query(
   59 |                 'manala.roles.php_extensions',
   60 |                 manala_php_extensions,
   61 |                 manala_php_extensions_available,
   62 |                 manala_php_sapis_available,
   63 |                 wantstate='absent',
   64 |                 wantmap=true
   65 |               )
   66 |             ),
   67 |             manala_php_version | string | escape
   68 |           )
   69 |         }}
   70 | 
   71 | - name: Install > Exclusive - Packages
   72 |   when: manala_php_sapis_exclusive
   73 |     or manala_php_extensions_exclusive
   74 |   block:
   75 | 
   76 |     # Use dpkg-query to find out installed packages
   77 |     - name: Install > Exclusive - Find packages
   78 |       ansible.builtin.command:
   79 |         cmd: >
   80 |           dpkg-query
   81 |           --showformat "${Status}    ${binary:Package}\n"
   82 |           --show "php*"
   83 |       register: __manala_php_install_packages_presents
   84 |       check_mode: false
   85 |       changed_when: false
   86 | 
   87 |     # Use debfoster to find out each package dependencies
   88 |     - name: Install > Exclusive - Find packages dependencies
   89 |       ansible.builtin.shell:  # noqa: risky-shell-pipe
   90 |         cmd: |
   91 |           for package in {{
   92 |             query(
   93 |               'manala.roles.php_packages',
   94 |               (
   95 |                 query(
   96 |                   'manala.roles.php_sapis',
   97 |                   manala_php_sapis | default(manala_php_sapis_default, True),
   98 |                   manala_php_sapis_available,
   99 |                   wantstate='present',
  100 |                   wantmap=true
  101 |                 )
  102 |                 + query(
  103 |                   'manala.roles.php_extensions',
  104 |                   manala_php_extensions,
  105 |                   manala_php_extensions_available,
  106 |                   manala_php_sapis_available,
  107 |                   wantstate='present',
  108 |                   wantmap=true
  109 |                 )
  110 |               ),
  111 |               manala_php_version | string | escape
  112 |             ) | join(' ')
  113 |           }}
  114 |           do
  115 |             debfoster --quiet --option UseRecommends=no --show-depends $package
  116 |           done
  117 |       register: __manala_php_install_packages_dependencies
  118 |       check_mode: false
  119 |       changed_when: false
  120 | 
  121 |     - name: Install > Exclusive - Packages absents
  122 |       ansible.builtin.apt:
  123 |         name: "{{ item }}"
  124 |         state: absent
  125 |         purge: true
  126 |         autoremove: true
  127 |       when: item | length
  128 |       loop:
  129 |         - |
  130 |           {{ query(
  131 |             'manala.roles.php_packages_exclusive',
  132 |             query(
  133 |               'manala.roles.php_packages',
  134 |               (
  135 |                 query(
  136 |                   'manala.roles.php_sapis',
  137 |                   manala_php_sapis | default(manala_php_sapis_default, True),
  138 |                   manala_php_sapis_available,
  139 |                   wantstate='present',
  140 |                   wantmap=true
  141 |                 )
  142 |                 + query(
  143 |                   'manala.roles.php_extensions',
  144 |                   manala_php_extensions,
  145 |                   manala_php_extensions_available,
  146 |                   manala_php_sapis_available,
  147 |                   wantstate='present',
  148 |                   wantmap=true
  149 |                 )
  150 |               ),
  151 |               manala_php_version | string | escape
  152 |             ),
  153 |             query(
  154 |               'manala.roles.php_packages',
  155 |               manala_php_sapis_available,
  156 |               manala_php_version | string | escape
  157 |             ),
  158 |             __manala_php_install_packages_presents.stdout_lines | default([]),
  159 |             __manala_php_install_packages_dependencies.stdout_lines | default([]),
  160 |             manala_php_sapis_exclusive,
  161 |             manala_php_extensions_exclusive
  162 |           ) }}
```
