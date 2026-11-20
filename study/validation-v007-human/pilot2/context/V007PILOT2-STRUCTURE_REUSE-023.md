# Frozen source context: V007PILOT2-STRUCTURE_REUSE-023

- Repository: `silogen/cluster-bloom`
- Commit: `6122fdec7e1e0feed6081e46be0e44cd45d08809`
- Family: structure_reuse
- Rule: `ansibleguard/unnecessary-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `pkg/ansible/runtime/playbooks/tasks/deploy_cluster/logrotate.yaml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`pkg/ansible/runtime/playbooks/tasks/deploy_cluster/logrotate.yaml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–156 of 156:

```text
    1 | ---
    2 | # Purpose: Configure log rotation for system and RKE2 logs
    3 | # Dependencies: None (system configuration)
    4 | # Usage: Imported by deploy_cluster/main.yaml
    5 | # Tags: [logging, deploy_cluster]
    6 | 
    7 | # Not /etc/logrotate.d: these configs name /var/log/syslog and /var/log/kern.log,
    8 | # which the distro's own rsyslog config already covers. logrotate refuses a
    9 | # duplicate log entry and aborts the whole run with "found error in file rsyslog,
   10 | # skipping", so the daily logrotate.service fails and nothing under
   11 | # /etc/logrotate.d gets rotated. They are driven by /etc/cron.d/logrotate-bloom
   12 | # with an explicit path, so a directory outside the include is enough.
   13 | - name: Create bloom logrotate directory
   14 |   file:
   15 |     path: /etc/logrotate-bloom.d
   16 |     state: directory
   17 |     mode: "0755"
   18 | 
   19 | - name: Create iSCSI aggressive logrotate config
   20 |   copy:
   21 |     content: |
   22 |       # /etc/logrotate-bloom.d/iscsi-aggressive.conf
   23 |       /var/log/kern.log
   24 |       /var/log/syslog
   25 |       {
   26 |           # /var/log is root:syslog 775, which logrotate refuses to rotate into
   27 |           # unless it is told whom to become. /etc/logrotate.conf carries the
   28 |           # same "su root adm", but the cron job runs logrotate against this
   29 |           # file alone and so never reads it: without this line every run ends
   30 |           # in "skipping ... because parent directory has insecure permissions"
   31 |           # and syslog is never rotated at all.
   32 |           su root adm
   33 |           size 200M
   34 |           rotate 10
   35 |           compress
   36 |           delaycompress
   37 |           missingok
   38 |           notifempty
   39 |           create 0640 syslog adm
   40 |           # No dateext. A size condition rotates more than once a day on a
   41 |           # busy node, and dateext names every archive after the day alone,
   42 |           # so the second rotation of a day collides with the first and is
   43 |           # skipped. The numbered suffix has no such limit and it is what
   44 |           # the distribution uses for every other log here.
   45 |           postrotate
   46 |               /usr/lib/rsyslog/rsyslog-rotate
   47 |           endscript
   48 |       }
   49 |     dest: /etc/logrotate-bloom.d/iscsi-aggressive.conf
   50 |     mode: "0644"
   51 | 
   52 | - name: Create RKE2 logrotate config
   53 |   copy:
   54 |     content: |
   55 |       /var/lib/rancher/rke2/agent/containerd/containerd.log
   56 |       {
   57 |           size 100M
   58 |           rotate 5
   59 |           compress
   60 |           delaycompress
   61 |           missingok
   62 |           notifempty
   63 |           create 0640 root root
   64 |           # No dateext, for the reason given on the iSCSI config above.
   65 |       }
   66 |     dest: /etc/logrotate-bloom.d/rke2.conf
   67 |     mode: "0644"
   68 | 
   69 | # The extensionless names are from the first version of this task, which was
   70 | # documented as "sudo cp ... /etc/logrotate.d/iscsi-aggressive". A later
   71 | # version switched to a .conf suffix without removing them, so int-test still
   72 | # carries both plus an .bak, and each one duplicates the same two log paths.
   73 | # One stale copy is enough to abort the whole logrotate run, so remove every
   74 | # name this task has ever written.
   75 | - name: Remove logrotate configs written by earlier bloom versions
   76 |   file:
   77 |     path: "/etc/logrotate.d/{{ item }}"
   78 |     state: absent
   79 |   loop:
   80 |     - iscsi-aggressive.conf
   81 |     - iscsi-aggressive
   82 |     - iscsi-aggressive.bak
   83 |     - rke2.conf
   84 |     - rke2
   85 | 
   86 | # Neither job runs on minute 0, and no two of them share a minute. Both use
   87 | # logrotate's default state file /var/lib/logrotate/status, and logrotate
   88 | # takes an exclusive lock on it: a second logrotate that starts while the
   89 | # first still holds the lock exits with "error: state file
   90 | # /var/lib/logrotate/status is already locked". Three runs used to meet on
   91 | # minute 0, the two below plus the distribution logrotate.service, which
   92 | # logrotate.timer starts at 00:00. The error is collected in
   93 | # /var/log/logrotate-bloom.log.
   94 | #
   95 | # No -f on either command. -f forces the rotation whatever the config says,
   96 | # so "size 200M" and "size 100M" below never applied: every run rotated, and
   97 | # with the dateext the configs used to carry, only the first run of a day
   98 | # could, the rest ending in "destination /var/log/syslog-<date> already
   99 | # exists, skipping rotation". Without -f logrotate rotates when the file
  100 | # passes the size, which is what the two configs were written for.
  101 | #
  102 | # Offsets rather than a state file for each job: the iSCSI config and the
  103 | # distribution rsyslog config both name /var/log/syslog and /var/log/kern.log,
  104 | # and the one shared state file is what stops the size rotation here and the
  105 | # weekly rotation there from rotating the same file twice.
  106 | - name: Create logrotate cron job
  107 |   copy:
  108 |     content: |
  109 |       # Managed by Ansible - cluster-bloom
  110 |       SHELL=/bin/sh
  111 |       PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
  112 | 
  113 |       # iSCSI logrotate - runs every 10 minutes, on minutes 1 to 51
  114 |       1,11,21,31,41,51 * * * * root /usr/sbin/logrotate /etc/logrotate-bloom.d/iscsi-aggressive.conf >> /var/log/logrotate-bloom.log 2>&1
  115 | 
  116 |       # logrotate for RKE2 logs - runs hourly, on minute 5
  117 |       5 * * * * root /usr/sbin/logrotate /etc/logrotate-bloom.d/rke2.conf >> /var/log/logrotate-bloom.log 2>&1
  118 |     dest: /etc/cron.d/logrotate-bloom
  119 |     mode: "0644"
  120 | 
  121 | - name: Configure rsyslog rate limiting
  122 |   block:
  123 |     # No module(load="imuxsock" ...) here: /etc/rsyslog.conf already loads
  124 |     # imuxsock, a second load is rejected with "module 'imuxsock' already in
  125 |     # this config", and the parameter was spelled SysSockRateLimit.Interval
  126 |     # rather than SysSock.RateLimit.Interval, so it never applied either.
  127 |     #
  128 |     # No dynaFile="default" on the action: omfile takes file or dynaFile, not
  129 |     # both, and no template named 'default' exists, so rsyslog disabled the
  130 |     # action and the rate limit never took effect.
  131 |     - name: Create rsyslog iSCSI filter
  132 |       copy:
  133 |         content: |
  134 |           # /etc/rsyslog.d/01-iscsi-filter.conf
  135 |           ruleset(name="iscsi_ratelimit") {
  136 |               if ($msg contains "detected conn error") or
  137 |               ($msg contains "session recovery timed out") or
  138 |               ($msg contains "longhorn") then {
  139 |                   action(type="omfile"
  140 |                       file="/var/log/syslog"
  141 |                       action.execOnlyEveryNthTime="500"
  142 |                       action.execOnlyEveryNthTimeTimeout="1200"
  143 |                   )
  144 |                   stop
  145 |               }
  146 |           }
  147 |         dest: /etc/rsyslog.d/01-iscsi-filter.conf
  148 |         mode: "0644"
  149 |       notify: Restart rsyslog
  150 |   tags: [logging, deploy_cluster]
  151 | 
  152 | - name: Ensure cron is running
  153 |   service:
  154 |     name: cron
  155 |     state: started
  156 |     enabled: yes
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `.`; 476 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: no
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

Listing exceeds 400: paths beside the cited file, then a per-directory count of ALL paths.
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/certificates.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/cilium_agent_ready.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/cilium_config.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/cluster_ready.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/docker_registry.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/join_command.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/k8s_tools.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/kubeconfig.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/kubeconfig_cluster_name.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/logrotate.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/main.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/node_labels.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/prepare_rke2.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/rke2_control_plane.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/rke2_first_node.yaml
pkg/ansible/runtime/playbooks/tasks/deploy_cluster/rke2_worker.yaml

Per-directory path counts:
.: 14
.github: 1
.github/workflows: 3
cmd: 6
cmd/web/static: 1
cmd/web/static/css: 1
cmd/web/static/js: 5
docs: 22
docs/examples: 1
experimental: 1
licenses: 1
licenses/crypto/internal/boring: 1
licenses/github.com/davecgh/go-spew/spew: 1
licenses/github.com/emicklei/go-restful/v3: 1
licenses/github.com/fsnotify/fsnotify: 1
licenses/github.com/fxamacker/cbor/v2: 1
licenses/github.com/gdamore/encoding: 1
licenses/github.com/gdamore/tcell/v2: 1
licenses/github.com/go-logr/logr: 1
licenses/github.com/go-openapi/jsonpointer: 1
licenses/github.com/go-openapi/jsonreference: 1
licenses/github.com/go-openapi/swag: 1
licenses/github.com/gogo/protobuf: 1
licenses/github.com/golang/protobuf: 1
licenses/github.com/google/gnostic-models: 1
licenses/github.com/google/go-cmp/cmp: 1
licenses/github.com/google/gofuzz: 1
licenses/github.com/google/uuid: 1
licenses/github.com/hashicorp/hcl: 15
licenses/github.com/hashicorp/hcl/.github: 1
licenses/github.com/hashicorp/hcl/hcl/ast: 3
licenses/github.com/hashicorp/hcl/hcl/fmtcmd: 2
licenses/github.com/hashicorp/hcl/hcl/fmtcmd/test-fixtures: 4
licenses/github.com/hashicorp/hcl/hcl/parser: 4
licenses/github.com/hashicorp/hcl/hcl/parser/test-fixtures: 30
licenses/github.com/hashicorp/hcl/hcl/printer: 3
licenses/github.com/hashicorp/hcl/hcl/printer/testdata: 37
licenses/github.com/hashicorp/hcl/hcl/scanner: 2
licenses/github.com/hashicorp/hcl/hcl/strconv: 2
licenses/github.com/hashicorp/hcl/hcl/test-fixtures: 15
licenses/github.com/hashicorp/hcl/hcl/token: [REDACTED_LITERAL]
licenses/github.com/hashicorp/hcl/json/parser: 3
licenses/github.com/hashicorp/hcl/json/parser/test-fixtures: 7
licenses/github.com/hashicorp/hcl/json/scanner: 2
licenses/github.com/hashicorp/hcl/json/test-fixtures: 4
licenses/github.com/hashicorp/hcl/json/token: [REDACTED_LITERAL]
licenses/github.com/hashicorp/hcl/test-fixtures: 55
licenses/github.com/hashicorp/hcl/testhelper: 1
licenses/github.com/josharian/intern: 1
licenses/github.com/json-iterator/go: 1
licenses/github.com/lucasb-eyer/go-colorful: 1
licenses/github.com/magiconair/properties: 1
licenses/github.com/mailru/easyjson: 1
licenses/github.com/mattn/go-runewidth: 1
licenses/github.com/mitchellh/mapstructure: 1
licenses/github.com/modern-go/concurrent: 1
licenses/github.com/modern-go/reflect2: 1
licenses/github.com/munnerz/goautoneg: 1
licenses/github.com/pelletier/go-toml/v2: 1
licenses/github.com/pkg/errors: 1
licenses/github.com/rivo/tview: 1
licenses/github.com/rivo/uniseg: 1
licenses/github.com/sagikazarmark/slog-shim: 1
licenses/github.com/silogen/cluster-bloom: 1
licenses/github.com/sirupsen/logrus: 1
licenses/github.com/spf13/afero: 1
licenses/github.com/spf13/cast: 1
licenses/github.com/spf13/cobra: 1
licenses/github.com/spf13/pflag: 1
licenses/github.com/spf13/viper: 1
licenses/github.com/subosito/gotenv: 1
licenses/github.com/x448/float16: 1
licenses/golang.org/x/net: 1
licenses/golang.org/x/oauth2: 1
licenses/golang.org/x/sys/unix: 1
licenses/golang.org/x/term: 1
licenses/golang.org/x/text: 1
licenses/golang.org/x/time/rate: 1
licenses/google.golang.org/protobuf: 1
licenses/gopkg.in/evanphx/json-patch.v4: 1
licenses/gopkg.in/inf.v0: 1
licenses/gopkg.in/ini.v1: 1
licenses/gopkg.in/yaml.v3: 2
licenses/k8s.io/api: 1
licenses/k8s.io/apimachinery/pkg: 1
licenses/k8s.io/apimachinery/third_party/forked/golang: 1
licenses/k8s.io/client-go: 1
licenses/k8s.io/klog/v2: 1
licenses/k8s.io/kube-openapi/pkg: 1
licenses/k8s.io/kube-openapi/pkg/internal/third_party/go-json-experiment/json: 1
licenses/k8s.io/kube-openapi/pkg/validation/spec: 1
licenses/k8s.io/utils: 1
licenses/k8s.io/utils/internal/third_party/forked/golang/net: 1
licenses/sigs.k8s.io/json: 1
licenses/sigs.k8s.io/structured-merge-diff/v4: 1
licenses/sigs.k8s.io/yaml: 1
licenses/sigs.k8s.io/yaml/goyaml.v2: 2
licenses/vendor/golang.org/x/crypto: 1
licenses/vendor/golang.org/x/net: 1
licenses/vendor/golang.org/x/text: 1
pkg/ansible/runtime: 19
pkg/ansible/runtime/manifests/local-path: 5
pkg/ansible/runtime/manifests/longhorn: 4
pkg/ansible/runtime/manifests/scripts: 1
pkg/ansible/runtime/playbooks: 4
pkg/ansible/runtime/playbooks/tasks: 4
pkg/ansible/runtime/playbooks/tasks/deploy_cluster: 16
pkg/ansible/runtime/playbooks/tasks/deploy_clusterforge: 7
pkg/ansible/runtime/playbooks/tasks/deploy_k8s_apps: 8
pkg/ansible/runtime/playbooks/tasks/prepare_node: 15
pkg/ansible/runtime/playbooks/tasks/update: 9
pkg/ansible/runtime/playbooks/tasks/update_certificate: 1
pkg/ansible/runtime/playbooks/tasks/validate_node: 5
pkg/config: 16
pkg/ssh: 1
pkg/webui: 3
tests/ansible: 6
tests/ansible/library: 4
tests/ansible/playbooks: 4
tests/ansible/unit: 7
tests/qemu: 5
tests/robot: 9
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- blocks in file: 1; blocks containing exactly one task: 1
  - block at line 121: block-level keys ['name', 'tags']; justifying keys ['tags']
```
