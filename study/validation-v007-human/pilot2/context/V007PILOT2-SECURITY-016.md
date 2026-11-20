# Frozen source context: V007PILOT2-SECURITY-016

- Repository: `theforeman/forklift`
- Commit: `ee24dec347fc0a785d22989fd1a183393fa4e054`
- Family: security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `roles/hammer_devel/defaults/main.yml` (reported anchor line 8)
- Flagged construct: not named by the finding; the anchor line 8 lies in the top-level key `hammer_devel_password` (line 8).
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–24 of 24:

```text
    1 | ---
    2 | hammer_devel_server_group: "server-{{ inventory_hostname }}"
    3 | hammer_devel_server: "centos9-katello-devel"
    4 | hammer_devel_server_protocol: 'https'
    5 | hammer_devel_server_port: 443
    6 | hammer_devel_host: "{{ hammer_devel_server_protocol }}://{{ hammer_devel_server }}:{{ hammer_devel_server_port }}"
    7 | hammer_devel_username: admin
    8 | hammer_devel_password: changeme
    9 | hammer_devel_github_fork_remote_name: "{{ hammer_devel_github_username }}"
   10 | hammer_devel_repositories:
   11 |   - theforeman/hammer-cli
   12 |   - theforeman/hammer-cli-foreman
   13 |   - theforeman/hammer-cli-foreman-tasks
   14 |   - theforeman/hammer_cli_foreman_remote_execution
   15 |   - theforeman/hammer-cli-foreman-rh-cloud
   16 |   - katello/hammer-cli-csv
   17 |   - katello/hammer-cli-katello
   18 | hammer_devel_local_gems: |-
   19 |   gem 'hammer_cli'
   20 |     gem 'hammer_cli_katello'
   21 |     gem 'hammer_cli_foreman_tasks'
   22 |     gem 'hammer_cli_foreman_remote_execution'
   23 |     gem 'hammer_cli_foreman_rh_cloud'
   24 |     gem 'hammer_cli_csv'
```
