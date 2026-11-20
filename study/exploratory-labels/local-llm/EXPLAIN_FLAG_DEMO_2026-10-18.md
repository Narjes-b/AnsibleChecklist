# `--explain`: wired into every output format, for both `diff` and plain scans

Built on `fix/local-llm-explainer-bugs-2026-10-18`'s two bug fixes. Adds an
opt-in `--explain` flag to `ansibleguard diff` that calls a local Ollama model
once per **introduced, actionable** occurrence and attaches `llm_*` fields to
it. Because the enrichment happens once, upstream, on
`comparison["introduced"]` in `diff_workflow.py::compare_outputs`, every
downstream writer that already knew how to carry fields through
(`occurrences.py`, `csv_writer.py`, `sarif_writer.py`, `pr_annotations.py`)
picks it up automatically — no per-format duplication.

## What's new

- `src/ansibleguard/report/llm_explain.py` — the enrichment itself. Reads the
  *actual scanned file* for context (±6 lines around the flagged line) rather
  than relying on a CSV column, so it doesn't have Bug 1 from
  `KNOWN_ISSUES_2026-10-18.md`. Uses the schema-constrained Ollama `format`
  from that same fix, so it doesn't have Bug 2 either. Never raises: a
  missing/slow Ollama degrades to no enrichment for that item, not a failed
  scan.
- `ansibleguard diff --explain [--explain-model] [--explain-host] [--explain-max-items]`
  — off by default. Deliberately **not** wired into `.github/workflows/ansibleguard.yml`
  — per the earlier false-positive-accuracy findings, this isn't ready to run
  unattended on every real PR yet.
- Every `llm_*` field always travels with `llm_disclaimer` — "AI-generated,
  unverified second opinion... known to confidently misjudge false positives
  that require cross-file context" — in SARIF `properties`, the CSV columns,
  and the PR annotation/job-summary text alike. The goal is that no renderer
  can show the suggested fix without the caveat attached.
- Deliberately did **not** populate SARIF's native `fix.artifactChanges`.
  SARIF requires that field to point at an exact, trustworthy replacement
  range; given this model's measured blind spot, that would overstate how
  much a viewer should trust it. The explanation and suggested fix live in
  `properties` as descriptive text instead.

## Demo: real PR fixture, full diff workflow, real model calls

Reused the exact same fixture as PR #1 on `JedidiAymen/AnsibleChecklist`
("test: validate AnsibleGuard GitHub PR reporting") — `myfork/version-0.0.2`
as base, `myfork/pr-validation-introduced-findings` as head:

```
ansibleguard diff . --base myfork/version-0.0.2 --head myfork/pr-validation-introduced-findings \
  --profile pr --policy ratchet --allow-incompatible-snapshots \
  --explain --explain-max-items 5 \
  -o <output>
```

(`--allow-incompatible-snapshots` was needed only because this sandbox's local
ansible-lint/gitleaks setup doesn't exactly match CI's — unrelated to
`--explain`.) Result: same 3 actionable introduced findings as the real CI
run (`insecure-permissions`, `missing-validate-certs`,
`shell-module-migration`), ratchet correctly failed (exit 1), and all 3 came
back from Ollama with `llm_status: ok`. Example
(`diff/introduced-actionable.sarif`, `properties`):

```json
{
  "llm_status": "ok",
  "llm_explanation": "World-writable permissions grant write access to other users.",
  "llm_suggested_fix": "Set a more restrictive file mode that limits access to only the owner and possibly a specific group. For example, '0644' for read-only by owner and group, or '0600' for read-write by owner only.",
  "llm_confidence": "high",
  "llm_disclaimer": "AI-generated, unverified second opinion from a single file's context. Known to confidently misjudge false positives that require cross-file context -- treat as a starting point, not a verdict."
}
```

The diff workflow only wrote JSON + SARIF + a Markdown summary before this
change; it now also writes `introduced.csv`/`introduced-actionable.csv` and
`introduced.txt`/`introduced-actionable.txt` (`diff_report.py`, reusing the
same `csv_writer`/`text_writer` the full-scan `output_contract.py` pipeline
already used), so every output format the tool produces anywhere now carries
these fields when `--explain` is on: SARIF `properties`, CSV columns, plain
text (`Fix:` + `AI suggestion (unverified):` lines), the raw JSON (automatic,
since enrichment happens once on `comparison["introduced"]` before anything
is written), the diff's own `summary.md` job-summary table
(`diff_report.py::_finding_table`), and the GitHub `::warning`/`::error`
annotation commands + job-summary Markdown table rendered by
`pr_annotations.py` (a separate, PR-comment-oriented renderer from
`summary.md`). Confirmed present in all of the above on this same run, e.g.:

```
::error file=github-pr-demo/roles/controlled_demo/tasks/main.yml,line=4,title=AnsibleGuard [security]: insecure-permissions::World-writable permissions grant write access to other users. AI suggestion (unverified): Set a more restrictive file mode... Why: Setting world-writable permissions on a configuration file can lead to security vulnerabilities... (AI-generated, unverified second opinion from a single file's context. Known to confidently misjudge false positives that require cross-file context -- treat as a starting point, not a verdict.)
```

## What this demo does NOT show

It does not demonstrate the false-positive case improving — this fixture's 3
findings are all real, intended defects (by the PR's own design), so there
was no false positive here to catch or miss. The 0/5 false-positive
blind spot measured in `KNOWN_ISSUES_2026-10-18.md` is unrelated to this
wiring and still applies to whatever `--explain` is pointed at; this change
makes the (unreliable) opinion reach every output format, it does not make
the opinion more reliable.

## Also wired into plain (non-diff) scans

`ansibleguard <target> --explain [--explain-max-items N]` enriches every
actionable canonical occurrence the same way (threaded through
`analyze_path` → `_write_rollups` → `output_contract.write_rollups_v3`,
enriching `occurrences` once right after `build_occurrences(...)`, before any
writer runs). Confirmed on a real run against the same `github-pr-demo`
fixture scanned directly (not as a diff): `canonical/occurrences.csv`,
`canonical/occurrences.txt`, `canonical/findings.sarif`, and the root-level
compatibility aliases (`findings.sarif`, etc.) all carry `llm_status`/
`llm_suggested_fix`/`llm_disclaimer` for `insecure-permissions`,
`missing-validate-certs`, `non-idempotent-command`, and
`shell-module-migration`. `OCCURRENCE_FIELDS` (`output_contract.py`) and
`write_occurrences_text` got the same `llm_*` column/line additions as the
diff pipeline's finding-based writers.

Note the scale difference versus diff mode: a plain scan has no
"introduced" filter, so `--explain` there calls the model once per
*actionable* occurrence found anywhere in the target, not just new ones. A
large repo scan (we measured ~1000+ findings on a full technical-full run
elsewhere in this project) could mean hundreds of model calls at ~10-60s
each — use `--explain-max-items` to bound that, there is no other cap by
default.

## Deliberately not done here

- Not wired into the live GitHub Actions workflow (`.github/workflows/ansibleguard.yml`).
  Runners there have no GPU, there's no model persisted between runs, and —
  more importantly — this would mean posting unverified, confidently-wrong
  "fixes" onto real PRs before the false-positive problem is addressed.
- Not applied to the `fixed` occurrence list, or to a full (non-diff) scan —
  scoped to introduced/actionable occurrences only, per the earlier
  cost/latency discussion (far fewer calls than scanning everything).
