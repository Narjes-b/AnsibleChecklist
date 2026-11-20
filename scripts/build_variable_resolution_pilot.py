"""Build the frozen cohort whose repositories contain role argument specs."""

from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.manifest.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = reader.fieldnames or []
        rows = list(reader)
    if not rows or "project" not in fieldnames or "repository_path" not in fieldnames:
        raise SystemExit("manifest must contain project and repository_path columns")

    selected = []
    for row in rows:
        repository = Path(row["repository_path"]).resolve()
        if not repository.is_dir():
            raise SystemExit(f"missing repository: {row['project']}: {repository}")
        specs = tuple(repository.glob("**/meta/argument_specs.y*ml"))
        if specs:
            selected.append(row)

    if not selected:
        raise SystemExit("no repositories with role argument specifications found")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(selected)
    os.replace(temporary, args.output)
    print(f"wrote {len(selected)} repositories to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
