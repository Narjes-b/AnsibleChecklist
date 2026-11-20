# Frozen source context: V007PILOT-SECURITY-047

- Repository: `openfun/arnold`
- Commit: `f19ea6d060de69f01e750fab289b9fb7a991e27d`
- Family: Security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `tasks/create_app_secrets.yml` (reported anchor line 20)
- Object: `task` `d8c27f6d28d14253c7f26c1c08022b2c06b96329c2530f0b9948d997900e2574`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–34 of 34:

```text
    1 | # Create secrets for an app
    2 | 
    3 | - name: Print app name
    4 |   ansible.builtin.debug:
    5 |     msg: "App name {{ app.name }}"
    6 |   tags: secret
    7 | 
    8 | - name: Set templates list for this app
    9 |   ansible.builtin.set_fact:
   10 |     raw_templates: "{{ app | json_query('services[*].templates[]') | list }}"
   11 |   tags: deploy
   12 | 
   13 | - include_tasks: tasks/filter_empty_templates_for_app.yml
   14 | 
   15 | - name: Set secrets to create
   16 |   ansible.builtin.set_fact:
   17 |     secrets: "{{ templates | map('regex_search', '.*/secret.*\\.yml\\.j2$') | select('string') | list }}"
   18 |   tags: secret
   19 | 
   20 | - name: Display k8s's secrets for this app
   21 |   ansible.builtin.debug:
   22 |     var: secrets
   23 |     verbosity: 2
   24 |   when: secrets is defined
   25 |   tags: secret
   26 | 
   27 | # Create all secrets for the current application
   28 | - name: Actually create the secrets in k8s
   29 |   kubernetes.core.k8s:
   30 |     state: present
   31 |     definition: "{{ lookup('template', item) | from_yaml_all }}"
   32 |   with_items: "{{ secrets }}"
   33 |   when: secrets is defined
   34 |   tags: secret
```
