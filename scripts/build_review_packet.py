#!/usr/bin/env python3
"""Create reviewer-ready packets from a reproducible stratified sample."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from ansibleguard.report.findings import RULE_CATALOG


def _read_rows(path: Path) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _source_path(source_root: Path, row: dict) -> Path:
    project = str(row.get("project") or "")
    path = str(row.get("path") or "")
    project_path = source_root / project / path
    return project_path if project and project_path.is_file() else source_root / path


def _context(path: Path, line: int, radius: int) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return ""
    start = max(0, line - radius - 1)
    end = min(len(lines), line + radius)
    return "\n".join(
        f"{index + 1}: {value}" for index, value in enumerate(lines[start:end], start)
    )


def build_review_packet(rows: list[dict], source_root: Path, radius: int = 3) -> list[dict]:
    packet = []
    for row in rows:
        output = dict(row)
        rule = RULE_CATALOG.get(row.get("rule_id"), {})
        line = int(row.get("line") or 1)
        source = _source_path(Path(source_root), row)
        output.update({
            "source_available": str(source.is_file()).lower(),
            "source_context": _context(source, line, radius),
            "rule_description": rule.get("description", ""),
            "rule_taxonomy": rule.get("taxonomy", ""),
            "rule_actionability": rule.get("actionability", ""),
            "rule_confidence": rule.get("confidence", ""),
        })
        packet.append(output)
    return packet


def write_packet(rows: list[dict], output: Path, metadata: Path | None = None) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    if metadata:
        Path(metadata).write_text(
            json.dumps({"rows": len(rows), "schema": "ansibleguard-review-packet-v1"}, indent=2) + "\n",
            encoding="utf-8",
        )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample", type=Path)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--context-lines", type=int, default=3)
    args = parser.parse_args(argv)
    rows = build_review_packet(_read_rows(args.sample), args.source_root, args.context_lines)
    write_packet(rows, args.output, args.metadata)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
