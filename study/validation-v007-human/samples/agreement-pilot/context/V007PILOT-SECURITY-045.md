# Frozen source context: V007PILOT-SECURITY-045

- Repository: `stackhpc/ansible-slurm-appliance`
- Commit: `f49fc24f6818ea960a28aa2e41910532c86214f9`
- Family: Security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `ansible/roles/k3s/defaults/main.yml` (reported anchor line 8)
- Object: `variable` `9a02056bd8c3cfaee1a34fc26f305c5cd6c1b2c49c378168dfb07ebf187af593`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–9 of 9:

```text
    1 | ---
    2 | # Warning: changes to these variables won't be reflected in the cluster/image if k3s is already installed
    3 | k3s_version: "v1.31.0+k3s1"
    4 | k3s_selinux_release: v1.6.latest.1
    5 | k3s_selinux_rpm_version: 1.6-1
    6 | k3s_helm_version: v3.11.0
    7 | k3s_bootstrap_token: [REDACTED_LITERAL]
    8 | k3s_bootstrap_token_expiry: [REDACTED_LITERAL]
    9 | k3s_server_name: "{{ None }}" # ansible managed
```
