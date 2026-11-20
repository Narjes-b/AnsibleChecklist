# Frozen source context: V007PILOT-STYLE_POLICY-033

- Repository: `trailofbits/algo`
- Commit: `20e22a8715c198b38c01c1ca62d0953b93587a74`
- Family: Style/policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/local/tasks/prompts.yml` (reported anchor line 1)
- Object: `source_location` `95997c4813e0a9d4c6e88b2755e25d9928d74d298942772150b813de09271e69`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–78 of 78:

```text
    1 | ---
    2 | - name: Display local installation warning
    3 |   pause:
    4 |     prompt: |
    5 | 
    6 |       ======================================================================
    7 |                           *** DESTRUCTIVE OPERATION ***
    8 |       ======================================================================
    9 | 
   10 |       Algo is designed for DEDICATED VPN servers only.
   11 | 
   12 |       This installation will:
   13 |         - Replace all firewall rules (blocks most incoming traffic)
   14 |         - Modify system network and DNS settings
   15 |         - Install and configure VPN services
   16 | 
   17 |       THERE IS NO UNINSTALL OPTION.
   18 | 
   19 |       If this server runs other services (web, database, mail, etc.),
   20 |       they will likely become inaccessible.
   21 | 
   22 |       Recommended: Take a snapshot/backup before proceeding.
   23 | 
   24 |       Documentation: https://trailofbits.github.io/algo/deploy-to-ubuntu.html
   25 | 
   26 |       ======================================================================
   27 | 
   28 |       Type 'yes' to confirm you understand the risks and want to proceed:
   29 |   register: _local_warning_confirm
   30 |   when:
   31 |     - not tests | default(false) | bool
   32 |     - not local_install_confirmed | default(false) | bool
   33 | 
   34 | - name: Abort if not confirmed
   35 |   fail:
   36 |     msg: "Installation aborted by user. Your server was not modified."
   37 |   when:
   38 |     - not tests | default(false) | bool
   39 |     - not local_install_confirmed | default(false) | bool
   40 |     - _local_warning_confirm.user_input | default('') | lower != 'yes'
   41 | 
   42 | - pause:
   43 |     prompt: |
   44 |       Enter the IP address of your server: (or use localhost for local installation):
   45 |       [localhost]
   46 |   register: _algo_server
   47 |   when: server is undefined
   48 | 
   49 | - name: Set the facts
   50 |   set_fact:
   51 |     cloud_instance_ip: >-
   52 |       {%- if server is defined -%}{{ server }}{%- elif _algo_server.user_input -%}{{ _algo_server.user_input }}{%- else -%}localhost{%- endif -%}
   53 | 
   54 | - when: cloud_instance_ip != "localhost"
   55 |   block:
   56 |     - pause:
   57 |         prompt: |
   58 |           What user should we use to login on the server? (note: passwordless login required, or ignore if you're deploying to localhost)
   59 |           [root]
   60 |       register: _algo_ssh_user
   61 |       when: ssh_user is undefined
   62 | 
   63 |     - name: Set the facts
   64 |       set_fact:
   65 |         ansible_ssh_user: >-
   66 |           {%- if ssh_user is defined -%}{{ ssh_user }}{%- elif _algo_ssh_user.user_input -%}{{ _algo_ssh_user.user_input }}{%- else -%}root{%- endif -%}
   67 | 
   68 | - pause:
   69 |     prompt: |
   70 |       Enter the public IP address or domain name of your server: (IMPORTANT! This is used to verify the certificate)
   71 |       [{{ cloud_instance_ip }}]
   72 |   register: _endpoint
   73 |   when: endpoint is undefined
   74 | 
   75 | - name: Set the facts
   76 |   set_fact:
   77 |     IP_subject_alt_name: >-
   78 |       {%- if endpoint is defined -%}{{ endpoint }}{%- elif _endpoint.user_input -%}{{ _endpoint.user_input }}{%- else -%}{{ cloud_instance_ip }}{%- endif -%}
```
