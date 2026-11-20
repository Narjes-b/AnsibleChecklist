# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-012

- Repository: `igou-io/igou-ansible`
- Commit: `5dac3e63735e0e15407c172e0abd56d431fe4e47`
- Family: maintainability_complexity
- Rule: `ansibleguard/unused-handler`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `playbooks/routeros/configure.yaml` (reported anchor line 54)
- Flagged construct: not named by the finding; the anchor line 54 lies in the task at line 54, name `Record that the baseline reported a change`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–114 of 114:

```text
    1 | ---
    2 | # Apply the david_igou.routeros_configuration.configure role to a routeros
    3 | # device using its host_vars/group_vars declarative baseline (the curated
    4 | # routeros_config dict). This is the canonical apply playbook — paths flow
    5 | # in through Ansible's normal var precedence, NOT sliced from a capture file.
    6 | #
    7 | # To preview without applying:
    8 | #   ansible-playbook playbooks/routeros/configure.yaml \
    9 | #     -i ../igou-inventory/inventory.yaml -e host=routeros --check
   10 | # To apply:
   11 | #   same command without --check.
   12 | # A check-mode run (the AAP routeros_configure_check template) additionally
   13 | # publishes drift_label ('clean'|'drift') and drift_summary as job artifacts,
   14 | # so an Automation Orchestrator workflow can branch on the audit result. See
   15 | # the post_tasks at the bottom.
   16 | # To ship a fresh S3 backup snapshot before the apply touches anything
   17 | # (the AAP routeros_configure template sets this):
   18 | #   ... -e routeros_pre_apply_backup=true
   19 | #
   20 | # Graduating new paths / onboarding a new device: see
   21 | # playbooks/routeros/configure_from_capture.yaml (capture-file harness),
   22 | # then append proven path blocks to igou-inventory/host_vars/<host>.yml and
   23 | # re-run this playbook in --check to confirm idempotency.
   24 | 
   25 | # Opt-in pre-apply backup: chains backup_s3.yaml so a fresh snapshot pair
   26 | # (.rsc + binary) lands in S3 before configure writes. Recovery from a bad
   27 | # apply is the normal restore path (fetch from S3, /import or
   28 | # /system backup load). Tier stays 'daily' so the snapshot ages out under
   29 | # the same lifecycle rule as scheduled backups.
   30 | - name: Pre-apply S3 backup (opt-in via routeros_pre_apply_backup)
   31 |   ansible.builtin.import_playbook: backup_s3.yaml
   32 |   vars:
   33 |     # Align backup_s3.yaml's default host (routeros, whole group) with this
   34 |     # playbook's default (routeros_router). `-e host=<x>` on the CLI
   35 |     # overrides this literal — extra-vars beat play vars.
   36 |     host: routeros_router
   37 |   when: routeros_pre_apply_backup | default(false) | bool
   38 | 
   39 | - name: Configure RouterOS device from declarative host_vars baseline
   40 |   hosts: "{{ host | default('routeros_router') }}"
   41 |   gather_facts: false
   42 | 
   43 |   vars:
   44 |     routeros_api_tls: true
   45 |     routeros_api_validate_certs: false
   46 |     routeros_api_port: 8729
   47 | 
   48 |   handlers:
   49 |     # Notified (via the `apply:` below) by every task the role runs that
   50 |     # reports changed. In CHECK mode nothing was written, so "changed" means
   51 |     # "the device does not match the baseline" — that is the drift signal the
   52 |     # role otherwise does not expose. In apply mode this only records that a
   53 |     # write happened; nothing reads it.
   54 |     - name: Record that the baseline reported a change
   55 |       ansible.builtin.set_fact:
   56 |         rcfg_changed: true
   57 | 
   58 |   pre_tasks:
   59 |     - name: Resolve api-ssl credentials once
   60 |       ansible.builtin.set_fact:
   61 |         routeros_api_username: "{{ routeros_api_credentials.username }}"
   62 |         routeros_api_password: "{{ routeros_api_credentials.password }}"
   63 |       no_log: true
   64 | 
   65 |     - name: Assert routeros_config is defined for this host
   66 |       ansible.builtin.assert:
   67 |         that:
   68 |           - routeros_config is defined
   69 |           - routeros_config | length > 0
   70 |         fail_msg: >-
   71 |           No routeros_config baseline found for {{ inventory_hostname }}. Add
   72 |           host_vars/{{ inventory_hostname }}.yml (or
   73 |           equivalent) before running configure.
   74 | 
   75 |   tasks:
   76 |     # Was a `roles:` entry. It is an include_role purely so `apply:` can attach
   77 |     # `notify:` to every task the role runs — including the nested _reconcile
   78 |     # includes, which is where api_modify actually reports changed. Execution
   79 |     # position (after pre_tasks, before post_tasks), role arguments, and module
   80 |     # arguments are all unchanged, so apply-mode behavior is unchanged.
   81 |     - name: Reconcile the declarative baseline
   82 |       ansible.builtin.include_role:
   83 |         name: david_igou.routeros_configuration.configure
   84 |         apply:
   85 |           notify: Record that the baseline reported a change
   86 | 
   87 |     - name: Flush handlers so the drift flag is set before it is read
   88 |       ansible.builtin.meta: flush_handlers
   89 | 
   90 |   # Check mode only: publish the drift verdict as orchestrator artifacts
   91 |   # (set_stats with per_host: false is how an Automation Orchestrator workflow
   92 |   # step reads a value back out of an AAP job). Skipped entirely on the
   93 |   # routeros_configure apply template — "changed" there means "converged",
   94 |   # not "drifted", so there is no apply-mode equivalent.
   95 |   post_tasks:
   96 |     - name: Publish drift labels for the orchestrator
   97 |       ansible.builtin.set_stats:
   98 |         data:
   99 |           drift_label: "{{ 'drift' if _drifted | length > 0 else 'clean' }}"
  100 |           drift_summary: "{{ _summary[:4000] }}"
  101 |         per_host: false
  102 |         aggregate: false
  103 |       vars:
  104 |         _drifted: >-
  105 |           {{ ansible_play_hosts | map('extract', hostvars)
  106 |              | selectattr('rcfg_changed', 'defined')
  107 |              | map(attribute='inventory_hostname') | list }}
  108 |         _summary: >-
  109 |           routeros drift check ({{ ansible_play_hosts | join(', ') }}):
  110 |           {{ 'DRIFT' if _drifted | length > 0 else 'CLEAN' }}.
  111 |           {{ rcfg_ordered_paths | default([]) | length }} baseline path(s) audited in check mode.
  112 |           {% if _drifted | length > 0 %}The declarative routeros_config baseline would change {{ _drifted | join(', ') }}. Run the routeros_configure job template to converge the device, or update host_vars if the device is the source of truth; this job's diff output carries the per-path detail.{% else %}The device already matches its host_vars baseline exactly.{% endif %}
  113 |       run_once: true
  114 |       when: ansible_check_mode
```

## Handler files of the role (all, including imported)

```text
[no handler files under `handlers`]
```
