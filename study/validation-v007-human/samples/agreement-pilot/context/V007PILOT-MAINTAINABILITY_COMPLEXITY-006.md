# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-006

- Repository: `wonderbird/ansible-all-my-things`
- Commit: `4993019d9dfb175eef6cb40fce4ea56138e6a374`
- Family: Maintainability/complexity
- Rule: `ansibleguard/incomplete-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `playbooks/update-versions/query-versions.yml` (reported anchor line 294)
- Object: `source_location` `9cbe600bf2dde91d993b06729c4dba66daac533abf8563c1fa92e724a35b8e88`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–426 of 426:

```text
    1 | #SPDX-License-Identifier: MIT-0
    2 | ---
    3 | - name: Query upstream versions for tracked tools
    4 |   hosts: localhost
    5 |   gather_facts: false
    6 |   vars:
    7 |     _roles_dir: "{{ playbook_dir }}/../../roles"
    8 |   tasks:
    9 |     # --- Read current pins from role defaults ---
   10 |     - name: Read flutter role defaults
   11 |       ansible.builtin.slurp:
   12 |         src: "{{ _roles_dir }}/flutter/defaults/main.yml"
   13 |       register: _flutter_defaults_raw
   14 | 
   15 |     - name: Read tmux role defaults
   16 |       ansible.builtin.slurp:
   17 |         src: "{{ _roles_dir }}/tmux/defaults/main.yml"
   18 |       register: _tmux_defaults_raw
   19 | 
   20 |     - name: Read nerd_font role defaults
   21 |       ansible.builtin.slurp:
   22 |         src: "{{ _roles_dir }}/nerd_font/defaults/main.yml"
   23 |       register: _nerd_font_defaults_raw
   24 | 
   25 |     - name: Read android_studio role defaults
   26 |       ansible.builtin.slurp:
   27 |         src: "{{ _roles_dir }}/android_studio/defaults/main.yml"
   28 |       register: _android_defaults_raw
   29 | 
   30 |     - name: Read java role defaults
   31 |       ansible.builtin.slurp:
   32 |         src: "{{ _roles_dir }}/java/defaults/main.yml"
   33 |       register: _java_defaults_raw
   34 | 
   35 |     - name: Read dolt_sql_server role defaults
   36 |       ansible.builtin.slurp:
   37 |         src: "{{ _roles_dir }}/dolt_sql_server/defaults/main.yml"
   38 |       register: _dolt_defaults_raw
   39 | 
   40 |     - name: Read opencode role defaults
   41 |       ansible.builtin.slurp:
   42 |         src: "{{ _roles_dir }}/opencode/defaults/main.yml"
   43 |       register: _opencode_defaults_raw
   44 | 
   45 |     - name: Read github_cli role defaults
   46 |       ansible.builtin.slurp:
   47 |         src: "{{ _roles_dir }}/github_cli/defaults/main.yml"
   48 |       register: _github_cli_defaults_raw
   49 | 
   50 |     - name: Read obsidian role defaults
   51 |       ansible.builtin.slurp:
   52 |         src: "{{ _roles_dir }}/obsidian/defaults/main.yml"
   53 |       register: _obsidian_defaults_raw
   54 | 
   55 |     - name: Read rtk role defaults
   56 |       ansible.builtin.slurp:
   57 |         src: "{{ _roles_dir }}/rtk/defaults/main.yml"
   58 |       register: _rtk_defaults_raw
   59 | 
   60 |     - name: Read beads_go role defaults
   61 |       ansible.builtin.slurp:
   62 |         src: "{{ _roles_dir }}/beads_go/defaults/main.yml"
   63 |       register: _beads_go_defaults_raw
   64 | 
   65 |     - name: Read beads_viewer role defaults
   66 |       ansible.builtin.slurp:
   67 |         src: "{{ _roles_dir }}/beads_viewer/defaults/main.yml"
   68 |       register: _beads_viewer_defaults_raw
   69 | 
   70 |     - name: Read beads_rust role defaults
   71 |       ansible.builtin.slurp:
   72 |         src: "{{ _roles_dir }}/beads_rust/defaults/main.yml"
   73 |       register: _beads_rust_defaults_raw
   74 | 
   75 |     - name: Read nodejs role defaults
   76 |       ansible.builtin.slurp:
   77 |         src: "{{ _roles_dir }}/nodejs/defaults/main.yml"
   78 |       register: _nodejs_defaults_raw
   79 | 
   80 |     - name: Read specify_cli role defaults
   81 |       ansible.builtin.slurp:
   82 |         src: "{{ _roles_dir }}/specify_cli/defaults/main.yml"
   83 |       register: _specify_cli_defaults_raw
   84 | 
   85 |     - name: Read claude_code role defaults
   86 |       ansible.builtin.slurp:
   87 |         src: "{{ _roles_dir }}/claude_code/defaults/main.yml"
   88 |       register: _claude_code_defaults_raw
   89 | 
   90 |     - name: Extract current pinned values from role defaults
   91 |       vars:
   92 |         _java_id_match: >-
   93 |           {{ _java_defaults_raw.content | b64decode
   94 |              | regex_search('java_sdkman_identifier:\s*"([^"]+)"', '\1')
   95 |              | default([], true) }}
   96 |       ansible.builtin.set_fact:
   97 |         current_flutter_version: >-
   98 |           {{ _flutter_defaults_raw.content | b64decode
   99 |              | regex_search('flutter_version:\s*"([^"]+)"', '\1')
  100 |              | default([], true) | first }}
  101 |         current_tmux_gitmux_version: >-
  102 |           {{ _tmux_defaults_raw.content | b64decode
  103 |              | regex_search('tmux_gitmux_version:\s*"([^"]+)"', '\1')
  104 |              | default([], true) | first }}
  105 |         current_nerd_font_version: >-
  106 |           {{ _nerd_font_defaults_raw.content | b64decode
  107 |              | regex_search('nerd_font_version:\s*"([^"]+)"', '\1')
  108 |              | default([], true) | first }}
  109 |         current_android_build: >-
  110 |           {{ _android_defaults_raw.content | b64decode
  111 |              | regex_search('android_cmdlinetools_build:\s*"([^"]+)"', '\1')
  112 |              | default([], true) | first }}
  113 |         current_java_identifier: "{{ _java_id_match | first }}"
  114 |         _current_java_major: "{{ (_java_id_match | first).split('.')[0] | int }}"
  115 |         current_dolt_version: >-
  116 |           {{ _dolt_defaults_raw.content | b64decode
  117 |              | regex_search('dolt_version:\s*"([^"]+)"', '\1')
  118 |              | default([], true) | first }}
  119 |         current_opencode_version: >-
  120 |           {{ _opencode_defaults_raw.content | b64decode
  121 |              | regex_search('opencode_version:\s*"([^"]+)"', '\1')
  122 |              | default([], true) | first }}
  123 |         current_github_cli_version: >-
  124 |           {{ _github_cli_defaults_raw.content | b64decode
  125 |              | regex_search('github_cli_version:\s*"([^"]+)"', '\1')
  126 |              | default([], true) | first }}
  127 |         current_obsidian_version: >-
  128 |           {{ _obsidian_defaults_raw.content | b64decode
  129 |              | regex_search('obsidian_version:\s*"([^"]+)"', '\1')
  130 |              | default([], true) | first }}
  131 |         current_rtk_version: >-
  132 |           {{ _rtk_defaults_raw.content | b64decode
  133 |              | regex_search('rtk_version:\s*"([^"]+)"', '\1')
  134 |              | default([], true) | first }}
  135 |         current_beads_go_version: >-
  136 |           {{ _beads_go_defaults_raw.content | b64decode
  137 |              | regex_search('beads_go_version:\s*"([^"]+)"', '\1')
  138 |              | default([], true) | first }}
  139 |         current_beads_viewer_version: >-
  140 |           {{ _beads_viewer_defaults_raw.content | b64decode
  141 |              | regex_search('beads_viewer_version:\s*"([^"]+)"', '\1')
  142 |              | default([], true) | first }}
  143 |         current_beads_rust_version: >-
  144 |           {{ _beads_rust_defaults_raw.content | b64decode
  145 |              | regex_search('beads_rust_version:\s*"([^"]+)"', '\1')
  146 |              | default([], true) | first }}
  147 |         current_node_version: >-
  148 |           {{ _nodejs_defaults_raw.content | b64decode
  149 |              | regex_search('node_version:\s*"([^"]+)"', '\1')
  150 |              | default([], true) | first }}
  151 |         current_specify_cli_version: >-
  152 |           {{ _specify_cli_defaults_raw.content | b64decode
  153 |              | regex_search('specify_cli_version:\s*"([^"]+)"', '\1')
  154 |              | default([], true) | first }}
  155 |         current_claude_code_version: >-
  156 |           {{ _claude_code_defaults_raw.content | b64decode
  157 |              | regex_search('claude_code_version:\s*"([^"]+)"', '\1')
  158 |              | default([], true) | first }}
  159 | 
  160 |     # --- Fetch upstream versions ---
  161 |     - name: Fetch Flutter upstream version
  162 |       ansible.builtin.include_tasks: tasks/fetch-flutter-version.yml
  163 | 
  164 |     - name: Fetch gitmux upstream version
  165 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  166 |       vars:
  167 |         github_repo: "arl/gitmux"
  168 | 
  169 |     - name: Save gitmux fetched tag
  170 |       ansible.builtin.set_fact:
  171 |         fetched_gitmux_tag: "{{ fetched_github_tag }}"
  172 | 
  173 |     - name: Fetch Nerd Fonts (Hack) upstream version
  174 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  175 |       vars:
  176 |         github_repo: "ryanoasis/nerd-fonts"
  177 | 
  178 |     - name: Save Nerd Fonts fetched tag
  179 |       ansible.builtin.set_fact:
  180 |         fetched_font_tag: "{{ fetched_github_tag }}"
  181 | 
  182 |     - name: Fetch Java upstream version for major {{ _current_java_major }}
  183 |       ansible.builtin.include_tasks: tasks/fetch-java-version.yml
  184 |       vars:
  185 |         java_sdkman_major: "{{ _current_java_major }}"
  186 | 
  187 |     - name: Fetch Android cmdline-tools upstream version
  188 |       ansible.builtin.include_tasks: tasks/fetch-android-version.yml
  189 | 
  190 |     - name: Fetch Dolt upstream version
  191 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  192 |       vars:
  193 |         github_repo: "dolthub/dolt"
  194 | 
  195 |     - name: Save Dolt fetched tag
  196 |       ansible.builtin.set_fact:
  197 |         fetched_dolt_tag: "{{ fetched_github_tag }}"
  198 | 
  199 |     - name: Fetch OpenCode upstream version
  200 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  201 |       vars:
  202 |         github_repo: "anomalyco/opencode"
  203 | 
  204 |     - name: Save OpenCode fetched tag
  205 |       ansible.builtin.set_fact:
  206 |         fetched_opencode_tag: "{{ fetched_github_tag }}"
  207 | 
  208 |     - name: Fetch GitHub CLI upstream version
  209 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  210 |       vars:
  211 |         github_repo: "cli/cli"
  212 | 
  213 |     - name: Save GitHub CLI fetched tag
  214 |       ansible.builtin.set_fact:
  215 |         fetched_github_cli_tag: "{{ fetched_github_tag }}"
  216 | 
  217 |     - name: Fetch Obsidian upstream version
  218 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  219 |       vars:
  220 |         github_repo: "obsidianmd/obsidian-releases"
  221 | 
  222 |     - name: Save Obsidian fetched tag
  223 |       ansible.builtin.set_fact:
  224 |         fetched_obsidian_tag: "{{ fetched_github_tag }}"
  225 | 
  226 |     - name: Fetch rtk upstream version
  227 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  228 |       vars:
  229 |         github_repo: "rtk-ai/rtk"
  230 | 
  231 |     - name: Save rtk fetched tag
  232 |       ansible.builtin.set_fact:
  233 |         fetched_rtk_tag: "{{ fetched_github_tag }}"
  234 | 
  235 |     - name: Fetch bd upstream version
  236 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  237 |       vars:
  238 |         github_repo: "gastownhall/beads"
  239 | 
  240 |     - name: Save bd fetched tag
  241 |       ansible.builtin.set_fact:
  242 |         fetched_beads_go_tag: "{{ fetched_github_tag }}"
  243 | 
  244 |     - name: Fetch bv upstream version
  245 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  246 |       vars:
  247 |         github_repo: "Dicklesworthstone/beads_viewer"
  248 | 
  249 |     - name: Save bv fetched tag
  250 |       ansible.builtin.set_fact:
  251 |         fetched_beads_viewer_tag: "{{ fetched_github_tag }}"
  252 | 
  253 |     - name: Fetch br upstream version
  254 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  255 |       vars:
  256 |         github_repo: "Dicklesworthstone/beads_rust"
  257 | 
  258 |     - name: Save br fetched tag
  259 |       ansible.builtin.set_fact:
  260 |         fetched_beads_rust_tag: "{{ fetched_github_tag }}"
  261 | 
  262 |     - name: Fetch Node.js upstream LTS version
  263 |       ansible.builtin.include_tasks: tasks/fetch-nodejs-version.yml
  264 | 
  265 |     - name: Fetch specify-cli upstream version
  266 |       ansible.builtin.include_tasks: tasks/fetch-github-release.yml
  267 |       vars:
  268 |         github_repo: "github/spec-kit"
  269 | 
  270 |     - name: Save specify-cli fetched tag
  271 |       ansible.builtin.set_fact:
  272 |         fetched_specify_cli_tag: "{{ fetched_github_tag }}"
  273 | 
  274 |     - name: Fetch Claude Code upstream version and checksums
  275 |       ansible.builtin.include_tasks: tasks/fetch-claude-code-version.yml
  276 | 
  277 |     # --- Compare and report ---
  278 |     - name: Report Flutter SDK version status
  279 |       ansible.builtin.debug:
  280 |         msg: >-
  281 |           Flutter SDK:
  282 |           current={{ current_flutter_version }},
  283 |           upstream={{ fetched_flutter_version }},
  284 |           status={{ 'UP TO DATE' if current_flutter_version == fetched_flutter_version else 'STALE' }}
  285 | 
  286 |     - name: Report gitmux version status
  287 |       ansible.builtin.debug:
  288 |         msg: >-
  289 |           gitmux:
  290 |           current={{ current_tmux_gitmux_version }},
  291 |           upstream={{ fetched_gitmux_tag }},
  292 |           status={{ 'UP TO DATE' if current_tmux_gitmux_version == fetched_gitmux_tag else 'STALE' }}
  293 | 
  294 |     - name: Report Nerd Fonts (Hack) version status
  295 |       ansible.builtin.debug:
  296 |         msg: >-
  297 |           Nerd Fonts (Hack):
  298 |           current={{ current_nerd_font_version }},
  299 |           upstream={{ fetched_font_tag }},
  300 |           status={{ 'UP TO DATE' if current_nerd_font_version == fetched_font_tag else 'STALE' }}
  301 | 
  302 |     - name: Report Java (Temurin) version status
  303 |       ansible.builtin.debug:
  304 |         msg: >-
  305 |           Java (Temurin):
  306 |           current={{ current_java_identifier }},
  307 |           upstream={{ fetched_java_identifier }},
  308 |           status={{ 'UP TO DATE' if current_java_identifier == fetched_java_identifier else 'STALE' }}
  309 | 
  310 |     - name: Report Android cmdline-tools version status
  311 |       ansible.builtin.debug:
  312 |         msg: >-
  313 |           Android cmdline-tools:
  314 |           current={{ current_android_build }},
  315 |           upstream={{ fetched_android_build }},
  316 |           status={{ 'UP TO DATE' if current_android_build == fetched_android_build else 'STALE' }}
  317 | 
  318 |     - name: Report Dolt version status
  319 |       ansible.builtin.debug:
  320 |         msg: >-
  321 |           Dolt:
  322 |           current={{ current_dolt_version }},
  323 |           upstream={{ fetched_dolt_tag }},
  324 |           status={{ 'UP TO DATE' if current_dolt_version == fetched_dolt_tag else 'STALE' }}
  325 | 
  326 |     - name: Report OpenCode version status
  327 |       ansible.builtin.debug:
  328 |         msg: >-
  329 |           OpenCode:
  330 |           current={{ current_opencode_version }},
  331 |           upstream={{ fetched_opencode_tag }},
  332 |           status={{ 'UP TO DATE' if current_opencode_version == fetched_opencode_tag else 'STALE' }}
  333 | 
  334 |     - name: Report GitHub CLI version status
  335 |       ansible.builtin.debug:
  336 |         msg: >-
  337 |           GitHub CLI:
  338 |           current={{ current_github_cli_version }},
  339 |           upstream={{ fetched_github_cli_tag }},
  340 |           status={{ 'UP TO DATE' if current_github_cli_version == fetched_github_cli_tag else 'STALE' }}
  341 | 
  342 |     - name: Report Obsidian version status
  343 |       ansible.builtin.debug:
  344 |         msg: >-
  345 |           Obsidian:
  346 |           current={{ current_obsidian_version }},
  347 |           upstream={{ fetched_obsidian_tag }},
  348 |           status={{ 'UP TO DATE' if current_obsidian_version == fetched_obsidian_tag else 'STALE' }}
  349 | 
  350 |     - name: Report rtk version status
  351 |       ansible.builtin.debug:
  352 |         msg: >-
  353 |           rtk:
  354 |           current={{ current_rtk_version }},
  355 |           upstream={{ fetched_rtk_tag }},
  356 |           status={{ 'UP TO DATE' if current_rtk_version == fetched_rtk_tag else 'STALE' }}
  357 | 
  358 |     - name: Report bd version status
  359 |       ansible.builtin.debug:
  360 |         msg: >-
  361 |           bd:
  362 |           current={{ current_beads_go_version }},
  363 |           upstream={{ fetched_beads_go_tag }},
  364 |           status={{ 'UP TO DATE' if current_beads_go_version == fetched_beads_go_tag else 'STALE' }}
  365 | 
  366 |     - name: Report bv version status
  367 |       ansible.builtin.debug:
  368 |         msg: >-
  369 |           bv:
  370 |           current={{ current_beads_viewer_version }},
  371 |           upstream={{ fetched_beads_viewer_tag }},
  372 |           status={{ 'UP TO DATE' if current_beads_viewer_version == fetched_beads_viewer_tag else 'STALE' }}
  373 | 
  374 |     - name: Report br version status
  375 |       ansible.builtin.debug:
  376 |         msg: >-
  377 |           br:
  378 |           current={{ current_beads_rust_version }},
  379 |           upstream={{ fetched_beads_rust_tag }},
  380 |           status={{ 'UP TO DATE' if current_beads_rust_version == fetched_beads_rust_tag else 'STALE' }}
  381 | 
  382 |     - name: Report Node.js version status
  383 |       ansible.builtin.debug:
  384 |         msg: >-
  385 |           Node.js:
  386 |           current={{ current_node_version }},
  387 |           upstream={{ fetched_nodejs_version }},
  388 |           status={{ 'UP TO DATE' if current_node_version == fetched_nodejs_version else 'STALE' }}
  389 | 
  390 |     - name: Report specify-cli version status
  391 |       ansible.builtin.debug:
  392 |         msg: >-
  393 |           specify-cli:
  394 |           current={{ current_specify_cli_version }},
  395 |           upstream={{ fetched_specify_cli_tag }},
  396 |           status={{ 'UP TO DATE' if current_specify_cli_version == fetched_specify_cli_tag else 'STALE' }}
  397 | 
  398 |     - name: Report Claude Code version status
  399 |       ansible.builtin.debug:
  400 |         msg: >-
  401 |           Claude Code:
  402 |           current={{ current_claude_code_version }},
  403 |           upstream={{ fetched_claude_code_version }},
  404 |           status={{ 'UP TO DATE' if current_claude_code_version == fetched_claude_code_version else 'STALE' }}
  405 | 
  406 |     - name: Fail if any version pins are stale
  407 |       ansible.builtin.fail:
  408 |         msg: >-
  409 |           One or more version pins are stale. Run perform-updates.yml to apply updates.
  410 |       when: >-
  411 |         current_flutter_version != fetched_flutter_version or
  412 |         current_tmux_gitmux_version != fetched_gitmux_tag or
  413 |         current_nerd_font_version != fetched_font_tag or
  414 |         current_java_identifier != fetched_java_identifier or
  415 |         current_android_build != fetched_android_build or
  416 |         current_dolt_version != fetched_dolt_tag or
  417 |         current_opencode_version != fetched_opencode_tag or
  418 |         current_github_cli_version != fetched_github_cli_tag or
  419 |         current_obsidian_version != fetched_obsidian_tag or
  420 |         current_rtk_version != fetched_rtk_tag or
  421 |         current_beads_go_version != fetched_beads_go_tag or
  422 |         current_beads_viewer_version != fetched_beads_viewer_tag or
  423 |         current_beads_rust_version != fetched_beads_rust_tag or
  424 |         current_node_version != fetched_nodejs_version or
  425 |         current_specify_cli_version != fetched_specify_cli_tag or
  426 |         current_claude_code_version != fetched_claude_code_version
```
