# V0.0.7 full-run partial and failure analysis

Run: `v007-full-repro-2026`

Run date: 2026-10-06

`ansible-lint`: version 26.4.0 in the recorded runner environment.

## Outcome

Of 207 frozen repositories, 171 are complete, 35 are partial, and one failed by timeout. All 35 partial rows have completed AnsibleGuard and GitLeaks scans; only the optional `ansible-lint` provider is partial. The timeout is separate: `encapsulate-xyz/cosmos-ansible` exceeded AnsibleGuard's 1,800-second limit before any provider output was produced.

The provider totals are `ansible-lint`: 171 completed / 35 partial / 1 missing, and GitLeaks: 206 completed / 1 missing. A partial `ansible-lint` result is missing external-provider evidence, not zero findings. It does not erase the completed AnsibleGuard results for those repositories, but those repositories cannot support complete cross-provider comparisons.

## Recorded causes for the 35 partial `ansible-lint` runs

The root repository `diagnostics.json` files yield these mutually exclusive primary-message groups:

| Repositories | Recorded evidence | Interpretation and limit |
|---:|---|---|
| 6 | ansible-lint rejects a repository config because `parseable` is an unexpected property; return code 3 | Configuration/schema incompatibility with the installed ansible-lint 26.4.0. The affected configs are in `ansible-collections/ibm_zos_core`, `ansible-lockdown/RHEL7-STIG`, `ansible/instruqt`, `Kubeinit/kubeinit`, `progmaticltd/homebox`, and `redhat-openstack/infrared`. Some repositories had more than one selected lint root using the same rejected config. |
| 25 | `ansible-playbook --syntax-check -vv <path>` returned nonzero: 416 code-1 diagnostics and 7 code-4 diagnostics (423 diagnostic records total) | The wrapper records which syntax-check command failed, but generally not its underlying stderr. Do not infer that all affected playbooks are intrinsically invalid; the preserved evidence is insufficient to distinguish project syntax/dependency issues from execution-environment causes. |
| 2 | ansible-lint says `load-failure` is unskippable and cannot appear in `skip_list` or `warn_list` | Repository lint configuration asks ansible-lint to suppress/warn on a rule it does not allow to be skipped. These are `ceph/ceph-cm-ansible` and `SkynetLabs/ansible-playbooks`. |
| 1 | `tests/requirements.yml` is rejected because its top-level keys are not limited to `roles` and `collections` | Provider validation of that requirements file fails. Repository: `bitsy-ai/ansible-collection-printnanny`. |
| 1 | ansible-lint exits 1 before producing valid JSON; captured diagnostic contains only a PATH-altered warning | The underlying cause is not recorded, so it cannot be diagnosed further from this run artifact. Repository: `CentOS-PaaS-SIG/linchpin`. |

These explain the recorded partial classification; they are not five guesses about one common error. In particular, only the six invalid-config cases share the unsupported `parseable` setting. The syntax-check group is a separate, broad failure mode. The runner often emitted a warning about `PATH` including the project virtual environment, but that warning alone is not evidence that it caused the syntax-check failures.

## Separate timeout

`encapsulate-xyz/cosmos-ansible` failed with `RuntimeError: AnsibleGuard timed out after 1800 seconds`. Its AnsibleGuard, ansible-lint, and GitLeaks outputs are missing. It must not be counted as a successful zero-finding repository or included among the 35 partial repositories.

## Evidence paths

- `study/runs/v007-full-repro-2026/FULL_RUN_REPORT.md` — execution state and incomplete-repository list.
- `study/runs/v007-full-repro-2026/tables/repository-execution-status.csv` — one row per repository and provider state.
- `study/runs/v007-full-repro-2026/tables/failures-and-partials.csv` — partial and timed-out repository list.
- `study/runs/v007-full-repro-2026/aggregate/provider-health.csv` — provider totals.
- `study/runs/v007-full-repro-2026/repositories/<repo-slug>/<commit>/diagnostics.json` — exact captured diagnostic messages and provider evidence.
- `study/runs/v007-full-repro-2026/logs/encapsulate-xyz__cosmos-ansible__a49d30281d2d.log` — timed-out repository runner log.

No repository configuration was edited to make this report. Any rerun that changes lint versions/configurations or retries the timeout must be recorded as a new run, not silently substituted into these results.
