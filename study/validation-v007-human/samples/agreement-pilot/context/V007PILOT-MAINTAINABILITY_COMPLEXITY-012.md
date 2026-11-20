# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-012

- Repository: `roots/trellis`
- Commit: `cd8e671076918a82efb43d5a313451f4e71da318`
- Family: Maintainability/complexity
- Rule: `ansibleguard/unused-handler`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `xdebug-tunnel.yml` (reported anchor line 16)
- Object: `source_location` `956249cff0318b620103448f53e0278fe69e09da4d0e8eb45478cd8ab68efe82`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–19 of 19:

```text
    1 | ---
    2 | - name: Test Connection and Determine Remote User
    3 |   hosts: "{{ xdebug_tunnel_inventory_host }}"
    4 |   gather_facts: false
    5 |   roles:
    6 |     - { role: connection, tags: [connection, always] }
    7 | 
    8 | - name: Enable or Disable Xdebug and SSH Tunnel
    9 |   hosts: "{{ xdebug_tunnel_inventory_host }}"
   10 |   become: yes
   11 |   roles:
   12 |     - { role: sshd, tags: [sshd] }
   13 |     - { role: xdebug, tags: [xdebug] }
   14 |     - { role: xdebug-tunnel, tags: [xdebug-tunnel] }
   15 |   handlers:
   16 |     - name: reload php-fpm
   17 |       service:
   18 |         name: php{{ php_version }}-fpm
   19 |         state: reloaded
```
