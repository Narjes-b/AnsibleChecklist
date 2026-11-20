# Frozen source context: V007PILOT-SECURITY-033

- Repository: `bluebanquise/bluebanquise`
- Commit: `fcc5b8776f3b1bde7ca4fba65b8cb2e77617f7b0`
- Family: Security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `collections/infrastructure/roles/pcs/defaults/main.yml` (reported anchor line 4)
- Object: `variable` `45bd45ff0ae4e527ae51afdc8320b3c8f950fbae5d2a02fd3d2aa1eb8ada9dd8`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–6 of 6:

```text
    1 | ---
    2 | pcs_cib_file_path: /root/ha_config.ansible.xml
    3 | pcs_ha_cluster_name: ha_cluster
    4 | pcs_ha_cluster_password: root
    5 | pcs_ha_cluster_password_sha512: [REDACTED_LITERAL]
    6 | pcs_autostart: false
```
