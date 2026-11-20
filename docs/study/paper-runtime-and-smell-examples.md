# Smell examples and measured runtime for the paper

The paper updates are in [the draft package](../paper-draft-2026-11-15/README.md). The examples below illustrate implemented static conditions. They are not independently validated defects or evidence of runtime exploitation.

## Full rule catalog

- [Generated inventory of all 76 catalog rules](../../RULE_REFERENCE.generated.md): rule IDs, concepts, maturity, severity, confidence and category. The catalog includes experimental rules and provider wrappers; 76 rules does not mean 76 independently validated defect types.
- [Detailed explanatory smell catalog](../rules/smell-catalog.md): purposes, implementation algorithms, thresholds and limitations. The generated inventory is the authority for completeness.
- [Canonical smell summary](../rules/detected-smells.md): compact detector descriptions.

## Three representative examples

These are illustrative snippets, not extracted examples from the evaluated repositories.

### Disabled TLS certificate verification: `missing-validate-certs`

```yaml
- name: Download the application archive
  ansible.builtin.get_url:
    url: https://example.invalid/app.tar.gz
    dest: /tmp/app.tar.gz
    mode: '0644'
    validate_certs: false
```

The explicit false value disables certificate validation. Whether enabling it is an appropriate change depends on the intended trust configuration. [Detector](../../src/ansibleguard/detectors/missing_validate_certs.py).

### World-writable target: `insecure-permissions`

```yaml
- name: Create the shared directory
  ansible.builtin.file:
    path: /srv/shared
    state: directory
    mode: '0777'
```

The mode grants write permission to other users (`mode & 0o002 != 0`). This is a security signal whose actionability depends on the intended sharing policy.

### Repeated mutating command: `non-idempotent-command`

```yaml
- name: Restart nginx
  ansible.builtin.command: systemctl restart nginx
```

The task repeats a mutating restart without a recognized execution/change guard. The appropriate module or handler depends on the desired behavior. The implementation and limitations of both this detector and the permissions detector are described in the [smell catalog](../rules/smell-catalog.md).

## Runtime table

| Measure | Observations | Time (seconds) |
|---|---:|---:|
| Median repository scan | 207 attempts | 22.9 |
| Median PR comparison | 21 comparisons | 34.4 |
| Maximum PR comparison | 21 comparisons | 326.0 |

The exact scan median is 22.881 seconds, rounded to one decimal. The 207 attempts comprise 171 complete scans, 35 provider-partial scans and one failed/timeout scan. All attempts are included in this median; it is not a complete-provider-only estimate. The 206 usable scans include the 35 partial-provider cases. PR runtime uses the `pr_seconds` column only, not the separate review-range pass.

Sources:

- [Raw scan runtimes](../../study/analysis-v0071-rerun-2026-10-22/run/tables/runtimes.csv).
- [Raw PR replay measurements](../../study/pr-replay-v007-2026-10-15/prs.csv).
- [PR replay selection, exclusions and attribution results](../../study/pr-replay-v007-2026-10-15/README.md).
- [Full corpus report](v0071-rerun-2026-10-22-full-report.md).

These are observed end-to-end timings from separate original runs. They are machine-dependent and do not establish a controlled speed advantage over ansible-lint or another tool. No new scan, PR replay or model experiment was run for this documentation change. Do not combine their elapsed times as if they came from one matched benchmark.

[The calculation script](../../scripts/summarize_paper_runtime.py) regenerates the statistics from the two CSVs; the [recorded summary](../paper-draft-2026-11-15/runtime-summary.json) preserves the values used in the papers.

## Detection accuracy is a separate question
