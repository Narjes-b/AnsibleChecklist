# Frozen source context: V007PILOT-STRUCTURE_REUSE-018

- Repository: `snyssen/infra-snyssen.be`
- Commit: `5f8652b4132407221a55c65660ac204d57cee3c5`
- Family: Structure/reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/firewall/defaults/main.yml` (reported anchor line 1)
- Object: `source_location` `f3c6bdad166a86ce0e9f711e30611f96967998f636e444ca569a77600f5d6e53`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–3 of 3:

```text
    1 | firewall_port: "80"
    2 | firewall_proto: tcp # 'tcp', 'udp', or 'service' if port should refer to a service instead of a numeric port
    3 | firewall_rule: allow
```

## Frozen tracked paths in the relevant role/scope

```text
roles/firewall/defaults/main.yml
roles/firewall/tasks/maint.yml
```
