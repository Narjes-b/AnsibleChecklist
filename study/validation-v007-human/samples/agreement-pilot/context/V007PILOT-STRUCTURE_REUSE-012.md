# Frozen source context: V007PILOT-STRUCTURE_REUSE-012

- Repository: `stackhpc/ansible-slurm-appliance`
- Commit: `f49fc24f6818ea960a28aa2e41910532c86214f9`
- Family: Structure/reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible/roles/nhc/defaults/main.yml` (reported anchor line 1)
- Object: `source_location` `a93cd87a2455799c71beca7562c50b303c0cd0131870e613ca154b6e4c1fd047`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–2 of 2:

```text
    1 | nhc_config_template: nhc.conf.j2
    2 | nhc_config_extra: ''
```

## Frozen tracked paths in the relevant role/scope

```text
ansible/roles/nhc/README.md
ansible/roles/nhc/defaults/main.yml
ansible/roles/nhc/files/5e18b7f-speedup-read-cpuinfo.patch
ansible/roles/nhc/library/infiniband_facts.py
ansible/roles/nhc/tasks/boot.yml
ansible/roles/nhc/tasks/export.yml
ansible/roles/nhc/tasks/facts.yml
ansible/roles/nhc/tasks/install.yml
ansible/roles/nhc/tasks/runtime.yml
ansible/roles/nhc/templates/nhc.conf.j2
```
