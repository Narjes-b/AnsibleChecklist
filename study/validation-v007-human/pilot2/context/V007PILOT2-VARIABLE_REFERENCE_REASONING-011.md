# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-011

- Repository: `theforeman/forklift`
- Commit: `ee24dec347fc0a785d22989fd1a183393fa4e054`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `pipelines/upgrade/09-proxy_to_final.yml` (reported anchor line 20)
- Flagged construct: variable `pipeline_type`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–24 of 24:

```text
    1 | ---
    2 | - name: upgrade proxy to final version
    3 |   hosts:
    4 |     - "{{ forklift_proxy_name }}"
    5 |   become: yes
    6 |   vars:
    7 |     foreman_proxy_content_upgrade: True
    8 |     foreman_proxy_content_server: "{{ forklift_server_name }}"
    9 |   vars_files:
   10 |     - ../vars/forklift_{{ pipeline_type }}.yml
   11 |     - ../vars/upgrade_base.yml
   12 |     - ../vars/repos_staging.yml
   13 |   roles:
   14 |     - role: forklift_versions
   15 |       scenario: "{{ pipeline_type }}"
   16 |       scenario_os: "{{ pipeline_os }}"
   17 |       scenario_version: "{{ pipeline_version }}"
   18 |       upgrade: True
   19 |     - role: forklift_versions
   20 |       scenario: "{{ pipeline_type }}"
   21 |       scenario_os: "{{ pipeline_os }}"
   22 |       scenario_version: "{{ forklift_upgrade_version_final }}"
   23 |     - foreman_server_repositories
   24 |     - foreman_proxy_content
```

## Visible variable references

```text
Whole-word search for `pipeline_type`: 64 matches in 27 files; 4 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
pipelines/vars/common/foreman_nightly_centos_stream_9.yml:2:pipeline_type: foreman
pipelines/vars/common/katello_nightly_centos_stream_9.yml:2:pipeline_type: katello
pipelines/vars/puppet_base.yml:1:pipeline_type: foreman
roles/forklift_versions/molecule/default/verify.yml:9:    pipeline_type: katello

Other references:
pipelines/clone/01-boxes.yml:6:    - ../vars/forklift_{{ pipeline_type }}.yml
pipelines/foreman_split_puppet.yml:18:      scenario: "{{ pipeline_type }}"
pipelines/foreman_split_puppet.yml:31:      scenario: "{{ pipeline_type }}"
pipelines/foreman_split_puppet.yml:57:      scenario: "{{ pipeline_type }}"
pipelines/foreman_split_puppet.yml:78:      scenario: "{{ pipeline_type }}"
pipelines/foreman_split_puppet.yml:109:      scenario: "{{ pipeline_type }}"
pipelines/install/01-boxes.yml:6:    - ../vars/forklift_{{ pipeline_type }}.yml
pipelines/install/02-setup.yml:15:      scenario: "{{ pipeline_type }}"
pipelines/install/03-install_server.yml:11:      scenario: "{{ pipeline_type }}"
pipelines/install/04-install_proxy.yml:24:      scenario: "{{ pipeline_type }}"
pipelines/install/05-tests.yml:14:      scenario: "{{ pipeline_type }}"
pipelines/install/05-tests.yml:18:      when: pipeline_type != 'foreman'
pipelines/upgrade/01-boxes.yml:6:    - ../vars/forklift_{{ pipeline_type }}.yml
pipelines/upgrade/02-setup.yml:15:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/02-setup.yml:20:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/03-install_server.yml:11:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/03-install_server.yml:16:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/04-install_proxy.yml:23:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/04-install_proxy.yml:28:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/05-server_to_intermediate.yml:7:    - ../vars/forklift_{{ pipeline_type }}.yml
pipelines/upgrade/05-server_to_intermediate.yml:14:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/05-server_to_intermediate.yml:19:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/06-proxy_to_intermediate.yml:7:    - ../vars/forklift_{{ pipeline_type }}.yml
pipelines/upgrade/06-proxy_to_intermediate.yml:15:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/06-proxy_to_intermediate.yml:20:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/07-server_to_final.yml:9:    - ../vars/forklift_{{ pipeline_type }}.yml
pipelines/upgrade/07-server_to_final.yml:14:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/07-server_to_final.yml:19:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/08-tests.yml:17:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/08-tests.yml:22:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/08-tests.yml:26:      when: pipeline_type != 'foreman'
pipelines/upgrade/08-tests.yml:29:        - pipeline_type != 'foreman'
pipelines/upgrade/08-tests.yml:30:        - pipeline_type != 'plugins'
pipelines/upgrade/09-proxy_to_final.yml:10:    - ../vars/forklift_{{ pipeline_type }}.yml
pipelines/upgrade/09-proxy_to_final.yml:15:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/09-proxy_to_final.yml:20:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/10-tests.yml:13:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/10-tests.yml:18:      scenario: "{{ pipeline_type }}"
pipelines/upgrade/10-tests.yml:22:      when: pipeline_type != 'foreman'
pipelines/vars/clone_base.yml:1:forklift_name: "pipe-{{ pipeline_type }}-{{ pipeline_version }}-{{ pipeline_os }}"
pipelines/vars/clone_base.yml:2:forklift_server_name: "pipe-{{ pipeline_type }}-server-{{ pipeline_version }}-{{ pipeline_os }}"
pipelines/vars/install_base.yml:2:forklift_name: "pipe-{{ pipeline_type }}-{{ pipeline_version }}-{{ pipeline_os }}"
pipelines/vars/install_base.yml:3:forklift_server_name: "pipe-{{ pipeline_type }}-server-{{ pipeline_version }}-{{ pipeline_os }}"
pipelines/vars/install_base.yml:4:forklift_proxy_name: "pipe-{{ pipeline_type }}-proxy-{{ pipeline_version }}-{{ pipeline_os }}"
pipelines/vars/install_base.yml:5:forklift_smoker_name: "pipe-{{ pipeline_type }}-smoker-{{ pipeline_version }}-{{ pipeline_os }}"
pipelines/vars/puppet_base.yml:14:forklift_name: "pipeline-{{ pipeline_type }}-{{ pipeline_version }}-{{ pipeline_os }}-split-puppet"
pipelines/vars/puppet_base.yml:15:forklift_server_name: "pipeline-{{ pipeline_type }}-{{ pipeline_version }}-{{ pipeline_os }}-server"
pipelines/vars/puppet_base.yml:16:forklift_proxy_name: "pipeline-{{ pipeline_type }}-{{ pipeline_version }}-{{ pipeline_os }}-proxy"
pipelines/vars/puppet_base.yml:17:forklift_puppet_name: "pipeline-{{ pipeline_type }}-{{ pipeline_version }}-{{ pipeline_os }}-puppet"
pipelines/vars/upgrade_base.yml:2:forklift_name: "pipe-upgrade-{{ pipeline_type }}-{{ pipeline_version}}-{{ pipeline_os }}"
pipelines/vars/upgrade_base.yml:3:forklift_server_name: "pipe-up-{{ pipeline_type }}-{{ pipeline_version}}-{{ pipeline_os }}"
pipelines/vars/upgrade_base.yml:4:forklift_proxy_name: "pipe-up-{{ pipeline_type }}-proxy-{{ pipeline_version}}-{{ pipeline_os }}"
pipelines/vars/upgrade_base.yml:5:forklift_smoker_name: "pipe-up-{{ pipeline_type }}-smoker-{{ pipeline_version }}-{{ pipeline_os }}"
playbooks/collect_debug.yml:6:    remote_dir: "/tmp/debug-{{ pipeline_type | default('foreman') }}-{{ pipeline_version | default('nightly') }}-{{ pipeline_os | default('el7') }}-{{ pipeline_action | default('install') }}"
roles/bats/defaults/main.yml:11:bats_remote_dir: "/tmp/debug-{{ pipeline_type | default('foreman') }}-{{ pipeline_version | default('nightly') }}-{{ pipeline_os | default('el7') }}-{{ pipeline_action | default('install') }}"
roles/forklift_versions/molecule/default/verify.yml:16:        scenario: "{{ pipeline_type }}"
roles/forklift_versions/molecule/default/verify.yml:31:        scenario: "{{ pipeline_type }}"
roles/forklift_versions/molecule/default/verify.yml:46:        scenario: "{{ pipeline_type }}"
roles/forklift_versions/molecule/default/verify.yml:61:        scenario: "{{ pipeline_type }}"
roles/sos_report/defaults/main.yml:4:sosreport_local_dir: "/tmp/debug-{{ pipeline_type | default('foreman') }}-{{ pipeline_version | default('nightly') }}-{{ pipeline_os | default('el7') }}-{{ pipeline_action | default('install') }}"
```
