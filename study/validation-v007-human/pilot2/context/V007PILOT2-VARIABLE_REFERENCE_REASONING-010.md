# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-010

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/role-variable-precedence-collision`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `roles/ece_upgrade/vars/main.yml` (reported anchor line 6)
- Flagged construct: variable `scale_rpmversion`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–10 of 10:

```text
    1 | ---
    2 | # Variables for the Erasure code Edition node role -
    3 | # these variables are *not* meant to be overridden
    4 | 
    5 | ## Compute RPM version from Spectrum Scale version
    6 | scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
    7 | 
    8 | ## Default scale extraction path
    9 | scale_extracted_default_path: "/usr/lpp/mmfs"
   10 | scale_extracted_path: "{{ scale_extracted_default_path }}/{{ scale_version }}"
```

## Visible variable references

```text
Whole-word search for `scale_rpmversion`: 50 matches in 41 files; 36 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
roles/afm_cos_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/afm_cos_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/callhome_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/core_common/vars/main.yml:10:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/core_configure/vars/main.yml:10:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/core_install/vars/main.yml:10:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/core_prepare/vars/main.yml:10:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/core_upgrade/vars/main.yml:10:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/ece_install/defaults/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/ece_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/ece_upgrade/defaults/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/ece_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/fal_configure/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/fal_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/fal_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/grafana_bridge_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/gui_configure/defaults/main.yml:13:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/gui_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/gui_prepare/defaults/main.yml:37:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/gui_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/hdfs_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/hdfs_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/nfs_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/nfs_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/obj_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/obj_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/perfmon_configure/defaults/main.yml:39:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/perfmon_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/perfmon_prepare/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/perfmon_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/perfmon_verify/defaults/main.yml:32:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/s3_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/s3_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/scaleadmd_install/vars/main.yml:10:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/smb_install/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"
roles/smb_upgrade/vars/main.yml:6:scale_rpmversion: "{{ scale_version | regex_replace('^([0-9.]+)\\.([0-9])$', '\\1-\\2') }}"

Other references:
roles/core_install/defaults/main.yml:56:#scale_install_gplbin_package: gpfs.gplbin-{{ ansible_kernel }}-{{ scale_rpmversion }}
roles/core_prepare/defaults/main.yml:80:#scale_install_gplbin_package: gpfs.gplbin-{{ ansible_kernel }}-{{ scale_rpmversion }}
roles/core_upgrade/defaults/main.yml:61:#scale_install_gplbin_package: gpfs.gplbin-{{ ansible_kernel }}-{{ scale_rpmversion }}
roles/gui_prepare/defaults/main.yml:18:  - gpfs.gui-{{ scale_rpmversion }}.noarch
roles/gui_prepare/defaults/main.yml:19:  - gpfs.java-{{ scale_rpmversion }}.{{ scale_architecture }}
roles/gui_prepare/defaults/main.yml:20:  - gpfs.gss.pmcollector-{{ scale_rpmversion }}.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}
roles/gui_prepare/defaults/main.yml:24:  - gpfs.gss.pmsensors-{{ scale_rpmversion }}.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}
roles/perfmon_configure/defaults/main.yml:18:  - gpfs.gss.pmcollector-{{ scale_rpmversion }}.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}
roles/perfmon_configure/defaults/main.yml:22:  - gpfs.gss.pmsensors-{{ scale_rpmversion }}.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}
roles/perfmon_prepare/defaults/main.yml:18:  - gpfs.gss.pmcollector-{{ scale_rpmversion }}.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}
roles/perfmon_prepare/defaults/main.yml:22:  - gpfs.gss.pmsensors-{{ scale_rpmversion }}.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}
roles/perfmon_verify/defaults/main.yml:18:  - gpfs.gss.pmcollector-{{ scale_rpmversion }}.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}
roles/perfmon_verify/defaults/main.yml:22:  - gpfs.gss.pmsensors-{{ scale_rpmversion }}.el{{ ansible_distribution_major_version }}.{{ scale_architecture }}
roles/scaleadmd_install/defaults/main.yml:57:#scale_install_gplbin_package: gpfs.gplbin-{{ ansible_kernel }}-{{ scale_rpmversion }}
```
