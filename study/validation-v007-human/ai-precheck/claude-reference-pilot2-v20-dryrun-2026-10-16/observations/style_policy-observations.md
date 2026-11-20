# style_policy observations (pilot2, 25 items)

Process
- check_labels.py fails on the supplied input: codebook_path is already "codebooks-v2/FAMILY_STYLE_POLICY_V2.md" and v2_family_file appends _V2 again (FileNotFoundError). I validated against a temp copy of the input with "_V2.md" rewritten to ".md"; result: 25/25 rows, 0 problems.
- Bundles still say "Codebook: codebooks/FAMILY_STYLE_POLICY.md" (v1), while the input list points to the v2 file.

Codebook ambiguities
- missing-file-extension (025) has no operational definition in FAMILY_STYLE_POLICY_V2. The file has a .yml extension; the only extension-less path is a runtime include_vars file. Labelled uncertain/policy-unknown with bundle_issue=codebook-ambiguous. duplicate-task-names also has no definition (scope: same file? same block? mutually exclusive when branches, 019?).
- inconsistent-naming-convention (002, 008, 014, 020): the rule's "special character" definition is not in the codebook. Counts are borderline for 014 (4 backticks + 3 underscores): positive only if backticks count. 008 follows a deliberate "module <|> description" project convention yet exceeds the threshold.
- long-statement URL exemption (015): is a postgres:// URI a "URL-bearing line"? Not defined. Also the effect of an author's inline "# yamllint disable rule:line-length" marker (003) on actionability is not covered.
- unnamed-task on import_tasks/include_tasks statements (012): predicate is literally true, but value of naming static imports is low; codebook gives no guidance.
- long-statement on non-task Ansible metadata (021 meta/runtime.yml in a collection): in scope or not is unspecified.
- Config overrides (ansible-lint/yamllint line length) are never visible in the bundles, so 160 default is assumed (003, 009, 015, 021).

Bundle defects and header problems
- "Flagged construct" text is wrong or misleading in many items: plays are described as "task at line N, unnamed" (005, 011, 017, 023); 021 says "task at line 55, unnamed" for a collection meta file; 018 says task named http-metrics-histograms-enabled for a Kustomize patch; 003/015 describe defaults variables as tasks.
- "Asserted subject: location" appears on file-level and play-level findings (001, 003, 005, 006, ...) where it is meaningless.
- Flagged construct names are truncated or case-normalised (004 truncated at 'item[', 016 and 022 lowercased) so the header cannot be used to measure length; only source text can.
- Duplicate-task-names items anchor on line 1 and name no task (001, 007, 013, 019), so the reviewer must find the duplicate pair; the bundle does not tell which names were duplicated.
- Windowed bundles (003, 010, 021) were sufficient, but 021 cut-off hides the rest of the file; fine for a physical-line predicate.

Detector false-positive patterns
- Non-Ansible YAML: Kustomize JSON6902 patches ('- op: add') flagged as unnamed tasks (018, 024).
- Duplicate task names in mutually exclusive branches (019) or on deliberately repeated tasks (013) are technically positive but low value.
- Long lines deliberately accepted: STIG verbatim names (010), deprecation warning_text (021), explicit yamllint-disable (003).

Redaction
- 003 redacts values in a way that changes lines 493-497 and 553; irrelevant to the predicate. No residual secrets noticed.
