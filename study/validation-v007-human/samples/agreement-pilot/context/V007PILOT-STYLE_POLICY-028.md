# Frozen source context: V007PILOT-STYLE_POLICY-028

- Repository: `UtrechtUniversity/yoda`
- Commit: `a9175010319fee30fb056665e9821937f0ec07c5`
- Family: Style/policy
- Rule: `ansibleguard/missing-tags`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/yoda_test/tasks/cleanup-data.yml` (reported anchor line 324)
- Object: `task` `6ce972d9df3346f4ef09e4c7c06076daa52f117fac8bc1f971b386423fdacd20`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–379 of 379:

```text
    1 | ---
    2 | # copyright Utrecht University
    3 | 
    4 | - name: Prepare test data research-groups for removal
    5 |   become_user: '{{ irods_service_account }}'
    6 |   become: true
    7 |   ansible.builtin.command:
    8 |     ichmod -rM own rods /{{ irods_zone }}/home/research-'{{ item.research }}'
    9 |   ignore_errors: true
   10 |   with_items:
   11 |     - "{{ deletion_research_groups }}"
   12 | 
   13 | 
   14 | - name: Prepare test data deposit-groups for removal
   15 |   become_user: '{{ irods_service_account }}'
   16 |   become: true
   17 |   ansible.builtin.command:
   18 |     ichmod -rM own rods /{{ irods_zone }}/home/deposit-'{{ item.deposit }}'
   19 |   ignore_errors: true
   20 |   with_items:
   21 |     - "{{ deletion_deposit_groups }}"
   22 | 
   23 | 
   24 | - name: Prepare test data (research) vault-groups for removal
   25 |   become_user: '{{ irods_service_account }}'
   26 |   become: true
   27 |   ansible.builtin.command:
   28 |     ichmod -rM own rods /{{ irods_zone }}/home/vault-'{{ item.research }}'
   29 |   ignore_errors: true
   30 |   with_items:
   31 |     - "{{ deletion_research_groups }}"
   32 | 
   33 | 
   34 | - name: Prepare test data (deposit) vault-groups for removal
   35 |   become_user: '{{ irods_service_account }}'
   36 |   become: true
   37 |   ansible.builtin.command:
   38 |     ichmod -rM own rods /{{ irods_zone }}/home/vault-'{{ item.deposit }}'
   39 |   ignore_errors: true
   40 |   with_items:
   41 |     - "{{ deletion_deposit_groups }}"
   42 | 
   43 | 
   44 | - name: Prepare test data datamanager-groups for removal
   45 |   become_user: '{{ irods_service_account }}'
   46 |   become: true
   47 |   ansible.builtin.command:
   48 |     ichmod -rM own rods /{{ irods_zone }}/home/datamanager-'{{ item.datamanager }}'
   49 |   ignore_errors: true
   50 |   with_items:
   51 |     - "{{ deletion_datamanager_groups }}"
   52 | 
   53 | 
   54 | - name: Prepare test data intake-groups for removal
   55 |   become_user: '{{ irods_service_account }}'
   56 |   become: true
   57 |   ansible.builtin.command:
   58 |     ichmod -rM own rods /{{ irods_zone }}/home/intake-'{{ item.intake }}'
   59 |   ignore_errors: true
   60 |   with_items:
   61 |     - "{{ deletion_intake_groups }}"
   62 | 
   63 | 
   64 | - name: Prepare test data intake-vault-groups for removal
   65 |   become_user: '{{ irods_service_account }}'
   66 |   become: true
   67 |   ansible.builtin.command:
   68 |     ichmod -rM own rods /{{ irods_zone }}/home/vault-'{{ item.intake }}'
   69 |   ignore_errors: true
   70 |   with_items:
   71 |     - "{{ deletion_intake_groups }}"
   72 | 
   73 | 
   74 | - name: Prepare test data grp-groups for removal
   75 |   become_user: '{{ irods_service_account }}'
   76 |   become: true
   77 |   ansible.builtin.command:
   78 |     ichmod -rM own rods /{{ irods_zone }}/home/grp-'{{ item.grp }}'
   79 |   ignore_errors: true
   80 |   with_items:
   81 |     - "{{ deletion_grp_groups }}"
   82 | 
   83 | 
   84 | - name: Prepare test data revisions research-groups for removal
   85 |   become_user: '{{ irods_service_account }}'
   86 |   become: true
   87 |   ansible.builtin.command:
   88 |     ichmod -rM own rods /{{ irods_zone }}/yoda/revisions/research-'{{ item.research }}'
   89 |   ignore_errors: true
   90 |   with_items:
   91 |     - "{{ deletion_research_groups }}"
   92 | 
   93 | 
   94 | - name: Prepare test data trash research-groups for removal
   95 |   become_user: '{{ irods_service_account }}'
   96 |   become: true
   97 |   ansible.builtin.command:
   98 |     ichmod -rM own rods /{{ irods_zone }}/trash/home/research-'{{ item.research }}'
   99 |   ignore_errors: true
  100 |   with_items:
  101 |     - "{{ deletion_research_groups }}"
  102 | 
  103 | 
  104 | - name: Prepare test data trash deposit-groups for removal
  105 |   become_user: '{{ irods_service_account }}'
  106 |   become: true
  107 |   ansible.builtin.command:
  108 |     ichmod -rM own rods /{{ irods_zone }}/trash/home/deposit-'{{ item.deposit }}'
  109 |   ignore_errors: true
  110 |   with_items:
  111 |     - "{{ deletion_deposit_groups }}"
  112 | 
  113 | 
  114 | - name: Prepare trash test users for removal
  115 |   become_user: '{{ irods_service_account }}'
  116 |   become: true
  117 |   ansible.builtin.command: |
  118 |     ichmod -rM own rods /{{ irods_zone }}/trash/home/'{{ item.name }}'
  119 |   ignore_errors: true
  120 |   with_items:
  121 |     - "{{ test_users + created_by_ta_users + eus_test_users }}"
  122 | 
  123 | 
  124 | - name: Remove test data research-groups
  125 |   become_user: '{{ irods_service_account }}'
  126 |   become: true
  127 |   ansible.builtin.command:
  128 |     irm -r /{{ irods_zone }}/home/research-'{{ item.research }}'
  129 |   ignore_errors: true
  130 |   with_items:
  131 |     - "{{ deletion_research_groups }}"
  132 | 
  133 | 
  134 | - name: Remove test data deposit-groups
  135 |   become_user: '{{ irods_service_account }}'
  136 |   become: true
  137 |   ansible.builtin.command:
  138 |     irm -r /{{ irods_zone }}/home/deposit-'{{ item.deposit }}'
  139 |   ignore_errors: true
  140 |   with_items:
  141 |     - "{{ deletion_deposit_groups }}"
  142 | 
  143 | 
  144 | - name: Remove test data (research) vault-groups
  145 |   become_user: '{{ irods_service_account }}'
  146 |   become: true
  147 |   ansible.builtin.command:
  148 |     irm -r /{{ irods_zone }}/home/vault-'{{ item.research }}'
  149 |   ignore_errors: true
  150 |   with_items:
  151 |     - "{{ deletion_research_groups }}"
  152 | 
  153 | 
  154 | - name: Remove test data (deposit) vault-groups
  155 |   become_user: '{{ irods_service_account }}'
  156 |   become: true
  157 |   ansible.builtin.command:
  158 |     irm -r /{{ irods_zone }}/home/vault-'{{ item.deposit }}'
  159 |   ignore_errors: true
  160 |   with_items:
  161 |     - "{{ deletion_deposit_groups }}"
  162 | 
  163 | 
  164 | - name: Remove test data datamanager-groups
  165 |   become_user: '{{ irods_service_account }}'
  166 |   become: true
  167 |   ansible.builtin.command:
  168 |     irm -r /{{ irods_zone }}/home/datamanager-'{{ item.datamanager }}'
  169 |   ignore_errors: true
  170 |   with_items:
  171 |     - "{{ deletion_datamanager_groups }}"
  172 | 
  173 | 
  174 | - name: Remove test data intake-groups
  175 |   become_user: '{{ irods_service_account }}'
  176 |   become: true
  177 |   ansible.builtin.command:
  178 |     irm -r /{{ irods_zone }}/home/intake-'{{ item.intake }}'
  179 |   ignore_errors: true
  180 |   with_items:
  181 |     - "{{ deletion_intake_groups }}"
  182 | 
  183 | 
  184 | - name: Remove test data intake-vault-groups
  185 |   become_user: '{{ irods_service_account }}'
  186 |   become: true
  187 |   ansible.builtin.command:
  188 |     irm -r /{{ irods_zone }}/home/vault-'{{ item.intake }}'
  189 |   ignore_errors: true
  190 |   with_items:
  191 |     - "{{ deletion_intake_groups }}"
  192 | 
  193 | 
  194 | - name: Remove test data grp-groups
  195 |   become_user: '{{ irods_service_account }}'
  196 |   become: true
  197 |   ansible.builtin.command:
  198 |     irm -r /{{ irods_zone }}/home/grp-'{{ item.grp }}'
  199 |   ignore_errors: true
  200 |   with_items:
  201 |     - "{{ deletion_grp_groups }}"
  202 | 
  203 | 
  204 | - name: Remove test data trash research-groups
  205 |   become_user: '{{ irods_service_account }}'
  206 |   become: true
  207 |   ansible.builtin.command:
  208 |     irm -r /{{ irods_zone }}/trash/home/research-'{{ item.research }}'
  209 |   ignore_errors: true
  210 |   with_items:
  211 |     - "{{ deletion_research_groups }}"
  212 | 
  213 | 
  214 | - name: Remove test data trash deposit-groups
  215 |   become_user: '{{ irods_service_account }}'
  216 |   become: true
  217 |   ansible.builtin.command:
  218 |     irm -r /{{ irods_zone }}/trash/home/deposit-'{{ item.deposit }}'
  219 |   ignore_errors: true
  220 |   with_items:
  221 |     - "{{ deletion_deposit_groups }}"
  222 | 
  223 | 
  224 | - name: Remove test data revisions research-groups
  225 |   become_user: '{{ irods_service_account }}'
  226 |   become: true
  227 |   ansible.builtin.command:
  228 |     irm -r /{{ irods_zone }}/yoda/revisions/research-'{{ item.research }}'
  229 |   ignore_errors: true
  230 |   with_items:
  231 |     - "{{ deletion_research_groups }}"
  232 | 
  233 | 
  234 | - name: Remove test research-groups
  235 |   become_user: '{{ irods_service_account }}'
  236 |   become: true
  237 |   ansible.builtin.command:
  238 |     iadmin rmgroup research-'{{ item.research }}'
  239 |   ignore_errors: true
  240 |   with_items:
  241 |     - "{{ deletion_research_groups }}"
  242 | 
  243 | 
  244 | - name: Remove test deposit-groups
  245 |   become_user: '{{ irods_service_account }}'
  246 |   become: true
  247 |   ansible.builtin.command:
  248 |     iadmin rmgroup deposit-'{{ item.deposit }}'
  249 |   ignore_errors: true
  250 |   with_items:
  251 |     - "{{ deletion_deposit_groups }}"
  252 | 
  253 | 
  254 | - name: Remove test (research) vault-groups
  255 |   become_user: '{{ irods_service_account }}'
  256 |   become: true
  257 |   ansible.builtin.command:
  258 |     iadmin rmgroup vault-'{{ item.research }}'
  259 |   ignore_errors: true
  260 |   with_items:
  261 |     - "{{ deletion_research_groups }}"
  262 | 
  263 | 
  264 | - name: Remove test (deposit) vault-groups
  265 |   become_user: '{{ irods_service_account }}'
  266 |   become: true
  267 |   ansible.builtin.command:
  268 |     iadmin rmgroup vault-'{{ item.deposit }}'
  269 |   ignore_errors: true
  270 |   with_items:
  271 |     - "{{ deletion_deposit_groups }}"
  272 | 
  273 | 
  274 | - name: Remove test (research) read-groups
  275 |   become_user: '{{ irods_service_account }}'
  276 |   become: true
  277 |   ansible.builtin.command:
  278 |     iadmin rmgroup read-'{{ item.research }}'
  279 |   ignore_errors: true
  280 |   with_items:
  281 |     - "{{ deletion_research_groups }}"
  282 | 
  283 | 
  284 | - name: Remove test (deposit) read-groups
  285 |   become_user: '{{ irods_service_account }}'
  286 |   become: true
  287 |   ansible.builtin.command:
  288 |     iadmin rmgroup read-'{{ item.deposit }}'
  289 |   ignore_errors: true
  290 |   with_items:
  291 |     - "{{ deletion_deposit_groups }}"
  292 | 
  293 | 
  294 | - name: Remove test intake-groups
  295 |   become_user: '{{ irods_service_account }}'
  296 |   become: true
  297 |   ansible.builtin.command:
  298 |     iadmin rmgroup intake-'{{ item.intake }}'
  299 |   ignore_errors: true
  300 |   with_items:
  301 |     - "{{ deletion_intake_groups }}"
  302 | 
  303 | 
  304 | - name: Remove test intake-vault-groups
  305 |   become_user: '{{ irods_service_account }}'
  306 |   become: true
  307 |   ansible.builtin.command:
  308 |     iadmin rmgroup vault-'{{ item.intake }}'
  309 |   ignore_errors: true
  310 |   with_items:
  311 |     - "{{ deletion_intake_groups }}"
  312 | 
  313 | 
  314 | - name: Remove test intake-read-groups
  315 |   become_user: '{{ irods_service_account }}'
  316 |   become: true
  317 |   ansible.builtin.command:
  318 |     iadmin rmgroup read-'{{ item.intake }}'
  319 |   ignore_errors: true
  320 |   with_items:
  321 |     - "{{ deletion_intake_groups }}"
  322 | 
  323 | 
  324 | - name: Remove test datamanager-groups
  325 |   become_user: '{{ irods_service_account }}'
  326 |   become: true
  327 |   ansible.builtin.command:
  328 |     iadmin rmgroup datamanager-'{{ item.datamanager }}'
  329 |   ignore_errors: true
  330 |   with_items:
  331 |     - "{{ deletion_datamanager_groups }}"
  332 | 
  333 | 
  334 | - name: Remove test grp-groups
  335 |   become_user: '{{ irods_service_account }}'
  336 |   become: true
  337 |   ansible.builtin.command:
  338 |     iadmin rmgroup grp-'{{ item.grp }}'
  339 |   ignore_errors: true
  340 |   with_items:
  341 |     - "{{ deletion_grp_groups }}"
  342 | 
  343 | 
  344 | - name: Remove trash data research-groups
  345 |   become_user: '{{ irods_service_account }}'
  346 |   become: true
  347 |   ansible.builtin.command:
  348 |     irmtrash -rM /{{ irods_zone }}/trash/home/'{{ item.research }}'
  349 |   ignore_errors: true
  350 |   with_items:
  351 |     - "{{ deletion_research_groups }}"
  352 | 
  353 | 
  354 | - name: Remove trash data deposit-groups
  355 |   become_user: '{{ irods_service_account }}'
  356 |   become: true
  357 |   ansible.builtin.command:
  358 |     irmtrash -rM /{{ irods_zone }}/trash/home/'{{ item.deposit }}'
  359 |   ignore_errors: true
  360 |   with_items:
  361 |     - "{{ deletion_deposit_groups }}"
  362 | 
  363 | 
  364 | - name: Remove test trash data user-homes
  365 |   become_user: '{{ irods_service_account }}'
  366 |   become: true
  367 |   ansible.builtin.command:
  368 |     irmtrash -rM /{{ irods_zone }}/trash/home/'{{ item.name }}'
  369 |   ignore_errors: true
  370 |   with_items:
  371 |     - '{{ test_users + created_by_ta_users + eus_test_users }}'
  372 | 
  373 | 
  374 | - name: Remove trash data rods-home
  375 |   become_user: '{{ irods_service_account }}'
  376 |   become: true
  377 |   ansible.builtin.command:
  378 |     irmtrash -rM /{{ irods_zone }}/trash/home/rods
  379 |   ignore_errors: true
```
