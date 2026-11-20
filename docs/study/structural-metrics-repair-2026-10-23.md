# Structural task metrics — 2026-10-23

Current definition: **`declared-leaf-tasks-v3`**, recorded as `reproducibility.structural_metrics_version` in new runs. V2 introduced the shared leaf traversal described below; V3 keeps that population and corrects name-presence/sentinel confusion. A base/head comparison rejects different versions, including a new version vs. absent legacy metadata, unless the existing explicit incompatibility override is used. Two entirely metadata-free legacy artifacts retain their pre-existing `legacy-unverified` comparison behavior.

## Name-presence repair after the construct audit

The [frozen lexical audit](../../study/evidence-constructs-2026-10-23/README.md) distinguishes generated placeholder subjects from actual source names. Reviewing its consumers exposed a concrete detector error: a task literally named `Unknown` was counted as unnamed, given name length zero, and excluded from duplicate-name detection.

- Added `task_has_name` in shared task semantics and `has_name` on measured task entries. Presence means the existing nonblank-string predicate; it does not depend on display wording.
- Missing/blank/non-string names still display `Unknown` for compatibility. A literal name `Unknown` is measured as a seven-character name, is not an unnamed task, and participates in duplicate-name checks within the existing play scope.
- V3 versions this metric/detector change separately from V2. Old frozen results, canonical identities, labels and construct diagnostics are retained. The construct diagnostic's dependency hashes identify the V2 code used to generate it.
- Four regressions cover both standalone/parsed-document loading and task-only/play shapes, with literal names alongside missing/null/blank/non-string names. They verify name presence, lengths, unnamed count and duplicate count together.
- A parser integration test still expected an outer wrapper in global task metrics; it now asserts the documented V2+ leaf population exactly, retaining its play-ID separation checks.
- **168 focused tests passed** across task/play/playbook metrics, naming consumers, parser integration, findings, runtime/profile provenance, diff and construct evidence. Full repository suite: **1,478 passed, 2 skipped** in 197.99 seconds. No population impact or accuracy rate is inferred from these fixtures.

## Problems fixed

1. Play task counting stopped after the first nested branch. A wrapper containing `block`, `rescue` and `always` counted only one branch, while task metrics counted all three.
2. Task metrics visited `tasks` but omitted `pre_tasks`, `post_tasks` and `handlers` in plays.
3. Task-only files passed `include_container=true`, counting outer block wrappers as tasks even though nested wrappers were skipped.
4. Raw summary counts included wrappers and therefore disagreed with task-level measurements. Changed-task counts could also include wrappers, omit the last line of flow-style mappings, or accidentally include indentation on the next task's line.

## Definition and implementation

[task_traversal.py](../../src/ansibleguard/task_traversal.py) supplies one traversal for Python mappings and YAML representation nodes. Task/play metrics and playbook summaries use the same leaf population.

- Visit `pre_tasks`, `tasks`, `post_tasks`, and `handlers`, and every nested `block`/`rescue`/`always` branch. Preserve the enclosing play ID; standalone task-file leaves retain `play_id=-1`.
- A block wrapper is a container, including an empty or malformed block section. Non-mapping entries and non-list branches do not become executable tasks. This traversal does not establish Ansible validity; parser/semantic diagnostics are separate.
- Count declarations, including conditional branches and handler declarations. These are **not executed task counts**. Imports/includes are counted as declarations, without expanding their targets or loop iterations. Handler invocation frequency is unknown.
- Repeated aliases at different declaration positions remain repeated declarations. A cycle in task containers fails explicitly. The walker uses an iterative stack and handles a 5,000-level synthetic structure without Python recursion.
- Retain the raw top-level return value from `calculate_metrics_task` for existing callers. Measured task entries now contain leaves only. The legacy field `num_global_tasks_playbook` retains its existing meaning of summed per-play task counts; this patch does not rename it.
- Direct changed-task counts use leaf spans. A wrapper-only edit is not a directly edited leaf; this count does not estimate all indirectly affected tasks. YAML compose shares nodes for aliases, so exact changed-line attribution for alias use sites remains a limitation.
- `LOC_task` and `LOC_play` remain normalized PyYAML serialization lengths. They are **not source LOC**; source-span measurement and human threshold validation still need a separately versioned decision. This patch does not silently redefine those cutoffs.

## Validation and research implications

The initial V2 traversal batch had **134 focused tests passed**: all structural detector suites, parse-once parity, runtime/profile provenance, findings, diff/source integration and shared traversal regressions. Tests verify equality across task/play/playbook/summary counts on all four play sections, all three nested branches and task-only files; source lines/play IDs; empty/malformed wrappers; aliases/cycles/deep nesting; changed-line boundaries; and incompatible-version rejection. V3's additional name-presence checks are recorded above.

The all-section regression fixture has eight declared leaves. Task, play, playbook and summary counts all equal eight in both parsed-document and standalone loading paths. No wrapper names enter task-name metrics. The task-only fixture has three leaves across all branches and an empty wrapper; the measured count is three, with the existing raw two-entry list still returned separately.

Affected outputs include task/play size and naming metrics, unnamed tasks, duplicate-name consumers, derived playbook averages/counts and report summaries. Historical frozen runs, sample selections, threshold pilot labels and manifests remain unchanged. Before publishing new frequencies or claiming a threshold improvement:

1. Rerun both sides with the new definition; do not compare new counts directly against old counts as tool improvement.
2. Audit impact by file shape, play section, rule, policy, certainty and repository group using exact frozen blobs. Retain failures and report this as a development diagnostic.
3. Revisit codebook unit definitions and run a fresh independent threshold agreement pilot. Existing three rounds reuse the same 75 IDs and do not become new independent evidence after a code change.
4. Keep source-unit boundaries, normalized-length predicates, semantic validity and usefulness judgments separate in sample packets.

See the [sampling methodology](sampling-methodology-2026-10-23.md) and [running repair log](recovery-progress.md).
