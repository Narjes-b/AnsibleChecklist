# Frozen source context: V007PILOT2-STYLE_POLICY-016

- Repository: `TechDufus/dotfiles`
- Commit: `abe3beabdf436c1a7aeeff66b6c2f5903f7b9878`
- Family: style_policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/github_release/tasks/find_asset.yml` (reported anchor line 16)
- Flagged construct: task `github release | {{ github_release_binary_name }} | fail if no matching asset found`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–135 of 135:

```text
    1 | ---
    2 | # Find matching asset from release
    3 | 
    4 | - name: "GitHub Release | {{ github_release_binary_name }} | Use provided asset name pattern if specified"
    5 |   when: github_release_asset_name_pattern != ""
    6 |   block:
    7 |     - name: "GitHub Release | {{ github_release_binary_name }} | Find asset by pattern"
    8 |       ansible.builtin.set_fact:
    9 |         _github_release_matching_assets: >-
   10 |           {{
   11 |             _github_release.assets |
   12 |             selectattr('name', 'match', github_release_asset_name_pattern) |
   13 |             list
   14 |           }}
   15 | 
   16 |     - name: "GitHub Release | {{ github_release_binary_name }} | Fail if no matching asset found"
   17 |       when: _github_release_matching_assets | length == 0
   18 |       ansible.builtin.fail:
   19 |         msg: "No asset matching pattern '{{ github_release_asset_name_pattern }}' found in release"
   20 | 
   21 |     - name: "GitHub Release | {{ github_release_binary_name }} | Select first matching asset"
   22 |       ansible.builtin.set_fact:
   23 |         _github_release_asset: "{{ _github_release_matching_assets[0] }}"
   24 | 
   25 | - name: "GitHub Release | {{ github_release_binary_name }} | Auto-detect asset based on OS and architecture"
   26 |   when: github_release_asset_name_pattern == ""
   27 |   block:
   28 |     - name: "GitHub Release | {{ github_release_binary_name }} | Build OS patterns"
   29 |       ansible.builtin.set_fact:
   30 |         _github_os_patterns: "{{ github_release_os_map[github_release_os] | default([github_release_os]) }}"
   31 | 
   32 |     - name: "GitHub Release | {{ github_release_binary_name }} | Build architecture patterns"
   33 |       ansible.builtin.set_fact:
   34 |         _github_arch_patterns: "{{ github_release_arch_map[github_release_arch] | default([github_release_arch]) }}"
   35 | 
   36 |     - name: "GitHub Release | {{ github_release_binary_name }} | Find assets matching OS and architecture"
   37 |       ansible.builtin.set_fact:
   38 |         _github_release_candidate_assets: >-
   39 |           {{
   40 |             _github_release.assets |
   41 |             selectattr('name', 'search', '(' + _github_os_patterns | join('|') + ')') |
   42 |             selectattr('name', 'search', '(' + _github_arch_patterns | join('|') + ')') |
   43 |             list
   44 |           }}
   45 | 
   46 |     - name: "GitHub Release | {{ github_release_binary_name }} | Handle no matching assets"
   47 |       when: _github_release_candidate_assets | length == 0
   48 |       block:
   49 |         - name: "GitHub Release | {{ github_release_binary_name }} | Try binary name only"
   50 |           ansible.builtin.set_fact:
   51 |             _github_release_candidate_assets: >-
   52 |               {{
   53 |                 _github_release.assets |
   54 |                 selectattr('name', 'match', '^' + github_release_binary_name + '$') |
   55 |                 list
   56 |               }}
   57 | 
   58 |         - name: "GitHub Release | {{ github_release_binary_name }} | Fail if still no matches"
   59 |           when: _github_release_candidate_assets | length == 0
   60 |           ansible.builtin.fail:
   61 |             msg: >
   62 |               No assets found matching OS '{{ github_release_os }}' and architecture '{{ github_release_arch }}'.
   63 |               Available assets: {{ _github_release.assets | map(attribute='name') | join(', ') }}
   64 | 
   65 |     - name: Prefer specific asset types
   66 |       when: github_release_asset_type == "auto"
   67 |       block:
   68 |         - name: Check for tar.gz
   69 |           ansible.builtin.set_fact:
   70 |             _github_release_asset: "{{ _github_release_candidate_assets | selectattr('name', 'match', '.*\\.tar\\.gz$') | list | first | default(None) }}"
   71 | 
   72 |         - name: Check for zip if no tar.gz
   73 |           when: _github_release_asset is none
   74 |           ansible.builtin.set_fact:
   75 |             _github_release_asset: "{{ _github_release_candidate_assets | selectattr('name', 'match', '.*\\.zip$') | list | first | default(None) }}"
   76 | 
   77 |         - name: Check for deb if no archives
   78 |           when: _github_release_asset is none and github_release_os == "linux"
   79 |           ansible.builtin.set_fact:
   80 |             _github_release_asset: "{{ _github_release_candidate_assets | selectattr('name', 'match', '.*\\.deb$') | list | first | default(None) }}"
   81 | 
   82 |         - name: Check for AppImage if no other formats
   83 |           when: _github_release_asset is none and github_release_os == "linux"
   84 |           ansible.builtin.set_fact:
   85 |             _github_release_asset: "{{ _github_release_candidate_assets | selectattr('name', 'match', '.*\\.AppImage$') | list | first | default(None) }}"
   86 | 
   87 |         - name: Use first candidate if no preferred type
   88 |           when: _github_release_asset is none
   89 |           ansible.builtin.set_fact:
   90 |             _github_release_asset: "{{ _github_release_candidate_assets[0] }}"
   91 | 
   92 |     - name: Select asset by specific type
   93 |       when: github_release_asset_type != "auto"
   94 |       block:
   95 |         - name: Find asset by type
   96 |           ansible.builtin.set_fact:
   97 |             _github_release_typed_assets: >-
   98 |               {{
   99 |                 _github_release_candidate_assets |
  100 |                 selectattr('name', 'match', '.*\\.' + github_release_asset_type + '$') |
  101 |                 list
  102 |               }}
  103 | 
  104 |         - name: Fail if type not found
  105 |           when: _github_release_typed_assets | length == 0
  106 |           ansible.builtin.fail:
  107 |             msg: "No {{ github_release_asset_type }} asset found for {{ github_release_os }}/{{ github_release_arch }}"
  108 | 
  109 |         - name: Use typed asset
  110 |           ansible.builtin.set_fact:
  111 |             _github_release_asset: "{{ _github_release_typed_assets[0] }}"
  112 | 
  113 | - name: "GitHub Release | {{ github_release_binary_name }} | Set asset details"
  114 |   ansible.builtin.set_fact:
  115 |     _github_release_asset_name: "{{ _github_release_asset.name }}"
  116 |     _github_release_asset_url: "{{ _github_release_asset.browser_download_url }}"
  117 | 
  118 | - name: "GitHub Release | {{ github_release_binary_name }} | Determine asset type"
  119 |   ansible.builtin.set_fact:
  120 |     _github_release_asset_type: >-
  121 |       {%- if _github_release_asset_name.endswith('.tar.gz') -%}tar.gz
  122 |       {%- elif _github_release_asset_name.endswith('.tar.bz2') or _github_release_asset_name.endswith('.tbz') -%}tar.bz2
  123 |       {%- elif _github_release_asset_name.endswith('.zip') -%}zip
  124 |       {%- elif _github_release_asset_name.endswith('.deb') -%}deb
  125 |       {%- elif _github_release_asset_name.endswith('.rpm') -%}rpm
  126 |       {%- elif _github_release_asset_name.endswith('.AppImage') -%}AppImage
  127 |       {%- else -%}binary
  128 |       {%- endif -%}
  129 | 
  130 | - name: "GitHub Release | {{ github_release_binary_name }} | Display selected asset"
  131 |   ansible.builtin.debug:
  132 |     msg:
  133 |       - "Selected asset: {{ _github_release_asset_name }}"
  134 |       - "Asset type: {{ _github_release_asset_type }}"
  135 |       - "Download URL: {{ _github_release_asset_url }}"
```
