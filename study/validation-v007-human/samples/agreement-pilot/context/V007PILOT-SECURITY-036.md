# Frozen source context: V007PILOT-SECURITY-036

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: Security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `ansible/roles/datadog.datadog/manual_tests/test_5_full.yml` (reported anchor line 6)
- Object: `source_location` `4ec13f7fc7e0d47667329b7daf2b0fd4ffc11cf0f2e5477cb1a70c75d9a9331b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–47 of 47:

```text
    1 | - hosts: all
    2 |   roles:
    3 |     - { role: ../../ansible-datadog, become: yes }  # On Ansible < 1.9, use `sudo: yes` instead of `become: yes`
    4 |   vars:
    5 |     datadog_agent_major_version: 5
    6 |     datadog_api_key: "123456"
    7 |     datadog_agent_version: "1:5.18.0-1" # for apt-based platforms, use a `5.12.3-1` format on yum-based platforms
    8 |     datadog_agent_allow_downgrade: true
    9 |     datadog_config:
   10 |       tags: "mytag0, mytag1"
   11 |       log_level: INFO
   12 |       apm_enabled: "true" # has to be set as a string
   13 |     datadog_config_ex:
   14 |       trace.config:
   15 |         env: dev
   16 |       trace.concentrator:
   17 |         extra_aggregators: version
   18 |     datadog_checks:
   19 |       process:
   20 |         init_config:
   21 |         instances:
   22 |           - name: ssh
   23 |             search_string: ['ssh', 'sshd' ]
   24 |           - name: syslog
   25 |             search_string: ['rsyslog' ]
   26 |             cpu_check_interval: 0.2
   27 |             exact_match: true
   28 |             ignore_denied_access: true
   29 |       ssh_check:
   30 |         init_config:
   31 |         instances:
   32 |           - host: localhost
   33 |             port: 22
   34 |             username: root
   35 |             password: changeme
   36 |             sftp_check: True
   37 |             private_key_file:[REDACTED VALUE BLOCK]
   38 |             add_missing_keys: True
   39 |       nginx:
   40 |         init_config:
   41 |         instances:
   42 |           - nginx_status_url: http://example.com/nginx_status/
   43 |             tags:
   44 |               - instance:foo
   45 |           - nginx_status_url: http://example2.com:1234/nginx_status/
   46 |             tags:
   47 |               - instance:bar
```
