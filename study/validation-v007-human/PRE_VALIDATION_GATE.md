# V007 human-validation pre-validation gate

**Gate status:** PASS for calibration-only source preparation, with the isolated caveats listed below. No human sample has been selected or frozen.

## Source identity

- **Source run:** `v007-full-repro-2026`; frozen population: 207 repositories; canonical acquisition/analysis worker count: 4.
- **Analysis commit recorded by the run:** `3391f2756c1079a7da9d2fd94c7a0960ff526ebd`.
- **Reporting/package code:** reporting repair `0ac344201299a9a8421bad55e39b725bae644758`; provider-attribution repair `7fb40155`; package refresh/build repair `cc1a8c6bc3839c703c3c11fcfdd1bfce7a694224`.
- **Validation identity builder:** commit `34df886a2586ead18703f568b0b360a890207d71`, branch `study/v007-human-validation`.
- **Validation branch base:** exact parent `cb304a52bb8fcc4db12f58aa8c44f53e4411ef18`, the verified reproducibility branch head.
- **Authoritative occurrence file:** `study/runs/v007-full-repro-2026/aggregate/all-internal-source-occurrences.csv`.
- **Authoritative source SHA-256:** `7ea8943bf40a6b05f2e33c4140446757c45b6d218e81a75096591f046a81978b`.
- **Analyzable AnsibleGuard repositories:** 206 of 207. Of the 206, 198 have source occurrences and 8 have zero source occurrences; all 206 remain eligible for the repository split.
- **Internal static-source occurrences:** 265,434; **observed AnsibleGuard static rules:** 60.
- The rule allocation matrix reconciles exactly: 58 `static` + 2 `static-special` rules match the 60 source rules; 5 `review-history` rules remain a separate universe.

## Source identity and context audit

The detector's raw `occurrence_id` is not globally unique: 844 duplicate-ID groups account for 1,007 excess rows across repositories. The scoped source tuple `(repository, commit_sha, provider, source_occurrence_id)` is unique. The validation identity table therefore derives:

```text
SHA256("v007-human-static-source-v1|repository|commit_sha|provider|source_occurrence_id")
```

The raw value is retained as `source_occurrence_id`; the derived `occurrence_id` is the stable sampling key. `study/validation-v007-human/identities/static-source-candidates.csv.gz` contains 265,434 rows and 265,434 unique derived IDs; its SHA-256 is `2b70672c1f89039386f6cfb4bb73460059f05014a6b7248e4865f951150c7d6b`.

All 265,434 candidate rows match their exact per-repository occurrence snapshot. The source-context audit checked 25,690 unique `(repository, commit, path)` references by reading Git blobs at the frozen commit, not the current worktree: 25,690 verified, 0 missing, 0 reported lines beyond blob EOF, and 0 Git object read errors. The script/manifest are `scripts/v007_validation_source.py` and `identities/static-source-candidates.manifest.json`. `line_start`/`line_end` denote the detector-reported anchor line, not a claimed syntactic span.

## Known exclusions and separation

- Static AnsibleGuard precision uses only provider `ansibleguard` and `source_population=production_ansible` from the authoritative file.
- The timed-out repository has no AnsibleGuard core result and is reliability/missingness evidence, never a zero-finding row.
- The run-level validation report is marked `failed` because of that single timed-out repository; source-population integrity and the 206 completed core results are independently checked and pass.
- The 35 partial runs completed AnsibleGuard and GitLeaks; only optional `ansible-lint` was partial. Core findings remain eligible.
- The recorded causes are detailed in `FULL_RUN_PARTIALS.md`: six rejected `parseable` config properties, 25 repositories with nonzero `ansible-playbook --syntax-check` results, two unskippable `load-failure` config entries, one invalid test requirements file, and one ansible-lint run that ended before valid JSON without a captured root cause.
- Eight analyzable repositories with zero source occurrences stay in the repository population and must not be treated as missing scans.
- `ansible-lint`, GitLeaks, and 497 review/history occurrences are excluded from static-source precision. Review/history remains a separate five-rule panel. External-tool overlap is not estimated because the equivalence mapping is unvalidated.

## Reporting defects: fixed or isolated

Fixed and regenerated from frozen raw snapshots without rerunning the 207 scans:

- Provider-prefixed attribution is used for native rules. The prior mixed-native-rule bug mislabeled 192 AnsibleGuard source rows as `ansible-lint/ignore-errors`; the corrected source has only `ansibleguard/*` IDs and reconciles to 60 rules.
- Failed core output remains missing rather than zero; the incomplete repository is visible in tables and charts.
- Internal density uses the AnsibleGuard production-source population; provider-completeness categories are exclusive; certainty and actionability are separate; unmodeled external overlap is blank/not-estimated.
- The tautological sanity assertion was replaced with substantive checks. Current run evidence reports all 20 sanity checks passed and all 45 deterministic artifacts identical.
- Generated docs/catalog checks pass on the current branch; they are not inputs to candidate selection.

Remaining issues are explicitly isolated from this AnsibleGuard source population:

- Environment metadata records Python 3.14.7 while the reproduction guide recommends Python 3.12; GitLeaks' exact version was not captured, and the recorded `ansible --version` probe failed. These must remain caveats in reproduction claims; they do not alter the already-frozen AnsibleGuard occurrence CSV.
- External-tool rule equivalence is still unvalidated, so external overlap is unavailable and cannot be interpreted as zero.
- 35 optional-provider partials and 1 core timeout remain as recorded execution limitations.

## Checks and CI

- Local full suite on commit `34df886a`: 1,035 passed, 2 skipped.
- `.venv/bin/python scripts/generate_docs.py --check`: passed.
- Source-identity builder run twice with identical candidate-file SHA-256 and identical audit counts.
- Full run sanity report: passed (20/20). Determinism report: 45/45 identical.
- GitHub CI for `34df886a` passed on both remotes: fork run [37389882234](https://github.com/JedidiAymen/AnsibleChecklist/actions/runs/37389882234), Narjes run [37389881523](https://github.com/Narjes-b/AnsibleChecklist/actions/runs/37389881523). Python 3.10 and 3.12 tests, research environment build, generated-doc check, and package checks passed; the optional remote-equivalence job was skipped.

## Decision

This gate authorizes the deterministic 144/62 repository split and calibration-only agreement-pilot preparation from the identity table. It does **not** authorize opening held-out occurrence samples, threshold tuning on held-out repositories, or making accuracy claims. No human labels or human samples are present at this gate.
