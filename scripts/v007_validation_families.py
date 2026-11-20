#!/usr/bin/env python3
"""Create the auditable V007 rule-to-human-validation-family mapping.

This stage classifies rule definitions only. It does not read finding rows,
select samples, inspect labels, or open heldout occurrence context.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


EXPECTED_MATRIX_SHA256 = "657759e3d5cf76e79ce3dacc9afcd7f2b0986fa5d86a43a8c7787d1ee1596c2f"
EXPECTED_CATALOG_SHA256 = "62b43e177be28773b8e926c06345fe00bacdf37e0fa4d069a5d2d77ec485c93e"


FAMILIES = {
    "objective_correctness": "Objective correctness",
    "variable_reference_reasoning": "Variable/reference reasoning",
    "security": "Security",
    "style_policy": "Style/policy",
    "maintainability_complexity": "Maintainability/complexity",
    "structure_reuse": "Structure/reuse",
    "review_history": "Review/history",
}


# These are intentional semantic overrides to catalog taxonomy/category.
# Reasons are preserved in the generated mapping so reviewers can audit them.
RULE_OVERRIDES = {
    "unguarded-variable": (
        "variable_reference_reasoning",
        "The finding is about whether a variable is defined, guarded, or supplied by a runtime input contract; uncertainty is central to this family.",
    ),
    "role-readme-absent": (
        "structure_reuse",
        "The supplied plan explicitly places absent role documentation in the structure/reuse review family; absence alone is not a correctness defect.",
    ),
    "unnecessary-set-fact": (
        "variable_reference_reasoning",
        "Judge whether the set_fact value is genuinely unused across visible references; do not treat the optional rule taxonomy as proof of a defect.",
    ),
    "missing-abstraction": (
        "structure_reuse",
        "The question is whether task organization should be factored into reusable roles/includes, not whether a numeric size cutoff is exceeded.",
    ),
    "unused-registered-variable": (
        "variable_reference_reasoning",
        "The semantic decision is whether a registered result is referenced in the available scope; dynamic/runtime references may require uncertainty.",
    ),
    "unnecessary-abstraction": (
        "structure_reuse",
        "A one-task block is a structure/reuse judgment; its presence does not by itself establish a harmful abstraction.",
    ),
    "duplicated-code": (
        "structure_reuse",
        "Review whether the flagged task blocks are semantically duplicated and whether reuse is appropriate; textual similarity alone is insufficient.",
    ),
    "deprecated-modules": (
        "maintainability_complexity",
        "The catalog defines this as a maintenance signal; review the actual deprecation status and migration context, not just the rule name.",
    ),
    "variable-use-before-definition": (
        "variable_reference_reasoning",
        "Requires ordering and scope reasoning about the registered result/fact; external or dynamic definitions must be considered.",
    ),
    "unscoped-shell-variable": (
        "variable_reference_reasoning",
        "Requires checking shell-variable expansion against Ansible environment mapping and execution scope.",
    ),
    "insufficient-modularization": (
        "structure_reuse",
        "The decision concerns play/task decomposition and reuse, even though the catalog currently labels it a maintainability signal.",
    ),
    "role-variable-precedence-collision": (
        "variable_reference_reasoning",
        "Requires Ansible precedence and effective-value reasoning across role defaults and vars.",
    ),
    "overriding-facts": (
        "variable_reference_reasoning",
        "Requires comparing set_fact assignments and whether the later value changes the effective variable; context can make apparent overrides intentional.",
    ),
    "redundant-default-value": (
        "variable_reference_reasoning",
        "Requires comparing an assignment to the role default and the effective variable contract; equality alone may be intentional documentation.",
    ),
    "missing-bool-filters": (
        "variable_reference_reasoning",
        "The predicate is a variable/value-type interpretation in a when condition; judge expression semantics and available type context.",
    ),
    "unsafe-file-write": (
        "security",
        "The supplied plan explicitly lists unsafe file writes as a security review case; judge actual write risk and relevant safeguards.",
    ),
    "shell-environment-export": (
        "variable_reference_reasoning",
        "The issue is whether a shell export is being used where Ansible's task environment mapping controls variable propagation.",
    ),
    "loop-legacy-syntax": (
        "objective_correctness",
        "This is a compatibility/deprecation predicate; determine whether the syntax is actually legacy for the supported Ansible context.",
    ),
    "redirected-module": (
        "objective_correctness",
        "This is a module-identity/compatibility condition; verify the redirect and target FQCN in the frozen source context.",
    ),
    "non-idempotent-command": (
        "objective_correctness",
        "Judge whether the mutating command can repeat harmful changes without a valid idempotency guard; command presence alone is insufficient.",
    ),
    "read-only-command-change": (
        "objective_correctness",
        "Judge whether the command is read-only and whether Ansible would falsely report a change in this actual task context.",
    ),
    "unpinned-ansible-dependency": (
        "objective_correctness",
        "Judge whether the dependency is genuinely unconstrained in the declared installation source; reproducibility impact and actionability are separate labels.",
    ),
    "molecule-test-absent": (
        "style_policy",
        "This is an optional testing-practice predicate; role testability and repository policy value must be judged separately from file absence.",
    ),
    "galaxy-meta-incomplete": (
        "style_policy",
        "This is an optional publication-metadata policy; judge whether Galaxy publication is in scope before judging actionability.",
    ),
    "vault-inline-overload": (
        "security",
        "The detector concerns inline encrypted-secret handling; assess exposure/operational risk while keeping the organization-specific threshold distinct.",
    ),
}


OUTPUT_COLUMNS = [
    "rule_id",
    "panel",
    "family_id",
    "family_name",
    "catalog_category",
    "catalog_taxonomy",
    "catalog_status",
    "concept_id",
    "family_assignment_basis",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _assign_family(
    rule_key: str, panel: str, catalog_rule: dict[str, Any]
) -> tuple[str, str]:
    if panel == "review-history":
        return (
            "review_history",
            "Review/history rules require commit-message and/or Git-range evidence and remain a separate panel from static source findings.",
        )
    if rule_key in RULE_OVERRIDES:
        return RULE_OVERRIDES[rule_key]

    taxonomy = catalog_rule.get("taxonomy")
    category = catalog_rule.get("category")
    if category == "structure":
        return (
            "structure_reuse",
            "Catalog category is structure; evaluate organization, placement, or reuse in repository context.",
        )
    if taxonomy == "RISK":
        return (
            "security",
            "Catalog taxonomy is RISK; determine whether the described security exposure is actually present, separately from actionability.",
        )
    if taxonomy in {"STYLE_POLICY", "OPTIONAL_PRACTICE"}:
        return (
            "style_policy",
            "Catalog taxonomy is style/policy or optional practice; distinguish predicate truth from usefulness/actionability in this repository.",
        )
    if taxonomy == "MAINTAINABILITY_SIGNAL":
        return (
            "maintainability_complexity",
            "Catalog taxonomy is MAINTAINABILITY_SIGNAL; judge a genuine maintainability condition independently of its detector cutoff.",
        )
    if taxonomy == "DEFECT":
        return (
            "objective_correctness",
            "Catalog taxonomy is DEFECT; judge the documented correctness, reliability, dependency, or compatibility condition in frozen source context.",
        )
    raise ValueError(
        f"no family rule for {rule_key!r}: panel={panel!r}, category={category!r}, taxonomy={taxonomy!r}"
    )


def build_family_mapping(root: Path, output_dir: Path) -> dict[str, Any]:
    mapping_dir = output_dir / "mappings"
    matrix_path = mapping_dir / "source-rule-allocation-matrix.csv"
    catalog_path = root / "rule-catalog.json"
    if not matrix_path.is_file():
        raise FileNotFoundError(f"copy the supplied allocation matrix to {matrix_path}")

    input_hashes = {
        "allocation_matrix": (matrix_path, EXPECTED_MATRIX_SHA256),
        "rule_catalog": (catalog_path, EXPECTED_CATALOG_SHA256),
    }
    for label, (path, expected) in input_hashes.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(
                f"{label} SHA-256 changed: expected {expected}, found {actual}; stop and review inputs"
            )

    matrix_rows = _read_csv(matrix_path)
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog_rules = catalog.get("rules", {})
    if len(matrix_rows) != 65:
        raise RuntimeError(f"expected 65 allocation-matrix rules, found {len(matrix_rows)}")

    output_rows: list[dict[str, str]] = []
    seen: set[str] = set()
    panel_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    for row in matrix_rows:
        rule_id = row["rule_id"]
        rule_key = rule_id.removeprefix("ansibleguard/")
        if rule_id in seen:
            raise RuntimeError(f"duplicate rule in allocation matrix: {rule_id}")
        seen.add(rule_id)
        if not rule_id.startswith("ansibleguard/"):
            raise RuntimeError(f"unexpected provider namespace in rule ID: {rule_id}")
        metadata = catalog_rules.get(rule_key)
        if metadata is None:
            raise RuntimeError(f"allocation rule is absent from rule catalog: {rule_id}")
        family_id, basis = _assign_family(rule_key, row["panel"], metadata)
        family_counts[family_id] += 1
        panel_counts[row["panel"]] += 1
        output_rows.append(
            {
                "rule_id": rule_id,
                "panel": row["panel"],
                "family_id": family_id,
                "family_name": FAMILIES[family_id],
                "catalog_category": str(metadata.get("category", "")),
                "catalog_taxonomy": str(metadata.get("taxonomy", "")),
                "catalog_status": str(metadata.get("status", "")),
                "concept_id": str(metadata.get("concept_id", "")),
                "family_assignment_basis": basis,
            }
        )

    expected_panels = Counter({"static": 58, "static-special": 2, "review-history": 5})
    if panel_counts != expected_panels:
        raise RuntimeError(f"unexpected allocation panels: {dict(panel_counts)}")
    if set(family_counts) != set(FAMILIES):
        raise RuntimeError(f"mapping did not cover all required families: {dict(family_counts)}")

    mapping_dir.mkdir(parents=True, exist_ok=True)
    mapping_path = mapping_dir / "rule-family-map.csv"
    with mapping_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)

    manifest = {
        "format_version": 1,
        "source_matrix": {
            "path": "mappings/source-rule-allocation-matrix.csv",
            "sha256": EXPECTED_MATRIX_SHA256,
            "rows": len(matrix_rows),
        },
        "rule_catalog": {
            "path": "../../rule-catalog.json",
            "sha256": EXPECTED_CATALOG_SHA256,
        },
        "mapping": {
            "path": "mappings/rule-family-map.csv",
            "sha256": sha256_file(mapping_path),
            "rows": len(output_rows),
            "panel_counts": dict(sorted(panel_counts.items())),
            "family_counts": dict(sorted(family_counts.items())),
            "family_rule_ids": {
                family_id: [row["rule_id"] for row in output_rows if row["family_id"] == family_id]
                for family_id in sorted(FAMILIES)
            },
        },
        "exceptions": {
            rule_id: {"family_id": family_id, "rationale": rationale}
            for rule_id, (family_id, rationale) in sorted(RULE_OVERRIDES.items())
            if f"ansibleguard/{rule_id}" in seen
        },
        "scope_note": "Rule-definition mapping only; no finding occurrence rows, reviewer samples, human labels, or heldout contexts are read or written.",
    }
    (mapping_dir / "rule-family-map.manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--output-dir", type=Path, default=Path("study/validation-v007-human")
    )
    args = parser.parse_args()
    manifest = build_family_mapping(args.root, args.output_dir)
    print(json.dumps(manifest["mapping"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
