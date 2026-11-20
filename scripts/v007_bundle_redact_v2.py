#!/usr/bin/env python3
"""Second-pass redaction for reviewer context bundles (writes a new directory).

Complements the frozen generator redaction without modifying it. Applies, line by line
(ignoring a leading ``  123 | `` line-number gutter):

- non-placeholder email addresses -> ``[REDACTED_EMAIL]``;
- vendor token prefixes (ghp_, AKIA, xox, sk-, glpat-, JWT) -> ``[REDACTED_TOKEN]``;
- lines of >= 60 base64 characters -> ``[REDACTED_BASE64_BLOCK]``;
- high-entropy words (same rule as the scanner) -> ``[REDACTED_TOKEN]``.

Input files are never changed; refuses to write into a non-empty directory. Run
``v007_bundle_secret_scan.py`` on the output; it must report 0 findings.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_bundle_secret_scan import (  # noqa: E402
    BASE64_LINE, EMAIL, GUTTER, HEXISH, PLACEHOLDER_DOMAINS, TOKEN_PREFIX, WORD, entropy,
)


def _email(match: re.Match) -> str:
    domain = match.group(0).rsplit("@", 1)[1].lower()
    if domain in PLACEHOLDER_DOMAINS or domain.endswith(".example"):
        return match.group(0)
    return "[REDACTED_EMAIL]"


def _word(match: re.Match) -> str:
    word = match.group(0)
    if ("/" in word and word.count("/") > 1) or HEXISH.match(word) or "REDACTED" in word or "_" in word or "-" in word:
        return word
    if entropy(word) >= 4.0 and any(c.isdigit() for c in word) and any(c.isalpha() for c in word):
        return "[REDACTED_TOKEN]"
    return word


def redact_line(line: str) -> str:
    gutter = GUTTER.match(line)
    prefix = gutter.group(0) if gutter else ""
    body = line[len(prefix):]
    if BASE64_LINE.match(body):
        indent = re.match(r"^[\s+\-]*", body).group(0)
        return prefix + indent + "[REDACTED_BASE64_BLOCK]"
    body = EMAIL.sub(_email, body)
    body = TOKEN_PREFIX.sub("[REDACTED_TOKEN]", body)
    body = WORD.sub(_word, body)
    return prefix + body


def redact_text(text: str) -> str:
    return "\n".join(redact_line(line) for line in text.split("\n"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(f"refusing to write into non-empty {args.output}")
    changed = total = 0
    for path in sorted(p for p in args.source.rglob("*") if p.is_file()):
        target = args.output / path.relative_to(args.source)
        target.parent.mkdir(parents=True, exist_ok=True)
        text = path.read_text(encoding="utf-8", errors="replace")
        new = redact_text(text)
        target.write_text(new, encoding="utf-8")
        total += 1
        changed += new != text
    print(f"files {total}; changed {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
