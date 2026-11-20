# Frozen source context: V007PILOT-STRUCTURE_REUSE-010

- Repository: `theforeman/forklift`
- Commit: `ee24dec347fc0a785d22989fd1a183393fa4e054`
- Family: Structure/reuse
- Rule: `ansibleguard/role-readme-absent`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/foreman_maintain_packages/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `c1ee355d0744a06d1398cf4f0a9dba14f15ebf20530605fccb285683ca10a092`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–7 of 7:

```text
    1 | ---
    2 | - name: Gather the package facts
    3 |   package_facts:
    4 |     manager: auto
    5 | - name: 'Allow Packages to be Installed'
    6 |   command: "foreman-maintain packages unlock -y" 
    7 |   when: "'rubygem-foreman_maintain' in ansible_facts.packages"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/foreman_maintain_packages/tasks/main.yml
```
