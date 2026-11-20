# Observations: maintainability_complexity (50 rows, AI reference reviewer)

## (a) Counts and hardest items
Semantic: positive 21, negative 25, uncertain 4, unreviewable 0. Actionability: not-applicable 25, advisory 16, actionable 5, uncertain 4. ai_confidence: high 19, medium 23, low 8.
By rule (positive/negative/uncertain): complex-expression 2/3/0; complex-playbook 0/5/0; deprecated-modules 5/0/0; excessive-nesting 2/0/0; high-coupling 2/3/0; incomplete-task 2/2/0; large-play 0/4/0; large-playbook 1/3/0; large-task 0/4/0; shell-instead-of-module 4/0/0; undocumented-complex-task 3/1/0; unused-handler 0/0/4.

Hardest items:
1. 005/017/028/039/050 (high-coupling): the predicate has no definition. Is a 9-role play "coupled", or is composing roles the playbook's job? I labelled plain role lists (005, 017, 028) negative/low and playbooks reaching into another role's internals via tasks_from or relative paths (039, 050) positive/low. Two careful reviewers could split every one of them.
2. 018 vs 029 vs 006/040 (incomplete-task): all four hinge on the substring "hack". 006 (font name "Hack") and 040 (URL path "hack/install_kustomize.sh") are clear false positives. 018 ("mariadb config hack") and 029 ("Hack - Use arm64 docker image") are self-declared workarounds, but the tasks are complete, so "incomplete" fits poorly. I labelled them positive/low and medium because the codebook calls markers a "stated concern".
3. 020 (large-playbook): the file is 4812 lines but the bundle shows lines 1-36. Size is known only from the header, and the content is uniform STIG blocks, so the maintenance burden is arguable. I labelled positive/medium, with bundle_issue=truncated-evidence.
4. 011 and 034 (undocumented-complex-task): a section comment sits nearby (011, line 463) or a file-level comment explains the logic (034, lines 6-7), but nothing is directly adjacent to the task. Whether that counts as "documented" is a judgement call.
5. 010 (shell-instead-of-module): `command: npm install ws` has a native equivalent (community.general.npm). It is a transient helper that is cleaned up afterwards, and the module needs an extra collection. I labelled positive/medium.

## (b) Bundle defects
- Only 3 of 50 bundles show a window: 009 (565-635 of 946), 011 (438-508 of 726), 020 (1-36 of 4812). Exactly 1 bundle (020) shows only lines 1-36 of a much larger file. In 009 and 011 the anchored task is complete, so I used bundle_issue=none. In 020 the size metric rests on the header only, so I used truncated-evidence. The other 47 bundles show the full file.
- Redaction artefacts that did not change any label, but mangle the source:
  - 014:124 and 023:143: the redaction swallows the rest of the line.
  - 021:96 and 118: line 118 is clipped to `changed_when: ... status =[REDACTED_LITERAL]`. A comparison operator and its value look like a secret.
  - 013:10, 035:19 and 179, 037:58, 042:113: literals are redacted.
  - 016:301-304 and 042:39-47: whole value blocks are replaced with "[REDACTED VALUE BLOCK]".
  Over-redaction hits non-secret values such as `true`, `==` and a sudoers hint line. 042 loses structure, but the file-size conclusion still holds.
- The mid-file header "Lines a-b of N" is reliable. The extra boilerplate sentence "If that prevents a defensible decision, use uncertain or unreviewable" appears only on windowed bundles.
- No bundle contains a reference search, tree or diff. Unused-handler (012, 024, 035, 046) and high-coupling need the role/import graph and none is supplied. All four handler rows are therefore uncertain by construction.
- 012 has no tasks section at all in the second play, which reads like a truncated play but is the real file (19 of 19 lines).
- 031 is a netbox resource data file and 026/037/042/048 are role task files, not playbooks.

## (c) Codebook and override ambiguities
- The codebook does not define any rule's predicate: no thresholds, no definition of "undocumented", "coupling", "incomplete", "large". Suggested fix: add one line per rule, e.g. "incomplete-task = TODO/FIXME/XXX/HACK marker or a clearly unfinished task body".
- Reason codes are missing for "native module equivalent exists" (shell-instead-of-module, 8 `other` uses) and for "marker present" (incomplete-task). I used `other` 8 times. Suggested: add `native-module-available` and `stated-concern-marker`.
- "Ignore the threshold itself when judging" conflicts with large-*/complex-* rules: with no independent notion of "large" the reviewer's judgement is the threshold. Suggested: give an anchoring rule of thumb (for example a play over about 150 lines, or a task over about 40 lines).
- The wording "unit is coherent/manageable in context" is subjective. For size rules, cohesive-and-short and cohesive-but-long are both negative candidates, and two reviewers will differ on 041, 008 and 020.
- Deprecation rules: "require the applicable Ansible/module context", but the bundles never state the target Ansible version, so every deprecated-modules row would be `uncertain` if read strictly. I treated the documented deprecation of bare `include:` as sufficient. State the rule explicitly.
- `uncertain` for handlers: does "uncertain" apply whenever a role is in the play, or only when a notify is plausible? Define it.
- The family question says "independent of detector cutoff" but the actionability labels (advisory vs actionable) have no rule for metric rules.
- RULE_OVERRIDES lists `deprecated-modules` as Maintainability/complexity "with version/deprecation test", while `missing-abstraction`, `duplicated-code`, etc. are moved to Structure/reuse. `high-coupling` and `large-*` stay here although they are really structure rules; that boundary is unclear.

## (d) Repeated detector patterns
- deprecated-modules (003, 015, 027, 038, 049): all five are the bare `include:` directive. True positives (deprecated since 2.4). In 015 `route53_facts` is also deprecated, but it is not the anchor.
- shell-instead-of-module (010, 022, 033, 044): all four are plain `command`/`shell` calls that map to a module: npm, chown -R, chmod -R, wget. True positives here. In no row was the command a real pipeline or something a module could not express.
- incomplete-task: keyword "hack" as substring: font name (006), URL path (040), task names (018, 029). Mechanism: case-insensitive substring match, no word boundary or context. 2 false positives, 2 marker hits.
- large-task (009, 021, 032, 043): all four anchor tasks are 11-24 lines; false positive by any reading. The measure may be per-file or per-parameter-key, or the anchor points at the wrong node. large-play (007, 019, 030) similarly flags plays of 80, 64 and 24 lines.
- complex-playbook (002, 014, 026, 037, 048): all negative. Several are role task files, not playbooks (026, 037, 048); the rule may be firing on file-level statistics (task counts, tags, when clauses).
- large-playbook: 031 is a data file and 042 is a 124-line role task file; 008 is long mostly because of vars. Only 020 (4812 lines) is genuinely large.
- complex-expression: 001 and 047 are plausible true positives; 013, 025 and 036 are one-to-two operand expressions. Mechanism may be raw character count or pipe count; 036 flags a short `a == b or c | default(false)`.
- excessive-nesting (004, 016): both true positives (4 and 5 levels of block).
- unused-handler (012, 024, 035, 046): all four play-level handlers in plays whose roles/imports are external; static analysis cannot see `notify` in roles. Likely false-positive producing for this pattern.
- high-coupling: mixed, see (a).

## (e) Sampling and evidence-generation concerns
- The sample appears to be stratified by rule (about 4-5 per rule, 12 rules) without regard to the detector's actual metric; 25 of 50 are negative, mostly because the cited unit is trivially small.
- The anchor line often does not identify the measured unit: line 1 or 2 for file-level metrics; line 6 in 001 and 197 in 036 for expressions, so the anchor is the line of the condition rather than the task.
- Anchors for large-playbook/complex-playbook are always line 1 of the file even when the file is a role task file or data file, indicating the wrong analysis unit.
- Because the bundle excludes anything outside the file, rules that need cross-file evidence (unused-handler, high-coupling) cannot be adjudicated with evidence-only bundles, so the family will have a structural "uncertain" floor.
- The `source_context` column duplicates the bundle for files under about 200 lines, but for 009/011/020 it should have been verified against the bundle windows (not checked beyond the headers).
- Heterogeneous repo ages (infrared 2016-18 era vs 2026 repos) make the deprecated-modules test version-dependent; sample IDs 003/015/027/038/049 are all old-style code.

## (f) Rule definition vs codebook
- I judged from the codebook only (rule catalog not allowed). Where the rule name implies a size/complexity threshold ("large", "complex", "excessive"), the codebook's instruction to ignore the threshold turns the rule into "is it big or hard to read", which conflicts with the rule name for rows like 019 (64 lines) and 030 (24 lines) that I labelled negative.
- Codebook says "A shell/command-to-module suggestion is not positive merely because a native module exists; compare semantics". I applied this and still found positives (022, 033, 044) where semantics clearly match; the gap is the missing reason code (see (c)).
- Codebook says "TODO/FIXME markers indicate a stated concern, not necessarily incomplete production behavior". That suggests positive for a marker present; but rule name "incomplete-task" suggests the task is unfinished. I followed the codebook for 018 and 029 (positive) and judged keyword-in-unrelated-context (006, 040) as negative.
