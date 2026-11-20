#!/usr/bin/env python3
"""Calibrate unguarded-variable occurrences using a per-repo symbol index.

For every unguarded-variable occurrence in labels.csv, this script:
  1. Extracts the variable name from the message field.
  2. Builds (or reuses a cached) symbol index for the cloned repository by
     scanning group_vars/, host_vars/, defaults/main.yml, vars/main.yml,
     register: assignments, and set_fact: blocks.
  3. Records whether the variable is defined anywhere in the repo.

Output: study/validation/unguarded_variable_annotations.csv

Reviewers can join this file to labels.csv on (project, occurrence_id)
to see `defined_in_repo` and `definition_files` before labeling.  A
variable that IS found in the repo is more likely to be a false positive
(the developer intended to pass it; `| default(...)` guard is missing but
the variable is declared).  A variable NOT found anywhere is ambiguous
(could be a runtime extra-var/secret, or genuinely undefined).

Usage
-----
    python scripts/calibrate_unguarded_variable.py \\
        study/validation/labels.csv \\
        --repos-root study/repositories \\
        --output study/validation/unguarded_variable_annotations.csv
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


_VAR_PATTERN = re.compile(r"Variable '([^']+)' is referenced")

# YAML files that commonly declare variables at the top level.
_DEFINITION_GLOBS = (
    "group_vars/**/*.yml",
    "group_vars/**/*.yaml",
    "host_vars/**/*.yml",
    "host_vars/**/*.yaml",
    "**/defaults/main.yml",
    "**/defaults/main.yaml",
    "**/vars/main.yml",
    "**/vars/main.yaml",
    "vars/*.yml",
    "vars/*.yaml",
)


def _extract_var_name(message: str) -> str | None:
    m = _VAR_PATTERN.search(message)
    return m.group(1) if m else None


def _top_level_keys_yaml(path: Path) -> set[str]:
    """Return top-level mapping keys from a YAML file."""
    if not _HAS_YAML:
        return set()
    try:
        data = _yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))
        if isinstance(data, dict):
            return set(data.keys())
    except Exception:
        pass
    return set()


def _register_names(path: Path) -> set[str]:
    """Scan a YAML file for `register: varname` patterns via regex (no full parse needed)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"\bregister:\s+([A-Za-z_][A-Za-z0-9_]*)", text))


def _set_fact_names(path: Path) -> set[str]:
    """Scan for set_fact keys via regex."""
    text = path.read_text(encoding="utf-8", errors="replace")
    # set_fact: {key: value}  or  set_fact:\n  key: value
    return set(re.findall(r"set_fact:\s*\{?\s*([A-Za-z_][A-Za-z0-9_]*)\s*:", text))


def build_symbol_index(repo_root: Path) -> dict[str, list[str]]:
    """Return {var_name: [relative_file_paths_where_defined]}."""
    index: dict[str, list[str]] = {}

    def _add(var: str, rel_path: str) -> None:
        index.setdefault(var, []).append(rel_path)

    # Definition files (group_vars, host_vars, defaults, vars)
    for glob in _DEFINITION_GLOBS:
        for path in repo_root.glob(glob):
            if not path.is_file():
                continue
            rel = str(path.relative_to(repo_root))
            for key in _top_level_keys_yaml(path):
                _add(key, rel)

    # register: and set_fact: across all yaml/yml files
    for path in repo_root.rglob("*.yml"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(repo_root))
        for name in _register_names(path):
            _add(name, rel)
        for name in _set_fact_names(path):
            _add(name, rel)
    for path in repo_root.rglob("*.yaml"):
        if not path.is_file():
            continue
        rel = str(path.relative_to(repo_root))
        for name in _register_names(path):
            _add(name, rel)
        for name in _set_fact_names(path):
            _add(name, rel)

    return index


def annotate(
    labels_path: Path,
    repos_root: Path,
    output_path: Path,
) -> None:
    rows = list(csv.DictReader(labels_path.open(newline="", encoding="utf-8")))
    uv_rows = [r for r in rows if r.get("concept_id") == "unguarded-variable"]

    if not uv_rows:
        print("No unguarded-variable rows found.")
        return

    # Build one symbol index per (project, commit_sha) pair.
    projects_seen: dict[str, dict[str, list[str]]] = {}
    results = []

    for row in uv_rows:
        project = row["project"]           # e.g. "AAROC/DevOps"
        occurrence_id = row["occurrence_id"]
        message = row["message"]
        var_name = _extract_var_name(message) or ""

        if project not in projects_seen:
            owner, _, repo_name = project.partition("/")
            repo_root = repos_root / owner / repo_name
            if repo_root.is_dir():
                idx = build_symbol_index(repo_root)
            else:
                idx = {}
            projects_seen[project] = idx

        idx = projects_seen[project]
        definition_files = idx.get(var_name, []) if var_name else []
        defined = bool(definition_files)

        results.append({
            "project": project,
            "occurrence_id": occurrence_id,
            "path": row["path"],
            "line": row["line"],
            "var_name": var_name,
            "defined_in_repo": "true" if defined else "false",
            "definition_count": len(definition_files),
            "definition_files": "|".join(definition_files[:5]),  # cap for readability
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "project", "occurrence_id", "path", "line",
            "var_name", "defined_in_repo", "definition_count", "definition_files",
        ])
        writer.writeheader()
        writer.writerows(results)

    defined_count = sum(1 for r in results if r["defined_in_repo"] == "true")
    print(
        f"Annotated {len(results)} unguarded-variable occurrences: "
        f"{defined_count} ({defined_count/len(results)*100:.1f}%) have a definition in the repo, "
        f"{len(results)-defined_count} ({(len(results)-defined_count)/len(results)*100:.1f}%) do not."
    )
    print(f"Wrote {output_path}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Calibrate unguarded-variable occurrences via repo symbol index."
    )
    parser.add_argument("labels_csv", type=Path)
    parser.add_argument(
        "--repos-root", type=Path,
        default=Path("study/repositories"),
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("study/validation/unguarded_variable_annotations.csv"),
    )
    args = parser.parse_args(argv)
    annotate(args.labels_csv, args.repos_root, args.output)


if __name__ == "__main__":
    main()
