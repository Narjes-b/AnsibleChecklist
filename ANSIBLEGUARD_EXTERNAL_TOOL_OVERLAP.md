# AnsibleGuard overlap with GitLeaks and ansible-lint

The word **overlap** covers several different relationships. They should not
all be interpreted as “AnsibleGuard copied the same rule.”

## Four meanings of overlap

| Type | Meaning |
|---|---|
| Exact integration | AnsibleGuard runs the external tool and converts every external result into an AnsibleGuard finding. There is only one underlying detection. |
| Substantial overlap | Both tools independently inspect nearly the same defect, so many findings may match. Their implementations and exact result sets can still differ. |
| Partial overlap | The rules intersect only for certain examples. Each rule also reports cases that the other does not. |
| Adjacent | The rules concern a similar quality area but test different predicates. Matching findings are uncommon or incidental. |

A useful set interpretation is:

```text
Exact integration:
AnsibleGuard findings = normalized external-tool findings

Substantial overlap:
AnsibleGuard findings ≈ ansible-lint findings

Partial overlap:
some AnsibleGuard findings ∩ some ansible-lint findings

Adjacent:
same general topic, but little direct intersection
```

## 1. GitLeaks overlap

### `hardcoded-credentials`: exact GitLeaks integration

This is the clearest and strongest overlap.

AnsibleGuard does not independently identify hardcoded secrets for this rule.
It:

1. Runs GitLeaks once against the target repository.
2. Requests JSON output.
3. Reads GitLeaks’ findings.
4. Converts every GitLeaks finding into an AnsibleGuard finding whose rule ID
   is `hardcoded-credentials`.

The invocation is implemented in
[`src/ansibleguard/external/gitleaks.py`](src/ansibleguard/external/gitleaks.py):

```text
gitleaks detect
  --source <repository>
  --no-git
  --report-format json
```

The conversion happens in
[`src/ansibleguard/report/findings.py`](src/ansibleguard/report/findings.py):

```python
for f in gitleaks_findings:
    line = f.get("StartLine") ...
    desc = f.get("Description") or f.get("RuleID") ...
    out.append(
        _finding(file, line, "hardcoded-credentials", desc)
    )
```

Therefore:

```text
One GitLeaks finding
        ↓
One AnsibleGuard hardcoded-credentials finding
```

For example, if GitLeaks returns:

```json
{
  "RuleID": "aws-access-token",
  "Description": "AWS Access Token",
  "File": "vars/main.yml",
  "StartLine": 12
}
```

AnsibleGuard normalizes it approximately as:

```json
{
  "rule_id": "hardcoded-credentials",
  "file": "vars/main.yml",
  "line": 12,
  "severity": "error",
  "message": "AWS Access Token"
}
```

#### What AnsibleGuard adds

AnsibleGuard adds:

- A common rule ID: `hardcoded-credentials`
- Its own severity: always `error`
- Integration into `findings.json`, CSV, text, and SARIF
- Association with per-file and project summaries
- Tool execution status and diagnostics
- Preservation of findings even if the YAML cannot be parsed
- Preservation of findings from non-YAML files such as `.env` files

The repository-level handling is implemented in
[`src/ansibleguard/cli.py`](src/ansibleguard/cli.py).

#### What AnsibleGuard does not add

It does not independently confirm that the string is a secret. GitLeaks owns:

- Secret patterns
- Entropy checks
- Provider-specific rules
- Allowlists
- GitLeaks configuration behavior
- The underlying detection decision

Consequently, a GitLeaks false positive becomes an AnsibleGuard
`hardcoded-credentials` false positive. If GitLeaks misses a secret, this rule
also misses it.

It is called **exact integration** because the detection population is imported
one-for-one—not because the output records remain identical. AnsibleGuard
collapses all GitLeaks native rule identities into one aggregate rule.

#### Profile limitation

`hardcoded-credentials` belongs to `EXTERNAL_RULES` in
[`src/ansibleguard/profiles.py`](src/ansibleguard/profiles.py). External tools
run under `technical-full`, but not under:

- `snapshot-source`
- `research-core`
- `extended-ansible`
- `review-range`

Therefore, `hardcoded-credentials` should not be counted as an independently
implemented AnsibleGuard research detector.

### `default-credentials`: small partial GitLeaks overlap

This is an independent AnsibleGuard detector.

It looks for:

1. A credential-like key, such as `password`, `secret`, or `token`.
2. A literal scalar value.
3. A known default value, or a value equal to the key name.
4. It excludes Jinja variables and Ansible Vault values.

The implementation is in
[`src/ansibleguard/detectors/review_checklist.py`](src/ansibleguard/detectors/review_checklist.py).

Example:

```yaml
database_password: admin
```

AnsibleGuard may report this because `admin` is a recognized default
credential.

GitLeaks might not report it because `admin` is short, common, and does not
necessarily match a secret signature.

Conversely:

```yaml
github_token: ghp_abcdefghijklmnopqrstuvwxyz123456
```

GitLeaks will likely recognize a provider-specific token. AnsibleGuard’s
`default-credentials` will not necessarily report it because the value is not
a known default.

The overlap is therefore:

```text
GitLeaks: “Does this literal look like a secret?”
AnsibleGuard: “Is this credential field using a known default value?”
```

They overlap only when a known default literal also happens to trigger a
GitLeaks generic or provider rule.

### `credentials-leaking-in-log`: conceptually related, but different

This rule asks whether an Ansible task handles something credential-related
without:

```yaml
no_log: true
```

The implementation searches task content for terms such as:

- `password`
- `secret`
- `api_key`
- `token`
- `access_key`
- `client_secret`

It then checks the task’s `no_log` value. See
[`src/ansibleguard/detectors/credentials_leaking_in_log.py`](src/ansibleguard/detectors/credentials_leaking_in_log.py).

Example:

```yaml
- name: Authenticate
  ansible.builtin.uri:
    url: https://example.test/login
    body:
      password: "{{ service_password }}"
```

AnsibleGuard can report `credentials-leaking-in-log` because the task handles
a password and lacks `no_log: true`.

GitLeaks probably will not report it because `{{ service_password }}` is a
variable reference, not a literal secret.

The opposite is also possible:

```yaml
api_token: "ghp_realLookingToken123..."
```

GitLeaks can report the literal token even if it appears outside an Ansible
task. The `credentials-leaking-in-log` rule might not apply because there is
no task execution or logging context.

Therefore:

```text
GitLeaks:
Is a secret literal present in the source?

credentials-leaking-in-log:
Could an Ansible task expose a sensitive value during execution?
```

One is secret detection; the other is execution-context/logging protection.

## 2. `ansible-lint-issue`: exact ansible-lint integration

This has the same architectural relationship as `hardcoded-credentials`.

AnsibleGuard runs:

```text
ansible-lint <target> -f json
```

through
[`src/ansibleguard/external/ansible_lint.py`](src/ansibleguard/external/ansible_lint.py).

Every JSON issue returned by ansible-lint is converted into:

```json
{
  "rule_id": "ansible-lint-issue",
  "severity": "warning",
  "line": "<line supplied by ansible-lint>",
  "message": "<message supplied by ansible-lint>"
}
```

The conversion is in
[`src/ansibleguard/report/findings.py`](src/ansibleguard/report/findings.py).

Thus:

```text
ansible-lint name[missing]
ansible-lint risky-file-permissions
ansible-lint yaml[key-duplicates]
ansible-lint fqcn
...
        ↓
All become “ansible-lint-issue”
```

### Why it is an overlap

It is not merely similar to ansible-lint. It is ansible-lint’s result imported
into AnsibleGuard.

The rule means:

> “ansible-lint reported some issue here.”

It does not mean:

> “AnsibleGuard independently reproduced an ansible-lint rule.”

### Information lost during normalization

The normalized finding preserves:

- File association
- Line
- Message
- AnsibleGuard severity

But it collapses the native rule ID. For example, both:

```text
name[missing]
yaml[key-duplicates]
```

become:

```text
ansible-lint-issue
```

That makes aggregate reporting simpler, but prevents normalized results from
answering:

> How many findings came specifically from `name[missing]`?

without consulting the raw ansible-lint output.

It also forces every imported issue to AnsibleGuard’s `warning` severity, even
if ansible-lint internally categorizes or tags them differently.

### Potential double reporting

Under `technical-full`, a problem can produce both:

```text
ansible-lint-issue
```

and a corresponding internal AnsibleGuard rule.

For example, a duplicate key might produce:

```text
ansible-lint-issue       ← imported yaml[key-duplicates]
overriden-keys           ← AnsibleGuard’s independent detector
```

Those are two output records describing one underlying source problem.

This is why `ansible-lint-issue` should not be mixed into a study that measures
unique AnsibleGuard detector behavior. The research profiles disable external
tools.

## 3. Substantial native ansible-lint overlaps

These rules independently test nearly the same defect as an ansible-lint rule.

### `overriden-keys` versus `yaml[key-duplicates]`

Both detect repeated keys at the same YAML mapping level:

```yaml
- name: Install package
  ansible.builtin.apt:
    name: nginx
  become: true
  become: false
```

The second `become` silently overrides the first.

AnsibleGuard:

- Loads YAML with duplicate keys permitted
- Divides the source into task spans
- Groups keys by indentation/structural depth
- Reports the duplicate key and all involved line numbers

See
[`src/ansibleguard/detectors/overriden_keys.py`](src/ansibleguard/detectors/overriden_keys.py).

The overlap is substantial because both are targeting the same YAML correctness
defect.

They can differ because:

- They use different YAML parsing paths.
- AnsibleGuard scopes its reporting around task spans.
- Indentation normalization may differ.
- ansible-lint’s configured YAML rules may be enabled, disabled, or configured
  differently.
- Malformed or unusual YAML may be accepted by one parser and rejected by
  another.

The AnsibleGuard ID contains the existing spelling `overriden-keys`; the
standard English spelling would be `overridden-keys`.

### `deprecated-modules` versus `deprecated-module`

Both report tasks that use deprecated modules.

AnsibleGuard uses a manually maintained map of deprecated or relocated modules
and recommended replacements. It also reports some supported short names as
informational migration recommendations. See
[`src/ansibleguard/detectors/deprecated_modules.py`](src/ansibleguard/detectors/deprecated_modules.py).

Example:

```yaml
- name: Create server
  os_server:
    name: example
```

AnsibleGuard recommends:

```text
openstack.cloud.server
```

The overlap is substantial because both inspect the task’s module identity.

Differences arise because:

- AnsibleGuard’s list is curated and versioned in its source.
- ansible-lint follows its own installed rule/catalog behavior.
- AnsibleGuard includes selected short-name/FQCN recommendations in this
  detector.
- One catalog may be newer or broader than the other.

### `shell-instead-of-module` versus command-related lint rules

Example:

```yaml
- name: Install nginx
  ansible.builtin.shell: apt-get install nginx
```

AnsibleGuard recognizes high-confidence command patterns and recommends modules
such as:

- `apt`
- `package`
- `systemd`
- `file`
- `get_url`
- `git`
- `unarchive`

See
[`src/ansibleguard/detectors/shell_instead_of_module.py`](src/ansibleguard/detectors/shell_instead_of_module.py).

It deliberately skips complicated shell expressions containing pipes,
redirects, loops, or command chaining.

The closest ansible-lint rules also discourage unnecessary command/shell use,
but their catalogs and exemptions differ. Consequently:

- Many simple cases will match.
- AnsibleGuard might recognize a command from its curated command catalog that
  ansible-lint handles differently.
- ansible-lint might report shell/command misuse outside AnsibleGuard’s pattern
  catalog.
- AnsibleGuard skips complex shell expressions even when another rule might
  criticize them.

### `non-idempotent-command` versus `no-changed-when`

Both can report:

```yaml
- name: Create account
  ansible.builtin.command: useradd service_user
```

AnsibleGuard first requires the command to match a recognized mutating command
family. It then accepts guards such as:

- `creates`
- `removes`
- `changed_when`
- `check_mode`

See
[`src/ansibleguard/detectors/review_checklist.py`](src/ansibleguard/detectors/review_checklist.py).

The important distinction is:

```text
AnsibleGuard:
This appears to be a mutating command and has no idempotency guard.

ansible-lint no-changed-when:
This command-like task lacks appropriate change-state handling.
```

AnsibleGuard is narrower at the initial classification stage because it must
recognize the command as mutating.

### `shell-environment-export` versus `inline-env-var`

Example:

```yaml
- name: Run service
  ansible.builtin.shell: export API_URL=https://example.test && run-service
```

AnsibleGuard detects `export NAME=...` inside shell/command content and
recommends:

```yaml
environment:
  API_URL: https://example.test
```

See
[`src/ansibleguard/detectors/review_checklist.py`](src/ansibleguard/detectors/review_checklist.py).

The overlap is substantial when both rules inspect environment assignments
embedded in commands. AnsibleGuard’s specific predicate is the presence of
shell `export` patterns, including shell/raw contexts supported by its
traversal.

### `long-statement` versus `yaml[line-length]`

AnsibleGuard:

- Ignores empty lines
- Ignores full-line comments
- Expands tabs to two spaces
- Uses a configurable default threshold of 120 characters
- Reports the physical source line and measured length

See
[`src/ansibleguard/detectors/paper_candidates.py`](src/ansibleguard/detectors/paper_candidates.py).

The findings overlap substantially only if ansible-lint’s YAML line-length
configuration uses equivalent:

- Thresholds
- Comment treatment
- Tab handling
- Exclusions

A 110-character line, for example, could be clean under AnsibleGuard’s
120-character threshold but fail under a stricter configuration.

### `unnamed-play` and `unnamed-task` versus `name[missing]`

Both detect missing `name` fields:

```yaml
- hosts: all
  tasks:
    - ansible.builtin.debug:
        msg: Hello
```

This can produce:

- `unnamed-play`
- `unnamed-task`
- Imported `ansible-lint-issue` findings from `name[missing]`

The basic predicate overlaps strongly. AnsibleGuard separates play-level and
task-level identities and feeds their counts and locations into its own metrics
and output model.

## 4. Partial ansible-lint overlaps

### `long-task-name`

AnsibleGuard measures task-name length against its configured threshold.

Example:

```yaml
- name: This is an extremely long task name that exceeds the configured limit...
```

This is only partially related to ansible-lint’s naming subrules because the
exact permitted length, qualifying object, and exemptions can differ. Both
tools may dislike the same name, but not necessarily for the same reason.

### `inconsistent-naming-convention`

AnsibleGuard counts excessive punctuation or special characters in task/play
names.

Native naming rules cover broader naming conventions, while AnsibleGuard uses
its own punctuation-oriented metric. Therefore, each tool can report names
accepted by the other.

### `credentials-leaking-in-log` versus `no-log-password`

Both can report a password-handling task without `no_log`, but:

- AnsibleGuard searches serialized task content for sensitive terms.
- The ansible-lint rule has its own triggering logic and
  availability/configuration.
- AnsibleGuard covers terms beyond just password.
- Both may differ on indirect variables and module argument structures.

### `insecure-permissions`

AnsibleGuard explicitly parses numeric or symbolic modes. It reports:

- World-writable permissions
- Symbolic modes granting world write
- World-readable permissions when the task appears sensitive

See
[`src/ansibleguard/detectors/review_checklist.py`](src/ansibleguard/detectors/review_checklist.py).

Native risky-permission rules cover related bad modes, but their defaults and
module-specific assumptions differ.

### `silent-error-suppression`

AnsibleGuard reports:

```yaml
ignore_errors: true
```

or:

```yaml
failed_when: false
```

when the task does not register its result for later handling.

See
[`src/ansibleguard/detectors/review_checklist.py`](src/ansibleguard/detectors/review_checklist.py).

The native `ignore-errors` rule is related, but AnsibleGuard’s predicate
explicitly combines failure suppression with absence of `register`.

### `large-playbook` and `large-play`

These overlap with complexity rules only in the general sense that both
identify oversized structures.

AnsibleGuard calculates its own:

- Playbook size metrics
- Play size metrics
- Task metrics
- Configurable thresholds

A file can therefore exceed AnsibleGuard’s task/size threshold without
exceeding ansible-lint’s complexity threshold, and vice versa.

### `missing-abstraction`

AnsibleGuard reports more than ten leaf tasks in one file when there is no:

- Role
- `include_tasks`
- `import_tasks`
- `include_role`
- `import_role`

See
[`src/ansibleguard/detectors/paper_candidates.py`](src/ansibleguard/detectors/paper_candidates.py).

This is only partially related to complexity limits. AnsibleGuard asks a
second architectural question:

> Has this large task collection been split into reusable abstractions?

### `invalid-task-attribute-type`

AnsibleGuard directly checks universal task attributes:

- Boolean attributes must be booleans.
- Integer attributes must be integers.
- `environment` and `vars` must be mappings.
- `tags` must be a string or list.

See
[`src/ansibleguard/detectors/partial_checklist.py`](src/ansibleguard/detectors/partial_checklist.py).

ansible-lint may detect some of these through schema, syntax, or argument
validation. However, it validates through different mechanisms and may cover
far more module-specific data.

### `invalid-numeric-value`

AnsibleGuard explicitly checks:

- Ports are within `1..65535`
- Retry/timing/task-control values are not negative

See
[`src/ansibleguard/detectors/partial_checklist.py`](src/ansibleguard/detectors/partial_checklist.py).

Native module validation may reject some of these values, but there is no
guarantee every generic numeric range is checked identically.

### `deprecated-module-option`

AnsibleGuard asks `ansible-doc` for installed module metadata and combines it
with project-specific configuration overrides. It then checks supplied module
options for deprecation metadata.

See
[`src/ansibleguard/detectors/missing_checklist.py`](src/ansibleguard/detectors/missing_checklist.py).

It partially overlaps with argument and deprecation validation, but its project
override mechanism can generate findings that native ansible-lint does not.

## 5. Mostly adjacent rather than directly overlapping

### `unstructured-module`

AnsibleGuard checks role layout, such as:

```text
roles/example/tasks/main.yml
roles/example/handlers/main.yml
roles/example/defaults/main.yml
```

It reports missing `main.yml` or `main.yaml` entry points. See
[`src/ansibleguard/detectors/paper_candidates.py`](src/ansibleguard/detectors/paper_candidates.py).

Galaxy and schema checks operate in a similar structural area, but they do not
necessarily enforce this exact directory-entry-point predicate.

### `unexpected-task-location`

AnsibleGuard maps role directories to expected document shapes:

- `defaults/`, `vars/`, and `meta/` should contain mappings.
- `tasks/` and `handlers/` should contain task lists.
- Plays do not belong under role task directories.
- `listen` under `tasks/` suggests handler content in the wrong location.

See
[`src/ansibleguard/detectors/missing_checklist.py`](src/ansibleguard/detectors/missing_checklist.py).

Schema or load checks might catch some invalid examples, but AnsibleGuard
explicitly reasons from the path and role section.

### `missing-file-extension`

Native rules commonly examine the extension of the YAML or template file
itself.

AnsibleGuard instead examines references inside tasks and asks whether a
referenced filename lacks an extension. Therefore, the names sound equivalent,
but the inspected object is different:

```text
Native:
Is the playbook/template filename valid?

AnsibleGuard:
Does a task attribute reference a file without an extension?
```

### `missing-bool-filters`

AnsibleGuard looks for bare Boolean-like conditions that may need `| bool`.

Related native Jinja rules discourage literal comparison or unnecessary Jinja
syntax, but none necessarily implements exactly:

> “This condition references a value without explicitly converting it to
> Boolean.”

### `missing-handler` and `unused-handler`

AnsibleGuard performs cross-reference analysis:

```text
notify targets ─────────→ defined handlers
```

It reports:

- A notification whose handler does not exist
- A defined handler that is never notified

The native `no-handler` rule has a different purpose: it commonly identifies
tasks that react to a registered `.changed` condition and should instead be
handlers. It is not a missing/unused handler graph check.

### `broken-role-dependency`

AnsibleGuard builds a local role dependency graph and detects:

- Missing local role dependencies
- Self-dependencies
- Dependency cycles

See
[`src/ansibleguard/detectors/paper_candidates.py`](src/ansibleguard/detectors/paper_candidates.py).

Metadata or load rules may notice a malformed or unloadable dependency, but
they do not necessarily construct the equivalent local graph.

## Practical interpretation for the study

The overlap should be reported in three separate categories.

### 1. External integrations

- `hardcoded-credentials`
- `ansible-lint-issue`

These are external findings normalized by AnsibleGuard. They are not original
AnsibleGuard detection logic.

### 2. Independent overlapping detectors

Examples include:

- `overriden-keys`
- `deprecated-modules`
- `shell-instead-of-module`
- `non-idempotent-command`
- `unnamed-task`

These can be compared empirically against corresponding ansible-lint results
using agreement, unique findings, and false positives.

### 3. Adjacent Ansible-specific detectors

Examples include:

- `missing-handler`
- `unused-handler`
- `broken-role-dependency`
- `unexpected-task-location`
- `missing-bool-filters`

These should not be presented as duplicates merely because ansible-lint has
rules in the same general quality category.

Most importantly, do not claim that AnsibleGuard has independently implemented
secret detection through `hardcoded-credentials` or independently implemented
all ansible-lint checks through `ansible-lint-issue`. Those two rules are
adapters that place external-tool results into AnsibleGuard’s unified reporting
contract.
