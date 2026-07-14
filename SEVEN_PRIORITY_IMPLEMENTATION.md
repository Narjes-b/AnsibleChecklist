# Seven-priority implementation record

This document records the seven follow-up items I implemented after reviewing
the detector and report pipeline.

## 1. Unified output coverage

I kept the existing raw per-file reports and added normalized project-wide
`findings.csv` and `findings.txt` alongside `findings.json` and SARIF. I also
append the normalized findings to each `Play_Level_Analysis.txt`. Git review
metrics now have their own `review_metrics.json`, so project-only rules are no
longer hidden inside a summary count.

All normalized formats use the same five fields: `file`, `line`, `rule_id`,
`severity`, and `message`.

## 2. Real source lines for five legacy detector groups

I replaced the five detectors' PyYAML-only load path with a shared ruamel
round-trip loader that preserves YAML coordinates. Missing tags, deprecated
modules, disabled certificate validation, shell/module alternatives, and both
handler checks now report their actual task, module, notify, or handler line.

## 3. Complete pull-request review range

The Git review checks now accept `ANSIBLEGUARD_BASE_SHA` and
`ANSIBLEGUARD_HEAD_SHA`. File changes use the complete `base...head` range,
commit-message rules inspect every commit in `base..head`, and copyright checks
compare committed base/head content instead of the working tree. GitHub Actions
fetches full history and supplies both PR SHAs. Local runs retain a safe
`HEAD^..HEAD` fallback.

## 4. End-to-end output contract tests

I added integration tests that execute the analyzer and assert that one known
rule has the same occurrence count in JSON, CSV, text, SARIF, and the per-file
text report. A second test guarantees that every normalized report exists even
for an empty scan. PR-range and exact legacy-line regressions are also covered.

## 5. Central detector configuration

`.ansibleguard.example.yml` documents the project configuration. The loader
searches from the analyzed file toward the repository root. It supports:

- overrides for both legacy `thresholds.csv` keys and the newer detector
  thresholds;
- project-specific default credential values;
- extra regular expressions for mutating commands;
- variables supplied outside visible YAML;
- stable rule IDs that should be suppressed.

Suppressions are applied after normalization, so every output format stays
consistent.

## 6. Corpus validation and false-positive tuning

I added `scripts/validate_detector_corpus.py`, ran it over all 56 bundled YAML
files, and recorded the results and two tuning corrections in
`CORPUS_VALIDATION.md`.

## 7. Reproducible local ansible-lint execution

The wrapper now resolves `ansible-lint` next to the active virtual-environment
Python executable before using `PATH`. It also supplies a writable
`ANSIBLE_LOCAL_TEMP`, avoiding failures when the user's normal Ansible cache is
read-only in a sandbox or CI worker.

I verified this from a newly created `/tmp/ansibleguard-clean-venv`: editable
installation completed, the CLI entry point displayed its help, and the wrapper
ran ansible-lint 26.6.0 against the issue fixture with status `completed` and
three structured findings.

## Completion boundary

I worked on all seven items and did not skip any implementation item. The only
result I cannot claim is a numerical precision/recall score: the corpus is not
labeled with ground truth. I documented that research limitation explicitly
rather than presenting candidate counts as accuracy statistics.
