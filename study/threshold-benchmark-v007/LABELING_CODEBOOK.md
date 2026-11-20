# Large-task manual-labeling codebook

## Review question

Should this executable Ansible task be considered excessively large and in need of decomposition?

Label the underlying condition, not whether AnsibleGuard's current threshold fired.

## Labels

- `positive`: the task combines separable responsibilities, contains a long procedural sequence inside one module invocation, or is difficult to understand/test safely as one task and should be decomposed or moved into a clearer abstraction.
- `negative`: the task is cohesive and its apparent size is mainly declarative data required by one operation; decomposition would reduce readability or would not create a meaningful reusable unit.
- `uncertain`: repository/runtime context is genuinely necessary, the source excerpt is incomplete, or the case remains evenly balanced after reading the whole task and nearby tasks.

## Decision rules

1. Inspect the entire task, including `when`, `loop`, `vars`, `environment`, `args`, and nested values.
2. Do not label a task positive merely because its serialized line count exceeds a candidate threshold.
3. Large inline templates, command scripts, firewall rule lists, and API payloads are not automatically positives. Ask whether an Ansible-native abstraction would make the task safer or clearer.
4. A block wrapper is not itself an executable task. Review leaf tasks, matching the detector's corrected traversal.
5. Formatting, comments, or YAML wrapping alone do not establish a smell.
6. Record a concrete reason. Avoid reasons that only restate the numerical value.
7. If the supplied excerpt contains no executable Ansible task at all in scope — e.g. the file is pure
   dispatch (only `include_tasks`/`import_playbook`/`import_tasks` selecting other files, with no leaf
   task body present), or the excerpt is cut off before the flagged task's own definition becomes
   visible — label `uncertain`, not `negative`. A missing task is not evidence the task is fine; it is
   evidence the reviewer cannot judge it. Do not label `negative` an excerpt you cannot evaluate.
8. Distinguish "one coherent outcome" from "several separable responsibilities" using the *number of
   distinct downstream effects*, not the number of shell/Jinja steps:
   - `negative`: every step in the task feeds a single derived value or a single resource mutation for
     one operation (e.g., two chained regex substitutions that together compute one identifier used once;
     an existence check that only guards one fallback action for one target). The task has one job; it
     just takes a few expressions to do it.
   - `positive`: the task performs multiple *independent* actions that each map to their own natural
     Ansible module or task (e.g., activating a virtualenv, then upgrading packaging tools, then
     installing requirements — three steps each with a dedicated idiomatic module — collapsed into one
     `shell`/`command` string), or interleaves unrelated concerns (provisioning a user account and
     configuring SSH access and editing sudoers in one `raw`/`shell` block). If you can name more than
     one plausible separate task/module this would naturally become without losing behavior, it is
     positive. Exception: a `raw` task chaining multiple commands specifically because no interpreter or
     module runtime is available yet on the target (e.g. bootstrapping Python before any other Ansible
     module can run) is not positive merely for containing multiple commands — no native-module
     alternative actually works at that point, so there is nothing to separate it *into*.
9. A fully-visible `import_role`/`include_role`/`import_tasks`/`include_tasks` call is itself a complete,
   judgeable task even though the referenced file's internals are not shown — that is normal delegation,
   not truncation. Judge the call as it stands (is invoking one role/task-list for one purpose
   excessive?), rather than labeling it `uncertain` under rule 7. Rule 7 applies only when the flagged
   line itself has no complete task definition in view (the file is dispatch-only with the flagged unit
   nowhere in the excerpt, or the excerpt is cut off mid-definition before the flagged task's own keys
   appear).

## Agreement procedure

Two reviewers label a pilot independently and cannot see each other's or the AI's answers. Run `scripts/compare_threshold_reviewers.py`. If Cohen's kappa is below 0.80, discuss only the disagreements, revise this codebook, and label a new pilot. Once the target is reached, freeze the codebook before primary labeling and retain every original label plus adjudication.

### Revision history

- **v2** (added rules 7–8): pilot round 1 (75 rows, seed `v007-threshold-benchmark-20260917`) scored
  Cohen's kappa 0.637 (raw agreement 88%, Gwet's AC1 0.857) — below the 0.80 target. All 9 disagreements
  fell into two patterns: (a) 3 cases where one reviewer read an orchestration-only or truncated excerpt
  as `uncertain` and the other as `negative` — rule 7 added; (b) 6 cases where reviewers disagreed on
  whether a multi-step shell/set_fact task with one overall outcome was cohesive (`negative`) or
  separable (`positive`) — rule 8 added to make the distinguishing test explicit.
- **v3** (added rule 9, refined rule 8): pilot round 2 (same 75 rows, fresh raters) scored kappa 0.635 —
  essentially unchanged despite raw agreement rising to 92%. Root cause found: the review packet omitted
  the flagged task's `line` number, so raters were guessing which task in the file was under review
  rather than disagreeing about the codebook. Round 3, with `line` included, scored kappa 0.754 (raw
  agreement 96%, 3 disagreements) — confirming most of the earlier disagreement was a packet-construction
  bug, not a codebook gap. The 3 residual round-3 disagreements were: (a) 2 cases where a fully-visible
  `import_role`/`include_role` call was read as `uncertain` (no body shown for the referenced role) by
  one rater and `negative` (a small, cohesive delegation) by the other — rule 9 added; (b) 1 case where a
  `raw` Python-bootstrap task chaining `apt update`/install commands was read as `positive` (multiple
  installs) by one rater and `negative` (no module alternative exists before Python is installed) by the
  other — rule 8's exception clause added.
