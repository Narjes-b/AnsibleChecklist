# structure_reuse observations (24 items)

Labels: positive 11, negative 12, unreviewable 1, uncertain 0.

## Process problems
- check_labels.py fails on the supplied input: codebook_path is already `codebooks-v2/FAMILY_STRUCTURE_V2.md`, but v2_family_file() appends `_V2` again (FileNotFoundError `FAMILY_STRUCTURE_V2_V2.md`). I ran the checker on a temp copy of the input with the v1 path (`codebooks/FAMILY_STRUCTURE.md`); result 0 problems. Bundle headers also still say `Codebook: codebooks/FAMILY_STRUCTURE.md` (v1).
- Bundle path is pilot2/context/..., reviewer instruction text mentions samples/agreement-pilot/context; harmless.

## Codebook gaps
- insufficient-modularization (002, 006, 011, 016, 021) and unexpected-task-location (024) have no operational definition in FAMILY_STRUCTURE_V2. I judged 002/006/011/021 negative because plays use roles/import/include mechanisms, 016 negative as an examples playbook, 024 positive (variable data under tasks/defaults/). All low confidence, bundle_issue=codebook-ambiguous. Rule predicate should be added or these rules dropped from the family.
- duplicated-code: no threshold for "parametric" duplication. 015 (three identical-logic STIG blocks differing by id/mount/message) labelled positive, advisory; 010 (two similar stop blocks with different conditions) labelled negative. A reviewer could reasonably flip either.
- missing-abstraction counts: whether rescue/always children count as leaf tasks is unstated (007 is >10 either way). 017, 022, 012 are barely above (11), so the leaf-count convention decides them.
- unstructured-module anchored on a non-tasks file (009 defaults/main.yml, 014 handlers/main.yml, 019 beaker_deps.yml): predicate is role-level and holds by definition, but these roles look deliberately tasks_from-only; "positive by definition" yields low-value findings.

## Bundle defects
- Every item is anchored at line 1 and the header says "names no single task" even for rules where the construct matters: 004 (unnecessary-abstraction, decisive block is L34-39) and duplicated-code items 001/005/010/015/020 (no duplicated pair named). Per the family file this would be unreviewable; I only used unreviewable for 001 because the file is also truncated (101 of 1161 lines). For the others the full file was visible so I judged the rule on the whole file.
- 001: ±100 line window of a 1161-line file; duplication cannot be judged.
- Large-repo scopes (002, 006, 011, 021, 023) print a truncated listing; not decisive for these rules.
- 009/014: listings are complete and presence check line makes the unstructured-module decision easy (good).

## Detector false-positive patterns
- unnecessary-abstraction: 008, 013, 023 are negative because block-level `when`/`tags` (013 L21-22, 023 L150) justify a single-task block; the nested-block case (008) wraps a 2-task nested block. Only 004 is a true one-task unjustified block.
- duplicated-code appears to fire on whole files with no real equivalent blocks (005, 020, 010).
- insufficient-modularization fires on role-based or import-based playbooks (006, 011).
- missing-abstraction is correct per predicate but of low value for 11-task, already-split role files (007, 012, 017, 022).
