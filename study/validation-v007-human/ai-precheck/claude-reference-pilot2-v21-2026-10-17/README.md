# Claude reference labels: pilot 2 (rebuilt, 171 items) under codebook v2.1

AI reference labels for the rebuilt pilot 2 (`pilot2/`, run v0071-full-2026), written 2026-10-17 by one Claude pass (Sonnet 5.5) working
item by item from the frozen bundles in `pilot2/context/` and the frozen v2.1 family codebooks. **NOT gold.** Never show to the human reviewers,
never mix into the human agreement numbers or any estimate. The form passes `scripts/v007_review_schema_v2.py` validation (0 problems);
`claude-reference-pilot2-v21-extra.csv` holds the AI's own confidence; `labels-by-family/` holds the per-family source files.

## Limits to keep in mind
- **Not independent of the tooling.** The same assistant helped write the generator and the v2.1 definitions, so agreement with the rules is likely inflated
  compared with an outside reviewer. Treat this as a smoke test of the bundles and codebook, not as ground truth.
- **Not blind.** Two rows of the older dry-run labels (security 001 and 002 of the first build) were visible in the session before labelling; the older
  dry-run label files were not opened. Item ids were rebuilt, so the earlier labels do not map onto these items.
- **Windowed reading.** To fit output limits, long source files were read as the anchor +/- 35 lines (file-level findings: first 90 lines) plus all computed-facts and
  reference sections. Where a decision depended on text beyond that, the line was fetched directly. Items judged on a partial file say so in `evidence_notes`
  (for example structure 015 and 020, variable 015).
- **Programmatic checks used instead of eyeballing:** commit-message length, blank line and body line width for all commit-message-format items; name length and special-character
  counts for style items; line length for long-statement items.
- **Rules the family files do not define** (for example `missing-bool-filters`, `shell-environment-export`, `unscoped-shell-variable` details) were judged on the plain reading
  of the rule name; those items carry low confidence and, where relevant, `codebook-ambiguous`.

## Distribution (see `claude-reference-pilot2-v21-summary.md`)
171 items: 119 positive, 36 negative, 15 uncertain, 1 unreviewable. Uncertain+unreviewable 9 % (gate 25 %: pass). Bundle issues 11 % (gate 5 %: **fail**).

Bundle-issue sources, for the next generator pass:
- `redaction-hides` (security 006, 010, 012, 019, 022; all five in the security family): decisive values are redacted, so placeholder vs real secret cannot be separated.
- `anchor-mismatch` (security 001, 008, 014; maintainability 001; style 021): the header names a task or construct that is actually a play, a list item or a different file type.
- `missing-file` (objective 005, 012, 014, 019; security 021): redirected-module and external-role items need routing facts or the sibling role tree, which the bundle does not carry.
- `truncated` (structure 001): duplicated-code on a 1161-line file with no computed candidate blocks.
- `codebook-ambiguous` (structure 010 and 020, variable 001): close calls the family file does not settle.

## Items worth a human look first
Low confidence or codebook gaps: maintainability 007, 014, 020; objective 017, 021; security 006, 010, 012, 019; structure 010, 015, 020; variable 001, 006, 011, 014, 016.
