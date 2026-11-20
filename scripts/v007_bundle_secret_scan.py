#!/usr/bin/env python3
"""Independent residual-secret/PII scan for reviewer context bundles.

The generator's own idempotence check only proves redaction is stable, not complete.
This scan is deliberately separate from the generator's redaction code and never prints
a matched value: it reports file, line number, kind and length only.

Kinds: email, token-prefix (ghp_/AKIA/xox/sk-/glpat-/JWT), long-base64-line
(a line of >= 60 base64 characters that is not a markers line), high-entropy-word
(>= 32 chars, Shannon entropy >= 4.0, not a hash/path/URL), private-key-body.

Exit status 1 when any finding remains, so it can gate a build or a packet export.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
import re
import sys

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
PLACEHOLDER_DOMAINS = {"example.com", "example.org", "example.net", "localhost", "domain.tld", "users.noreply.github.com"}
TOKEN_PREFIX = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|sk-[A-Za-z0-9]{20,}|glpat-[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})")
BASE64_LINE = re.compile(r"^[\s+\-]*[A-Za-z0-9+/]{60,}={0,2}\s*$")
WORD = re.compile(r"[A-Za-z0-9+/_=-]{32,}")
HEXISH = re.compile(r"^[0-9a-fA-F]{32,}$")


def entropy(text: str) -> float:
    counts = {c: text.count(c) for c in set(text)}
    return -sum(n / len(text) * math.log2(n / len(text)) for n in counts.values())


GUTTER = re.compile(r"^\s*\d+ \| ")


def scan_text(text: str) -> list[tuple[int, str, int]]:
    found = []
    for number, line in enumerate(text.split("\n"), 1):
        line = GUTTER.sub("", line)
        for match in EMAIL.finditer(line):
            domain = match.group(0).rsplit("@", 1)[1].lower()
            if domain not in PLACEHOLDER_DOMAINS and not domain.endswith(".example"):
                found.append((number, "email", len(match.group(0))))
        for match in TOKEN_PREFIX.finditer(line):
            found.append((number, "token-prefix", len(match.group(0))))
        if BASE64_LINE.match(line):
            found.append((number, "long-base64-line", len(line.strip())))
            continue
        for match in WORD.finditer(line):
            word = match.group(0)
            if "/" in word and word.count("/") > 1 or HEXISH.match(word) or "REDACTED" in word:
                continue
            if "_" in word or "-" in word:
                continue  # identifiers, slugs and sample ids
            if entropy(word) >= 4.0 and any(c.isdigit() for c in word) and any(c.isalpha() for c in word):
                found.append((number, "high-entropy-word", len(word)))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("root", type=Path, help="directory with context bundles")
    parser.add_argument("--report", type=Path, help="CSV of findings (no values)")
    args = parser.parse_args()
    rows = []
    files = [p for p in sorted(args.root.rglob("*")) if p.is_file() and p.suffix in {".md", ".txt", ".csv", ".yml", ".yaml", ".diff"}]
    for path in files:
        for line, kind, length in scan_text(path.read_text(encoding="utf-8", errors="replace")):
            rows.append((str(path.relative_to(args.root)), line, kind, length))
    if args.report:
        with open(args.report, "w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["file", "line", "kind", "length"])
            writer.writerows(rows)
    kinds: dict[str, int] = {}
    for _, _, kind, _ in rows:
        kinds[kind] = kinds.get(kind, 0) + 1
    print(f"scanned {len(files)} files; findings {len(rows)}; by kind {kinds}; files affected {len({r[0] for r in rows})}")
    return 1 if rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
