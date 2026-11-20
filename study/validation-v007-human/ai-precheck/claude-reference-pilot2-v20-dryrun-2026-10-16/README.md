# Claude reference labels: pilot 2 under codebook v2.0 (a DRY RUN, not the final reference)

Seven blind agents (one per family) labelled the first build of pilot 2 (171 items, run v0071-full-2026) with codebook v2.0.
It is kept as evidence of what v2.0 got wrong; the sample and the codebook are being revised (v2.1) because of these findings,
so these labels will be superseded by a pass over the rebuilt pilot 2. NOT gold; never show to reviewers or use in estimates.

Result against the pilot gates: uncertain+unreviewable 11 % overall (pass; pilot 1 under v1 was 21 %), bundle issues 8 % overall
(fails the 5 % gate; pilot 1 was 21 %). Worst families: structure 29 % bundle issues, security 29 % uncertain+unreviewable and 12 % bundle issues.
See `claude-reference-pilot2-summary.md`, the agents' `observations/`, and `docs/study/v007-pilot2-dryrun-findings.md`.
The form file passes `scripts/v007_review_schema_v2.py` validation; `extra.csv` holds the agents' confidence.
