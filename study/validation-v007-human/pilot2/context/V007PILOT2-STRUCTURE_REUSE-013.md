# Frozen source context: V007PILOT2-STRUCTURE_REUSE-013

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: structure_reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/custom/matrix-bridge-mautrix-discord/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/custom/matrix-bridge-mautrix-discord/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–25 of 25:

```text
    1 | # SPDX-FileCopyrightText: 2022 - 2023 Slavi Pantaleev
    2 | # SPDX-FileCopyrightText: 2022 MDAD project contributors
    3 | #
    4 | # SPDX-License-Identifier: AGPL-3.0-or-later
    5 | 
    6 | ---
    7 | 
    8 | - tags:
    9 |     - setup-all
   10 |     - setup-mautrix-discord
   11 |     - install-all
   12 |     - install-mautrix-discord
   13 |   block:
   14 |     - when: matrix_bridge_mautrix_discord_enabled | bool
   15 |       ansible.builtin.include_tasks: "{{ role_path }}/tasks/validate_config.yml"
   16 | 
   17 |     - when: matrix_bridge_mautrix_discord_enabled | bool
   18 |       ansible.builtin.include_tasks: "{{ role_path }}/tasks/setup_install.yml"
   19 | 
   20 | - tags:
   21 |     - setup-all
   22 |     - setup-mautrix-discord
   23 |   block:
   24 |     - when: not matrix_bridge_mautrix_discord_enabled | bool
   25 |       ansible.builtin.include_tasks: "{{ role_path }}/tasks/setup_uninstall.yml"
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/custom/matrix-bridge-mautrix-discord`; 15 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: no
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: yes

roles/custom/matrix-bridge-mautrix-discord/defaults/main.yml
roles/custom/matrix-bridge-mautrix-discord/molecule/default/converge.yml
roles/custom/matrix-bridge-mautrix-discord/molecule/default/molecule.yml
roles/custom/matrix-bridge-mautrix-discord/molecule/default/prepare.yml
roles/custom/matrix-bridge-mautrix-discord/molecule/default/requirements.yml
roles/custom/matrix-bridge-mautrix-discord/molecule/default/verify.yml
roles/custom/matrix-bridge-mautrix-discord/tasks/main.yml
roles/custom/matrix-bridge-mautrix-discord/tasks/setup_install.yml
roles/custom/matrix-bridge-mautrix-discord/tasks/setup_uninstall.yml
roles/custom/matrix-bridge-mautrix-discord/tasks/validate_config.yml
roles/custom/matrix-bridge-mautrix-discord/templates/config.yaml.j2
roles/custom/matrix-bridge-mautrix-discord/templates/config.yaml.j2.license
roles/custom/matrix-bridge-mautrix-discord/templates/labels.j2
roles/custom/matrix-bridge-mautrix-discord/templates/systemd/matrix-mautrix-discord.service.j2
roles/custom/matrix-bridge-mautrix-discord/templates/systemd/matrix-mautrix-discord.service.j2.license
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- blocks in file: 2; blocks containing exactly one task: 1
  - block at line 20: block-level keys ['tags']; justifying keys ['tags']
```
