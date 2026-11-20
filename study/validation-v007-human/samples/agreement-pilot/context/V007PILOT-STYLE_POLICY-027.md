# Frozen source context: V007PILOT-STYLE_POLICY-027

- Repository: `ansible-collections/azure`
- Commit: `45e49bd7cc781b6324b2c726ea5cde3cbe1d0f93`
- Family: Style/policy
- Rule: `ansibleguard/long-task-name`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/azure_arc/tasks/main.yml` (reported anchor line 141)
- Object: `task` `15e7ff58a2e630d8448a5ebc7f54f4c50b258b23157ed798f2d4cf70eb883543`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–157 of 157:

```text
    1 | ---
    2 | - name: Gather facts if not already available
    3 |   ansible.builtin.setup:
    4 |   when: ansible_system is not defined
    5 | 
    6 | - name: Set helper fact for OS type reported in logs
    7 |   ansible.builtin.set_fact:
    8 |     azure_arc_os_type: "{{ 'windows' if ansible_os_family == 'Windows' else 'linux' }}"
    9 | 
   10 | - name: Generate correlation id
   11 |   ansible.builtin.set_fact:
   12 |     azure_arc_correlation_id: "{{ (2**64) | random | to_uuid }}"
   13 | 
   14 | - name: Generate tags string
   15 |   ansible.builtin.set_fact:
   16 |     azure_arc_processed_tags: |-
   17 |       {%- for k, v in azure_arc_tags.items() %}
   18 |       {{ k | quote }}={{ v | replace(",", "\,") | quote }}{% if not loop.last %},{% endif %}
   19 |       {%- endfor %}
   20 | 
   21 | - name: Set helper fact for proxy proxy.url if needed
   22 |   when: proxy is defined
   23 |   ansible.builtin.set_fact:
   24 |     azure_arc_proxy_url: "http://{{ proxy['hostname'] }}:{{ proxy['port'] }}"
   25 | 
   26 | - name: Set helper fact for desired_version if needed
   27 |   when: desired_version is defined
   28 |   ansible.builtin.set_fact:
   29 |     azure_arc_desired_version: "{{ desired_version }}"
   30 | 
   31 | - name: Set helper fact for altdownload if needed
   32 |   when: altdownload is defined
   33 |   ansible.builtin.set_fact:
   34 |     azure_arc_altdownload: "{{ altdownload }}"
   35 | 
   36 | - name: Gather Resource Group info
   37 |   azure.azcollection.azure_rm_resourcegroup_info:
   38 |     name: "{{ azure_arc_resource_group }}"
   39 |   register: __azure_arc_rg_info
   40 |   delegate_to: localhost
   41 |   when: azure_arc_location is not defined
   42 | 
   43 | - name: Set azure_location from resource_group
   44 |   ansible.builtin.set_fact:
   45 |     azure_arc_location: "{{ __azure_arc_rg_info.resourcegroups.0.location }}"
   46 |   when: azure_arc_location is not defined
   47 | 
   48 | - name: Include install tasks for Linux
   49 |   ansible.builtin.include_tasks: "linux_install.yml"
   50 |   when: ansible_system == 'Linux'
   51 | 
   52 | - name: Include install tasks for Windows
   53 |   ansible.builtin.include_tasks: "windows_install.yml"
   54 |   when: ansible_os_family == 'Windows'
   55 | 
   56 | - name: Include show tasks for Linux
   57 |   ansible.builtin.include_tasks: "linux_show.yml"
   58 |   when: ansible_system == 'Linux'
   59 | 
   60 | - name: Include show tasks for Windows
   61 |   ansible.builtin.include_tasks: "windows_show.yml"
   62 |   when: ansible_os_family == 'Windows'
   63 | 
   64 | - name: Set helper fact for configuration
   65 |   ansible.builtin.set_fact:
   66 |     azure_arc_show: "{{ azure_arc_show_json.stdout | ansible.builtin.from_json }}"
   67 | 
   68 | - name: Set azcmagent proxy setting if not already set correctly
   69 |   when: azure_arc_proxy_url is defined and azure_arc_show.httpsProxy != azure_arc_proxy_url
   70 |   block:
   71 |     - name: Include proxy tasks for Linux
   72 |       ansible.builtin.include_tasks: "linux_proxy.yml"
   73 |       when: ansible_system == 'Linux'
   74 | 
   75 |     - name: Include proxy tasks for Windows
   76 |       ansible.builtin.include_tasks: "windows_proxy.yml"
   77 |       when: ansible_os_family == 'Windows'
   78 | 
   79 | # When registered with Azure, validate current configuration is equal to expected configuration and set the resource id as ansible fact
   80 | - name: Assert that configuration is matching expected values and set resource id fact
   81 |   when: azure_arc_show.resourceId | default('') != ''
   82 |   block:
   83 |     - name: Set resource id as variable for easy access in other roles (already connected to azure arc)
   84 |       ansible.builtin.set_fact:
   85 |         azure_arc_resource_id: "{{ azure_arc_show.resourceId }}"
   86 | 
   87 |     - name: Verify configuration settings match expected values
   88 |       ansible.builtin.assert:
   89 |         that:
   90 |           - azure_arc_show.cloud == azure_arc_cloud
   91 |           - azure_arc_show.resourceGroup == azure_arc_resource_group
   92 |           - azure_arc_show.location == azure_arc_location
   93 |           - azure_arc_show.tenantId == azure_arc_tenant_id
   94 |           - azure_arc_show.subscriptionId == azure_arc_subscription_id
   95 | 
   96 | - name: Connect if not already connected to azure
   97 |   when: azure_arc_show.resourceId | default('') == ''
   98 |   block:
   99 |     - name: Get access token for arc onboarding  # noqa: jinja[invalid]
  100 |       # Run on localhost, so that service principal secrets don't leave control node
  101 |       delegate_to: localhost
  102 |       # This command produces output that includes an access token
  103 |       no_log: true
  104 |       azure.azcollection.azure_rm_accesstoken_info:[REDACTED VALUE BLOCK]
  105 |         [REDACTED ENCRYPTED VALUE]
  106 |         [REDACTED ENCRYPTED VALUE]
  107 |         [REDACTED ENCRYPTED VALUE]
  108 |         [REDACTED ENCRYPTED VALUE]
  109 |         [REDACTED ENCRYPTED VALUE]
  110 |           [REDACTED ENCRYPTED VALUE]
  111 |         [REDACTED ENCRYPTED VALUE]
  112 |       register: azure_arc_access_token
  113 | 
  114 |     - name: Include Connect tasks for Linux
  115 |       ansible.builtin.include_tasks: "linux_connect.yml"
  116 |       when: ansible_system == 'Linux'
  117 | 
  118 |     - name: Include Connect tasks for Windows
  119 |       ansible.builtin.include_tasks: "windows_connect.yml"
  120 |       when: ansible_os_family == 'Windows'
  121 | 
  122 |     # The connect task is no_log (its command line carries an access token), so
  123 |     # surface only stderr here to keep failures debuggable without leaking the token.
  124 |     - name: Fail if azcmagent connect was unsuccessful
  125 |       when: azure_arc_azcmagent_connect_json.rc != 0
  126 |       ansible.builtin.fail:
  127 |         msg: >-
  128 |           azcmagent connect failed (rc={{ azure_arc_azcmagent_connect_json.rc }}):
  129 |           {{ azure_arc_azcmagent_connect_json.stderr | default('') }}
  130 | 
  131 |     - name: Log onboarding success
  132 |       vars:
  133 |         azure_arc_signal_message_type: info
  134 |         azure_arc_signal_message: "azcmagent connect succeeded via Ansible azure_arc role"
  135 |       ansible.builtin.include_tasks: "log_signal.yml"
  136 | 
  137 |     - name: Transform json stdout output to variable
  138 |       ansible.builtin.set_fact:
  139 |         azure_arc_azcmagent_connect: "{{ azure_arc_azcmagent_connect_json.stdout | ansible.builtin.from_json }}"
  140 | 
  141 |     - name: Set resource id as variable for easy access in other roles (newly registered system in azure arc)
  142 |       ansible.builtin.set_fact:
  143 |         azure_arc_resource_id: "{{ azure_arc_azcmagent_connect.resourceId }}"
  144 |   rescue:
  145 |     - name: Log onboarding failure
  146 |       vars:
  147 |         azure_arc_signal_message_type: error
  148 |         azure_arc_signal_message: >-
  149 |           azcmagent connect failed:
  150 |           {{ ansible_failed_result.msg | default(ansible_failed_result.stderr | default('unknown error')) }}
  151 |       ansible.builtin.include_tasks: "log_signal.yml"
  152 | 
  153 |     - name: Raise Azure Arc onboarding failure
  154 |       ansible.builtin.fail:
  155 |         msg: >-
  156 |           Azure Arc onboarding (azcmagent connect) failed:
  157 |           {{ ansible_failed_result.msg | default(ansible_failed_result.stderr | default('unknown error')) }}
```
