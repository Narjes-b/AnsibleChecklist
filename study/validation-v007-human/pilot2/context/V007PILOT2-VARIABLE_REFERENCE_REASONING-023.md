# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-023

- Repository: `NSLS2/nsls2.ioc_deploy`
- Commit: `10518de6b2fbd124ce01d7b67512558f3bcf7b8e`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/variable-use-before-definition`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `roles/deploy_ioc/tasks/process-env.yml` (reported anchor line 7)
- Flagged construct: variable `deploy_ioc_merged_env`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–45 of 45:

```text
    1 | ---
    2 | 
    3 | - name: Show env var to process
    4 |   ansible.builtin.debug:
    5 |     msg: "Processing {{ item }} with value {{ deploy_ioc_merged_env[item] }}"
    6 | 
    7 | - name: Identify macros in envvar value
    8 |   ansible.builtin.set_fact:
    9 |     deploy_ioc_macros_in_var: "{{ deploy_ioc_merged_env[item] |
   10 |                         regex_findall('\\$\\(([A-Za-z_][A-Za-z0-9_]*)\\)') }}"
   11 | 
   12 | - name: Show macros found in var
   13 |   ansible.builtin.debug:
   14 |     msg: "Found macros {{ deploy_ioc_macros_in_var }} in {{ item }}"
   15 | 
   16 | - name: Assign temporary replacement envvar
   17 |   ansible.builtin.set_fact:
   18 |     deploy_ioc_replaced_macros: "{{ deploy_ioc_merged_env[item] }}"
   19 | 
   20 | - name: Replace macros in envvar
   21 |   ansible.builtin.include_tasks: replace-macros.yml
   22 |   loop: "{{ deploy_ioc_macros_in_var }}"
   23 |   loop_control:
   24 |     loop_var: "deploy_ioc_macro_in_var"
   25 | 
   26 | - name: Replace value of var in merged env with temp
   27 |   ansible.builtin.set_fact:
   28 |     deploy_ioc_merged_env:
   29 |       "{{ deploy_ioc_merged_env | combine(deploy_ioc_updated_macro) }}"
   30 |   vars:
   31 |     deploy_ioc_updated_macro:
   32 |       "{ '{{ item }}': '{{ deploy_ioc_replaced_macros }}' }"
   33 | 
   34 | 
   35 | # We need to recursively do this again and again until no macros remain
   36 | - name: Find envvars that use macros
   37 |   ansible.builtin.set_fact:
   38 |     deploy_ioc_envvars_with_macros: "{{ deploy_ioc_merged_env | dict2items |
   39 |                                       selectattr('value', 'search', '\\$\\(') |
   40 |                                       map(attribute='key') |
   41 |                                       list }}"
   42 | 
   43 | - name: Expand all macros in value of {{ item }}
   44 |   ansible.builtin.include_tasks: process-env.yml
   45 |   with_items: "{{ deploy_ioc_envvars_with_macros }}"
```

## Visible variable references

```text
Whole-word search for `deploy_ioc_merged_env`: 83 matches in 28 files; 5 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
roles/deploy_ioc/tasks/process-env.yml:28:    deploy_ioc_merged_env:
roles/deploy_ioc/tasks/set-facts.yml:71:    deploy_ioc_merged_env:
roles/deploy_ioc/tasks/set-facts.yml:77:    deploy_ioc_merged_env:
roles/deploy_ioc/tasks/set-facts.yml:84:    deploy_ioc_merged_env:
roles/deploy_ioc/tasks/set-facts.yml:99:    deploy_ioc_merged_env:

Other references:
roles/deploy_ioc/tasks/process-env.yml:5:    msg: "Processing {{ item }} with value {{ deploy_ioc_merged_env[item] }}"
roles/deploy_ioc/tasks/process-env.yml:9:    deploy_ioc_macros_in_var: "{{ deploy_ioc_merged_env[item] |
roles/deploy_ioc/tasks/process-env.yml:18:    deploy_ioc_replaced_macros: "{{ deploy_ioc_merged_env[item] }}"
roles/deploy_ioc/tasks/process-env.yml:29:      "{{ deploy_ioc_merged_env | combine(deploy_ioc_updated_macro) }}"
roles/deploy_ioc/tasks/process-env.yml:38:    deploy_ioc_envvars_with_macros: "{{ deploy_ioc_merged_env | dict2items |
roles/deploy_ioc/tasks/replace-macros.yml:9:#  when: deploy_ioc_merged_env[deploy_ioc_macro_in_var] | regex_search('\\$\\(')
roles/deploy_ioc/tasks/replace-macros.yml:20:                        deploy_ioc_merged_env[deploy_ioc_macro_in_var]) }}"
roles/deploy_ioc/tasks/set-facts.yml:78:      "{{ deploy_ioc_merged_env
roles/deploy_ioc/tasks/set-facts.yml:85:      "{{ deploy_ioc_merged_env | combine(ioc.environment) }}"
roles/deploy_ioc/tasks/set-facts.yml:100:      "{{ deploy_ioc_merged_env
roles/deploy_ioc/tasks/set-facts.yml:107:         | select('in', deploy_ioc_merged_env)
roles/deploy_ioc/tasks/set-facts.yml:114:  when: "'EPICS_DB_INCLUDE_PATH' not in deploy_ioc_merged_env"
roles/deploy_ioc/tasks/set-facts.yml:118:    msg: "{{ deploy_ioc_merged_env }}"
roles/deploy_ioc/tasks/set-facts.yml:122:    deploy_ioc_envvars_with_macros: "{{ deploy_ioc_merged_env | dict2items |
roles/deploy_ioc/tasks/set-facts.yml:133:    msg: "{{ deploy_ioc_merged_env }}"
roles/deploy_ioc/templates/common.cmd.j2:43:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined %}
roles/deploy_ioc/templates/common.cmd.j2:49:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/deploy_ioc/templates/common.cmd.j2:55:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/deploy_ioc/templates/common.cmd.j2:64:{% if deploy_ioc_merged_env.IOC_PREFIX is defined %}
roles/deploy_ioc/templates/common.cmd.j2:66:{% elif deploy_ioc_merged_env.CT_PREFIX is defined %}
roles/deploy_ioc/templates/common.cmd.j2:72:{% if deploy_ioc_merged_env.CT_PREFIX is defined %}
roles/deploy_ioc/templates/common.cmd.j2:75:{% elif deploy_ioc_merged_env.IOC_PREFIX is defined %}
roles/deploy_ioc/templates/common.cmd.j2:78:{% elif deploy_ioc_merged_env.PREFIX is defined %}
roles/deploy_ioc/templates/common.cmd.j2:106:{% if deploy_ioc_merged_env.CT_PREFIX is defined %}
roles/deploy_ioc/templates/common.cmd.j2:108:{% elif deploy_ioc_merged_env.IOC_PREFIX is defined %}
roles/deploy_ioc/templates/common.cmd.j2:110:{% elif deploy_ioc_merged_env.PREFIX is defined %}
roles/deploy_ioc/templates/default.substitutions.j2:15:"{{ instance[loop.index - 1] | replace("$(" + macro + ")", deploy_ioc_merged_env[macro]) }}"
roles/deploy_ioc/templates/epicsEnv.cmd.j2:6:{% for envvar in deploy_ioc_merged_env|dict2items %}
roles/deploy_ioc/templates/epicsEnv.cmd.j2:9:{% for macro in deploy_ioc_merged_env|dict2items %}
roles/device_roles/adandor3/templates/auto_settings.req.j2:4:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined %}
roles/device_roles/adandor3/templates/auto_settings.req.j2:7:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adandor3/templates/auto_settings.req.j2:10:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adaravis/templates/auto_settings.req.j2:7:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined %}
roles/device_roles/adaravis/templates/auto_settings.req.j2:10:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adaravis/templates/auto_settings.req.j2:13:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adgermanium/templates/common.cmd.j2:32:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined %}
roles/device_roles/adgermanium/templates/common.cmd.j2:38:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adgermanium/templates/common.cmd.j2:44:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adgermanium/templates/epicsEnv.cmd.j2:5:{% for envvar in deploy_ioc_merged_env|dict2items %}
roles/device_roles/adgermanium/templates/epicsEnv.cmd.j2:8:{% for macro in deploy_ioc_merged_env|dict2items %}
roles/device_roles/adkinetix/templates/auto_settings.req.j2:3:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined%}
roles/device_roles/adkinetix/templates/auto_settings.req.j2:6:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adkinetix/templates/auto_settings.req.j2:9:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adpilatus/templates/auto_settings.req.j2:3:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined %}
roles/device_roles/adpilatus/templates/auto_settings.req.j2:6:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adpilatus/templates/auto_settings.req.j2:9:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adsimdetector/templates/auto_settings.req.j2:3:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined%}
roles/device_roles/adsimdetector/templates/auto_settings.req.j2:6:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adsimdetector/templates/auto_settings.req.j2:9:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adtimepix3/templates/auto_settings.req.j2:3:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined%}
roles/device_roles/adtimepix3/templates/auto_settings.req.j2:6:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adtimepix3/templates/auto_settings.req.j2:9:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adtucam/templates/auto_settings.req.j2:11:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined %}
roles/device_roles/adtucam/templates/auto_settings.req.j2:14:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adtucam/templates/auto_settings.req.j2:17:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adurl/templates/auto_settings.req.j2:3:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined%}
roles/device_roles/adurl/templates/auto_settings.req.j2:6:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/adurl/templates/auto_settings.req.j2:9:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/aduvc/templates/auto_settings.req.j2:3:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined%}
roles/device_roles/aduvc/templates/auto_settings.req.j2:6:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/aduvc/templates/auto_settings.req.j2:9:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/advimba/templates/auto_settings.req.j2:3:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined%}
roles/device_roles/advimba/templates/auto_settings.req.j2:6:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/advimba/templates/auto_settings.req.j2:9:{% if deploy_ioc_merged_env.ADPLUGINBAR is defined %}
roles/device_roles/adxspd/templates/auto_settings.req.j2:3:{% if deploy_ioc_merged_env.FFMPEGSERVER is defined and ioc.environment.FFMSTREAM_PORT is defined%}
roles/device_roles/adxspd/templates/auto_settings.req.j2:6:{% if deploy_ioc_merged_env.ADCOMPVISION is defined %}
roles/device_roles/bltiming/templates/epicsEnv.cmd.j2:5:{% for envvar in deploy_ioc_merged_env|dict2items %}
roles/device_roles/bltiming/templates/epicsEnv.cmd.j2:8:{% for macro in deploy_ioc_merged_env|dict2items %}
roles/device_roles/powerpmac/templates/autohome.substitutions.j2:9:{{"{"}}"{{ deploy_ioc_merged_env.SYS }}", "{{"{"}}{{ axis.component }}-Ax:{{ axis.name }}{{"}"}}", {{ axis.num + 7 }}, "{{ deploy_ioc_merged_env.SSH_PORT }}"{{"}"}}
roles/device_roles/powerpmac/templates/autohome.substitutions.j2:13:{{"{"}}"{{ deploy_ioc_merged_env.SYS }}", "{{"{"}}{{ axis.component }}-Ax:{{ axis.name }}{{"}"}}", {{ axis.home_plc }}, "{{ deploy_ioc_merged_env.SSH_PORT }}"{{"}"}}
roles/device_roles/powerpmac/templates/base.cmd.j2:11:pmacCreateController("$(CTRL_PORT)", "$(SSH_PORT)", 0, $(NUM_AXES), {{ deploy_ioc_merged_env.MOVING_POLL_PERIOD }}, {{ deploy_ioc_merged_env.IDLE_POLL_PERIOD }})
roles/device_roles/powerpmac/templates/cs.substitutions.j2:11:{{"{"}}"{{ deploy_ioc_merged_env.SYS }}", "{{"{"}}{{ axis.component }}-Ax:{{ axis.name }}{{"}"}}", "CS{{ axis.cs }}", "{{ deploy_ioc_merged_env.CTRL_PORT }}", {{ axis.num }}, "{{ axis.desc }}", {{ axis.mres }}, "{{ axis.egu }}", 4{{"}"}}
roles/device_roles/powerpmac/templates/cs.substitutions.j2:22:{{"{"}}"{{ deploy_ioc_merged_env.SYS }}", "{{"{"}}{{ axis.component }}-Ax:{{ axis.name }}{{"}"}}", "{{ deploy_ioc_merged_env.CTRL_PORT }}", {{ axis.num }}{{"}"}}
roles/device_roles/powerpmac/templates/motor.substitutions.j2:9:{{"{"}}"{{ deploy_ioc_merged_env.SYS }}", "{{"{"}}{{ axis.component }}-Ax:{{ axis.name }}{{"}"}}", "{{ deploy_ioc_merged_env.CTRL_PORT }}", "{{ deploy_ioc_merged_env.SSH_PORT }}", {{ axis.num }}, "{{ axis.desc }}", {{ axis.mres }}, "{{ axis.egu }}", 4{{"}"}}
roles/device_roles/powerpmac/templates/motorstatus.substitutions.j2:9:{{"{"}}"{{ deploy_ioc_merged_env.SYS }}", "{{"{"}}{{ axis.component }}-Ax:{{ axis.name }}{{"}"}}", "{{ deploy_ioc_merged_env.CTRL_PORT }}", {{ axis.num }}, "{{ deploy_ioc_merged_env.CT_SYS }}", "{{"{"}}{{ deploy_ioc_merged_env.CONTROLLER }}-Ax:{{ axis.num }}{{"}"}}"{{"}"}}
roles/device_roles/powerpmac/templates/pmacStatus.substitutions.j2:8:{{"{"}}"{{ deploy_ioc_merged_env.CT_SYS }}", "{{ deploy_ioc_merged_env.CONTROLLER }}", 1, 5, "{{ deploy_ioc_merged_env.CTRL_PORT }}", {{ deploy_ioc_merged_env.NUM_AXES }}{{"}"}}
roles/device_roles/zpsc/templates/base.cmd.j2:45:epicsEnvSet("IOC_TOP", "{{ deploy_ioc_merged_env.TOP }}")
roles/device_roles/zubpm/templates/base.cmd.j2:25:epicsEnvSet("IOC_TOP", "{{ deploy_ioc_merged_env.TOP }}")
```
