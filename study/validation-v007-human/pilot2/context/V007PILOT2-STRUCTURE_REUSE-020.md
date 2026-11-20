# Frozen source context: V007PILOT2-STRUCTURE_REUSE-020

- Repository: `NSLS2/nsls2.ioc_deploy`
- Commit: `10518de6b2fbd124ce01d7b67512558f3bcf7b8e`
- Family: structure_reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/deploy_ioc/tasks/set-facts.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/deploy_ioc/tasks/set-facts.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–144 of 144:

```text
    1 | ---
    2 | 
    3 | - name: Reload default configuration variables
    4 |   ansible.builtin.include_vars:
    5 |     file: defaults/main.yml
    6 | 
    7 | - name: Set IOC configuration to variable
    8 |   ansible.builtin.set_fact:
    9 |     ioc: "{{ host_config[deploy_ioc_ioc_name] }}"
   10 | 
   11 | - name: Display read IOC configuration
   12 |   ansible.builtin.debug:
   13 |     msg: "{{ ioc }}"
   14 | 
   15 | - name: Get IOC type specific default vars
   16 |   ansible.builtin.include_vars: "vars/{{ ioc.type }}.yml"
   17 | 
   18 | - name: Check to make sure IOC can be deployed on this host
   19 |   ansible.builtin.fail:
   20 |     msg: "EL version {{ ansible_distribution_major_version }} not supported"
   21 |   when: >
   22 |     deploy_ioc_supported_el_versions is defined
   23 |     and ansible_distribution == "RedHat"
   24 |     and ansible_distribution_major_version | int not in deploy_ioc_supported_el_versions
   25 | 
   26 | - name: Handle any module requirements
   27 |   when: deploy_ioc_required_module is defined or ioc.required_module is defined
   28 |   block:
   29 |     - name: Set required module
   30 |       ansible.builtin.set_fact:
   31 |         deploy_ioc_required_module: "{{ deploy_ioc_required_module }}"
   32 |       when: deploy_ioc_required_module is defined
   33 | 
   34 |     - name: Override default required module if specified
   35 |       ansible.builtin.set_fact:
   36 |         deploy_ioc_required_module: "{{ ioc.required_module }}"
   37 |       when: ioc.required_module is defined
   38 | 
   39 |     - name: Install any modules that are required for this IOC type
   40 |       ansible.builtin.include_role:
   41 |         name: nsls2.ioc_deploy.install_module
   42 |       vars:
   43 |         install_module_name: "{{ deploy_ioc_required_module }}"
   44 | 
   45 |     - name: Create variable that stores path to installed required module
   46 |       ansible.builtin.set_fact:
   47 |         deploy_ioc_required_module_path: "{{ install_module_leaf_module_path }}"
   48 | 
   49 |     - name: If specified, save module-level executable
   50 |       ansible.builtin.set_fact:
   51 |         deploy_ioc_executable: "{{ install_module_leaf_executable }}"
   52 |       when: install_module_leaf_executable is defined and deploy_ioc_executable is not defined
   53 | 
   54 |     - name: If specified, save module-level template root path
   55 |       ansible.builtin.set_fact:
   56 |         deploy_ioc_template_root_path: "{{ install_module_leaf_template_root_path }}"
   57 |       when: install_module_leaf_template_root_path is defined and deploy_ioc_template_root_path is not defined
   58 | 
   59 | - name: Override IOC exe name with instance-level value, if set
   60 |   ansible.builtin.set_fact:
   61 |     deploy_ioc_executable: "{{ ioc.executable }}"
   62 |   when: ioc.executable is defined
   63 | 
   64 | - name: Override IOC template root path with instance-level value, if set
   65 |   ansible.builtin.set_fact:
   66 |     deploy_ioc_template_root_path: "{{ ioc.ioc_template_root_path }}"
   67 |   when: ioc.ioc_template_root_path is defined
   68 | 
   69 | - name: Get default environment variables for ioc type
   70 |   ansible.builtin.set_fact:
   71 |     deploy_ioc_merged_env:
   72 |       "{{ deploy_ioc_default_env |
   73 |           combine(deploy_ioc_device_specific_env) }}"
   74 | 
   75 | - name: Merge any installed module locations into environment
   76 |   ansible.builtin.set_fact:
   77 |     deploy_ioc_merged_env:
   78 |       "{{ deploy_ioc_merged_env
   79 |           | combine(install_module_epics_deps, install_module_installed) }}"
   80 |   when: deploy_ioc_required_module is defined
   81 | 
   82 | - name: Merge in instance specific environment
   83 |   ansible.builtin.set_fact:
   84 |     deploy_ioc_merged_env:
   85 |       "{{ deploy_ioc_merged_env | combine(ioc.environment) }}"
   86 |   when: ioc.environment is defined
   87 | 
   88 | # Auto-compute EPICS_DB_INCLUDE_PATH from locally-installed module locations
   89 | # so device role vars don't have to set it manually. Honors any explicit
   90 | # value the user already supplied via device_specific_env or ioc.environment.
   91 | #
   92 | # Only `install_module_installed` is consulted: it lists modules built into
   93 | # non-bundle paths that need their own `$(MOD)/db` entry. The other env
   94 | # dicts (install_module_default_epics_deps, install_module_epics_deps) all
   95 | # point at /usr/lib/epics for unbuilt modules, which is the EPICS_BASE
   96 | # bundle path already covered by `$(EPICS_BASE)/db` at the tail of the list.
   97 | - name: Auto-compute EPICS_DB_INCLUDE_PATH if not explicitly set
   98 |   ansible.builtin.set_fact:
   99 |     deploy_ioc_merged_env:
  100 |       "{{ deploy_ioc_merged_env
  101 |           | combine({'EPICS_DB_INCLUDE_PATH':
  102 |                      deploy_ioc_auto_db_include_path}) }}"
  103 |   vars:
  104 |     deploy_ioc_db_module_keys: >-
  105 |       {{ (install_module_installed | default({})).keys() | list
  106 |          | reject('equalto', 'EPICS_BASE')
  107 |          | select('in', deploy_ioc_merged_env)
  108 |          | list }}
  109 |     deploy_ioc_auto_db_include_path: >-
  110 |       {{ (['$(TOP)/db']
  111 |           + (deploy_ioc_db_module_keys
  112 |              | map('regex_replace', '^(.*)$', '$(\1)/db') | list)
  113 |           + ['$(EPICS_BASE)/db']) | join(':') }}
  114 |   when: "'EPICS_DB_INCLUDE_PATH' not in deploy_ioc_merged_env"
  115 | 
  116 | - name: Show merged environment pre-macro substitution
  117 |   ansible.builtin.debug:
  118 |     msg: "{{ deploy_ioc_merged_env }}"
  119 | 
  120 | - name: Find envvars that use macros
  121 |   ansible.builtin.set_fact:
  122 |     deploy_ioc_envvars_with_macros: "{{ deploy_ioc_merged_env | dict2items |
  123 |                                       selectattr('value', 'search', '\\$\\(') |
  124 |                                       map(attribute='key') |
  125 |                                       list }}"
  126 | 
  127 | - name: Expand all macros in value of {{ item }}
  128 |   ansible.builtin.include_tasks: process-env.yml
  129 |   with_items: "{{ deploy_ioc_envvars_with_macros }}"
  130 | 
  131 | - name: Display merged environment
  132 |   ansible.builtin.debug:
  133 |     msg: "{{ deploy_ioc_merged_env }}"
  134 | 
  135 | - name: Get list of substitution files
  136 |   ansible.builtin.set_fact:
  137 |     substitutions: "{{ ioc.substitutions }}"
  138 |   when: ioc.substitutions is defined
  139 | 
  140 | - name: Merge any ioc specific dbpf entries
  141 |   ansible.builtin.set_fact:
  142 |     deploy_ioc_dbpf_list:
  143 |       "{{ deploy_ioc_dbpf_list + ioc.dbpf }}"
  144 |   when: ioc.dbpf is defined
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/deploy_ioc`; 91 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

roles/deploy_ioc/README.md
roles/deploy_ioc/defaults/main.yml
roles/deploy_ioc/schema.yml
roles/deploy_ioc/tasks/deploy-ioc.yml
roles/deploy_ioc/tasks/generate-substitutions-file.yml
roles/deploy_ioc/tasks/main.yml
roles/deploy_ioc/tasks/process-env.yml
roles/deploy_ioc/tasks/replace-macros.yml
roles/deploy_ioc/tasks/set-facts.yml
roles/deploy_ioc/tasks/update-config.yml
roles/deploy_ioc/templates/README.md.j2
roles/deploy_ioc/templates/common.cmd.j2
roles/deploy_ioc/templates/config.j2
roles/deploy_ioc/templates/default.substitutions.j2
roles/deploy_ioc/templates/epicsEnv.cmd.j2
roles/deploy_ioc/templates/netsetup.j2
roles/deploy_ioc/templates/postInit.cmd.j2
roles/deploy_ioc/templates/st.cmd.j2
roles/deploy_ioc/templates/st_top.cmd.j2
roles/deploy_ioc/vars/acmi2.yml
roles/deploy_ioc/vars/adandor3.yml
roles/deploy_ioc/vars/adaravis.yml
roles/deploy_ioc/vars/adeiger.yml
roles/deploy_ioc/vars/adgermanium.yml
roles/deploy_ioc/vars/adkinetix.yml
roles/deploy_ioc/vars/admerlin.yml
roles/deploy_ioc/vars/admythen.yml
roles/deploy_ioc/vars/adpco.yml
roles/deploy_ioc/vars/adphantom.yml
roles/deploy_ioc/vars/adpicam.yml
roles/deploy_ioc/vars/adpilatus.yml
roles/deploy_ioc/vars/adprosilica.yml
roles/deploy_ioc/vars/adscanpb.yml
roles/deploy_ioc/vars/adsimdetector.yml
roles/deploy_ioc/vars/adtimepix3.yml
roles/deploy_ioc/vars/adtimepix3_pipeline.yml
roles/deploy_ioc/vars/adtucam.yml
roles/deploy_ioc/vars/adurl.yml
roles/deploy_ioc/vars/aduvc.yml
roles/deploy_ioc/vars/advimba.yml
roles/deploy_ioc/vars/adxspd.yml
roles/deploy_ioc/vars/apcpdu.yml
roles/deploy_ioc/vars/axis_caproto.yml
roles/deploy_ioc/vars/base_soft_ioc.yml
roles/deploy_ioc/vars/bltiming.yml
roles/deploy_ioc/vars/caparoc.yml
roles/deploy_ioc/vars/cas_switch.yml
roles/deploy_ioc/vars/cyberpowerpdu.yml
roles/deploy_ioc/vars/eguns7.yml
roles/deploy_ioc/vars/elio.yml
roles/deploy_ioc/vars/eps.yml
roles/deploy_ioc/vars/es150.yml
roles/deploy_ioc/vars/etherip.yml
roles/deploy_ioc/vars/eurotherm3k.yml
roles/deploy_ioc/vars/f460.yml
roles/deploy_ioc/vars/germcaproto.yml
roles/deploy_ioc/vars/hiden_rga.yml
roles/deploy_ioc/vars/hiden_stream.yml
roles/deploy_ioc/vars/i400.yml
roles/deploy_ioc/vars/i404.yml
roles/deploy_ioc/vars/iologik.yml
roles/deploy_ioc/vars/lakeshore331.yml
roles/deploy_ioc/vars/lakeshore336.yml
roles/deploy_ioc/vars/linkamt96.yml
roles/deploy_ioc/vars/mcs.yml
roles/deploy_ioc/vars/mdrive.yml
roles/deploy_ioc/vars/motorpigcs2.yml
roles/deploy_ioc/vars/motorsim.yml
roles/deploy_ioc/vars/mrftiming.yml
roles/deploy_ioc/vars/nsls2em.yml
roles/deploy_ioc/vars/omega_rtc.yml
roles/deploy_ioc/vars/pandabox.yml
roles/deploy_ioc/vars/pi-e621.yml
roles/deploy_ioc/vars/powerpmac.yml
roles/deploy_ioc/vars/qepro.yml
roles/deploy_ioc/vars/rbd9103.yml
roles/deploy_ioc/vars/remote_svc_ctrl.yml
roles/deploy_ioc/vars/sr570.yml
roles/deploy_ioc/vars/stanford_dg645.yml
roles/deploy_ioc/vars/tektronix_afg3k.yml
roles/deploy_ioc/vars/tetramm.yml
roles/deploy_ioc/vars/turbopmac.yml
roles/deploy_ioc/vars/va.yml
roles/deploy_ioc/vars/vtcplc.yml
roles/deploy_ioc/vars/wienercrate.yml
roles/deploy_ioc/vars/xrt_caproto.yml
roles/deploy_ioc/vars/xspress3.yml
roles/deploy_ioc/vars/zebra.yml
roles/deploy_ioc/vars/zebra_saver_caproto.yml
roles/deploy_ioc/vars/zpsc.yml
roles/deploy_ioc/vars/zubpm.yml
```
