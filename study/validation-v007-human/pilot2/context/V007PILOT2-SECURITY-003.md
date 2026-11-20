# Frozen source context: V007PILOT2-SECURITY-003

- Repository: `folio-org/folio-ansible`
- Commit: `dde7c5f2011b34eb79b03ef38f334b34449e67af`
- Family: security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `roles/cron-jobs/defaults/main.yml` (reported anchor line 9)
- Flagged construct: not named by the finding; the anchor line 9 lies in the top-level key `admin_user` (line 7).
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–20 of 20:

```text
    1 | ---
    2 | # defaults
    3 | okapi_port: 9130
    4 | okapi_url: "http://{{ ansible_default_ipv4.address }}:{{ okapi_port }}"
    5 | folio_cron_branch: master
    6 | tenant: diku
    7 | admin_user:
    8 |   username: diku_admin
    9 |   password: admin
   10 | # Optional, will default to config from folioCronService package
   11 | # config_dir: folio_cron_jobs # Optional, default to "folio_cron_jobs" in Ansible user's directory
   12 | # folio_cron_jobs:
   13 | #   - name: scheduled-age-to-lost-fee-charging
   14 | #     user_config_section: DEFAULT # Optional, default "DEFAULT"
   15 | #     cron_time: "*/30 * * * *"
   16 | #     tenant: diku # Optional, default "{{ tenant }}"
   17 | #     api_path: "/circulation/scheduled-age-to-lost-fee-charging"
   18 | #     method: POST
   19 | #     data: # Optional, default to empty object
   20 | #       active: "true" # note quoted value, these are query params
```
