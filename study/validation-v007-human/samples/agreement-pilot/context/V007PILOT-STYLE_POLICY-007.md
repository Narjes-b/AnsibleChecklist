# Frozen source context: V007PILOT-STYLE_POLICY-007

- Repository: `ansible-collections/ibm_zos_core`
- Commit: `f0cc9ddc4402424c1f91d920ca9455d4133c9d21`
- Family: Style/policy
- Rule: `ansibleguard/missing-tags`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/gather_diagnostics/tasks/zos_managed.yml` (reported anchor line 362)
- Object: `task` `5f8f5ef8f449edfeb9c5f35af6c2279769101b637d653fea5fb8bde68a4eb601`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–370 of 370:

```text
    1 | # Copyright (c) IBM Corporation 2026
    2 | # Licensed under the Apache License, Version 2.0 (the "License");
    3 | # you may not use this file except in compliance with the License.
    4 | # You may obtain a copy of the License at
    5 | #     http://www.apache.org/licenses/LICENSE-2.0
    6 | # Unless required by applicable law or agreed to in writing, software
    7 | # distributed under the License is distributed on an "AS IS" BASIS,
    8 | # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    9 | # See the License for the specific language governing permissions and
   10 | # limitations under the License.
   11 | ---
   12 | - name: "Z/OS | Check ZOAU installation and version"
   13 |   ansible.builtin.command:
   14 |     cmd: "zoaversion -c"
   15 |   register: gather_diagnostics_managed_zoaversion
   16 |   changed_when: false
   17 |   ignore_errors: true
   18 | 
   19 | - name: "Z/OS | Debug: Check ZOAU installation"
   20 |   ansible.builtin.debug:
   21 |     msg: >-
   22 |       WARNING: 'zoaversion -c' command failed (rc={{ gather_diagnostics_managed_zoaversion.rc }}).
   23 |       This often means ZOAU is not installed or not in the user's PATH.
   24 |   when: gather_diagnostics_managed_zoaversion.rc | default(0) != 0
   25 | 
   26 | - name: "Z/OS | Gather Python version"
   27 |   ansible.builtin.command:
   28 |     cmd: "python3 --version"
   29 |   register: gather_diagnostics_managed_python_version
   30 |   changed_when: false
   31 |   ignore_errors: true
   32 | 
   33 | - name: "Z/OS | Debug: Check Python installation"
   34 |   ansible.builtin.debug:
   35 |     msg: >-
   36 |       WARNING: 'python3 --version' command failed (rc={{ gather_diagnostics_managed_python_version.rc }}).
   37 |       This often means Python 3 is not installed or not in the user's PATH.
   38 |   when: gather_diagnostics_managed_python_version.rc | default(0) != 0
   39 | 
   40 | - name: "Z/OS | Gather system locale"
   41 |   ansible.builtin.command:
   42 |     cmd: "locale"
   43 |   register: gather_diagnostics_managed_locale
   44 |   changed_when: false
   45 |   ignore_errors: true
   46 | 
   47 | - name: "Z/OS | Gather environment variables"
   48 |   ansible.builtin.command:
   49 |     cmd: "env"
   50 |   register: gather_diagnostics_managed_env
   51 |   changed_when: false
   52 |   ignore_errors: true
   53 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
   54 | 
   55 | - name: "Z/OS | Gather system facts"
   56 |   block:
   57 |     - name: "Z/OS | Gather Ansible facts using zos_gather_facts"
   58 |       ibm.ibm_zos_core.zos_gather_facts:
   59 |         gather_subset:
   60 |           - ipl
   61 |           - sys
   62 |           - cpu
   63 |           - iodf
   64 |       register: gather_diagnostics_zos_facts
   65 |   rescue:
   66 |     - name: "Z/OS | Fallback: Attempt to get IPL info via zinfo shell command"
   67 |       ansible.builtin.command: "zinfo -a"
   68 |       register: gather_diagnostics_zos_facts_fallback
   69 |       changed_when: false
   70 |       ignore_errors: true
   71 | 
   72 | - name: "Z/OS | List installed pip packages"
   73 |   ansible.builtin.command:
   74 |     cmd: "python3 -m pip list"
   75 |   register: gather_diagnostics_managed_pip_list
   76 |   changed_when: false
   77 |   ignore_errors: true
   78 | 
   79 | - name: "Z/OS | Gather user limits"
   80 |   ansible.builtin.command:
   81 |     cmd: "ulimit -a"
   82 |   register: gather_diagnostics_managed_ulimit
   83 |   changed_when: false
   84 |   ignore_errors: true
   85 | 
   86 | - name: "Z/OS | Gather user's OMVS segment"
   87 |   ansible.builtin.shell:
   88 |     cmd: "tsocmd \"lu $(whoami) omvs\""
   89 |   register: gather_diagnostics_managed_omvs_segment
   90 |   changed_when: false
   91 |   ignore_errors: true
   92 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
   93 | 
   94 | - name: "Z/OS | Extract paths from environment variables"
   95 |   ansible.builtin.set_fact:
   96 |     gather_diagnostics_zoau_home_path: >-
   97 |       {{ (gather_diagnostics_managed_env.stdout_lines
   98 |          | select('match', '^(ZOAU_HOME|ZOAU)=')
   99 |          | first
  100 |          | default('=not_found')
  101 |          | split('='))[1] }}
  102 |     gather_diagnostics_python_exe_path: >-
  103 |       {{ (gather_diagnostics_managed_env.stdout_lines
  104 |          | select('match', '^_=.*/v3r[0-9]{1,2}/pyz/bin/python')
  105 |          | first
  106 |          | default('=not_found')
  107 |          | split('='))[1] }}
  108 |   when: gather_diagnostics_managed_env.stdout_lines is defined
  109 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  110 | 
  111 | - name: "Z/OS | Determine Python home from executable path"
  112 |   ansible.builtin.set_fact:
  113 |     gather_diagnostics_python_home_path: "{{ (gather_diagnostics_python_exe_path | ansible.builtin.dirname) | ansible.builtin.dirname }}"
  114 |   when: gather_diagnostics_python_exe_path is defined and gather_diagnostics_python_exe_path != 'not_found'
  115 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  116 | 
  117 | - name: "Z/OS | Check ZOAU home mount status (df)"
  118 |   ansible.builtin.command:
  119 |     cmd: "df -P {{ gather_diagnostics_zoau_home_path }}"
  120 |   register: gather_diagnostics_managed_df_zoau
  121 |   changed_when: false
  122 |   ignore_errors: true
  123 |   when: gather_diagnostics_zoau_home_path is defined and gather_diagnostics_zoau_home_path != 'not_found'
  124 | 
  125 | - name: "Z/OS | Check APF bits in ZOAU bin directory"
  126 |   ansible.builtin.command:
  127 |     cmd: "ls -laE {{ gather_diagnostics_zoau_home_path }}/bin"
  128 |   register: gather_diagnostics_managed_bin_apf_bits
  129 |   changed_when: false
  130 |   ignore_errors: true
  131 |   when: gather_diagnostics_zoau_home_path is defined and gather_diagnostics_zoau_home_path != 'not_found'
  132 | 
  133 | - name: "Z/OS | Check Python home mount status (df)"
  134 |   ansible.builtin.command:
  135 |     cmd: "df -P {{ gather_diagnostics_python_home_path }}"
  136 |   register: gather_diagnostics_managed_df_python
  137 |   changed_when: false
  138 |   ignore_errors: true
  139 |   when: gather_diagnostics_python_home_path is defined and gather_diagnostics_python_home_path != 'not_found'
  140 | 
  141 | - name: "Z/OS | OPTIONAL: Gather operator command output"
  142 |   when: gather_diagnostics_gather_syslog
  143 |   block:
  144 |     - name: "Run MVS operator command 'D A,L'"
  145 |       ibm.ibm_zos_core.zos_operator:
  146 |         cmd: "D A,L"
  147 |       register: gather_diagnostics_managed_operator_output
  148 |       ignore_errors: true
  149 |       no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  150 | 
  151 |     - name: "Run MVS operator command 'D OMVS,LIMITS'"
  152 |       ibm.ibm_zos_core.zos_operator:
  153 |         cmd: "D OMVS,LIMITS"
  154 |       register: gather_diagnostics_managed_omvs_limits
  155 |       ignore_errors: true
  156 |       no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  157 | 
  158 |     - name: "Run MVS operator command 'D OMVS,OPTIONS'"
  159 |       ibm.ibm_zos_core.zos_operator:
  160 |         cmd: "D OMVS,OPTIONS"
  161 |       register: gather_diagnostics_managed_omvs_options
  162 |       ignore_errors: true
  163 |       no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  164 |   rescue:
  165 |     - name: "Note: Operator command failed"
  166 |       ansible.builtin.debug:
  167 |         msg: "The 'zos_operator' command failed. This may be due to 'gather_diagnostics_gather_syslog' being true but the user lacking operator authority."
  168 | 
  169 | - name: "Z/OS | Gather SSH configuration files"
  170 |   when: gather_diagnostics_gather_ssh_config
  171 |   block:
  172 |     - name: "Z/OS | Gather user's ~/.ssh/rc"
  173 |       ansible.builtin.command: "cat ~/.ssh/rc"
  174 |       register: gather_diagnostics_managed_ssh_rc
  175 |       changed_when: false
  176 |       ignore_errors: true
  177 |       no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  178 | 
  179 |     - name: "Z/OS | Gather system /etc/ssh/sshrc"
  180 |       ansible.builtin.command: "cat /etc/ssh/sshrc"
  181 |       register: gather_diagnostics_managed_etc_ssh_rc
  182 |       changed_when: false
  183 |       ignore_errors: true
  184 |       no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  185 | 
  186 |     - name: "Z/OS | Gather system /etc/ssh/ssh_config"
  187 |       ansible.builtin.command: "cat /etc/ssh/ssh_config"
  188 |       register: gather_diagnostics_managed_etc_ssh_config
  189 |       changed_when: false
  190 |       ignore_errors: true
  191 |       no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  192 | 
  193 |     - name: "Z/OS | Gather system /etc/ssh/sshd_config"
  194 |       ansible.builtin.command: "cat /etc/ssh/sshd_config"
  195 |       register: gather_diagnostics_managed_etc_sshd_config
  196 |       changed_when: false
  197 |       ignore_errors: true
  198 |       no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  199 | 
  200 |   rescue:
  201 |     - name: "SSH config file gathering failed"
  202 |       ansible.builtin.debug:
  203 |         msg: "The attempt to gather SSH config files failed. This may be due to permission issues or files not existing."
  204 | 
  205 | # --- DISPLAY MANAGED NODE RESULTS ---
  206 | 
  207 | - name: "Z/OS | --- RESULTS (sensitive data is hidden if gather_diagnostics_save_managed_node_log=false) ---"
  208 |   ansible.builtin.debug:
  209 |     msg: "Starting z/OS managed node diagnostics display"
  210 | 
  211 | - name: "Z/OS | ZOAU Version"
  212 |   ansible.builtin.debug:
  213 |     var: gather_diagnostics_managed_zoaversion.stdout
  214 |   when: gather_diagnostics_managed_zoaversion is defined
  215 | 
  216 | - name: "Z/OS | Python Version (stdout)"
  217 |   ansible.builtin.debug:
  218 |     var: gather_diagnostics_managed_python_version.stdout
  219 |   when: gather_diagnostics_managed_python_version is defined and gather_diagnostics_managed_python_version.stdout != ""
  220 | 
  221 | - name: "Z/OS | Python Version (stderr)"
  222 |   ansible.builtin.debug:
  223 |     var: gather_diagnostics_managed_python_version.stderr
  224 |   when: gather_diagnostics_managed_python_version is defined and gather_diagnostics_managed_python_version.stderr != ""
  225 | 
  226 | - name: "Z/OS | Locale"
  227 |   ansible.builtin.debug:
  228 |     var: gather_diagnostics_managed_locale.stdout_lines
  229 |   when: gather_diagnostics_managed_locale is defined
  230 | 
  231 | - name: "Z/OS | Environment"
  232 |   ansible.builtin.debug:
  233 |     var: gather_diagnostics_managed_env.stdout_lines
  234 |   when: gather_diagnostics_managed_env is defined
  235 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  236 | 
  237 | - name: "Z/OS | Core Facts"
  238 |   ansible.builtin.debug:
  239 |     var: gather_diagnostics_zos_facts.ansible_facts
  240 |   when: gather_diagnostics_zos_facts is defined and gather_diagnostics_zos_facts.ansible_facts is defined
  241 | 
  242 | - name: "Z/OS | Core Facts (Fallback)"
  243 |   ansible.builtin.debug:
  244 |     var: gather_diagnostics_zos_facts_fallback.stdout_lines
  245 |   when: gather_diagnostics_zos_facts_fallback is defined
  246 | 
  247 | - name: "Z/OS | Pip List"
  248 |   ansible.builtin.debug:
  249 |     var: gather_diagnostics_managed_pip_list.stdout_lines
  250 |   when: gather_diagnostics_managed_pip_list is defined
  251 | 
  252 | - name: "Z/OS | User Limits"
  253 |   ansible.builtin.debug:
  254 |     var: gather_diagnostics_managed_ulimit.stdout_lines
  255 |   when: gather_diagnostics_managed_ulimit is defined
  256 | 
  257 | - name: "Z/OS | OMVS Segment"
  258 |   ansible.builtin.debug:
  259 |     var: gather_diagnostics_managed_omvs_segment.stdout_lines
  260 |   when: gather_diagnostics_managed_omvs_segment is defined
  261 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  262 | 
  263 | - name: "Z/OS | ZOAU Path Mount Status"
  264 |   ansible.builtin.debug:
  265 |     var: gather_diagnostics_managed_df_zoau.stdout_lines
  266 |   when: gather_diagnostics_managed_df_zoau is defined and gather_diagnostics_managed_df_zoau.stdout_lines is defined
  267 | 
  268 | - name: "Z/OS | ZOAU apf attributes"
  269 |   ansible.builtin.debug:
  270 |     var: gather_diagnostics_managed_bin_apf_bits.stdout_lines
  271 |   when: gather_diagnostics_managed_bin_apf_bits is defined and gather_diagnostics_managed_bin_apf_bits.stdout_lines is defined
  272 | 
  273 | - name: "Z/OS | Python Path Mount Status"
  274 |   ansible.builtin.debug:
  275 |     var: gather_diagnostics_managed_df_python.stdout_lines
  276 |   when: gather_diagnostics_managed_df_python is defined and gather_diagnostics_managed_df_python.stdout_lines is defined
  277 | 
  278 | - name: "Z/OS | Operator Output (D A,L)"
  279 |   ansible.builtin.debug:
  280 |     var: gather_diagnostics_managed_operator_output.content
  281 |   when: gather_diagnostics_managed_operator_output is defined and gather_diagnostics_managed_operator_output.content is defined
  282 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  283 | 
  284 | - name: "Z/OS | Operator Output (D OMVS,LIMITS)"
  285 |   ansible.builtin.debug:
  286 |     var: gather_diagnostics_managed_omvs_limits.content
  287 |   when: gather_diagnostics_managed_omvs_limits is defined and gather_diagnostics_managed_omvs_limits.content is defined
  288 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  289 | 
  290 | - name: "Z/OS | Operator Output (D OMVS,OPTIONS)"
  291 |   ansible.builtin.debug:
  292 |     var: gather_diagnostics_managed_omvs_options.content
  293 |   when: gather_diagnostics_managed_omvs_options is defined and gather_diagnostics_managed_omvs_options.content is defined
  294 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  295 | 
  296 | - name: "Z/OS | User ~/.ssh/rc"
  297 |   ansible.builtin.debug:
  298 |     var: gather_diagnostics_managed_ssh_rc.stdout_lines
  299 |   when: gather_diagnostics_gather_ssh_config and gather_diagnostics_managed_ssh_rc is defined and gather_diagnostics_managed_ssh_rc.rc is defined
  300 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  301 | 
  302 | - name: "Z/OS | System /etc/ssh/sshrc"
  303 |   ansible.builtin.debug:
  304 |     var: gather_diagnostics_managed_etc_ssh_rc.stdout_lines
  305 |   when: gather_diagnostics_gather_ssh_config and gather_diagnostics_managed_etc_ssh_rc is defined and gather_diagnostics_managed_etc_ssh_rc.rc is defined
  306 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  307 | 
  308 | - name: "Z/OS | System /etc/ssh/ssh_config"
  309 |   ansible.builtin.debug:
  310 |     var: gather_diagnostics_managed_etc_ssh_config.stdout_lines
  311 |   when: >-
  312 |     gather_diagnostics_gather_ssh_config and
  313 |     gather_diagnostics_managed_etc_ssh_config is defined and
  314 |     gather_diagnostics_managed_etc_ssh_config.rc is defined
  315 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  316 | 
  317 | - name: "Z/OS | System /etc/ssh/sshd_config"
  318 |   ansible.builtin.debug:
  319 |     var: gather_diagnostics_managed_etc_sshd_config.stdout_lines
  320 |   when: >-
  321 |     gather_diagnostics_gather_ssh_config and
  322 |     gather_diagnostics_managed_etc_sshd_config is defined and
  323 |     gather_diagnostics_managed_etc_sshd_config.rc is defined
  324 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  325 | 
  326 | - name: "Z/OS | Consolidate all results into one variable"
  327 |   ansible.builtin.set_fact:
  328 |     gather_diagnostics_managed_results:
  329 |       zoau_version: "{{ gather_diagnostics_managed_zoaversion.stdout | default('N/A') }}"
  330 |       zoau_version_stderr: "{{ gather_diagnostics_managed_zoaversion.stderr | default('N/A') }}"
  331 |       python_version: "{{ gather_diagnostics_managed_python_version.stdout | default('N/A') }}"
  332 |       python_version_stderr: "{{ gather_diagnostics_managed_python_version.stderr | default('N/A') }}"
  333 |       locale: "{{ gather_diagnostics_managed_locale.stdout_lines | default('N/A') }}"
  334 |       environment: "{{ gather_diagnostics_managed_env.stdout_lines | default('N/A') }}"
  335 |       zos_facts: "{{ gather_diagnostics_zos_facts.ansible_facts | default('N/A') }}"
  336 |       zos_facts_fallback: "{{ gather_diagnostics_zos_facts_fallback.stdout_lines | default('N/A') }}"
  337 |       pip_list: "{{ gather_diagnostics_managed_pip_list.stdout_lines | default('N/A') }}"
  338 |       user_limits: "{{ gather_diagnostics_managed_ulimit.stdout_lines | default('N/A') }}"
  339 |       omvs_segment: "{{ gather_diagnostics_managed_omvs_segment.stdout_lines | default('N/A') }}"
  340 |       df_zoau_path: "{{ gather_diagnostics_managed_df_zoau.stdout_lines | default('N/A') }}"
  341 |       zoau_bin_attributes: "{{ gather_diagnostics_managed_bin_apf_bits.stdout_lines | default('N/A') }}"
  342 |       df_python_path: "{{ gather_diagnostics_managed_df_python.stdout_lines | default('N/A') }}"
  343 |       operator_d_a_l: "{{ gather_diagnostics_managed_operator_output.content | default('N/A', true) }}"
  344 |       operator_d_omvs_limits: "{{ gather_diagnostics_managed_omvs_limits.content | default('N/A', true) }}"
  345 |       operator_d_omvs_options: "{{ gather_diagnostics_managed_omvs_options.content | default('N/A', true) }}"
  346 |       ssh_rc_content: "{{ gather_diagnostics_managed_ssh_rc.stdout_lines | default('N/A', true) }}"
  347 |       etc_ssh_rc_content: "{{ gather_diagnostics_managed_etc_ssh_rc.stdout_lines | default('N/A', true) }}"
  348 |       etc_ssh_config_content: "{{ gather_diagnostics_managed_etc_ssh_config.stdout_lines | default('N/A', true) }}"
  349 |       etc_sshd_config_content: "{{ gather_diagnostics_managed_etc_sshd_config.stdout_lines | default('N/A', true) }}"
  350 |   no_log: "{{ not gather_diagnostics_save_managed_node_log }}"
  351 | 
  352 | - name: "Z/OS | Ensure output directory exists on control node"
  353 |   ansible.builtin.file:
  354 |     path: "{{ gather_diagnostics_output_dir }}"
  355 |     state: directory
  356 |     mode: '0755'
  357 |   delegate_to: localhost
  358 |   vars:
  359 |     ansible_python_interpreter: "{{ ansible_playbook_python }}"
  360 |   when: gather_diagnostics_managed_results is defined and gather_diagnostics_save_managed_node_log
  361 | 
  362 | - name: "Z/OS | Save managed node results to a YAML file on the control node"
  363 |   ansible.builtin.copy:
  364 |     dest: "{{ gather_diagnostics_output_dir }}/gather_diagnostics_report_managed_node_{{ inventory_hostname }}.yml"
  365 |     content: "{{ gather_diagnostics_managed_results | to_nice_yaml }}"
  366 |     mode: '0644'
  367 |   delegate_to: localhost
  368 |   vars:
  369 |     ansible_python_interpreter: "{{ ansible_playbook_python }}"
  370 |   when: gather_diagnostics_managed_results is defined and gather_diagnostics_save_managed_node_log
```
