# Frozen source context: V007PILOT-SECURITY-048

- Repository: `IAreKyleW00t/k2net`
- Commit: `63cf522a122691ae38ec90146c10a6d332231d00`
- Family: Security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `ansible/roles/k3s/defaults/main.yaml` (reported anchor line 7)
- Object: `source_location` `8c5ae56d7e0a3a7261ced750dc0c6b2c29aee5b360fbfac0b12b2e7801978123`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–17 of 17:

```text
    1 | ---
    2 | # General k3s settings
    3 | k3s_node_type: server # or agent
    4 | k3s_readiness_timeout: 600s
    5 | k3s_version: v1.27.4+k3s1
    6 | k3s_url: ""
    7 | k3s_token: SECRET
    8 | k3s_server_args: ""
    9 | k3s_agent_args: ""
   10 | k3s_leader: false
   11 | 
   12 | # DNS settings
   13 | k3s_resolvconf_timeout: 1
   14 | k3s_resolvconf_attempts: 2
   15 | k3s_resolvconf_rotate: false # round-robin between nameservers
   16 | k3s_nameservers: []
   17 | # - 9.9.9.9
```
