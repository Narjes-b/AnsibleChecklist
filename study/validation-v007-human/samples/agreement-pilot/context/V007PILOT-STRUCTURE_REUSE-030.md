# Frozen source context: V007PILOT-STRUCTURE_REUSE-030

- Repository: `azimuth-cloud/ansible-collection-azimuth-ops`
- Commit: `396972118edcecb213e69497f9f2c70e7abd0611`
- Family: Structure/reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/velero/defaults/main.yml` (reported anchor line 1)
- Object: `source_location` `b1dca230d8623b314a6c4f56ea48fa649a11b6eb19ca568b4f81a480d6f806d7`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–287 of 287:

```text
    1 | ---
    2 | # Disable by default so that existing deployments don't break when bucket isn't configured
    3 | # Can be overwritten in azimuth-config as needed
    4 | velero_enabled: false
    5 | 
    6 | #####
    7 | # Velero installation and setup config
    8 | #####
    9 | 
   10 | # Velero CLI archive URL
   11 | velero_cli_repo: https://github.com/vmware-tanzu/velero
   12 | velero_cli_version: v1.18.2
   13 | velero_cli_os: "{{ ansible_system | lower }}"
   14 | velero_cli_arch: "{{ 'amd64' if ansible_architecture == 'x86_64' else ansible_architecture }}"
   15 | velero_cli_archive_name: >-
   16 |   velero-{{ velero_cli_version }}-{{ velero_cli_os }}-{{ velero_cli_arch }}.tar.gz
   17 | velero_cli_archive_url: >-
   18 |   {{ velero_cli_repo }}/releases/download/{{ velero_cli_version }}/{{ velero_cli_archive_name }}
   19 | # The directory into which the Velero CLI archive should be unpacked
   20 | velero_cli_unpack_directory: "/opt/velero/{{ velero_cli_version }}"
   21 | # The directory into which the Velero CLI binary should be placed
   22 | velero_cli_bin_directory: /usr/local/bin
   23 | 
   24 | # The trust bundle to use with the S3 endpoint
   25 | velero_trust_bundle: "{{ system_trust_ca_bundle | default('') }}"
   26 | 
   27 | # The URL endpoint for the target object store
   28 | velero_s3_url: "{{ undef(hint='velero_s3_url is required') }}"
   29 | 
   30 | # The name of a pre-existing bucket in the target object store
   31 | velero_bucket_name: "{{ undef(hint='velero_bucket_name is required') }}"
   32 | 
   33 | # The name of the s3 region to connect to.
   34 | velero_s3_region: "notused"
   35 | 
   36 | # The name to use for the secret containing the object store credentials
   37 | velero_s3_creds_secret_name: [REDACTED_LITERAL]
   38 | 
   39 | # S3 credentials
   40 | velero_aws_access_key_id: "{{ undef(hint='velero_aws_access_key_id is required') }}"
   41 | velero_aws_secret_access_key: "{{ undef(hint='velero_aws_secret_access_key is required') }}"
   42 | 
   43 | # Kubernetes CSI Snapshot Controller config
   44 | velero_csi_snapshot_controller_chart_name: snapshot-controller
   45 | velero_csi_snapshot_controller_chart_repo: https://piraeus.io/helm-charts/
   46 | velero_csi_snapshot_controller_chart_version: 5.2.0
   47 | velero_csi_snapshot_controller_release_namespace: kube-system
   48 | velero_csi_snapshot_controller_release_name: csi-snapshot-controller
   49 | velero_csi_snapshot_controller_wait_timeout: 10m
   50 | velero_csi_snapshot_controller_release_defaults: {}
   51 | velero_csi_snapshot_controller_release_overrides: {}
   52 | velero_csi_snapshot_controller_release_values: >-
   53 |   {{-
   54 |     velero_csi_snapshot_controller_release_defaults |
   55 |       combine(velero_csi_snapshot_controller_release_overrides, recursive = True)
   56 |   }}
   57 | 
   58 | velero_csi_snapshot_controller_crds:
   59 |   - volumegroupsnapshotclasses.groupsnapshot.storage.k8s.io
   60 |   - volumegroupsnapshotcontents.groupsnapshot.storage.k8s.io
   61 |   - volumegroupsnapshots.groupsnapshot.storage.k8s.io
   62 |   - volumesnapshotclasses.snapshot.storage.k8s.io
   63 |   - volumesnapshotcontents.snapshot.storage.k8s.io
   64 |   - volumesnapshots.snapshot.storage.k8s.io
   65 | 
   66 | # The name of the volume snapshot class
   67 | velero_cinder_snapshot_class_name: cinder-csi-snapshot
   68 | 
   69 | # Velero plugin config
   70 | velero_s3_plugin_image_source: velero/velero-plugin-for-aws
   71 | velero_s3_plugin_image_version: v1.14.2
   72 | 
   73 | # The default backup storage location
   74 | # We disable checksums because older Ceph doesn't implement them properly
   75 | velero_default_backup_storage_location: >-
   76 |   {{-
   77 |     {
   78 |       "name": "default",
   79 |       "default": True,
   80 |       "provider": "aws",
   81 |       "bucket": velero_bucket_name,
   82 |       "credential": [REDACTED VALUE BLOCK]
   83 |         [REDACTED ENCRYPTED VALUE]
   84 |         [REDACTED ENCRYPTED VALUE]
   85 |       },
   86 |       "config": {
   87 |         "region": velero_s3_region,
   88 |         "s3Url": velero_s3_url,
   89 |         "s3ForcePathStyle": True,
   90 |         "checksumAlgorithm": "",
   91 |       },
   92 |     } |
   93 |       combine(
   94 |         {"caCert": (velero_trust_bundle | b64encode)}
   95 |         if velero_trust_bundle
   96 |         else {}
   97 |       )
   98 |   }}
   99 | 
  100 | # Velero Helm chart config
  101 | velero_chart_name: velero
  102 | velero_chart_repo: https://vmware-tanzu.github.io/helm-charts
  103 | velero_chart_version: 12.1.0
  104 | velero_release_namespace: velero
  105 | velero_release_name: velero
  106 | velero_wait_timeout: 10m
  107 | velero_release_defaults:
  108 |   metrics:
  109 |     enabled: true
  110 |     serviceMonitor:
  111 |       enabled: true
  112 |     prometheusRule:
  113 |       enabled: true
  114 |       spec:
  115 |         - alert: VeleroBackupPartialFailures
  116 |           annotations:
  117 |             # Use raw tags to prevent Ansible trying to render it as a template
  118 |             message: >-
  119 |               {%- raw -%}
  120 |               Velero schedule '{{ $labels.schedule }}' has partially failed backups in the last 24 hours.
  121 |               {%- endraw -%}
  122 |           expr: |-
  123 |             sum(increase(velero_backup_partial_failure_total{schedule!=""}[24h])) by(schedule) > 0
  124 |           for: 15m
  125 |           labels:
  126 |             severity: warning
  127 | 
  128 |         - alert: VeleroBackupFailures
  129 |           annotations:
  130 |             # Use raw tags to prevent Ansible trying to render it as a template
  131 |             message: >-
  132 |               {%- raw -%}
  133 |               Velero schedule '{{ $labels.schedule }}' has failed backups in the last 24 hours.
  134 |               {%- endraw -%}
  135 |           expr: |-
  136 |             sum(increase(velero_backup_failure_total{schedule!=""}[24h])) by(schedule) > 0
  137 |           for: 15m
  138 |           labels:
  139 |             severity: warning
  140 |   configuration:
  141 |     features: EnableCSI
  142 |     backupStorageLocation:
  143 |       - "{{ velero_default_backup_storage_location }}"
  144 |     volumeSnapshotLocation: []
  145 |   initContainers:
  146 |     - name: velero-plugin-for-aws
  147 |       image: "{{ velero_s3_plugin_image_source }}:{{ velero_s3_plugin_image_version }}"
  148 |       imagePullPolicy: IfNotPresent
  149 |       volumeMounts:
  150 |         - mountPath: /target
  151 |           name: plugins
  152 | velero_release_overrides: {}
  153 | velero_release_values: >-
  154 |   {{-
  155 |     velero_release_defaults |
  156 |       combine(velero_release_overrides, recursive = True)
  157 |   }}
  158 | 
  159 | #####
  160 | # Velero backup config
  161 | #####
  162 | 
  163 | # Whether or not to enable the scheduled backups
  164 | # NOTE(mkjpryor)
  165 | # When set to false, the schedule objects are still created but in a paused state
  166 | # This allows ad-hoc backups to be created using the scheduled backup as a template
  167 | velero_backup_schedule_enabled: true
  168 | 
  169 | # The name of the backup schedule
  170 | velero_backup_schedule_name: default
  171 | 
  172 | # The schedule for backups, using cron syntax
  173 | # See https://en.wikipedia.org/wiki/Cron for format options
  174 | velero_backup_schedule: "{{ velero_backup_schedule_timings | default('0 0 * * *') }}"
  175 | 
  176 | # Time-to-live for backups
  177 | # See https://pkg.go.dev/time#ParseDuration for duration format options
  178 | velero_backup_ttl: "{{ velero_schedule_ttl | default('168h') }}"
  179 | 
  180 | # Configuration for the backup
  181 | #   NOTE(mkjpryor)
  182 | #   The only critical volume with persistent state is the Keycloak DB
  183 | #   Restoring the metrics and logging volumes is harder because they are managed by the
  184 | #   CAPI Helm charts so are created before we have a chance to enact a restore, and restoring
  185 | #   a volume that already exists is a no-op
  186 | 
  187 | #   List of namespaces to include/exclude in backups
  188 | #     Velero does not handle wildcards other than "*" on its own here
  189 | #     So in order to catch all the per-tenant namespaces where platform resources are created,
  190 | #     we must exclude the system namespaces that we don't want to back up
  191 | #     Essentially, the included namespaces should be az-*, keycloak-system and zenith-services
  192 | velero_backup_included_namespaces:
  193 |   - "*"
  194 | velero_backup_excluded_namespaces:
  195 |   - azimuth
  196 |   - calico-apiserver
  197 |   - calico-system
  198 |   - capi-addon-system
  199 |   - capi-janitor-system
  200 |   - capi-kubeadm-bootstrap-system
  201 |   - capi-kubeadm-control-plane-system
  202 |   - capi-system
  203 |   - capo-system
  204 |   - cert-manager
  205 |   - default
  206 |   - harbor
  207 |   - ingress-nginx
  208 |   - kube-node-lease
  209 |   - kube-public
  210 |   - kube-system
  211 |   - kubernetes-dashboard
  212 |   - monitoring-system
  213 |   - node-problem-detector
  214 |   - openstack-system
  215 |   - postgres-operator
  216 |   - tigera-operator
  217 |   - velero
  218 | #   List of cluster-scoped resources to include/exclude in backups
  219 | velero_backup_included_cluster_scoped_resources:
  220 |   - clustertypes.caas.azimuth.stackhpc.com
  221 |   - clustertemplates.azimuth.stackhpc.com
  222 |   - apptemplates.azimuth.stackhpc.com
  223 |   - persistentvolumes
  224 | velero_backup_excluded_cluster_scoped_resources: []
  225 | #   List of namespace-scoped resources to include/exclude in backups
  226 | velero_backup_included_namespace_scoped_resources:
  227 |   - "*"
  228 | velero_backup_excluded_namespace_scoped_resources:
  229 |   - events
  230 | #   The spec for the scheduled backup
  231 | velero_backup_schedule_spec_defaults:
  232 |   paused: "{{ not velero_backup_schedule_enabled }}"
  233 |   schedule: "{{ velero_backup_schedule }}"
  234 |   useOwnerReferencesInBackup: false
  235 |   template:
  236 |     includedNamespaces: "{{ velero_backup_included_namespaces }}"
  237 |     excludedNamespaces: "{{ velero_backup_excluded_namespaces }}"
  238 |     includedClusterScopedResources: "{{ velero_backup_included_cluster_scoped_resources }}"
  239 |     excludedClusterScopedResources: "{{ velero_backup_excluded_cluster_scoped_resources }}"
  240 |     includedNamespaceScopedResources: "{{ velero_backup_included_namespace_scoped_resources }}"
  241 |     excludedNamespaceScopedResources: "{{ velero_backup_excluded_namespace_scoped_resources }}"
  242 |     snapshotVolumes: true
  243 |     ttl: "{{ velero_backup_ttl }}"
  244 | velero_backup_schedule_spec_overrides: {}
  245 | velero_backup_schedule_spec: >-
  246 |   {{-
  247 |     velero_backup_schedule_spec_defaults |
  248 |       combine(velero_backup_schedule_spec_overrides, recursive = True)
  249 |   }}
  250 | 
  251 | # TODO: Configure alerts for failed backups
  252 | # See https://github.com/vmware-tanzu/helm-charts/blob/1e6a5b46a59d2dae8153fa8c0794bad84e1d63e1/charts/velero/values.yaml#L239
  253 | 
  254 | #####
  255 | # Velero restore config (applies to restore playbook)
  256 | #####
  257 | 
  258 | # Name of backup to use for restore process
  259 | # If not given, the most recent successful backup for the schedule is used
  260 | velero_restore_backup_name: "{{ undef(hint='velero_restore_backup_name is required') }}"
  261 | 
  262 | # Name of restore object to create
  263 | velero_restore_name: >-
  264 |   {{ velero_restore_backup_name }}-{{ "%Y%m%d%H%M%S" | strftime(ansible_date_time.epoch) }}
  265 | 
  266 | # Resources that require their status to be restored in order to function correctly
  267 | velero_restore_include_resource_status:
  268 |   - clusters.caas.azimuth.stackhpc.com
  269 |   - leases.scheduling.azimuth.stackhpc.com
  270 | 
  271 | velero_restore_spec_defaults:
  272 |   restoreStatus:
  273 |     includedResources: "{{ velero_restore_include_resource_status }}"
  274 |   includeClusterResources: true
  275 |   restorePVs: true
  276 |   existingResourcePolicy: update
  277 |   backupName: "{{ velero_restore_backup_name }}"
  278 | velero_restore_spec_overrides: {}
  279 | velero_restore_spec: >-
  280 |   {{-
  281 |     velero_restore_spec_defaults |
  282 |       combine(velero_restore_spec_overrides, recursive = True)
  283 |   }}
  284 | 
  285 | # If true, allow restores from partially failed backups
  286 | # If false (the default), only allow restores from backups that completed without error
  287 | velero_restore_allow_partial: "{{ not (velero_restore_strict | default(True)) }}"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/velero/defaults/main.yml
roles/velero/files/grafana_dashboard.json
roles/velero/tasks/annotate-crds.yml
roles/velero/tasks/install.yml
roles/velero/tasks/restore.yml
roles/velero/tasks/schedule.yml
```
