# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-009

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: Maintainability/complexity
- Rule: `ansibleguard/large-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/custom/matrix_playbook_migration/tasks/validate_config.yml` (reported anchor line 600)
- Object: `task` `d55939d188d5cde54272f35de9c266fb155acb2c357cf22a5de4a69df6e54bf8`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 565–635 of 946:

```text
  565 |       The traefik role in the playbook now lives under the MASH organization (https://github.com/mother-of-all-self-hosting/ansible-role-traefik).
  566 |       The new role is pretty much the same, but uses differently named variables.
  567 | 
  568 |       Please rename all `devture_traefik_`-prefixed variables (`devture_traefik_*` -> `traefik_*`) on your configuration file (vars.yml).
  569 | 
  570 |       After renaming them, please do not forget to fetch the Ansible role. See docs/maintenance-upgrading-services.md for details about how to do so.
  571 | 
  572 |       The following variables in your configuration need to be renamed: {{ lookup('ansible.builtin.varnames', '^devture_traefik_.+', wantlist=True) | join(', ') }}
  573 |   when: "lookup('ansible.builtin.varnames', '^devture_traefik_.+', wantlist=True) | length > 0"
  574 | 
  575 | - name: (Deprecation) Catch and report devture_container_socket_proxy variables
  576 |   ansible.builtin.fail:
  577 |     msg: |-
  578 |       The container-socket-proxy role in the playbook now lives under the MASH organization (https://github.com/mother-of-all-self-hosting/ansible-role-container-socket-proxy).
  579 |       The new role is pretty much the same, but uses differently named variables.
  580 | 
  581 |       Please rename all `devture_container_socket_proxy_`-prefixed variables (`devture_container_socket_proxy_*` -> `container_socket_proxy_*`) on your configuration file (vars.yml).
  582 | 
  583 |       After renaming them, please do not forget to fetch the Ansible role. See docs/maintenance-upgrading-services.md for details about how to do so.
  584 | 
  585 |       The following variables in your configuration need to be renamed: {{ lookup('ansible.builtin.varnames', '^devture_container_socket_proxy_.+', wantlist=True) | join(', ') }}
  586 |   when: "lookup('ansible.builtin.varnames', '^devture_container_socket_proxy_.+', wantlist=True) | length > 0"
  587 | 
  588 | - name: (Deprecation) Catch and report Go-NEB variables
  589 |   ansible.builtin.fail:
  590 |     msg: |-
  591 |       Go-NEB was completely removed from the playbook in May 2026.
  592 | 
  593 |       Please remove all `matrix_bot_go_neb_*` variables from your configuration file (vars.yml).
  594 | 
  595 |       You may also wish to uninstall the bot manually. See `docs/configuring-playbook-bot-go-neb.md` for more information.
  596 | 
  597 |       The following variables in your configuration need to be removed: {{ lookup('ansible.builtin.varnames', '^matrix_bot_go_neb_.+', wantlist=True) | join(', ') }}
  598 |   when: "lookup('ansible.builtin.varnames', '^matrix_bot_go_neb_.+', wantlist=True) | length > 0"
  599 | 
  600 | - name: (Deprecation) Catch and report ma1sd variables
  601 |   ansible.builtin.fail:
  602 |     msg: |-
  603 |       ma1sd was completely removed from the playbook in February 2026.
  604 | 
  605 |       Please remove all `matrix_ma1sd_*` variables from your configuration file (vars.yml).
  606 | 
  607 |       You may also wish to uninstall the component manually. See `docs/configuring-playbook-ma1sd.md` for more information.
  608 | 
  609 |       The following variables in your configuration need to be removed: {{ lookup('ansible.builtin.varnames', '^matrix_ma1sd_.+', wantlist=True) | join(', ') }}
  610 |   when: "lookup('ansible.builtin.varnames', '^matrix_ma1sd_.+', wantlist=True) | length > 0"
  611 | 
  612 | - name: (Deprecation) Catch and report matrix-appservice-slack variables
  613 |   ansible.builtin.fail:
  614 |     msg: |-
  615 |       matrix-appservice-slack was completely removed from the playbook in February 2026.
  616 | 
  617 |       Please remove all `matrix_appservice_slack_*` variables from your configuration file (vars.yml).
  618 | 
  619 |       You may also wish to uninstall the bridge manually. See `docs/configuring-playbook-bridge-appservice-slack.md` for more information.
  620 | 
  621 |       The following variables in your configuration need to be removed: {{ lookup('ansible.builtin.varnames', '^matrix_appservice_slack_.+', wantlist=True) | join(', ') }}
  622 | 
  623 |       You might probably wish to have a look at mautrix-slack, another bridge to Slack. Refer to `docs/configuring-playbook-bridge-mautrix-slack.md` for more information.
  624 |   when: "lookup('ansible.builtin.varnames', '^matrix_appservice_slack_.+', wantlist=True) | length > 0"
  625 | 
  626 | - name: (Deprecation) Catch and report matrix-appservice-webhooks variables
  627 |   ansible.builtin.fail:
  628 |     msg: |-
  629 |       matrix-appservice-webhooks was completely removed from the playbook in November 2025.
  630 | 
  631 |       Please remove all `matrix_appservice_webhooks_*` variables from your configuration file (vars.yml).
  632 | 
  633 |       You may also wish to uninstall the bridge manually. See `docs/configuring-playbook-bridge-appservice-webhooks.md` for more information.
  634 | 
  635 |       The following variables in your configuration need to be removed: {{ lookup('ansible.builtin.varnames', '^matrix_appservice_webhooks_.+', wantlist=True) | join(', ') }}
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.
