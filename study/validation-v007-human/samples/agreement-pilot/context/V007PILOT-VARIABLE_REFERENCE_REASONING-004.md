# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-004

- Repository: `ansible-lockdown/RHEL8-STIG`
- Commit: `baa075468dfa59050141c99d99dcacd2e977248c`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/role-variable-precedence-collision`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `vars/main.yml` (reported anchor line 11)
- Object: `variable` `279a7dea6fc4ac220096c2cbd5806843a98a0ecc57260f5c2eea018e1e0605a3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–22 of 22:

```text
    1 | ---
    2 | 
    3 | rhel8stig_min_ansible_version: 2.12.1
    4 | 
    5 | # RHEL 8 STIG requirements
    6 | combined_crypto_policy_config: FIPS
    7 | 
    8 | rhel8stig_sysctl_reload: "{{ not system_is_container }}"
    9 | 
   10 | # Allow automated discovery of UIDs
   11 | discover_int_uid: true
   12 | 
   13 | # Used to control warning summary
   14 | warn_control_list: ""
   15 | warn_count: 0
   16 | 
   17 | company_title: 'MindPoint Group - A Tyto Athene Company'
   18 | 
   19 | file_managed_by_ansible: |-
   20 |   # File managed by ansible as part of {{ benchmark }} benchmark
   21 |   # As part of Ansible-lockdown
   22 |   # Provided by {{ company_title }}
```

## Visible variable references

```text
baa075468dfa59050141c99d99dcacd2e977248c:defaults/main.yml:720:discover_int_uid: true
baa075468dfa59050141c99d99dcacd2e977248c:tasks/prelim.yml:38:  when: discover_int_uid
baa075468dfa59050141c99d99dcacd2e977248c:vars/main.yml:11:discover_int_uid: true
```
