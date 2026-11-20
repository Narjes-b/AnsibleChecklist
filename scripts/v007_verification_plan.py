#!/usr/bin/env python3
"""Per-rule verification mode and human-labelling allocation for the v0.0.7 study.

Every rule is assigned ONE verification mode (a proposal that must be confirmed
by reading the detector before the analysis plan is pre-registered):

A  deterministic predicate -> verify the whole population with an independent
   re-implementation or an external oracle; humans only audit a small sample of
   edge cases (is the predicate applied to the right object?).
B  metric/threshold rule  -> the question is whether the threshold is
   meaningful, not whether the metric is computed correctly; validated by the
   threshold-calibration panels (banded by metric value), not by precision
   sampling.
C  semantic judgement      -> the full human design (stratified two-stage
   sample per rule, census for rare rules).

Allocation (heldout required occurrences N):
A: min(N, 10) audit items; B: min(N, 30) banded items (or all if N <= 30);
C: all items if N <= 30, otherwise 30 (mid, N < 500) or 40 (large, N >= 500).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

A, B, C = "A-deterministic", "B-threshold", "C-semantic"

MODES: dict[str, tuple[str, str]] = {
    # rule -> (mode, oracle / how the population is verified)
    "loop-legacy-syntax": (A, "independent scan for with_* keys; ansible-core accepts with_* so the claim is deprecation policy"),
    "redirected-module": (A, "ansible-core runtime.yml / ansible-doc plugin routing for the resolved collection"),
    "deprecated-modules": (A, "ansible-core runtime.yml deprecation metadata"),
    "invalid-task-attribute-type": (A, "ansible-core task attribute definitions (Task.fattributes isa)"),
    "invalid-numeric-value": (A, "ansible-core argument spec / port range"),
    "overriden-keys": (A, "YAML parser duplicate-key detection (ruamel/PyYAML strict)"),
    "unnamed-task": (A, "parser: task has no name key"),
    "unnamed-play": (A, "parser: play has no name key"),
    "duplicate-task-names": (A, "parser: equal names within one play"),
    "missing-file-extension": (A, "parser: included file reference without extension"),
    "missing-bool-filters": (A, "parser: quoted 'true'/'false' in when"),
    "unexpected-task-location": (A, "role layout check: tasks/ file that is a mapping"),
    "unstructured-module": (A, "role layout check: no tasks/main.{yml,yaml}"),
    "empty-abstraction": (A, "role/include layout check"),
    "unpinned-ansible-dependency": (A, "requirements/meta parser: dependency without version"),
    "incomplete-task": (A, "regex over task names/comments (independent regex)"),
    "unnecessary-abstraction": (A, "parser: block with exactly one task"),
    "redundant-default-value": (A, "compare set value with role defaults (independent resolver)"),
    "role-variable-precedence-collision": (A, "same key in defaults/ and vars/ of one role"),
    "unsafe-file-write": (A, "parser: unsafe_writes true"),
    "missing-validate-certs": (A, "parser: validate_certs false (module honours the option per ansible-doc)"),
    "missing-handler": (A, "independent handler resolution incl. imports, listen, role handlers"),
    "unused-handler": (A, "independent notify resolution incl. includes and roles"),
    "shell-environment-export": (A, "parser: export in shell task"),
    "broken-role-dependency": (A, "role dependency graph self-reference / cycle"),
    "role-readme-absent": (A, "file existence"),
    "galaxy-meta-incomplete": (A, "meta/main.yml required keys"),
    "vault-inline-overload": (A, "count of inline vault blocks"),
    "missing-tags": (A, "parser: no tags on task or inherited"),
    "variable-naming-convention": (A, "regex over variable names / role prefix"),
    "molecule-test-absent": (A, "file existence"),
    "large-task": (B, "threshold LOC_task = 15"),
    "large-play": (B, "thresholds LOC_play 50 / num_tasks_play 7 / avg_task_play 15"),
    "large-playbook": (B, "thresholds LOC_playbook 110 / num_plays 4 / avg_play_size 50"),
    "complex-playbook": (B, "complexity budget over playbook thresholds"),
    "complex-expression": (B, "thresholds complex_expression_length 100 / score 6"),
    "excessive-nesting": (B, "threshold excessive_nesting_depth 3"),
    "high-coupling": (B, "thresholds Num_Imports 4 / Num_Roles 5"),
    "missing-abstraction": (B, "threshold missing_abstraction_tasks 10"),
    "insufficient-modularization": (B, "size thresholds across plays"),
    "duplicated-code": (B, "similarity thresholds 0.4 / 0.5"),
    "undocumented-complex-task": (B, "undocumented_complex_* thresholds plus comment presence"),
    "long-statement": (B, "threshold long_statement_length 160"),
    "long-task-name": (B, "threshold task_name_len 75"),
    "inconsistent-naming-convention": (B, "threshold special_chars 3 over task/play names"),
    "become-scope-too-broad": (B, "threshold MIN_TASKS_FOR_BROAD_BECOME = 5"),
    "unguarded-variable": (C, "variable resolution; uncertainty by design (role inputs, includes)"),
    "variable-use-before-definition": (C, "task-order reasoning over includes"),
    "overriding-facts": (C, "set_fact reassignment intent"),
    "unused-registered-variable": (C, "use across files, includes, roles"),
    "unnecessary-set-fact": (C, "bounded execution graph reasoning"),
    "unscoped-shell-variable": (C, "shell semantics versus task environment"),
    "non-idempotent-command": (C, "command semantics (guards, check mode)"),
    "read-only-command-change": (C, "command semantics (read-only query)"),
    "shell-instead-of-module": (C, "module availability and equivalence"),
    "silent-error-suppression": (C, "whether failure is handled elsewhere"),
    "credentials-leaking-in-log": (C, "module argument_spec no_log as partial oracle; dynamic no_log expressions need humans"),
    "plaintext-sensitive-variable": (C, "secret versus path/placeholder judgement"),
    "default-credentials": (C, "well-known default versus documented example"),
    "insecure-permissions": (C, "mode predicate plus what path/key the mode protects"),
}


def allocation(mode: str, heldout_required: int) -> tuple[int, str]:
    if heldout_required == 0:
        return 0, "no heldout required occurrences"
    if mode == A:
        return min(heldout_required, 10), "audit of edge cases; whole population verified automatically"
    if mode == B:
        return min(heldout_required, 30), "banded by metric value for the threshold panel"
    if heldout_required <= 30:
        return heldout_required, "census"
    return (40 if heldout_required >= 500 else 30), "stratified two-stage sample"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rule-profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with open(args.rule_profile, newline="", encoding="utf-8") as stream:
        profile = {row["rule_id"].split("/")[-1]: row for row in csv.DictReader(stream)}
    missing = sorted(set(profile) - set(MODES))
    unknown = sorted(set(MODES) - set(profile))
    if missing or unknown:
        raise SystemExit(f"mode table out of sync with run: unassigned={missing} not-in-run={unknown}")
    rows = []
    for name, row in sorted(profile.items(), key=lambda kv: (MODES[kv[0]][0], kv[1]["category"], kv[0])):
        mode, oracle = MODES[name]
        held = int(row["heldout_required_occurrences"])
        uniform = 0 if held == 0 else (held if held <= 30 else (40 if held >= 500 else 30))
        items, how = allocation(mode, held)
        rows.append({
            "rule_id": row["rule_id"], "category": row["category"], "family": row["family"],
            "required_occurrences": row["required_occurrences"], "optional_occurrences": row["optional_occurrences"],
            "heldout_required": held, "heldout_required_repositories": row["heldout_required_repositories"],
            "catalog_status": row["catalog_status"], "verification_mode": mode, "oracle_or_basis": oracle,
            "human_items_this_design": items, "human_items_uniform_design": uniform, "allocation_note": how,
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    for mode in (A, B, C):
        sel = [r for r in rows if r["verification_mode"] == mode]
        print(mode, "rules", len(sel), "required occurrences", sum(int(r["required_occurrences"]) for r in sel),
              "human items", sum(r["human_items_this_design"] for r in sel),
              "(uniform design", sum(r["human_items_uniform_design"] for r in sel), ")")
    print("total human items", sum(r["human_items_this_design"] for r in rows),
          "uniform", sum(r["human_items_uniform_design"] for r in rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
