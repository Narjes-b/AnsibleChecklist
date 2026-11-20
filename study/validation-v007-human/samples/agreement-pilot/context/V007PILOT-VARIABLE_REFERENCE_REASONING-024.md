# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-024

- Repository: `stackhpc/ansible-slurm-appliance`
- Commit: `f49fc24f6818ea960a28aa2e41910532c86214f9`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unnecessary-set-fact`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `ansible/ci/get_image_ids.yml` (reported anchor line 13)
- Object: `variable` `b4a6f2d7cfd96ca275810b167155538a947084a23c616561ece054db9d0f4559`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–13 of 13:

```text
    1 | ---
    2 | - name: Read packer build manifest
    3 |   ansible.builtin.set_fact:
    4 |     manifest: "{{ lookup('file', manifest_path) | from_json }}"
    5 |   vars:
    6 |     manifest_path: "{{ lookup('env', 'APPLIANCES_REPO_ROOT') }}/packer/packer-manifest.json"
    7 |   delegate_to: localhost
    8 | 
    9 | - name: Get latest image builds
   10 |   ansible.builtin.set_fact:
   11 |     login_build: "{{ manifest['builds'] | selectattr('custom_data', 'eq', {'source': 'login'}) | last }}"
   12 |     compute_build: "{{ manifest['builds'] | selectattr('custom_data', 'eq', {'source': 'compute'}) | last }}"
   13 |     control_build: "{{ manifest['builds'] | selectattr('custom_data', 'eq', {'source': 'control'}) | last }}"
```

## Visible variable references

```text
f49fc24f6818ea960a28aa2e41910532c86214f9:ansible/ci/get_image_ids.yml:13:    control_build: "{{ manifest['builds'] | selectattr('custom_data', 'eq', {'source': 'control'}) | last }}"
```
