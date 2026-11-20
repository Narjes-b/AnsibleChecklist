# Pilot 2 (codebook v2.1, run v0071-full-2026)

171 items from CALIBRATION repositories, REQUIRED occurrences only, built by `scripts/v007_build_pilot2.py`
(seed `v007-pilot2-20261016`; see `pilot2-manifest.json`). Per family: 24-25 (target 25; four items were dropped after selection
because their frozen commit is not in the local clone cache). 55 rules are covered.

- No pilot-1 item (matched by repository, rule, path, line); vendored third-party content, non-Ansible YAML (Kubernetes manifests, JSON6902 patches, other tools' files), bot-authored and merge commits (by git parents or `Merge ...` subject) excluded;
  at most 2 items per repository per family; one item per (repository, rule, directory); up to 3 reserved slots per family for
  rare rules (population < 5) so the codebook is exercised on them.
- All 171 bundles pass `v007_bundle_validate_v2.py` (0 problems, secret scan 0 findings).
- Blank v2 forms: `reviewer-a/pilot2.csv`, `reviewer-b/pilot2.csv` (identical, schema `v007_review_schema_v2`).
- Evaluate returned forms with `scripts/v007_agreement_v2.py` (gates: decided κ ≥ 0.70, uncertain ≤ 25 %, bundle issues ≤ 5 %).

Earlier builds were replaced before distribution. The sampler excludes merge commits by subject because shallow clones can obscure their parent count.

Exclusion counts of this build: merge commit 42, non-Ansible YAML 340, pilot-1 item 275, sibling of an earlier candidate 40160, vendored third-party content 2192.

Known composition limits: review/history draws mostly from `commit-message-format` because the other review rules have few
eligible calibration items with a recoverable first parent; the vendored-content filter is a path heuristic (`vendor/`, `roles/<ns>.<name>/`).
Review using only the assigned packet. Use the v1 reviewer instructions together with
`codebooks-v2/` (COMMON_V2 wins on conflicts).
