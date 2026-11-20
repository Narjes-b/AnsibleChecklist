# Frozen source context: V007PILOT-STRUCTURE_REUSE-046

- Repository: `NSLS2/nsls2.ioc_deploy`
- Commit: `10518de6b2fbd124ce01d7b67512558f3bcf7b8e`
- Family: Structure/reuse
- Rule: `ansibleguard/role-readme-absent`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/device_roles/xrt_caproto/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `8ef6b3c6a620a4d6e38e264efaa7f5fc296ed9a65ef9e73141f81f28fc9da2d0`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–50 of 50:

```text
    1 | ---
    2 | 
    3 | - name: Check if pixi.toml exists
    4 |   ansible.builtin.stat:
    5 |     path: "{{ deploy_ioc_ioc_directory }}/pixi.toml"
    6 |   register: pixi_toml_stat
    7 | 
    8 | - name: Initialize Pixi
    9 |   ansible.builtin.command:
   10 |     # yamllint disable-line rule:line-length
   11 |     cmd: "{{ ioc.pixi_executable_path | default(deploy_ioc_pixi_executable_path) }} init"
   12 |     chdir: "{{ deploy_ioc_ioc_directory }}"
   13 |   when: not pixi_toml_stat.stat.exists
   14 |   changed_when: not pixi_toml_stat.stat.exists
   15 | 
   16 | - name: Add Python, numpy, h5py dependency
   17 |   ansible.builtin.command:
   18 |     # yamllint disable-line rule:line-length
   19 |     cmd: "{{ ioc.pixi_executable_path | default(deploy_ioc_pixi_executable_path) }} add 'python{{ ioc.python_version | default(device_roles_xrt_caproto_python_version) }}' numpy h5py"
   20 |     chdir: "{{ deploy_ioc_ioc_directory }}"
   21 |   changed_when: true
   22 | 
   23 | - name: Add caproto git repository and xrt as PyPI dependencies via Pixi
   24 |   ansible.builtin.command:
   25 |     # yamllint disable-line rule:line-length
   26 |     cmd: "{{ ioc.pixi_executable_path | default(deploy_ioc_pixi_executable_path) }} add --pypi 'caproto @ git+https://github.com/thopkins32/caproto.git@e3f8966b177b813f92331553ced85c20288b1712' xrt>=2.0.0b1"
   27 |     chdir: "{{ deploy_ioc_ioc_directory }}"
   28 |   changed_when: true
   29 | 
   30 | - name: Install dependencies
   31 |   ansible.builtin.command:
   32 |     # yamllint disable-line rule:line-length
   33 |     cmd: "{{ ioc.pixi_executable_path | default(deploy_ioc_pixi_executable_path) }} install"
   34 |     chdir: "{{ deploy_ioc_ioc_directory }}"
   35 |   changed_when: true
   36 | 
   37 | - name: Verify xrt_caproto Python dependencies import
   38 |   ansible.builtin.command:
   39 |     # yamllint disable-line rule:line-length
   40 |     cmd: "{{ ioc.pixi_executable_path | default(deploy_ioc_pixi_executable_path) }} run python -c 'import xrt.backends.raycing; import caproto.ioc_examples.xrt_xml_ioc'"
   41 |     chdir: "{{ deploy_ioc_ioc_directory }}"
   42 |   changed_when: false
   43 | 
   44 | - name: Install startup script
   45 |   ansible.builtin.template:
   46 |     src: "templates/st.cmd.j2"
   47 |     dest: "{{ deploy_ioc_ioc_directory }}/st.cmd"
   48 |     owner: "{{ host_config.softioc_user }}"
   49 |     group: "{{ host_config.softioc_group }}"
   50 |     mode: "0775"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/device_roles/acmi2/README.md
roles/device_roles/acmi2/example.yml
roles/device_roles/acmi2/schema.yml
roles/device_roles/acmi2/tasks/main.yml
roles/device_roles/acmi2/templates/base.cmd.j2
roles/device_roles/adandor3/README.md
roles/device_roles/adandor3/example.yml
roles/device_roles/adandor3/schema.yml
roles/device_roles/adandor3/tasks/main.yml
roles/device_roles/adandor3/templates/auto_settings.req.j2
roles/device_roles/adandor3/templates/base.cmd.j2
roles/device_roles/adaravis/README.md
roles/device_roles/adaravis/defaults/main.yml
roles/device_roles/adaravis/example.yml
roles/device_roles/adaravis/schema.yml
roles/device_roles/adaravis/tasks/autogen_files.yml
roles/device_roles/adaravis/tasks/main.yml
roles/device_roles/adaravis/templates/auto_settings.req.j2
roles/device_roles/adaravis/templates/base.cmd.j2
roles/device_roles/adeiger/README.md
roles/device_roles/adeiger/example.yml
roles/device_roles/adeiger/schema.yml
roles/device_roles/adeiger/tasks/main.yml
roles/device_roles/adeiger/tasks/validate_local_intf.yml
roles/device_roles/adeiger/templates/base.cmd.j2
roles/device_roles/adgermanium/example.yml
roles/device_roles/adgermanium/schema.yml
roles/device_roles/adgermanium/tasks/main.yml
roles/device_roles/adgermanium/templates/base.cmd.j2
roles/device_roles/adgermanium/templates/common.cmd.j2
roles/device_roles/adgermanium/templates/epicsEnv.cmd.j2
roles/device_roles/adgermanium/templates/postInit.cmd.j2
roles/device_roles/adgermanium/templates/st.cmd.j2
roles/device_roles/adkinetix/examples/kinetix-det1/config.yml
roles/device_roles/adkinetix/examples/kinetix-det1/verify.yml
roles/device_roles/adkinetix/schema.yml
roles/device_roles/adkinetix/tasks/main.yml
roles/device_roles/adkinetix/templates/auto_settings.req.j2
roles/device_roles/adkinetix/templates/base.cmd.j2
roles/device_roles/admerlin/README.md
roles/device_roles/admerlin/example.yml
roles/device_roles/admerlin/schema.yml
roles/device_roles/admerlin/tasks/main.yml
roles/device_roles/admerlin/tasks/validate_local_intf.yml
roles/device_roles/admerlin/templates/base.cmd.j2
roles/device_roles/admythen/README.md
roles/device_roles/admythen/example.yml
roles/device_roles/admythen/schema.yml
roles/device_roles/admythen/tasks/main.yml
roles/device_roles/admythen/templates/auto_settings.req.j2
roles/device_roles/admythen/templates/base.cmd.j2
roles/device_roles/adpco/README.md
roles/device_roles/adpco/examples/pco-det1/config.yml
roles/device_roles/adpco/examples/pco-det1/verify.yml
roles/device_roles/adpco/schema.yml
roles/device_roles/adpco/tasks/main.yml
roles/device_roles/adpco/templates/auto_settings.req.j2
roles/device_roles/adpco/templates/base.cmd.j2
roles/device_roles/adphantom/README.md
roles/device_roles/adphantom/example.yml
roles/device_roles/adphantom/files/auto_settings.req
roles/device_roles/adphantom/schema.yml
roles/device_roles/adphantom/tasks/main.yml
roles/device_roles/adphantom/templates/base.cmd.j2
roles/device_roles/adpicam/README.md
roles/device_roles/adpicam/examples/adpicam-01/config.yml
roles/device_roles/adpicam/examples/adpicam-01/verify.yml
roles/device_roles/adpicam/files/80-picam.rules
roles/device_roles/adpicam/schema.yml
roles/device_roles/adpicam/tasks/main.yml
roles/device_roles/adpicam/templates/auto_settings.req.j2
roles/device_roles/adpicam/templates/base.cmd.j2
roles/device_roles/adpilatus/README.md
roles/device_roles/adpilatus/example.yml
roles/device_roles/adpilatus/schema.yml
roles/device_roles/adpilatus/tasks/main.yml
roles/device_roles/adpilatus/templates/auto_settings.req.j2
roles/device_roles/adpilatus/templates/base.cmd.j2
roles/device_roles/adprosilica/README.md
roles/device_roles/adprosilica/example.yml
roles/device_roles/adprosilica/schema.yml
roles/device_roles/adprosilica/tasks/main.yml
roles/device_roles/adprosilica/templates/auto_settings.req.j2
roles/device_roles/adprosilica/templates/base.cmd.j2
roles/device_roles/adscanpb/README.md
roles/device_roles/adscanpb/example.yml
roles/device_roles/adscanpb/schema.yml
roles/device_roles/adscanpb/tasks/main.yml
roles/device_roles/adscanpb/templates/base.cmd.j2
roles/device_roles/adsimdetector/examples/sim-cam-test/config.yml
roles/device_roles/adsimdetector/examples/sim-cam-test/verify.yml
roles/device_roles/adsimdetector/schema.yml
roles/device_roles/adsimdetector/tasks/main.yml
roles/device_roles/adsimdetector/templates/auto_settings.req.j2
roles/device_roles/adsimdetector/templates/base.cmd.j2
roles/device_roles/adtimepix3/README.md
roles/device_roles/adtimepix3/example.yml
roles/device_roles/adtimepix3/schema.yml
roles/device_roles/adtimepix3/tasks/main.yml
roles/device_roles/adtimepix3/templates/auto_settings.req.j2
roles/device_roles/adtimepix3/templates/base.cmd.j2
roles/device_roles/adtimepix3_pipeline/defaults/main.yml
roles/device_roles/adtimepix3_pipeline/examples/adtimepix3_pipeline_01/config.yml
roles/device_roles/adtimepix3_pipeline/examples/adtimepix3_pipeline_01/verify.yml
roles/device_roles/adtimepix3_pipeline/files/tpx3.json
roles/device_roles/adtimepix3_pipeline/schema.yml
roles/device_roles/adtimepix3_pipeline/tasks/main.yml
roles/device_roles/adtimepix3_pipeline/templates/pixi.lock.j2
roles/device_roles/adtimepix3_pipeline/templates/pixi.toml.j2
roles/device_roles/adtimepix3_pipeline/templates/st.cmd.j2
roles/device_roles/adtucam/README.md
roles/device_roles/adtucam/examples/axisDet1/config.yml
roles/device_roles/adtucam/examples/axisDet1/verify.yml
roles/device_roles/adtucam/schema.yml
roles/device_roles/adtucam/tasks/main.yml
roles/device_roles/adtucam/templates/auto_settings.req.j2
roles/device_roles/adtucam/templates/base.cmd.j2
roles/device_roles/adurl/README.md
roles/device_roles/adurl/example.yml
roles/device_roles/adurl/schema.yml
[listing truncated after 120 paths]
```
