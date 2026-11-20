# PR Diff-Mode Validation Study — AnsibleGuard v0.0.4

**Study ID:** pr-validation-v1  
**Tool version:** AnsibleGuard v0.0.4  
**Study type:** Controlled precision measurement, PR diff mode  
**Date:** 2026-08-13  
**Author:** Aymen Jedidi  
**Status:** Test branches committed; execution and labelling pending

---

## Table of Contents

1. [Objectives](#1-objectives)
2. [Controlled Changes Design](#2-controlled-changes-design)
3. [Execution Protocol](#3-execution-protocol)
4. [SARIF Upload and GitHub Code Scanning Setup](#4-sarif-upload-and-github-code-scanning-setup)
5. [Labelling Protocol](#5-labelling-protocol)
6. [Precision Calculation](#6-precision-calculation)
7. [Expected Results](#7-expected-results)
8. [Results Recording Format](#8-results-recording-format)

---

## 1. Objectives

### 1.1 Primary Research Question

Does AnsibleGuard's PR diff mode correctly isolate *newly introduced* quality issues from
pre-existing ones, and does it do so with sufficient precision to be actionable for
practitioners reviewing pull requests?

Formally: what is the **per-finding precision of the "introduced" classification** across
five real-world Ansible roles, when the changed lines are fully known and ground-truth
labels are manually assigned?

### 1.2 Why This Is Distinct from Snapshot Precision

The v0.0.3 snapshot study measured precision over full-repository scans of 149 GitHub
repositories. In that setting, all findings are evaluated regardless of when they were
introduced. The PR diff mode has a different and more demanding error model:

- **Correct behaviour:** a finding is classified as "introduced" only if the
  corresponding code smell appeared for the first time in the diff — it was not present
  on the base branch.
- **False positive type A (surfacing):** a pre-existing finding is incorrectly classified
  as "introduced" because the diff engine matched it to changed lines by proximity or
  heuristic rather than by actual introduction.
- **False positive type B (detector):** the underlying rule fires on the changed lines
  but the pattern it matched is not actually a smell (classic detector FP, same as
  snapshot mode).
- **False negative:** a genuine new smell is classified as "unchanged" or missed entirely.

This study measures **Types A and B combined** — the overall precision of the introduced
set — which is the metric that determines the signal-to-noise ratio a developer sees when
reviewing GitHub code scanning annotations on their PR.

### 1.3 Scope

- **Five repositories:** forked from geerlingguy (nginx, docker, mysql, security, nodejs)
- **One test branch per repo:** `test/pr-validation` vs. `main`
- **Controlled changes:** manually designed to include known true positives, known
  negative controls, and one ambiguous case per repo
- **Rules under measurement:** shell-instead-of-module, plaintext-sensitive-variable,
  default-credentials, silent-error-suppression, unnamed-task, incomplete-task
- **SARIF integration:** end-to-end upload and annotation verification on each fork

### 1.4 Out of Scope

- Recall (false negative rate) is not measured; ground truth for all *un-introduced*
  smells would require exhaustive enumeration.
- Performance, latency, or scalability are not measured.
- Rules not triggered by the controlled changes are not evaluated.

---

## 2. Controlled Changes Design

Each test branch introduces 7–8 changes: a mix of true-positive injections, negative
controls (changes that resemble smells but should not fire), and one borderline case.
All changes are appended after existing content to avoid disrupting existing task
structure and to ensure the diff engine sees unambiguous line additions.

The test branches were committed with the message:
`test: introduce controlled quality issues for PR validation study`

### 2.1 ansible-role-nginx

**Fork:** JedidiAymen/ansible-role-nginx  
**Original:** geerlingguy/ansible-role-nginx  
**Test commit:** `e8c806b`

#### Changes in `tasks/main.yml`

```yaml
# --- PR Validation Test Changes (v0.0.4) ---
- name: Install additional nginx modules
  shell: apt-get install -y nginx-extras          # [C1] shell-instead-of-module
  become: true

- shell: rm -rf /tmp/nginx-cache                  # [C2] shell-instead-of-module (anchored rm)
  become: true                                    #       + unnamed-task

- name: Check nginx config
  shell: nginx -t                                 # [C3] NEGATIVE CONTROL — nginx -t has no
  register: nginx_check                           #      module replacement; ignore_errors does
  ignore_errors: true                             #      not fire silent-error-suppression
                                                  #      because register is present

- name: Download nginx theme
  shell: wget https://example.com/theme.tar.gz -O /tmp/theme.tar.gz  # [C4] shell-instead-of-module
```

#### Changes in `defaults/main.yml`

```yaml
# --- PR Validation Test Variables (v0.0.4) ---
nginx_ssl_secret_key: "my_nginx_secret_key_value"   # [C5] plaintext-sensitive-variable
nginx_ssl_token: "hardcoded_ssl_token_12345"         # [C6] plaintext-sensitive-variable
nginx_worker_timeout: 30                             # [C7] NEGATIVE CONTROL — integer, _timeout suffix
nginx_max_connections: 512                           # [C8] NEGATIVE CONTROL — integer
```

#### Expected finding map

| Change | File | Rule | Expected label | Rationale |
|--------|------|------|---------------|-----------|
| C1 | tasks/main.yml | shell-instead-of-module | TP | `apt-get` → `apt` / `package` module |
| C2 | tasks/main.yml | shell-instead-of-module | TP | `rm` anchored to command start |
| C2 | tasks/main.yml | unnamed-task | TP | No `name:` key |
| C3 | tasks/main.yml | (none) | — | `nginx -t` is diagnostic; register present suppresses silent-error-suppression |
| C4 | tasks/main.yml | shell-instead-of-module | TP | `wget` URL download → `get_url` module |
| C5 | defaults/main.yml | plaintext-sensitive-variable | TP | String literal with `_key` suffix |
| C6 | defaults/main.yml | plaintext-sensitive-variable | TP | String literal with `_token` suffix |
| C7 | defaults/main.yml | (none) | — | Integer value; `_timeout` in NON_SECRET_SUFFIXES |
| C8 | defaults/main.yml | (none) | — | Integer value; `_connections` not a secret suffix |

### 2.2 ansible-role-docker

**Fork:** JedidiAymen/ansible-role-docker  
**Original:** geerlingguy/ansible-role-docker  
**Test commit:** `d2cbd53`

#### Changes in `tasks/main.yml`

```yaml
# --- PR Validation Test Changes (v0.0.4) ---
- name: "TODO: implement Docker healthcheck"
  shell: pip install docker-compose             # [C1] incomplete-task (TODO in name)
  become: true                                  #      + shell-instead-of-module (pip)

- name: Cleanup old docker layers
  shell: rm -rf /var/lib/docker/tmp/*           # [C2] shell-instead-of-module (anchored rm)
  become: true

- name: Check docker socket
  shell: ls -la /var/run/docker.sock            # [C3] NEGATIVE CONTROL — ls has no
  register: docker_sock_check                   #      module replacement

- name: Fix docker permissions
  shell: chmod 666 /var/run/docker.sock         # [C4] shell-instead-of-module (anchored chmod)
  become: true
```

#### Changes in `defaults/main.yml`

```yaml
# --- PR Validation Test Variables (v0.0.4) ---
docker_api_secret: "docker_secret_api_key_value"  # [C5] plaintext-sensitive-variable
docker_registry_token: "my_registry_access_token" # [C6] plaintext-sensitive-variable
docker_connection_timeout: 60                      # [C7] NEGATIVE CONTROL — integer, _timeout suffix
docker_max_retries: 3                              # [C8] NEGATIVE CONTROL — integer
```

#### Expected finding map

| Change | File | Rule | Expected label | Rationale |
|--------|------|------|---------------|-----------|
| C1 | tasks/main.yml | incomplete-task | TP | Task name starts with `TODO:` |
| C1 | tasks/main.yml | shell-instead-of-module | TP | `pip install` → `pip` / `pip3` module |
| C2 | tasks/main.yml | shell-instead-of-module | TP | `rm` anchored to command start |
| C3 | tasks/main.yml | (none) | — | `ls` produces no module finding; `register` present |
| C4 | tasks/main.yml | shell-instead-of-module | TP | `chmod` anchored to command start |
| C5 | defaults/main.yml | plaintext-sensitive-variable | TP | String with `_secret` suffix |
| C6 | defaults/main.yml | plaintext-sensitive-variable | TP | String with `_token` suffix |
| C7 | defaults/main.yml | (none) | — | Integer; `_timeout` in NON_SECRET_SUFFIXES |
| C8 | defaults/main.yml | (none) | — | Integer; `_retries` not a secret suffix |

### 2.3 ansible-role-mysql

**Fork:** JedidiAymen/ansible-role-mysql  
**Original:** geerlingguy/ansible-role-mysql  
**Test commit:** `b10c4be`

#### Changes in `tasks/main.yml`

```yaml
# --- PR Validation Test Changes (v0.0.4) ---
- name: Reset MySQL root credentials
  shell: mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '{{ mysql_root_password }}'"
  become: true                                   # [C1] silent-error-suppression (ignore_errors + no register)
  ignore_errors: true                            #      NEGATIVE CONTROL for shell-instead-of-module
                                                 #      (complex authenticated DB command, no module replacement)

- name: Backup MySQL databases
  shell: mkdir -p /var/backups/mysql             # [C2] shell-instead-of-module (anchored mkdir → file module)
  become: true

- name: "TODO: implement incremental backup"
  shell: mysqldump --all-databases > /tmp/backup.sql  # [C3] incomplete-task (TODO in name)
  become: true                                        #      shell-instead-of-module: uncertain
                                                      #      (mysqldump has no direct module)
```

#### Changes in `defaults/main.yml`

```yaml
# --- PR Validation Test Variables (v0.0.4) ---
mysql_backup_secret_key: "backup_encryption_key_abc123"  # [C4] plaintext-sensitive-variable
mysql_replication_password: "replication_secret_pass"    # [C5] plaintext-sensitive-variable
mysql_connection_ttl: 300                                # [C6] NEGATIVE CONTROL — integer, _ttl suffix
mysql_max_allowed_packet: 64                             # [C7] NEGATIVE CONTROL — integer
```

**Note on base state:** `defaults/main.yml` on the `main` branch already contains
`mysql_root_password: root` (a pre-existing default-credentials finding). The diff mode
must NOT classify this as "introduced". If it does, that is a Type-A false positive
(surfacing a pre-existing issue).

#### Expected finding map

| Change | File | Rule | Expected label | Rationale |
|--------|------|------|---------------|-----------|
| C1 | tasks/main.yml | silent-error-suppression | TP | `ignore_errors: true` with no `register` |
| C1 | tasks/main.yml | shell-instead-of-module | NEGATIVE | `mysql` authenticated CLI; no module replacement |
| C2 | tasks/main.yml | shell-instead-of-module | TP | `mkdir` anchored to command start → `file` module |
| C3 | tasks/main.yml | incomplete-task | TP | Task name starts with `TODO:` |
| C3 | tasks/main.yml | shell-instead-of-module | uncertain | `mysqldump` has no stdlib module |
| C4 | defaults/main.yml | plaintext-sensitive-variable | TP | String with `_key` suffix |
| C5 | defaults/main.yml | plaintext-sensitive-variable | TP | String with `_password` suffix |
| C6 | defaults/main.yml | (none) | — | Integer; `_ttl` in NON_SECRET_SUFFIXES |
| C7 | defaults/main.yml | (none) | — | Integer; `_packet` not a secret suffix |
| (pre-existing) | defaults/main.yml | default-credentials | NOT introduced | `mysql_root_password: root` exists on `main`; diff must suppress it |

### 2.4 ansible-role-security

**Fork:** JedidiAymen/ansible-role-security  
**Original:** geerlingguy/ansible-role-security  
**Test commit:** `e198368`

#### Changes in `tasks/main.yml`

```yaml
# --- PR Validation Test Changes (v0.0.4) ---
- name: Add security audit user
  shell: useradd -m -s /bin/bash audituser      # [C1] shell-instead-of-module (user module)
  become: true

- shell: chmod 600 /etc/ssh/sshd_config         # [C2] shell-instead-of-module (anchored chmod)
  become: true                                  #      + unnamed-task

- name: Check listening ports
  shell: netstat -tlnp                          # [C3] NEGATIVE CONTROL — no module for netstat;
  register: listening_ports                     #      changed_when: false; diagnostic command
  changed_when: false

- name: Rotate SSH keys
  shell: rm -f /root/.ssh/authorized_keys       # [C4] shell-instead-of-module (anchored rm)
  become: true                                  #      + silent-error-suppression (ignore_errors,
  ignore_errors: true                           #        no register)
```

#### Changes in `defaults/main.yml`

```yaml
# --- PR Validation Test Variables (v0.0.4) ---
security_admin_password: "admin"                    # [C5] default-credentials (trivial password)
                                                    #      + plaintext-sensitive-variable
security_api_token: "security_monitoring_token_xyz" # [C6] plaintext-sensitive-variable
security_ssh_port_timeout: 30                       # [C7] NEGATIVE CONTROL — integer, _timeout suffix
security_max_login_attempts: 5                      # [C8] NEGATIVE CONTROL — integer
```

#### Expected finding map

| Change | File | Rule | Expected label | Rationale |
|--------|------|------|---------------|-----------|
| C1 | tasks/main.yml | shell-instead-of-module | TP | `useradd` → `ansible.builtin.user` module |
| C2 | tasks/main.yml | shell-instead-of-module | TP | `chmod` anchored to command start |
| C2 | tasks/main.yml | unnamed-task | TP | No `name:` key on shell task |
| C3 | tasks/main.yml | (none) | — | No module for `netstat`; `changed_when: false` is correct idiom |
| C4 | tasks/main.yml | shell-instead-of-module | TP | `rm` anchored to command start |
| C4 | tasks/main.yml | silent-error-suppression | TP | `ignore_errors: true` without `register` |
| C5 | defaults/main.yml | default-credentials | TP | `"admin"` is a trivial credential |
| C5 | defaults/main.yml | plaintext-sensitive-variable | TP | String with `_password` suffix |
| C6 | defaults/main.yml | plaintext-sensitive-variable | TP | String with `_token` suffix |
| C7 | defaults/main.yml | (none) | — | Integer; `_timeout` in NON_SECRET_SUFFIXES |
| C8 | defaults/main.yml | (none) | — | Integer; `_attempts` not a secret suffix |

### 2.5 ansible-role-nodejs

**Fork:** JedidiAymen/ansible-role-nodejs  
**Original:** geerlingguy/ansible-role-nodejs  
**Test commit:** `403e581`

#### Changes in `tasks/main.yml`

```yaml
# --- PR Validation Test Changes (v0.0.4) ---
- name: Install global npm packages
  shell: npm install -g forever pm2             # [C1] shell-instead-of-module (npm module)
  become: true

- name: "TODO: implement npm audit in CI"
  shell: touch /tmp/npm-audit-placeholder       # [C2] incomplete-task (TODO in name)
  become: true                                  #      + shell-instead-of-module (anchored touch)

- name: Set npm registry
  shell: npm config set registry https://registry.npmjs.org/  # [C3] shell-instead-of-module (npm module)
  become: true

- name: Fix npm permissions
  shell: chmod -R 755 /usr/local/lib/npm        # [C4] shell-instead-of-module (anchored chmod)
  become: true
```

#### Changes in `defaults/main.yml`

```yaml
# --- PR Validation Test Variables (v0.0.4) ---
nodejs_npm_token: "npm_secret_access_token_for_private_registry"  # [C5] plaintext-sensitive-variable
nodejs_registry_password: "npm_registry_pass"                     # [C6] plaintext-sensitive-variable
nodejs_connection_timeout: 30                                     # [C7] NEGATIVE CONTROL — integer, _timeout
nodejs_max_retry_count: 3                                         # [C8] NEGATIVE CONTROL — integer
```

#### Expected finding map

| Change | File | Rule | Expected label | Rationale |
|--------|------|------|---------------|-----------|
| C1 | tasks/main.yml | shell-instead-of-module | TP | `npm install -g` → `npm` module with `global: true` |
| C2 | tasks/main.yml | incomplete-task | TP | Task name starts with `TODO:` |
| C2 | tasks/main.yml | shell-instead-of-module | TP | `touch` anchored to command start |
| C3 | tasks/main.yml | shell-instead-of-module | TP | `npm config set` → `npm` module |
| C4 | tasks/main.yml | shell-instead-of-module | TP | `chmod` anchored to command start |
| C5 | defaults/main.yml | plaintext-sensitive-variable | TP | String with `_token` suffix |
| C6 | defaults/main.yml | plaintext-sensitive-variable | TP | String with `_password` suffix |
| C7 | defaults/main.yml | (none) | — | Integer; `_timeout` in NON_SECRET_SUFFIXES |
| C8 | defaults/main.yml | (none) | — | Integer; `_count` not a secret suffix |

### 2.6 Summary: Designed Finding Count

| Repo | Expected TPs | Negative controls | Notes |
|------|-------------|-------------------|-------|
| ansible-role-nginx | 6 | 3 | C3 is ambiguous (nginx -t diagnostic) |
| ansible-role-docker | 6 | 3 | C3 is NEGATIVE (ls diagnostic) |
| ansible-role-mysql | 6 | 4 | C1 shell is NEGATIVE; pre-existing root_password must not appear |
| ansible-role-security | 8 | 3 | C3 is NEGATIVE (netstat diagnostic) |
| ansible-role-nodejs | 7 | 2 | All shell tasks have clear module replacements |
| **Total** | **33** | **15** | |

---

## 3. Execution Protocol

### 3.1 Prerequisites

```bash
# AnsibleGuard v0.0.4 is installed from source at:
ANSIBLEGUARD_SRC=/home/aymmzn/Documents/AnsibleChecklist

# Verify version
cd $ANSIBLEGUARD_SRC
python3 -m ansibleguard.cli --version
# Expected: ansibleguard 0.0.4

# Study base directory
STUDY_DIR=$ANSIBLEGUARD_SRC/study/pr-validation-v1
```

### 3.2 Step A: Verify Branch State

For each repository, confirm the `test/pr-validation` branch is ahead of `main` by
exactly one commit containing the controlled changes.

```bash
for REPO in ansible-role-nginx ansible-role-docker ansible-role-mysql \
            ansible-role-security ansible-role-nodejs; do
  echo "=== $REPO ==="
  cd $STUDY_DIR/$REPO
  echo "Current branch: $(git branch --show-current)"
  echo "Commits ahead of main: $(git log main..HEAD --oneline | wc -l)"
  git log main..HEAD --oneline
  echo ""
done
```

Expected output for each repo: `1` commit ahead of `main`, with message
`test: introduce controlled quality issues for PR validation study`.

### 3.3 Step B: Push Test Branches to Forks

If not already pushed:

```bash
for REPO in ansible-role-nginx ansible-role-docker ansible-role-mysql \
            ansible-role-security ansible-role-nodejs; do
  cd $STUDY_DIR/$REPO
  git push origin test/pr-validation
  echo "Pushed $REPO"
done
```

### 3.4 Step C: Create Pull Requests

```bash
for REPO in ansible-role-nginx ansible-role-docker ansible-role-mysql \
            ansible-role-security ansible-role-nodejs; do
  cd $STUDY_DIR/$REPO
  gh pr create \
    --title "test: PR validation study for AnsibleGuard v0.0.4" \
    --body "Controlled changes for PR diff-mode precision measurement. See study/pr-validation-v1/PR_VALIDATION_STUDY.md for methodology." \
    --base main \
    --head test/pr-validation
done
```

### 3.5 Step D: Run the AnsibleGuard Diff Analysis

Run from the AnsibleGuard source directory so that the installed package is on the
Python path. The `target` positional argument points to the repository under analysis.

```bash
cd $ANSIBLEGUARD_SRC

for REPO in ansible-role-nginx ansible-role-docker ansible-role-mysql \
            ansible-role-security ansible-role-nodejs; do

  REPO_DIR=$STUDY_DIR/$REPO
  OUTPUT_DIR=/tmp/ag-pr-diff-${REPO}

  echo "=== Running diff analysis: $REPO ==="
  python3 -m ansibleguard.cli diff \
    "$REPO_DIR" \
    --base main \
    --head test/pr-validation \
    --output "$OUTPUT_DIR" \
    --profile pr

  echo "Exit code: $?"
  echo ""
done
```

**Profile selection note:** Use `--profile pr` for PR validation. This profile activates
the same detectors as `snapshot-source` but suppresses findings on unchanged lines. If
the `pr` profile is unavailable in v0.0.4, substitute `--profile snapshot-source` and
filter to `introduced` findings manually.

### 3.6 Step E: Collect and Review Introduced Findings

```bash
for REPO in ansible-role-nginx ansible-role-docker ansible-role-mysql \
            ansible-role-security ansible-role-nodejs; do

  OUTPUT_DIR=/tmp/ag-pr-diff-${REPO}

  echo ""
  echo "=========================================="
  echo "REPO: $REPO"
  echo "=========================================="
  echo "--- Summary ---"
  cat "$OUTPUT_DIR/diff/summary.md"

  echo ""
  echo "--- Introduced findings (pretty-printed) ---"
  python3 -m json.tool "$OUTPUT_DIR/diff/introduced.json"
done
```

For a single repo during interactive investigation:

```bash
REPO=ansible-role-nodejs
OUTPUT_DIR=/tmp/ag-pr-diff-${REPO}

# Human-readable summary
cat $OUTPUT_DIR/diff/summary.md

# Introduced findings with full detail
python3 -m json.tool $OUTPUT_DIR/diff/introduced.json | \
  python3 -c "
import json, sys
findings = json.load(sys.stdin)
for f in findings:
    print(f\"{f.get('rule_id','?'):45s} {f.get('path','?')}:{f.get('line','?')} — {f.get('message','')[:80]}\")
"

# Count by classification
python3 -m json.tool $OUTPUT_DIR/diff/diff_findings.json | \
  python3 -c "
import json, sys, collections
findings = json.load(sys.stdin)
counts = collections.Counter(f.get('classification') for f in findings)
for cls, n in sorted(counts.items()):
    print(f'{cls}: {n}')
"
```

### 3.7 Step F: Record Raw Output Before Labelling

Before labelling, archive the raw output to prevent accidental overwrite:

```bash
ARCHIVE=$STUDY_DIR/raw-output-$(date +%Y%m%d)
mkdir -p $ARCHIVE

for REPO in ansible-role-nginx ansible-role-docker ansible-role-mysql \
            ansible-role-security ansible-role-nodejs; do
  cp -r /tmp/ag-pr-diff-${REPO} $ARCHIVE/
done

echo "Raw output archived to $ARCHIVE"
```

### 3.8 Step G: Manual Labelling

Open each `introduced.json` file and label each finding as TP, FP, or uncertain
using the protocol in Section 5. Record results in `$STUDY_DIR/labels.csv`
(format in Section 8).

---

## 4. SARIF Upload and GitHub Code Scanning Setup

### 4.1 Prerequisites for Code Scanning

GitHub Code Scanning is available by default on public repositories. All five forks
(JedidiAymen/ansible-role-*) are public and do not require additional configuration to
accept SARIF uploads via the API.

### 4.2 Add AnsibleGuard Workflow to Fork (optional CI path)

If continuous scanning via GitHub Actions is desired, add the following workflow to
each fork's `main` branch. This workflow runs on every PR against `main`.

```yaml
# .github/workflows/ansibleguard.yml
name: AnsibleGuard

on:
  pull_request:
    branches: [main]

jobs:
  ansibleguard:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0       # needed for diff mode to reach base branch

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install AnsibleGuard
        run: |
          git clone https://github.com/JedidiAymen/AnsibleChecklist /tmp/ansibleguard
          pip install -e /tmp/ansibleguard

      - name: Run AnsibleGuard diff
        run: |
          python3 -m ansibleguard.cli diff . \
            --base origin/main \
            --head ${{ github.sha }} \
            --output /tmp/ag-output \
            --profile pr

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: /tmp/ag-output/diff/introduced.sarif
```

**Note:** If AnsibleGuard cannot be installed from a public source in CI, use the
manual upload path described in Section 4.3.

### 4.3 Manual SARIF Upload via gh API

The diff output includes a SARIF file at `<output>/diff/introduced.sarif`. The GitHub
API requires the SARIF to be gzip-compressed and base64-encoded before upload.

#### 4.3.1 Compress and Encode

```bash
REPO=ansible-role-nodejs
OUTPUT_DIR=/tmp/ag-pr-diff-${REPO}

# Compress the SARIF
gzip -9 -c "$OUTPUT_DIR/diff/introduced.sarif" > "$OUTPUT_DIR/diff/introduced.sarif.gz"

# Base64-encode (required by the API)
SARIF_B64=$(base64 -w 0 "$OUTPUT_DIR/diff/introduced.sarif.gz")

echo "Compressed and encoded SARIF ready for upload."
echo "Size: $(wc -c < $OUTPUT_DIR/diff/introduced.sarif.gz) bytes (gzipped)"
```

#### 4.3.2 Upload via gh api

```bash
REPO=ansible-role-nodejs
OWNER=JedidiAymen
OUTPUT_DIR=/tmp/ag-pr-diff-${REPO}

# Get the HEAD SHA of the test branch
cd $STUDY_DIR/$REPO
HEAD_SHA=$(git rev-parse test/pr-validation)

# Upload SARIF
gh api \
  --method POST \
  /repos/${OWNER}/${REPO}/code-scanning/sarifs \
  --field commit_sha="$HEAD_SHA" \
  --field ref="refs/heads/test/pr-validation" \
  --field sarif="$(base64 -w 0 $OUTPUT_DIR/diff/introduced.sarif.gz)" \
  --field tool_name="ansibleguard"
```

The response includes a `url` field pointing to the upload status. Wait a few seconds,
then verify:

```bash
# Check upload status (use the id from the response above)
UPLOAD_ID=<id-from-response>
gh api /repos/${OWNER}/${REPO}/code-scanning/sarifs/${UPLOAD_ID}
```

#### 4.3.3 Batch Upload for All Repos

```bash
cd $ANSIBLEGUARD_SRC

for REPO in ansible-role-nginx ansible-role-docker ansible-role-mysql \
            ansible-role-security ansible-role-nodejs; do

  OWNER=JedidiAymen
  OUTPUT_DIR=/tmp/ag-pr-diff-${REPO}
  SARIF_FILE="$OUTPUT_DIR/diff/introduced.sarif"

  if [ ! -f "$SARIF_FILE" ]; then
    echo "WARN: $SARIF_FILE not found — skipping $REPO"
    continue
  fi

  HEAD_SHA=$(cd $STUDY_DIR/$REPO && git rev-parse test/pr-validation)

  gzip -9 -kf "$SARIF_FILE"

  echo "Uploading $REPO (commit $HEAD_SHA)..."
  RESPONSE=$(gh api \
    --method POST \
    /repos/${OWNER}/${REPO}/code-scanning/sarifs \
    --field commit_sha="$HEAD_SHA" \
    --field ref="refs/heads/test/pr-validation" \
    --field sarif="$(base64 -w 0 ${SARIF_FILE}.gz)" \
    --field tool_name="ansibleguard" 2>&1)
  echo "$RESPONSE" | python3 -m json.tool
  echo ""
done
```

### 4.4 Verify Annotations Appear on the PR

1. Open the PR page for each fork on GitHub:
   `https://github.com/JedidiAymen/<REPO>/pull/<PR_NUMBER>`
2. Navigate to the **Security** tab → **Code scanning alerts**
3. Filter by: `Branch: test/pr-validation`
4. Confirm that each uploaded finding appears as an inline annotation in the **Files
   changed** tab, anchored to the correct line.

Key things to verify:
- The annotation points to the correct file and line number (not a pre-existing line)
- The rule description is human-readable (SARIF `shortDescription.text`)
- The severity level is correct (error/warning/note per the rule's configured severity)
- No pre-existing findings from the `main` branch appear as new annotations

---

## 5. Labelling Protocol

### 5.1 Labeller Profile

Labelling is performed by a single expert annotator (Aymen Jedidi) familiar with
Ansible best practices and the AnsibleGuard rule set. A second pass may be performed
to check uncertain cases.

### 5.2 Label Definitions

#### TP — True Positive

The change introduced in this PR **genuinely** created the quality issue that the finding
describes. Criteria:
- The flagged code is on a line added in the diff (not a pre-existing line)
- The rule correctly describes the problem (e.g., the task genuinely uses `shell:` where
  the `apt` module could be used; the variable genuinely stores a hardcoded string
  credential)
- A practitioner reviewing this PR should act on this finding

#### FP — False Positive

The finding fires incorrectly. Subcategories for tracking:
- **FP-A (surfacing):** the finding was already present on the base branch but the diff
  engine classified it as "introduced" (pre-existing issue surfaced by diff heuristic)
- **FP-B (detector):** the finding fires on a newly-added line but the rule logic itself
  produces an incorrect match (e.g., `nginx -t` flagged as shell-instead-of-module when
  no module replacement exists)
- **FP-C (context):** the finding is technically valid in isolation but is inappropriate
  in context (e.g., a `changed_when: false` diagnostic task flagged for shell usage)

#### Uncertain

Cannot determine without runtime information. Examples:
- A `shell:` command that *may* have a module replacement depending on the Ansible
  collection version installed
- A variable whose string value looks like a token but might be a template placeholder
  in the project's actual use

### 5.3 Labelling Procedure

For each entry in `introduced.json`:

1. Open the flagged file in the repository at the HEAD commit
2. Read the full task or variable definition, not just the flagged line
3. Check the base branch (`main`) to confirm the finding was NOT present before
4. Apply the label (TP / FP-A / FP-B / FP-C / uncertain)
5. Write a brief note (1–2 sentences) explaining the decision
6. Record in `labels.csv` (format in Section 8)

### 5.4 Handling Pre-existing Findings

The mysql repo has `mysql_root_password: root` on the `main` branch, which fires the
`default-credentials` rule. This finding must **not** appear in `introduced.json`. If it
does, label it **FP-A** with note `pre-existing on main branch`.

### 5.5 Handling Rule Co-occurrences

A single changed line may trigger multiple rules (e.g., an unnamed `shell:` task
triggering both `unnamed-task` and `shell-instead-of-module`). Each rule-file-line
triple is a separate finding entry and must be labelled independently.

---

## 6. Precision Calculation

### 6.1 Primary Metric: Overall PR-Diff Precision

Let:
- N = total number of decidable findings across all repos (TP + FP; uncertain excluded)
- TP = count of true-positive findings
- FP = count of false-positive findings (FP-A + FP-B + FP-C combined)

```
Precision_overall = TP / (TP + FP) = TP / N
```

95% Wilson-score confidence interval (for binomial proportion):

```
p̂ = TP / N
z = 1.96

lower = (p̂ + z²/(2N) - z * sqrt(p̂(1-p̂)/N + z²/(4N²))) / (1 + z²/N)
upper = (p̂ + z²/(2N) + z * sqrt(p̂(1-p̂)/N + z²/(4N²))) / (1 + z²/N)
```

Python calculation:

```python
import math

def wilson_ci(tp, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = tp / n
    centre = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    margin = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return (max(0, centre - margin), min(1, centre + margin))

# Example
tp, fp = 28, 5
n = tp + fp
p_hat = tp / n
lo, hi = wilson_ci(tp, n)
print(f"Precision: {p_hat:.3f}  95% CI: [{lo:.3f}, {hi:.3f}]  (n={n})")
```

### 6.2 Per-Rule Precision

For rules with 5 or more decidable findings, compute separate precision with
Wilson-score CI:

| Rule | Expected n | Applies CI? |
|------|-----------|-------------|
| shell-instead-of-module | ~15 | Yes |
| plaintext-sensitive-variable | ~10 | Yes |
| silent-error-suppression | ~3 | No (report point estimate only) |
| unnamed-task | ~3 | No |
| incomplete-task | ~4 | No (borderline) |
| default-credentials | ~1 | No |

### 6.3 Negative Control Pass Rate

Separately, count how many negative controls produced zero findings in `introduced.json`.
A detector that fires on a negative control is a confirmed false positive and its
precision estimate should be adjusted.

```
Negative_control_pass_rate = (controls with zero findings) / (total controls)
```

### 6.4 FP Subtype Breakdown

Report the fraction of FPs that are Type-A (surfacing) vs Type-B (detector) vs Type-C
(context). Type-A FPs indicate diff-engine flaws; Types B and C indicate rule flaws.
These have different remediation paths.

### 6.5 Comparison to Snapshot Precision Baseline

Compare PR-diff precision against the v0.0.3 snapshot precision for the same rules
(from the 149-repo study). The PR-diff mode may legitimately differ because:
- The controlled corpus is smaller and more targeted
- All test changes are designed to be representative; random-sample precision from the
  wild may be lower
- The v0.0.4 rule improvements affect both modes identically

---

## 7. Expected Results

Based on v0.0.3 snapshot-study precision measurements and the specific rule fixes in
v0.0.4, the following precision estimates are projected for the PR diff mode.

### 7.1 shell-instead-of-module

- **v0.0.3 snapshot precision:** ~39%
- **v0.0.4 fix:** anchored all file-operation patterns (`cp`, `mv`, `rm`, `mkdir`,
  `chmod`, `chown`, `touch`, `find`) to the start of the command string
  (`^(?:sudo\s+)?<cmd>\b`). This eliminates matches on path components or arguments
  containing these strings.
- **Expected PR-diff precision:** ~60–65%
- **Key risk:** Commands with no module replacement (e.g., `nginx -t`, `netstat -tlnp`,
  `mysql -u root ...`) remain false positives if the detector lacks a command-specific
  allowlist. These are controlled by the NEGATIVE CONTROL cases in this study.

### 7.2 plaintext-sensitive-variable

- **v0.0.3 snapshot precision:** ~4%
- **v0.0.4 fixes:**
  1. `_plaintext_literal()` now returns `False` for `bool`, `int`, and `float` values
     immediately (secrets are always strings).
  2. Added 14 entries to `NON_SECRET_SUFFIXES`: `backend`, `count`, `dir`, `format`,
     `hash`, `header`, `limit`, `max`, `min`, `mode`, `prefix`, `size`, `suffix`,
     `timeout`, `ttl`.
- **Expected PR-diff precision:** ~30–40%
- **Key risk:** The controlled test variables (`nginx_ssl_secret_key`, `docker_api_secret`,
  etc.) were designed to be unambiguous TPs. The main risk is FP-B on edge-case
  key names not covered by `NON_SECRET_SUFFIXES`.

### 7.3 default-credentials

- **v0.0.3 snapshot precision:** ~50%
- **v0.0.4 changes:** None (rule not modified in this release).
- **Expected PR-diff precision:** ~50%
- **In this study:** Only one injected case (`security_admin_password: "admin"`).
  The pre-existing `mysql_root_password: root` must not appear as "introduced".

### 7.4 silent-error-suppression

- **v0.0.3 snapshot precision:** ~66%
- **v0.0.4 changes:** None.
- **Expected PR-diff precision:** ~66%
- **In this study:** Two injected cases (mysql C1, security C4). Both have
  `ignore_errors: true` without `register:`, which is the canonical pattern.

### 7.5 unnamed-task

- **v0.0.3 snapshot precision:** not separately reported (grouped with structural rules)
- **v0.0.4 changes:** None.
- **Expected PR-diff precision:** ~70–80%
- **In this study:** Two injected cases (nginx C2, security C2).

### 7.6 incomplete-task

- **v0.0.3 snapshot precision:** ~9%
- **v0.0.4 fix:** Rewritten to scan only parsed task dict fields (task name and module
  argument values). YAML comments are no longer scanned. The `TODO:` pattern in comment
  lines no longer fires.
- **Expected PR-diff precision:** ~70–80%
- **In this study:** Three injected cases (docker C1, mysql C3, nodejs C2). All have
  `TODO:` in the task `name:` key, which is the canonical pattern after the fix.

### 7.7 Composite Expected Precision (Projected)

Assuming the controlled study produces approximately the finding volumes in Section 2.6:

| Rule | Injected TPs | Expected FPs | Projected precision |
|------|-------------|-------------|-------------------|
| shell-instead-of-module | 13 | 3–5 | 72–81% |
| plaintext-sensitive-variable | 10 | 0–2 | 83–100% |
| default-credentials | 1 | 0 | 100% |
| silent-error-suppression | 2 | 0 | 100% |
| unnamed-task | 2 | 0 | 100% |
| incomplete-task | 3 | 0 | 100% |
| **Overall** | **31** | **3–7** | **82–91%** |

**Caveat:** These projections are based on the *designed* changes. Actual precision may
differ if the diff engine surfaces pre-existing findings (Type-A FPs) or if the detector
fires on unexpected constructs in the test files.

---

## 8. Results Recording Format

### 8.1 Primary Label File: `labels.csv`

Location: `$STUDY_DIR/labels.csv`

```
repo,rule_id,file,line,change_id,classification,label,fp_subtype,notes
```

Field definitions:

| Field | Type | Description |
|-------|------|-------------|
| repo | string | Short repo name, e.g. `ansible-role-nginx` |
| rule_id | string | AnsibleGuard rule identifier, e.g. `shell-instead-of-module` |
| file | string | Repo-relative path, e.g. `tasks/main.yml` |
| line | integer | 1-indexed line number reported by AnsibleGuard |
| change_id | string | Change code from Section 2 (C1–C8), or `pre-existing` |
| classification | string | `introduced` / `unchanged` / `fixed` (as reported by diff engine) |
| label | string | `TP` / `FP` / `uncertain` |
| fp_subtype | string | `A` / `B` / `C` / empty (only if label=FP) |
| notes | string | Free text; quote if contains commas |

Example rows:

```csv
repo,rule_id,file,line,change_id,classification,label,fp_subtype,notes
ansible-role-nginx,shell-instead-of-module,tasks/main.yml,57,C1,introduced,TP,,"apt-get install → apt module"
ansible-role-nginx,shell-instead-of-module,tasks/main.yml,60,C2,introduced,TP,,"rm anchored pattern fires correctly"
ansible-role-nginx,unnamed-task,tasks/main.yml,60,C2,introduced,TP,,"no name key on shell task"
ansible-role-nginx,shell-instead-of-module,tasks/main.yml,63,C3,introduced,FP,B,"nginx -t is diagnostic; no module replacement"
ansible-role-nginx,shell-instead-of-module,tasks/main.yml,68,C4,introduced,TP,,"wget → get_url module"
ansible-role-nginx,plaintext-sensitive-variable,defaults/main.yml,99,C5,introduced,TP,,"string credential in _key variable"
ansible-role-nginx,plaintext-sensitive-variable,defaults/main.yml,100,C6,introduced,TP,,"string credential in _token variable"
ansible-role-mysql,default-credentials,defaults/main.yml,11,pre-existing,introduced,FP,A,"pre-existing on main branch — diff engine error"
```

### 8.2 Negative Control Log: `negative_controls.csv`

Location: `$STUDY_DIR/negative_controls.csv`

```
repo,file,line,change_id,variable_or_command,rule_that_should_not_fire,fired,notes
```

Example rows:

```csv
repo,file,line,change_id,variable_or_command,rule_that_should_not_fire,fired,notes
ansible-role-nginx,defaults/main.yml,101,C7,nginx_worker_timeout: 30,plaintext-sensitive-variable,false,"integer value; _timeout suffix"
ansible-role-nginx,tasks/main.yml,63,C3,"shell: nginx -t",shell-instead-of-module,true,"fired but no module replacement exists"
ansible-role-mysql,defaults/main.yml,11,pre-existing,mysql_root_password: root,default-credentials,false,"correctly not in introduced set"
```

### 8.3 Aggregate Summary Table: `precision_summary.csv`

Location: `$STUDY_DIR/precision_summary.csv`

```
rule_id,total_introduced,tp,fp,fp_a,fp_b,fp_c,uncertain,precision,wilson_lo,wilson_hi
```

### 8.4 Session Metadata

Record the following at the start of each labelling session:

```
# label_session_metadata.txt
date: 2026-MM-DD
labeller: Aymen Jedidi
ansibleguard_version: 0.0.4
git_sha_ansibleguard: <output of: git -C $ANSIBLEGUARD_SRC rev-parse HEAD>
repos_labelled: [comma-separated list]
notes: [any deviations from protocol]
```

---

## Appendix A: Rule Reference for Labelling

### shell-instead-of-module

Fires when `shell:` or `command:` is used where a built-in Ansible module exists.
The v0.0.4 detector checks for:
- Package managers: `apt-get`, `yum`, `dnf`, `pip`, `npm`
- File operations (anchored): `rm`, `mkdir`, `chmod`, `chown`, `cp`, `mv`, `touch`
- Network downloads: `wget`, `curl` (URL downloads)
- User management: `useradd`, `userdel`, `usermod`, `groupadd`
- Service management: `service`, `systemctl`
- Archive operations: `tar`, `unzip`

**Does NOT fire on** (known legitimate shell uses): `nginx -t`, `netstat`, `ss`, `ip`,
diagnostic commands with `changed_when: false`, commands with complex pipes/redirects
that have no idiomatic module equivalent.

### plaintext-sensitive-variable

Fires when a YAML variable in `defaults/` or `vars/` has:
- A name matching SENSITIVE_PARTS (contains `password`, `secret`, `token`, `key`, `api`,
  `credential`, `auth`, `cert`, `private`, etc.)
- AND the value is a non-empty string literal
- AND the value is not a Jinja2 expression (`{{ ... }}`)
- AND the value is not `""` (empty string)
- AND the key does not end with a NON_SECRET_SUFFIX

**Does NOT fire on** integers, floats, booleans, Jinja2 expressions, or keys ending in:
`backend`, `count`, `dir`, `format`, `hash`, `header`, `limit`, `max`, `min`, `mode`,
`prefix`, `size`, `suffix`, `timeout`, `ttl`.

### default-credentials

Fires when a variable name matches `*_password` or `*_user*` patterns and the value is
a trivially weak credential (`root`, `admin`, `password`, `123456`, `changeme`, etc.).
This is a subset of `plaintext-sensitive-variable` with a more specific weak-value check.

### silent-error-suppression

Fires when a task has `ignore_errors: true` **and** no `register:` key. The `register`
key indicates that the caller intends to inspect the error result, which is a legitimate
use of `ignore_errors`. Without `register`, the error is silently discarded.

### unnamed-task

Fires when a task block lacks a `name:` key entirely. Applies to tasks in the top-level
list and in `block:` / `rescue:` / `always:` sections.

### incomplete-task

Fires when a task's `name:` value contains a `TODO:`, `FIXME:`, `HACK:`, or `XXX:`
marker (case-insensitive). Applies only to the `name:` field value, not to YAML
comments or module argument strings.

---

## Appendix B: Diff Engine Behaviour Reference

The AnsibleGuard diff engine compares findings from two scans (base and head) using the
following classification logic:

| Classification | Condition |
|---------------|-----------|
| `introduced` | Finding present in HEAD scan, absent in BASE scan (matched by rule_id + file + content hash) |
| `fixed` | Finding present in BASE scan, absent in HEAD scan |
| `unchanged` | Finding present in both BASE and HEAD scans |
| `moved` | Finding present in both scans, same file and rule, different line number |
| `uncertain` | Cannot determine due to large diff or rename heuristics |

For this study, only `introduced` findings are labelled. The `moved` category is treated
as pre-existing (not introduced) and should not appear in `introduced.json`.

The diff engine uses **content-based matching** (rule_id + normalised YAML subtree hash)
rather than line-number matching. This means a finding that has been moved within a file
by refactoring is correctly classified as `moved` rather than `introduced + fixed`.

---

## Appendix C: File Inventory

| File | Description |
|------|-------------|
| `PR_VALIDATION_STUDY.md` | This document |
| `README.md` | Short overview of the study directory |
| `labels.csv` | Per-finding TP/FP labels (filled in during execution) |
| `negative_controls.csv` | Log of negative control behaviour |
| `precision_summary.csv` | Aggregate precision by rule |
| `label_session_metadata.txt` | Session metadata for reproducibility |
| `raw-output-YYYYMMDD/` | Archived diff engine output (created at execution time) |
| `ansible-role-nginx/` | Fork clone, branch `test/pr-validation` |
| `ansible-role-docker/` | Fork clone, branch `test/pr-validation` |
| `ansible-role-mysql/` | Fork clone, branch `test/pr-validation` |
| `ansible-role-security/` | Fork clone, branch `test/pr-validation` |
| `ansible-role-nodejs/` | Fork clone, branch `test/pr-validation` |
