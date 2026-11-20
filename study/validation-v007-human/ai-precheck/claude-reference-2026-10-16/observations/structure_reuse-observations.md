# structure_reuse reference labelling: observations

Labels: negative 27, positive 16, uncertain 6 (012, 018, 030, 036, 042, 046), unreviewable 1 (049). Positives: 001, 004, 005, 010, 016, 019, 022, 023, 025, 028, 031, 032, 034, 035, 040, 048. bundle_issue != none: 5 rows (005, 007, 013, 046, 049).

## (a) Hardest five
- 033 (missing-abstraction, 276-line MacOSX.yml): heterogeneous concerns (homebrew, JCK, kernel tuning, core dumps) vs. cohesion, per-OS file convention, no repetition. Labelled negative, low.
- 005 (unnecessary-abstraction): anchor is line 1, no construct named. Only visible candidate is a keyword-less nested block (L148-162). Labelled positive, low.
- 023 / 035 (unnecessary-abstraction): one-task block carrying only when/vars; override says one-task block is not automatically harmful and the caller (main.yml) is not shown. Positive, low, not-actionable; a second reviewer could well say negative. I treated these differently from 017 (tag-carrying blocks in a consistent repo convention) and 029 (block/rescue).
- 012/018/030/036/042 (unstructured-module): see (c). Labelled uncertain.
- 019 and 025 (duplicated-code): real small within-file duplication (URL join twice; three identical stop blocks) but the detector's intended pair is unknown (possibly cross-file).

## (b) Bundle defects
- Listing truncated after 120 paths: 001, 002, 007, 008, 009, 011, 013, 014, 020, 026, 027, 032, 037, 038, 044, 046, 048, 049. It affected the decision in: 046 (xrt_caproto path never shown; README presence undecidable -> uncertain), 007 and 013 (sibling files needed to judge cross-file duplication not shown; decided on visible file only, low confidence), 049 (see below). Not decisive for the rest. For 011 the caller main.yml is not shown, but sibling roles show the convention.
- 049: the excerpt is only lines 1-36 of 654 ("larger than the inline-context limit; only the stated anchor window is included"). Labelled unreviewable. The codebook's own text points to uncertain/unreviewable but does not say which when 95% of the file is absent.
- Anchor line 1 for every row: no row identifies the flagged construct (block, play, duplicate pair, missing file). For duplicated-code rows the second copy / other file is never named. This is the main evidence-generation flaw for this family.
- Source-file redaction placeholders appear mid-YAML (030 L82-84, 032 L36/200/262, 034 L45/53, 042 L8-9, 045 L30); they do not affect structure decisions. 032 L262 and 034 L53 swallow the rest of the line/expression, so the file looks syntactically broken.
- 'Frozen tracked paths' for role-scoped rows (e.g. 035, 026, 038, 046) is sometimes a whole-repo prefix listing rather than the role directory, so truncation hits it; for role-readme-absent rows with a short role listing (004, 010, 016, 022, 028, 034, 040) the listing was complete and decisive.

## (c) Codebook / override ambiguities
- unstructured-module: no definition in the codebook or override. Five rows (006, 012, 018, 024, 030, 036, 042) are roles with no tasks/main.yml and named entry-point task files. If the rule means 'role lacks tasks/main.yml' the condition is literally present in all of them; if it means 'role layout is not valid' they are negative where a convention is visible (006 vendor roles, 024). Wording to fix: FAMILY_STRUCTURE.md 'the documented organization/placement/reuse condition is present' vs 'the referenced structure is valid'. Suggest: state the rule's predicate per rule, and say whether a role used via include_role tasks_from without main.yml counts as positive-with-not-actionable or negative.
- Same issue for the flagged file: 006/012/018/024/030/036/042 are anchored on defaults/main.yml or meta/main.yml, which exist and are fine; the rule name suggests the missing file is the subject, so the anchor misdirects.
- unnecessary-abstraction: override 'A one-task block is not automatically harmful; judge its interface/caller role' gives no test for a block that carries only when/vars/tags. Suggest: 'positive only if removing the wrapper changes nothing (no rescue/always, no shared keywords used by 2+ tasks, no convention of tag-blocks)'.
- missing-abstraction: override says size is not the criterion but gives no positive criterion. Suggest listing: repeated sequence (>=3 occurrences differing by parameters), or separable concern with its own variables.
- duplicated-code: 'semantically equivalent enough' is not quantified (e.g. 025 stop blocks vs parallel host-group setup; 043 primary/standby shared tasks, documented as intentional). Intentional-duplication threshold should be defined (comment documenting intent?).
- insufficient-modularization: no criterion; a playbook of roles (008, 014, 020, 026, 044) vs inline monolith (032). Suggest: positive when substantial inline logic (not role calls) dominates, or large repeated preambles.
- role-readme-absent: actionability for 7-line roles (010) vs real roles; the instructions give no proportionality rule. I used not-actionable for 010.
- 'external_context_type' has no controlled list in the instructions (only examples); I used 'role caller' and 'repository files'.

## (d) Detector patterns
- role-readme-absent: true positive whenever the role listing was complete (004, 010, 016, 022, 028, 034, 040); 046 undecidable due to truncation.
- unstructured-module on roles with no tasks/main.yml but named entry points: probable false positives in repos using tasks_from (006, 024 judged negative; 012, 018, 030, 036, 042 uncertain). Mechanism: file-existence check without caller analysis.
- insufficient-modularization / missing-abstraction: size-triggered; most flagged files (002, 003, 008, 009, 014, 015, 020, 021, 026, 027, 033, 039, 044, 050) are cohesive or already role-driven, so mostly false positives. True positives: 032 only (plus 049 unknown).
- unnecessary-abstraction: flagged legitimate dispatchers/extension points (011 validate_config, 041 service.yml, 047 loop include, 029 block/rescue, 017 tag blocks); possible weak positives 005, 023, 035.
- duplicated-code: true positives with exact repeats (001, 031, 048, weaker 019, 025); false positives where repetition is documented examples or intentional (038 is an insufficient-modularization row, 043 duplicated-code with documented intent, 037 only a copy-paste bug).

## (e) Sampling / evidence generation
- Order of rows suggests round-robin over 6 rules; every row anchored line 1 and 'source_location' only.
- 037 contains a real bug (node_exporter start task starts prometheus) irrelevant to the rule; 008 L180-187 'Install git' installs libicu/libselinux-python. Not rule-related.
- Several repos (006, 013, 038, 045) are families of near-identical sibling files; cross-file rules cannot be assessed from single-file bundles.
- 027 is a vendored third-party role (konstruktoid.hardening) inside packer/ansible/roles: findings in vendored code are of doubtful value; sampling frame may want to exclude vendored paths.
- A /tmp helper script was overwritten by another process during my run (a different family's output appeared); I re-read affected bundles directly. No labels used the wrong content.

## (f) Rule definition vs codebook
- I did not have the rule catalog definitions (not an allowed file), so I could not check agreement. The codebook's 'negative = rule's repository premise is false' implies the detector premise is something I can only infer from the rule name; this is itself a gap: reviewers are told not to use the rule name as evidence yet need it to know what to test.
