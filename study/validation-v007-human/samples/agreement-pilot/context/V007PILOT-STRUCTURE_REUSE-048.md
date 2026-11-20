# Frozen source context: V007PILOT-STRUCTURE_REUSE-048

- Repository: `dfroberg/cluster`
- Commit: `7bc521db65db986a2deef35ea955704bb0621dbd`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `provision/ansible/kubernetes/playbooks/kubernetes/k3s-nuke.yml` (reported anchor line 1)
- Object: `source_location` `2d42d1a2a77a726d5d163d8d861df5b40e83bb1c364987b939588cff6d91f268`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–181 of 181:

```text
    1 | ---
    2 | - hosts:
    3 |     - master
    4 |     - worker
    5 |     - storage
    6 |     - postgres
    7 |   become: true
    8 |   gather_facts: true
    9 |   serial: "{{ SERIAL_COUNT | default('100%') }}"
   10 |   any_errors_fatal: true
   11 |   pre_tasks:
   12 |     - setup:
   13 |       register: setup_status
   14 |       until: setup_status is success
   15 |       delay: 10
   16 |       retries: 30
   17 |     - block:
   18 |         - stat: path=/var/run/reboot-required
   19 |           register: reboot_required
   20 |           check_mode: no
   21 |       when: allow_reboot is not defined or (allow_reboot is defined and allow_reboot == true)
   22 |   post_tasks:
   23 |     - block:
   24 |         - stat: path=/var/run/reboot-required
   25 |           register: reboot_required
   26 |           check_mode: no
   27 | 
   28 |         - name: "Restart Server"
   29 |           reboot:
   30 |             msg: "Reboot Ansible-Playbook after update"
   31 |             reboot_timeout: 3600
   32 |           register: result
   33 |           when: reboot_required.stat.exists
   34 | 
   35 |         - name: "Info if Reboot was sucessful"
   36 |           debug:
   37 |             msg: "{{ inventory_hostname }} has rebooted: {{ result.rebooted }}, it has taken: {{ result.elapsed }} seconds"
   38 |           when: reboot_required.stat.exists
   39 |       when: allow_reboot is not defined or (allow_reboot is defined and allow_reboot == true)
   40 | 
   41 |   tasks:
   42 |     - name: Nuke iptables on all nodes F
   43 |       ansible.builtin.command:
   44 |         cmd: iptables -F
   45 |       when:
   46 |         - ansible_hostname != "postgres"
   47 |     - name: Nuke iptables on all nodes X
   48 |       ansible.builtin.command:
   49 |         cmd: iptables -X
   50 |       when:
   51 |         - ansible_hostname != "postgres"
   52 | 
   53 |     - name: Remove containerd-hack
   54 |       ansible.builtin.file:
   55 |         path: /etc/systemd/system/containerd-hack.service
   56 |         state: absent
   57 |       notify:
   58 |         - Reload systemd daemon
   59 |       when:
   60 |         - ansible_hostname != "postgres"
   61 |     - name: Gather ramdisk backups to delete
   62 |       find:
   63 |         paths: /var/ramdisk-backup/
   64 |         patterns: "*"
   65 |       register: files_to_delete
   66 |       when:
   67 |         - ansible_hostname != "postgres"
   68 |     - name: Delete ramdisk backup files
   69 |       ansible.builtin.file:
   70 |         path: "{{ item.path }}"
   71 |         state: absent
   72 |       loop: "{{ files_to_delete.files }}"
   73 |       when:
   74 |         - ansible_hostname != "postgres"
   75 | 
   76 |     - name: Ensure /var/ramdisk-backup is not there
   77 |       ansible.builtin.file:
   78 |         state: absent
   79 |         path: "{{ item }}"
   80 |       loop:
   81 |         - "/var/ramdisk-backup"
   82 |       when:
   83 |         - ansible_hostname != "postgres"
   84 | 
   85 |     - name: Kill k3s
   86 |       ansible.builtin.command: /usr/local/bin/k3s-killall.sh
   87 |       when:
   88 |         - ansible_hostname != "postgres"
   89 |     - name: Uninstall k3s
   90 |       ansible.builtin.command:
   91 |         cmd: /usr/local/bin/k3s-uninstall.sh
   92 |         removes: /usr/local/bin/k3s-uninstall.sh
   93 |       when:
   94 |         - ansible_hostname != "postgres"
   95 |     - name: Uninstall k3s agent
   96 |       ansible.builtin.command:
   97 |         cmd: /usr/local/bin/k3s-agent-uninstall.sh
   98 |         removes: /usr/local/bin/k3s-agent-uninstall.sh
   99 |       when:
  100 |         - ansible_hostname != "postgres"
  101 |     - name: Gather list of CNI files to delete
  102 |       find:
  103 |         paths: /etc/cni/net.d
  104 |         patterns: "*"
  105 |       register: files_to_delete
  106 |       when:
  107 |         - ansible_hostname != "postgres"
  108 |     - name: Delete CNI files
  109 |       ansible.builtin.file:
  110 |         path: "{{ item.path }}"
  111 |         state: absent
  112 |       loop: "{{ files_to_delete.files }}"
  113 |       when:
  114 |         - ansible_hostname != "postgres"
  115 | 
  116 |     - name: Gather list of /var/lib/rancher files to delete
  117 |       find:
  118 |         paths: /var/lib/rancher
  119 |         patterns: "*"
  120 |       register: rancher_files_to_delete
  121 |       when:
  122 |         - ansible_hostname != "postgres"
  123 |     - name: Delete /var/lib/rancher files
  124 |       ansible.builtin.file:
  125 |         path: "{{ item.path }}"
  126 |         state: absent
  127 |       loop: "{{ rancher_files_to_delete.files }}"
  128 |       when:
  129 |         - ansible_hostname != "postgres"
  130 | 
  131 |     - name: Gather list of /var/lib/kubelet files to delete
  132 |       find:
  133 |         paths: /var/lib/kubelet
  134 |         patterns: "*"
  135 |       register: kubelet_files_to_delete
  136 |       when:
  137 |         - ansible_hostname != "postgres"
  138 |     - name: Delete /var/lib/kubelet files
  139 |       ansible.builtin.file:
  140 |         path: "{{ item.path }}"
  141 |         state: absent
  142 |       loop: "{{ kubelet_files_to_delete.files }}"
  143 |       when:
  144 |         - ansible_hostname != "postgres"
  145 | 
  146 |     - name: Gather list of /var/lib/longhorn files to delete
  147 |       find:
  148 |         paths: /var/lib/longhorn
  149 |         patterns: "*"
  150 |       register: longhorn_files_to_delete
  151 |       when:
  152 |         - ansible_hostname != "postgres"
  153 |     - name: Delete /var/lib/longhorn files
  154 |       ansible.builtin.file:
  155 |         path: "{{ item.path }}"
  156 |         state: absent
  157 |       loop: "{{ longhorn_files_to_delete.files }}"
  158 |       when:
  159 |         - ansible_hostname != "postgres"
  160 |     - name: Truncate kine table in cluster database
  161 |       ansible.builtin.command:
  162 |         cmd: sudo -i -u postgres psql cluster -c "truncate kine;"
  163 |       when:
  164 |         - ansible_hostname == "postgres"
  165 |     - name: Delete extra files
  166 |       ansible.builtin.file:
  167 |         path: '{{ item }}'
  168 |         state: absent
  169 |       with_items:
  170 |         - /usr/local/bin/cilium
  171 |         - /usr/local/bin/flux
  172 |         - /etc/systemd/system/k3s-killall.service
  173 |         - /usr/local/bin/kubectl
  174 |         - /usr/local/bin/kustomize
  175 |         - /usr/local/bin/calicoctl
  176 |       when:
  177 |         - ansible_hostname != "postgres"
  178 |   handlers:
  179 |     - name: Reload systemd daemon
  180 |       systemd:
  181 |         daemon-reload: true
```

## Frozen tracked paths in the relevant role/scope

```text
.gitattributes
.github/CODEOWNERS
.github/ISSUE_TEMPLATE/bug-report.md
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/feature-request.md
.github/ISSUE_TEMPLATE/question.md
.github/PULL_REQUEST_TEMPLATE.md
.github/dfroberg.yaml
.github/lint/.ansible-lint
.github/lint/.markdownlint.yaml
.github/lint/.prettierignore
.github/lint/.prettierrc.yaml
.github/lint/.tflint.hcl
.github/lint/.yamllint.yaml
.github/renovate.json5
.github/renovate/autoMerge.json
.github/renovate/labels.json
.github/renovate/semanticCommits.json
.github/workflows/diff-helm-releases.yaml
.github/workflows/flux-upgrade-schedule.yaml
.github/workflows/helm-dep-update-schedule.yaml
.github/workflows/invalid-template.yaml
.github/workflows/lint-markdown.yaml
.github/workflows/lint-shell.yaml
.github/workflows/lint-yaml.yaml
.github/workflows/publish-docs.yaml
.github/workflows/renovate-annotations-schedule.yaml
.github/workflows/support.yaml
.gitignore
.pre-commit-config.yaml
.sops.yaml
.taskfiles/ansible.yml
.taskfiles/cluster.yml
.taskfiles/docker.yml
.taskfiles/etcd.yml
.taskfiles/flux.yml
.taskfiles/format.yml
.taskfiles/lint.yml
.taskfiles/pre-commit.yml
.taskfiles/terraform.yml
.taskfiles/velero.yml
LICENSE
README.md
Taskfile.yml
charts/kah-common/Chart.lock
charts/kah-common/Chart.yaml
charts/kah-common/charts/common-4.5.2.tgz
charts/kah-common/templates/common.yaml
cluster/apps/collab/bookstack/export-job.yaml
cluster/apps/collab/bookstack/helm-release.yaml
cluster/apps/collab/bookstack/kustomization.yaml
cluster/apps/collab/bookstack/volumes.yaml
cluster/apps/collab/gollum/helm-release.yaml
cluster/apps/collab/gollum/kustomization.yaml
cluster/apps/collab/gollum/volume.yaml
cluster/apps/collab/joplin/helm-release.yaml
cluster/apps/collab/joplin/joplin-postgresql-secret.enc.yaml
cluster/apps/collab/joplin/kustomization.yaml
cluster/apps/collab/kustomization.yaml
cluster/apps/collab/recipes/helm-release.yaml
cluster/apps/collab/recipes/kustomization.yaml
cluster/apps/collab/recipes/volume.yaml
cluster/apps/collab/rxresume/helm-release.yaml
cluster/apps/collab/rxresume/kustomization.yaml
cluster/apps/collab/teamspeak/helm-release.yaml
cluster/apps/collab/teamspeak/kustomization.yaml
cluster/apps/collab/teamspeak/teamspeak-data-pvc.yaml
cluster/apps/collab/vikunja/config-map.yaml
cluster/apps/collab/vikunja/helm-release.yaml
cluster/apps/collab/vikunja/kustomization.yaml
cluster/apps/collab/vikunja/vikunja-files-pvc.yaml
cluster/apps/collab/vikunja/vikunja-postgresql-pvc.yaml
cluster/apps/collab/yourls/helm-release.yaml
cluster/apps/collab/yourls/kustomization.yaml
cluster/apps/collab/yourls/yourls-config-pvc.yaml
cluster/apps/collab/yourls/yourls-mysql-pvc.yaml
cluster/apps/comms/kustomization.yaml
cluster/apps/comms/matrix-media-repo/configmap.yaml
cluster/apps/comms/matrix-media-repo/helm-release.yaml
cluster/apps/comms/matrix-media-repo/kustomization.yaml
cluster/apps/comms/matrix-media-repo/matrix-media-repo-postgresql-pvc.yaml
cluster/apps/comms/matrix-slack/config.yaml
cluster/apps/comms/matrix-slack/helm-release.yaml
cluster/apps/comms/matrix-slack/kustomization.yaml
cluster/apps/comms/matrix-slack/matrix-slack-postgresql-pvc.yaml
cluster/apps/comms/matrix-synapse-admin/helm-release.yaml
cluster/apps/comms/matrix-synapse-admin/kustomization.yaml
cluster/apps/comms/matrix-synapse/helm-release.yaml
cluster/apps/comms/matrix-synapse/kustomization.yaml
cluster/apps/comms/matrix-synapse/matrix-media-pvc.yaml
cluster/apps/comms/matrix-synapse/postgresql-data-pvc.yaml
cluster/apps/comms/matrix-synapse/signing-key.sops.yaml
cluster/apps/comms/matrix-webhook/deployment.yaml
cluster/apps/comms/matrix-webhook/ingress.yaml
cluster/apps/comms/matrix-webhook/kustomization.yaml
cluster/apps/comms/matrix-webhook/secrets.sops.yaml
cluster/apps/comms/matrix-webhook/service.yaml
cluster/apps/comms/mautrix-facebook/config.yaml
cluster/apps/comms/mautrix-facebook/helm-release.yaml
cluster/apps/comms/mautrix-facebook/kustomization.yaml
cluster/apps/comms/mautrix-facebook/mautrix-facebook-postgresql-pvc.yaml
cluster/apps/default/hajimari/config-pvc.yaml
cluster/apps/default/hajimari/helm-release.yaml
cluster/apps/default/hajimari/ingress.yaml
cluster/apps/default/hajimari/kustomization.yaml
cluster/apps/default/kustomization.yaml
cluster/apps/default/vaultwarden/config-pvc.yaml
cluster/apps/default/vaultwarden/helm-release.yaml
cluster/apps/default/vaultwarden/kustomization.yaml
cluster/apps/default/vaultwarden/secret.sops.yaml
cluster/apps/gitlab/gitlab-cache-secrets.sops.yaml
cluster/apps/gitlab/gitlab-runner-token-secret.sops.yaml
cluster/apps/gitlab/gitlabcred.sops.yaml
cluster/apps/gitlab/helm-release.yaml
cluster/apps/gitlab/kustomization.yaml
cluster/apps/kustomization.yaml
cluster/apps/mailu/config-pvc.yaml
cluster/apps/mailu/helm-release.yaml
cluster/apps/mailu/kustomization.yaml
cluster/apps/media/bazarr/config-pvc.yaml
[listing truncated after 120 paths]
```
