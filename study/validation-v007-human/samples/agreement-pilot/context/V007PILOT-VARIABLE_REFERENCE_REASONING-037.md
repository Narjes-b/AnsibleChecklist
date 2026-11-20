# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-037

- Repository: `adoptium/infrastructure`
- Commit: `d31f47293b3a0166a4f9d7b8c51475d548999408`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/overriding-facts`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `ansible/playbooks/AdoptOpenJDK_AIX_Playbook/roles/users/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `dc96e4b52dba11404ed20a4d4a310d50ea23777a7416285cf54f81d3a52b298a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–67 of 67:

```text
    1 | # Role to manage users for Adoptium Build Farm
    2 | # Role can be called with an argument - to override the default userlist
    3 | # by default, vars are included from role/vars/main.yml and
    4 | # role/default/main.yml
    5 | # by default, ssh keys are generated during creation, which also creates ~/.ssh
    6 | # these new keys can be overwritten by other keys, if so desired/needed.
    7 | #
    8 | # No tags here: the role is tagged in main.yml
    9 | # sub-tasks must be tagged there as 'include_tasks' do not
   10 | # execute the included_tasks - only lists them.
   11 | ---
   12 | # note: the append: element is needed to get the user: mod to report 'ok'
   13 | # versus 'changed'
   14 | - name: "Create account"
   15 |   include_tasks: create_user.yml
   16 |   loop:
   17 |     "{{ users }}"
   18 |   loop_control:
   19 |     loop_var: username
   20 | 
   21 | # Not in user module - set default account attributes
   22 | # ALWAYS done, just in case.
   23 | # As tasks are included HERE {{ username }} is different for each iteration
   24 | - name: "Set/reset {{ username }} attributes"
   25 |   include_tasks: user_attributes.yml
   26 |   loop:
   27 |     "{{ users }}"
   28 |   loop_control:
   29 |     loop_var: username
   30 | 
   31 | # Since task_file existence cannot be determined in the role's
   32 | # tasks directory, all included user tasks must exist.
   33 | # A template customization is supplied in tasks/customization.template:
   34 | # to simplify task file creation (touch also works)
   35 | - name: "Perform customization"
   36 |   include_tasks: "{{ username }}.yml"
   37 |   loop:
   38 |     "{{ users }}"
   39 |   loop_control:
   40 |     loop_var: username
   41 | 
   42 | # zeus and nagios are not getting user_attributes so "in-lining" their management
   43 | - name: Zeus account management
   44 |   tags:
   45 |     - zeus_user
   46 |     - adoptopenjdk
   47 |   block:
   48 |     - name: Assign username variable
   49 |       set_fact:
   50 |         username: zeus
   51 |     - name: Create account
   52 |       include_tasks: create_user.yml
   53 |     - name: Perform customization for zeus
   54 |       include_tasks: "{{ username }}.yml"
   55 | 
   56 | - name: Nagios account management
   57 |   tags:
   58 |     - nagios
   59 |     - adoptopenjdk
   60 |   block:
   61 |     - name: Assign username variable
   62 |       set_fact:
   63 |         username: nagios
   64 |     - name: Create account
   65 |       include_tasks: create_user.yml
   66 |     - name: Perform customization for zeus
   67 |       include_tasks: "{{ username }}.yml"
```
