# What ansible-lint and GitLeaks detect, and where AnsibleGuard overlaps

## The answer first

Yes, AnsibleGuard overlaps with both tools.

- GitLeaks is already the implementation behind AnsibleGuard's
  `hardcoded-credentials` rule. It is not a second independent detector.
- ansible-lint is already integrated, but all of its native findings are
  normalized as the single generic ID `ansible-lint-issue`.
- Several AnsibleGuard internal rules substantially or partially repeat
  ansible-lint checks.
- Most AnsibleGuard research, semantic, Git-review, variable-flow, duplicate,
  and role-graph rules are not provided by GitLeaks and do not have a direct
  ansible-lint equivalent.

This audit was checked on 22 July 2026 against:

- locally installed ansible-lint 26.4.0 with ansible-core 2.21.0;
- the 53 top-level rules returned locally by `ansible-lint -L`;
- the [official ansible-lint rule index](https://docs.ansible.com/projects/lint/rules/);
- AnsibleGuard's pinned GitLeaks 8.30.1 binary;
- the 222 rules in the [official GitLeaks 8.30.1 default configuration](https://github.com/gitleaks/gitleaks/blob/v8.30.1/config/gitleaks.toml);
- the [official GitLeaks usage/configuration documentation](https://github.com/gitleaks/gitleaks).

The versions matter. `ansible-lint` is not pinned in `pyproject.toml`, so a
fresh installation can expose different rules or behavior.

## Do not confuse the three tools

| Tool | Main question |
|---|---|
| AnsibleGuard internal rules | Does this Ansible source/repository/review contain one of our 58 defined conditions? |
| ansible-lint | Does Ansible content violate official/community syntax, formatting, idiom, safety, metadata, or packaging rules? |
| GitLeaks | Does text look like a real secret, token, private key, or credential format? |

GitLeaks does not understand plays, handlers, tags, idempotency, role
structure, or Git commit-message policy. ansible-lint does not replace a
secret scanner or the empirical-study pipeline.

## How AnsibleGuard runs ansible-lint today

Code: `src/ansibleguard/external/ansible_lint.py`.

Slowly:

1. find `ansible-lint` beside the running Python, otherwise use `PATH`;
2. set a writable `ANSIBLE_LOCAL_TEMP` under the temporary directory;
3. run one target-level command with JSON output;
4. treat return codes 0 and 2 as a completed lint run;
5. parse the JSON;
6. match issues back to files;
7. normalize each issue to `ansible-lint-issue` with its file, line, and
   message;
8. record missing/failed/invalid-output cases as tool diagnostics.

The wrapper does not pass `--profile`, `--enable-list`, or `--fix`. The target
project's ansible-lint configuration and ansible-lint defaults determine what
runs. A rule shown by `-L` is not necessarily enabled: opt-in and experimental
rules may require configuration.

ansible-lint runs only in AnsibleGuard's `technical-full` profile. It is
intentionally absent from `snapshot-source`, `research-core`, and
`extended-ansible`.

## The 53 ansible-lint 26.4.0 top-level rules

The descriptions below are intentionally simple. Many IDs contain narrower
subrules, such as `name[casing]` or `yaml[line-length]`.

### Loading, syntax, schema, and arguments

| Native ID | What it catches |
|---|---|
| `args` | invalid module arguments that can be validated from module specs; experimental |
| `internal-error` | an unexpected ansible-lint internal failure |
| `load-failure` | content that cannot be loaded or classified |
| `parser-error` | an Ansible parser error |
| `schema` | JSON-schema violations for known file kinds |
| `syntax-check` | failures from Ansible syntax checking |
| `warning` | other warnings emitted during the run; experimental |

These checks are especially useful because AnsibleGuard's safe parser tries to
preserve evidence even when full structural analysis is impossible.

### Commands, shell, idempotency, and safety

| Native ID | What it catches |
|---|---|
| `command-instead-of-module` | a command that should use a native module |
| `command-instead-of-shell` | `shell` used when `command` is enough |
| `ignore-errors` | broad `ignore_errors` instead of explicit failure conditions |
| `inline-env-var` | environment assignment embedded in `command` syntax |
| `latest` | non-repeatable “latest” behavior in selected modules |
| `no-changed-when` | commands that do not define when they changed |
| `no-free-form` | discouraged free-form module/action syntax |
| `no-handler` | a task conditioned on a previous result's change that should likely be a handler |
| `package-latest` | package installation requesting latest |
| `risky-file-permissions` | missing or unsafe file-creation permissions |
| `risky-octal` | ambiguous octal permission notation |
| `risky-shell-pipe` | a shell pipe without `pipefail` protection |

Important naming trap: ansible-lint's `no-handler` does not mean “a notify
references a missing handler.” It recommends turning certain conditional tasks
into handlers. AnsibleGuard's `missing-handler` and `unused-handler` are
different checks.

### Jinja, comparisons, variables, and execution behavior

| Native ID | What it catches |
|---|---|
| `avoid-implicit` | implicit behavior that can be unpredictable |
| `deprecated-bare-vars` | obsolete unbraced/bare variable syntax |
| `empty-string-compare` | direct comparison with an empty string; opt-in |
| `jinja` | Jinja spacing/syntax/formatting problems |
| `literal-compare` | comparison with literal `True`/`False` |
| `loop-var-prefix` | role loop variable lacks the configured prefix |
| `no-jinja-when` | Jinja delimiters used inside `when` |
| `run-once` | unsafe `run_once` interaction with free strategy |
| `var-naming` | variable names violate the configured convention |

These are adjacent to some AnsibleGuard variable rules, but none builds the
same repository/local symbol model as `unguarded-variable` or checks linear
`variable-use-before-definition` in the same way.

### Deprecation and Ansible style

| Native ID | What it catches |
|---|---|
| `deprecated-local-action` | old `local_action` instead of `delegate_to` |
| `deprecated-module` | use of a deprecated module |
| `fqcn` | actions not using preferred fully qualified collection names |
| `partial-become` | `become_user` without corresponding `become` |
| `only-builtins` | non-builtin actions when a project opts into builtin-only policy |
| `sanity` | invalid entries in Ansible sanity ignore files |

### Names, paths, formatting, and YAML

| Native ID | What it catches |
|---|---|
| `jinja-template-extension` | template files without `.j2`; opt-in |
| `key-order` | discouraged ordering of task/play keys |
| `name` | missing/name-format/casing/template-placement issues |
| `no-relative-paths` | discouraged relative `src` paths |
| `no-tabs` | tab characters where they are unsafe/undesired |
| `playbook-extension` | playbooks not using `.yml` or `.yaml` |
| `yaml` | yamllint formatting/syntax rules such as indentation, spacing, key duplication, truthy values, and configured line length |

`yaml` is an umbrella. The precise enabled subrules depend on yamllint and
project configuration.

### Role, collection, and metadata rules

| Native ID | What it catches |
|---|---|
| `galaxy` | collection/Galaxy metadata problems |
| `galaxy-version-incorrect` | collection version not greater than 1.0.0; opt-in |
| `meta-incorrect` | role `meta/main.yml` placeholder/default metadata |
| `meta-no-tags` | invalid Galaxy metadata tags |
| `meta-runtime` | unsupported `requires_ansible` in `meta/runtime.yml` |
| `meta-video-links` | malformed metadata video links |
| `role-argument-spec` | role lacks an argument specification; opt-in |
| `role-name` | role name violates lowercase identifier rules |

### Security and transfer behavior

| Native ID | What it catches |
|---|---|
| `no-log-password` | password-handling loop/task should use `no_log`; opt-in and experimental |
| `no-prompting` | interactive prompting; opt-in |
| `no-same-owner` | risky preservation of owner/group across hosts; opt-in |

### Experimental complexity

| Native ID | What it catches |
|---|---|
| `complexity` | excessive play/playbook complexity according to ansible-lint's current limits; experimental |

The installed profile display also mentions planned/profile-level checks whose
top-level implementations are not returned by this environment's `-L`, such as
`max-block-depth`, `max-tasks`, `layout`, and `single-entry-point`. Do not claim
those as active local rules merely because a profile description names them.

## How AnsibleGuard runs GitLeaks today

Code:

- `src/ansibleguard/external/install_gitleaks.py` pins version 8.30.1;
- `src/ansibleguard/external/gitleaks.py` runs it.

Current command shape:

```text
gitleaks detect --source <target> --no-git
  --report-format json --report-path <temporary-file>
```

Behavior:

1. scan the current directory/file content, not Git history;
2. use `<target>/.gitleaks.toml` when one exists;
3. otherwise use GitLeaks' built-in default configuration;
4. accept exit code 0 (no leak) or 1 (leaks found) as completed;
5. read the temporary JSON report;
6. preserve non-YAML secret findings in project rollups;
7. normalize every result to `hardcoded-credentials`.

The official Gitleaks documentation notes that `detect` was deprecated/hidden
after 8.19 in favor of `dir`, `git`, and `stdin`, although it remains available
for compatibility. The wrapper should eventually move to `gitleaks dir`.

## What GitLeaks' 222 default rules cover

GitLeaks 8.30.1 contains provider- and format-specific secret detectors. It is
more useful to understand the families than memorize 222 IDs.

| Family | Examples from the pinned configuration |
|---|---|
| cloud credentials | AWS, Azure AD, GCP, Alibaba, Cloudflare, DigitalOcean, OpenShift |
| source control and CI/CD | GitHub, GitLab, Bitbucket, Travis CI, Drone CI, Codecov |
| AI services | Anthropic, Cohere, Hugging Face, OpenAI, Perplexity |
| package/artifact registries | Artifactory, JFrog, npm, NuGet, PyPI, RubyGems, Clojars |
| monitoring/observability | Datadog, Dynatrace, Grafana, New Relic, Sentry, Sumo Logic |
| communication/social | Discord, Slack, Teams webhook, Telegram, Twitter, Twitch |
| databases/data/SaaS | Airtable, Algolia, Confluent, Contentful, Databricks, LaunchDarkly, Notion |
| commerce/payment | Coinbase, Flutterwave, Plaid, Shopify, Square, Stripe, Twilio |
| infrastructure/dev tools | HashiCorp Terraform, Vault, Pulumi, Snyk, Sonar, Infracost |
| generic and cryptographic material | generic API keys, JWT/JWT-base64, private keys, PKCS#12, curl authentication, Kubernetes Secret YAML |

The exact 222 IDs are authoritative in the pinned default config linked at the
top of this file. Some notable Ansible-relevant IDs are:

```text
aws-access-token
azure-ad-client-secret
gcp-api-key
generic-api-key
github-pat
gitlab-pat
jwt
kubernetes-secret-yaml
openai-api-key
private-key
vault-batch-token
vault-service-token
```

<details>
<summary>Complete GitLeaks 8.30.1 built-in rule-ID list (222 IDs)</summary>

This list was extracted from the pinned official default configuration. A
target `.gitleaks.toml` can extend, disable, replace, or add rules, so the
effective target list can differ.

- `1password-secret-key`
- `1password-service-account-token`
- `adafruit-api-key`
- `adobe-client-id`
- `adobe-client-secret`
- `age-secret-key`
- `airtable-api-key`
- `airtable-personnal-access-token`
- `algolia-api-key`
- `alibaba-access-key-id`
- `alibaba-secret-key`
- `anthropic-admin-api-key`
- `anthropic-api-key`
- `artifactory-api-key`
- `artifactory-reference-token`
- `asana-client-id`
- `asana-client-secret`
- `atlassian-api-token`
- `authress-service-client-access-key`
- `aws-access-token`
- `aws-amazon-bedrock-api-key-long-lived`
- `aws-amazon-bedrock-api-key-short-lived`
- `azure-ad-client-secret`
- `beamer-api-token`
- `bitbucket-client-id`
- `bitbucket-client-secret`
- `bittrex-access-key`
- `bittrex-secret-key`
- `cisco-meraki-api-key`
- `clickhouse-cloud-api-secret-key`
- `clojars-api-token`
- `cloudflare-api-key`
- `cloudflare-global-api-key`
- `cloudflare-origin-ca-key`
- `codecov-access-token`
- `cohere-api-token`
- `coinbase-access-token`
- `confluent-access-token`
- `confluent-secret-key`
- `contentful-delivery-api-token`
- `curl-auth-header`
- `curl-auth-user`
- `databricks-api-token`
- `datadog-access-token`
- `defined-networking-api-token`
- `digitalocean-access-token`
- `digitalocean-pat`
- `digitalocean-refresh-token`
- `discord-api-token`
- `discord-client-id`
- `discord-client-secret`
- `doppler-api-token`
- `droneci-access-token`
- `dropbox-api-token`
- `dropbox-long-lived-api-token`
- `dropbox-short-lived-api-token`
- `duffel-api-token`
- `dynatrace-api-token`
- `easypost-api-token`
- `easypost-test-api-token`
- `etsy-access-token`
- `facebook-access-token`
- `facebook-page-access-token`
- `facebook-secret`
- `fastly-api-token`
- `finicity-api-token`
- `finicity-client-secret`
- `finnhub-access-token`
- `flickr-access-token`
- `flutterwave-encryption-key`
- `flutterwave-public-key`
- `flutterwave-secret-key`
- `flyio-access-token`
- `frameio-api-token`
- `freemius-secret-key`
- `freshbooks-access-token`
- `gcp-api-key`
- `generic-api-key`
- `github-app-token`
- `github-fine-grained-pat`
- `github-oauth`
- `github-pat`
- `github-refresh-token`
- `gitlab-cicd-job-token`
- `gitlab-deploy-token`
- `gitlab-feature-flag-client-token`
- `gitlab-feed-token`
- `gitlab-incoming-mail-token`
- `gitlab-kubernetes-agent-token`
- `gitlab-oauth-app-secret`
- `gitlab-pat`
- `gitlab-pat-routable`
- `gitlab-ptt`
- `gitlab-rrt`
- `gitlab-runner-authentication-token`
- `gitlab-runner-authentication-token-routable`
- `gitlab-scim-token`
- `gitlab-session-cookie`
- `gitter-access-token`
- `gocardless-api-token`
- `grafana-api-key`
- `grafana-cloud-api-token`
- `grafana-service-account-token`
- `harness-api-key`
- `hashicorp-tf-api-token`
- `hashicorp-tf-password`
- `heroku-api-key`
- `heroku-api-key-v2`
- `hubspot-api-key`
- `huggingface-access-token`
- `huggingface-organization-api-token`
- `infracost-api-token`
- `intercom-api-key`
- `intra42-client-secret`
- `jfrog-api-key`
- `jfrog-identity-token`
- `jwt`
- `jwt-base64`
- `kraken-access-token`
- `kubernetes-secret-yaml`
- `kucoin-access-token`
- `kucoin-secret-key`
- `launchdarkly-access-token`
- `linear-api-key`
- `linear-client-secret`
- `linkedin-client-id`
- `linkedin-client-secret`
- `lob-api-key`
- `lob-pub-api-key`
- `looker-client-id`
- `looker-client-secret`
- `mailchimp-api-key`
- `mailgun-private-api-token`
- `mailgun-pub-key`
- `mailgun-signing-key`
- `mapbox-api-token`
- `mattermost-access-token`
- `maxmind-license-key`
- `messagebird-api-token`
- `messagebird-client-id`
- `microsoft-teams-webhook`
- `netlify-access-token`
- `new-relic-browser-api-token`
- `new-relic-insert-key`
- `new-relic-user-api-id`
- `new-relic-user-api-key`
- `notion-api-token`
- `npm-access-token`
- `nuget-config-password`
- `nytimes-access-token`
- `octopus-deploy-api-key`
- `okta-access-token`
- `openai-api-key`
- `openshift-user-token`
- `perplexity-api-key`
- `pkcs12-file`
- `plaid-api-token`
- `plaid-client-id`
- `plaid-secret-key`
- `planetscale-api-token`
- `planetscale-oauth-token`
- `planetscale-password`
- `postman-api-token`
- `prefect-api-token`
- `private-key`
- `privateai-api-token`
- `pulumi-api-token`
- `pypi-upload-token`
- `rapidapi-access-token`
- `readme-api-token`
- `rubygems-api-token`
- `scalingo-api-token`
- `sendbird-access-id`
- `sendbird-access-token`
- `sendgrid-api-token`
- `sendinblue-api-token`
- `sentry-access-token`
- `sentry-org-token`
- `sentry-user-token`
- `settlemint-application-access-token`
- `settlemint-personal-access-token`
- `settlemint-service-access-token`
- `shippo-api-token`
- `shopify-access-token`
- `shopify-custom-access-token`
- `shopify-private-app-access-token`
- `shopify-shared-secret`
- `sidekiq-secret`
- `sidekiq-sensitive-url`
- `slack-app-token`
- `slack-bot-token`
- `slack-config-access-token`
- `slack-config-refresh-token`
- `slack-legacy-bot-token`
- `slack-legacy-token`
- `slack-legacy-workspace-token`
- `slack-user-token`
- `slack-webhook-url`
- `snyk-api-token`
- `sonar-api-token`
- `sourcegraph-access-token`
- `square-access-token`
- `squarespace-access-token`
- `stripe-access-token`
- `sumologic-access-id`
- `sumologic-access-token`
- `telegram-bot-api-token`
- `travisci-access-token`
- `twilio-api-key`
- `twitch-api-token`
- `twitter-access-secret`
- `twitter-access-token`
- `twitter-api-key`
- `twitter-api-secret`
- `twitter-bearer-token`
- `typeform-api-token`
- `vault-batch-token`
- `vault-service-token`
- `yandex-access-token`
- `yandex-api-key`
- `yandex-aws-access-token`
- `zendesk-secret-key`

</details>

GitLeaks rules typically combine a provider pattern, keywords, secret capture
group, optional Shannon entropy threshold, and allowlists. Newer versions can
also use required/proximity subrules.

## What GitLeaks does not detect

GitLeaks does not decide whether:

- `no_log: true` is missing;
- `validate_certs: false` is unsafe;
- a file mode is world writable;
- `admin` is a weak product default without matching a secret rule;
- a command is non-idempotent;
- a handler, tag, role dependency, or variable is wrong;
- a task/play is too large or unnamed;
- a commit lacks a release note/test/bug reference;
- two smells co-occur or correlate with defects.

It can sometimes find the literal secret involved in one of those situations,
but that is not the same detector.

## Direct and substantial overlap with AnsibleGuard

### GitLeaks overlap

| AnsibleGuard rule | GitLeaks relationship | Verdict |
|---|---|---|
| `hardcoded-credentials` | Every GitLeaks finding becomes this rule | Same implementation, exact integration |
| `default-credentials` | A provider/generic rule may coincidentally match a default literal | Small partial overlap; GitLeaks is not a default-value checker |
| `credentials-leaking-in-log` | GitLeaks may find the literal secret in source | Different; it does not reason about `no_log` |
| every other rule | no corresponding GitLeaks behavior | No overlap |

### ansible-lint overlap

| AnsibleGuard rule | Closest native ansible-lint rule | Overlap judgment | Important difference |
|---|---|---|---|
| `ansible-lint-issue` | all enabled native rules | Exact integration | native IDs are collapsed |
| `overriden-keys` | `yaml[key-duplicates]` | Substantial | exact YAML parser/config behavior can differ |
| `deprecated-modules` | `deprecated-module` | Substantial | AnsibleGuard uses its own curated map |
| `shell-instead-of-module` | `command-instead-of-module`, partly `command-instead-of-shell` | Substantial | catalogs and recommendations differ |
| `non-idempotent-command` | `no-changed-when` | Substantial/partial | AnsibleGuard first recognizes mutating command families |
| `shell-environment-export` | `inline-env-var` | Substantial for command syntax | AnsibleGuard also examines shell/raw export patterns |
| `long-statement` | configured `yaml[line-length]` | Substantial when enabled identically | thresholds/comment handling may differ |
| `unnamed-play`, `unnamed-task` | `name[missing]` behavior | Substantial | AnsibleGuard also feeds its own metrics/output |
| `long-task-name` | selected `name` limits/subrules | Partial | exact length rule and threshold differ |
| `inconsistent-naming-convention` | `name`, `var-naming`, `role-name` | Partial | AnsibleGuard counts punctuation in task/play names |
| `credentials-leaking-in-log` | `no-log-password` | Partial | ansible-lint rule is opt-in/experimental and has narrower triggering logic |
| `insecure-permissions` | `risky-file-permissions`, `risky-octal` | Partial | AnsibleGuard parses explicit world bits and sensitive world-read context |
| `silent-error-suppression` | `ignore-errors` | Partial | AnsibleGuard also considers `failed_when: false` and `register` |
| `large-playbook`, `large-play` | `complexity` | Partial | metrics and thresholds are different |
| `missing-abstraction` | `complexity` and profile-described max-task checks | Partial | AnsibleGuard additionally asks whether includes/roles exist |
| `invalid-task-attribute-type` | `args`, `schema`, `syntax-check` | Partial | AnsibleGuard checks universal task keyword YAML types directly |
| `invalid-numeric-value` | `args`/module validation | Small partial | AnsibleGuard has explicit port and retry/timing ranges |
| `deprecated-module-option` | `args`, deprecation-related validation | Partial | AnsibleGuard reads deprecation metadata and project overrides |
| `unstructured-module` | `galaxy`, metadata/schema and layout-adjacent checks | Partial | AnsibleGuard requires role directory main entry points |
| `unexpected-task-location` | `schema`, `load-failure` | Partial | AnsibleGuard explicitly maps role directories to document shapes |
| `missing-file-extension` | `playbook-extension`, `jinja-template-extension` | Similar words, mostly different | AnsibleGuard examines task attribute references, not just filenames |
| `missing-bool-filters` | `literal-compare`, `no-jinja-when`, `jinja` | Adjacent, not equivalent | none requires AnsibleGuard's bare condition `| bool` rule |
| `missing-handler`, `unused-handler` | `no-handler`, `syntax-check` | Mostly different | `no-handler` has a different meaning; cross-reference logic is AnsibleGuard's |
| `broken-role-dependency` | `load-failure`, metadata/schema rules | Small partial | no local missing/self/cycle graph equivalent |

## AnsibleGuard rules with no direct ansible-lint or GitLeaks equivalent

The following groups remain distinctive in this repository.

### Data flow and local symbol reasoning

```text
overriding-facts
unguarded-variable
variable-use-before-definition
unscoped-shell-variable
redundant-default-value
unnecessary-set-fact
unused-include-vars
unused-registered-variable
```

ansible-lint has variable syntax/naming checks, but not these same definition,
reference, ordering, and dead-state algorithms.

### Exact duplication and local handler graph

```text
duplicated-code
duplicate-task-names
missing-handler
unused-handler
broken-role-dependency
high-coupling
```

Some load/syntax failures can reveal related problems, but not the same count
or graph definition.

### Paper/research-specific structural and semantic rules

```text
complex-expression
incomplete-task
empty-abstraction
excessive-nesting
incohesive-playbook
incohesive-play
```

ansible-lint's Jinja formatting and experimental complexity are not equivalent
to AnsibleGuard's expression score or spaCy pairwise semantic similarity.

### AnsibleGuard-specific operational checks

```text
missing-validate-certs
default-credentials
missing-tags
unnecessary-abstraction
undocumented-complex-task
unused-handler
```

There can be neighboring ansible-lint rules, but no active top-level native
rule implements these same predicates.

### Git review-range rules

```text
missing-release-note
missing-bug-reference
invalid-depends-on-reference
commit-message-format
removed-copyright-notice
missing-test-update
untested-override-change
```

These inspect base-to-head Git evidence. Standard ansible-lint and GitLeaks
directory scans do not implement them.

## Why overlap is not automatically bad

Overlap can provide:

- independent confirmation;
- richer AnsibleGuard study metrics;
- a fallback when one tool is unavailable;
- different thresholds or project configuration;
- one normalized output contract for CI.

But overlap creates problems when counts are added as if each tool found a
different smell. One physical problem can appear as both an internal finding
and `ansible-lint-issue`.

For engineering reports, showing both can be useful. For research prevalence,
the project must define an occurrence key and deduplicate or keep detector
families in separate tables.

## The biggest current integration gaps

### 1. ansible-lint native identity is lost

Current output records:

```text
rule_id = ansible-lint-issue
```

It should additionally preserve fields such as:

```text
external_tool = ansible-lint
external_rule_id = no-changed-when
external_subrule = name[casing]
external_version = 26.4.0
```

Without that identity, “ansible-lint smell prevalence” is not scientifically
meaningful.

### 2. GitLeaks native identity is lost

Current output records only:

```text
rule_id = hardcoded-credentials
message = native description
```

It should retain native `RuleID`, entropy, fingerprint, tags, tool version, and
scan mode in structured fields while redacting secret material.

### 3. ansible-lint is not dependency-pinned

`pyproject.toml` says `ansible-lint` without a version. Reproducing research
requires a locked environment and saved `ansible-lint --version`.

### 4. GitLeaks uses current-tree mode only

`--no-git` is correct for a frozen snapshot secret scan, but it will not find a
secret deleted from HEAD but still present in history. A historical secret
question needs a separate `gitleaks git` protocol, not silent replacement of
the snapshot definition.

### 5. custom `.gitleaks.toml` can change the rule population

The wrapper explicitly uses a target config when present. In GitLeaks, a
custom config can replace defaults unless it declares `[extend] useDefault =
true`. The run metadata should hash the effective config and record whether
defaults were extended or replaced.

### 6. the wrapper uses a deprecated command name

GitLeaks still supports `detect`, but official documentation directs new use
to `dir`, `git`, or `stdin`. Updating to `dir` should be covered by a pinned
version test so output compatibility is deliberate.

## Recommended division of responsibility

Use:

- GitLeaks for real secret formats and entropy/pattern scanning;
- ansible-lint for official syntax, schemas, module arguments, formatting,
  standard idioms, and packaging conventions;
- AnsibleGuard internal rules for the study constructs, specialized role/data
  flow, semantic/size metrics, project review checks, and gaps not covered by
  the external tools.

Do not add a new internal clone of a native external rule unless the project
needs a different formal definition, source-line/detail contract, or
independent research construct. When it does overlap, document the exact
difference and deduplication policy.

## Reproducing this audit locally

```bash
mkdir -p /tmp/ansibleguard-ansible-tmp
ANSIBLE_LOCAL_TEMP=/tmp/ansibleguard-ansible-tmp \
  .venv/bin/ansible-lint --version
ANSIBLE_LOCAL_TEMP=/tmp/ansibleguard-ansible-tmp \
  .venv/bin/ansible-lint -L -f md
/home/aymmzn/.ansibleguard/gitleaks-bin/gitleaks version
```

The exact active result of a target scan also depends on its `.ansible-lint`,
yamllint, `.gitleaks.toml`, and `.gitleaksignore` files. Save those or their
hashes with any research run.
