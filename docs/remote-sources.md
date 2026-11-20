# Remote Source Architecture and Operations

## Contract

Every input is materialized as a `SourceSnapshot` and then passed to the same
`analyze_path()` function used by local analysis. Provider code performs
resolution, authenticated acquisition, secure extraction, cleanup, caching,
and provenance only. It does not contain detectors, profile rules, manifest
selection, symbol logic, or report generation.

```text
LocalSource / GitHubSource / GitLabSource
                    |
                    v
              SourceSnapshot
                    |
                    v
              analyze_path()
                    |
                    v
       canonical findings + SARIF
```

`run_metadata.json` records the provider, repository, requested ref, resolved
full SHA, acquisition mode, tree fingerprint, source capabilities,
submodule/LFS policy, and cache verification state. It never records tokens,
authorization headers, or signed URLs.

## Commands

```bash
# Local
ansibleguard .

# GitHub default branch, ref/tag, or commit
ansibleguard github owner/repo
ansibleguard github owner/repo --ref develop
ansibleguard github owner/repo --commit abc123

# GitHub comparison and PR (fork heads are resolved from their own repository)
ansibleguard github-diff owner/repo --base main --head feature/security
ansibleguard github-pr owner/repo 42
ansibleguard github-pr https://github.com/owner/repo/pull/42

# Explicit downstream comment publication
ansibleguard github-pr owner/repo 42 --comment

# GitHub Enterprise
ansibleguard github owner/repo --github-host github.company.example

# GitLab.com or self-managed GitLab
ansibleguard gitlab group/project --ref develop
ansibleguard gitlab group/project --gitlab-host gitlab.company.example
```

Remote source-only profiles select secure archive acquisition in `auto` mode.
Profiles containing Git review checks select a temporary Git checkout with the
analyzed commit and its parent. A user may select `--acquisition archive` or
`--acquisition git`, but AnsibleGuard rejects a profile when the selected
source cannot provide its required history/diff capability.

## Authentication and redaction

GitHub credential priority:

1. `GITHUB_TOKEN`;
2. `GH_TOKEN`;
3. `gh auth token --hostname HOST`;
4. anonymous API access.

GitLab credential priority:

1. `GITLAB_TOKEN`;
2. `GL_TOKEN`;
3. `glab auth token --hostname HOST`;
4. anonymous API access.

API tokens stay in HTTP headers. Git subprocesses receive an ephemeral
per-process HTTP header through environment-scoped Git configuration. Remote
URLs remain tokenless and the repository `.git/config` never contains a
credential. Source exceptions deliberately omit response bodies and redact
known secrets.

## Archive safety

Archive materialization rejects:

- absolute and parent-traversal paths;
- symlinks escaping the destination;
- hard links, devices, FIFOs, sockets, and unsupported entries;
- multiple top-level source roots;
- excessive compressed bytes, uncompressed bytes, or file count.

Extraction copies validated entries individually and never calls
`extractall()`. Partial directories are removed on every failure.

## Submodules and Git LFS

Defaults are conservative:

- submodules are detected but not initialized;
- Git LFS pointers are detected but objects are not fetched.

Opt in with:

```bash
ansibleguard github owner/repo --include-submodules --include-lfs
```

Submodule materialization requires Git acquisition. It rejects escaping paths,
credentialed/cross-host transports, and executable `update` commands. Each
materialized submodule records its URL, exact commit, and tree fingerprint.
LFS provenance records pointer count, whether materialization was requested,
and whether pointers remain.

## Tree equivalence

The source fingerprint hashes a sorted manifest of:

```text
relative path | object kind | SHA256(content or symlink target)
```

`.git`, AnsibleGuard cache/output directories, and Python bytecode caches are
excluded. Absolute acquisition paths and temporary directory names never enter
the hash. The release gate compares local, GitHub archive, GitHub Git, and
GitLab snapshots at identical commits and requires identical tree hashes,
symbol graphs, findings, occurrence IDs, and counts.

## Cache

The CLI default is a private filesystem cache under
`~/.cache/ansibleguard/sources`. Keys contain provider, host, complete
repository identity, full 40-character commit SHA, acquisition mode,
submodule policy, and LFS policy. Every hit is tree-fingerprint verified before
reuse; corrupt entries are invalidated.

```bash
ansibleguard cache info
ansibleguard cache clean --older-than 30
ansibleguard cache clean --include-pinned
```

Pinned entries survive normal cleanup. Private cache directories/files remove
group and world permissions.

Redis is optional:

```bash
python -m pip install -e '.[cache]'
export ANSIBLEGUARD_REDIS_URL=redis://localhost:6379/0
ansibleguard github owner/repo --cache-backend redis
```

Redis stores metadata and distributed locks. Filesystem/object storage stores
the repository trees. This prevents large private repository blobs from
consuming Redis memory and lets concurrent workers acquire one immutable SHA
only once.

## API foundation

Install optional server dependencies and construct an
`ansibleguard.api.AnalysisService` with filesystem/object outputs and either an
in-memory or Redis job store. `create_app(service)` exposes:

```text
POST /api/v1/analysis/github
POST /api/v1/analysis/gitlab
POST /api/v1/analysis/pr
POST /api/v1/analysis/local
GET  /api/v1/analysis/{id}
GET  /api/v1/analysis/{id}/findings
```

Server-local analysis is disabled by default and, when enabled, is confined to
explicit roots. Workers transition through queued, acquiring, analyzing,
completed, or failed state while report artifacts remain outside Redis.

## GitHub Actions, SARIF, and comments

The existing `.github/workflows/ansibleguard.yml` scans exact PR SHAs, compares
canonical base/head outputs, publishes annotations, uploads introduced-only
SARIF when safe, and retains full artifacts. `github-pr --comment` is a separate
downstream publisher: it cannot change analysis or occurrence identity and is
only activated by the explicit flag.

## Research boundary

The corrected 149-repository study does not use remote acquisition or Redis.
It uses the frozen local checkouts, frozen classification manifests,
`LocalSource`, and the frozen research image. Remote support is subject to the
same equivalence/security gates before the final semantic freeze.
