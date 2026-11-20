# Frozen source context: V007PILOT2-SECURITY-022

- Repository: `dryvist/ansible-proxmox-apps`
- Commit: `b179574eb875a6b7be09df83d001f623a68a2681`
- Family: security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `roles/openbao/defaults/main/01-kv-hierarchy-and-rbac.yml` (reported anchor line 78)
- Flagged construct: not named by the finding; the anchor line 78 lies in the task at line 44, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–208 of 208:

```text
    1 | ---
    2 | # --- KV hierarchy / RBAC policies + AppRoles ---------------------------------
    3 | # Secret hierarchy (see terraform-proxmox docs/SECRETS_HIERARCHY.md):
    4 | #   secret/infra/*     IaC kernel (proxmox/aws/network) — terraform-apply writes
    5 | #   secret/platform/*  shared platform services (dns/traefik/terrakube/splunk/
    6 | #                      cribl/object-storage/compute/...)
    7 | #   secret/apps/*      application credentials (media/monitoring/home-automation)
    8 | #   secret/ai/*        LLM stack + AI-agent creds
    9 | #   secret/public/*    non-secret, non-exploitable facts (domain/subdomain) —
   10 | #                      readable by a fixed, low-privilege AppRole
   11 | #   secret/ci/*        CI/CD tokens
   12 | openbao_kv_mount: secret
   13 | # Non-secret configuration mount. Holds values that are sensitive-but-not-
   14 | # exploitable — operator selections, tunables, thresholds, coordination and
   15 | # inventory-ish facts — that today sit inside the credential mounts.
   16 | #
   17 | # It is a separate MOUNT, not a path prefix, for the same reason
   18 | # secrets-external is: a prefix shares one policy namespace, so every wildcard
   19 | # already granted on `secret/` reaches across it and the boundary is decorative.
   20 | # A distinct mount is unreachable by any policy that does not name it.
   21 | #
   22 | # Named `config` rather than a `secret*` sibling deliberately: an operator
   23 | # reading `bao secrets list` sees `secret/`, `secrets-external/`, `config/` and
   24 | # can tell at a glance which mount is not a credential store. A name like
   25 | # `secrets-internal-public` would blend into the credential mounts it must be
   26 | # distinguished from.
   27 | openbao_config_mount: config
   28 | # KV v2 version retention for the config mount. Browsable history and rollback
   29 | # are half the reason this mount exists, so retention is set explicitly rather
   30 | # than left on the KV v2 default of 10. Config values are short strings that
   31 | # change rarely, so 30 versions is years of history at negligible Raft cost,
   32 | # while still bounding what a runaway writer can grow. delete_version_after is
   33 | # deliberately left at its default (0 = versions never time-expire): history
   34 | # that silently ages out is not history you can roll back to.
   35 | openbao_config_mount_max_versions: 30
   36 | # Every KV v2 mount this role provisions (add-if-missing, then tuned to the
   37 | # declared retention). `max_versions` is optional — omit it to leave a mount on
   38 | # the KV v2 default, which is what the two credential mounts do today.
   39 | openbao_kv_mounts:
   40 |   - path: "{{ openbao_kv_mount }}"
   41 |   # External-SaaS credentials; a literal here for the same reason the policy
   42 |   # templates use a literal (see tasks/init.yml).
   43 |   - path: secrets-external
   44 |   - path: "{{ openbao_config_mount }}"
   45 |     max_versions: "{{ openbao_config_mount_max_versions }}"
   46 | # Derived: the subset that declares retention. Defined once because init.yml
   47 | # zips it against its own read results — the two loops must be the same list in
   48 | # the same order, which two separate inline filters would not guarantee.
   49 | openbao_kv_tuned_mounts: >-
   50 |   {{ openbao_kv_mounts | selectattr('max_versions', 'defined') | list }}
   51 | # Legacy demo subtree the terraform-proxmox vault-secrets proof writes to; kept
   52 | # writable by the terraform-apply policy so that read/write proof keeps working.
   53 | openbao_homelab_path: homelab
   54 | 
   55 | # App secrets PROMOTED into secret/apps/<app> so OpenBao is their canonical
   56 | # home. Each app maps each KV field to the converge-env var carrying its value.
   57 | # The promote step (init.yml → promote_app_secret.yml) runs only on the
   58 | # bootstrap host under the admin token, writes only when a value differs from
   59 | # what is already stored, and skips any field whose env var is empty — so a
   60 | # converge without those values (or with unchanged values) writes nothing.
   61 | #
   62 | # Promotion vs generation: a value that ALREADY EXISTS and must keep its current
   63 | # value goes here. A value that may simply be created fresh goes in
   64 | # openbao_generated_app_secrets below. Getting this backwards on a key that
   65 | # decrypts stored data destroys that data silently.
   66 | openbao_promoted_app_secrets:[REDACTED VALUE BLOCK]
   67 |   [REDACTED ENCRYPTED VALUE]
      [... 26 further identical redacted lines, through 93]
   94 | 
   95 | # App service secrets GENERATED (random, generate-if-absent) in OpenBao itself,
   96 | # replacing the retired terraform-proxmox vault-secrets root. Each app maps to
   97 | # its field list; every field gets a random alnum value created once at
   98 | # secret/apps/<app> and never rotated (init.yml → seed_generated_app_secret.yml).
   99 | # openbao_secrets then exposes these paths to the nautobot/zammad roles.
  100 | openbao_generated_app_secrets:[REDACTED VALUE BLOCK]
  101 |   [REDACTED ENCRYPTED VALUE]
      [... 97 further identical redacted lines, through 198]
  199 | # Random length for generated app credentials (alnum). secret_key needs more
  200 | # entropy than a login credential, so it gets its own length (matches the 64-char
  201 | # key the nautobot role generates locally when none is supplied).
  202 | openbao_app_secret_length: [REDACTED_LITERAL]
  203 | openbao_app_secret_key_length: [REDACTED_LITERAL]
  204 | # A generated *_username is a real login name, so it is lowercase-only and
  205 | # short enough for the 32-character limit Linux enforces. 16 lowercase letters
  206 | # is ~75 bits, which is far more than a login name needs to be unguessable.
  207 | openbao_app_secret_username_suffix: [REDACTED_LITERAL]
  208 | openbao_app_secret_username_length: [REDACTED_LITERAL]
```
