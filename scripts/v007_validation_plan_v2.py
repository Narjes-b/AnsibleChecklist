#!/usr/bin/env python3
"""Importance-weighted human-labelling allocation (validation plan v2).

Reads ``rule-verification-plan.csv`` (v1 modes) and writes the v2 allocation:

- Mode A (deterministic): the population is verified by an oracle or an independent
  re-implementation; humans audit at most ``A_AUDIT`` edge cases per rule.
- Mode B (threshold): ``B_BAND`` banded items per rule (was 30).
- Mode C (semantic): census when N <= 30; otherwise 30 / 40 by size as in v1, plus
  ``HIGH_CONSEQUENCE_BONUS`` for rules in consequence tier 1 with N >= 100, capped at 50.
- Consequence tiers: 1 = security, reliability, correctness; 2 = compatibility,
  dependencies; 3 = everything else.
- Overheads: ``DUPLICATE_SHARE`` of the main items are re-inserted for the
  intra-rater consistency check; ``ADJUDICATION_SHARE`` of the main items are adjudicated.

Hours use the minutes per item of ``docs/study/v007-validation-protocol.md`` section 8.
Nothing here is an estimate of precision; it only allocates effort.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

A_AUDIT, B_BAND, HIGH_CONSEQUENCE_BONUS, C_CAP = 8, 20, 10, 50
DUPLICATE_SHARE, ADJUDICATION_SHARE = 0.08, 0.20
MINUTES = {"A-deterministic": 2, "B-threshold": 5, "C-semantic": 4}
TIER = {"security": 1, "reliability": 1, "correctness": 1, "compatibility": 2, "dependencies": 2}


def tier(category: str) -> int:
    return TIER.get(category, 3)


def items_for(mode: str, heldout: int, category: str) -> int:
    if heldout == 0:
        return 0
    if mode == "A-deterministic":
        return min(heldout, A_AUDIT)
    if mode == "B-threshold":
        return min(heldout, B_BAND)
    if heldout <= 30:
        return heldout
    base = 40 if heldout >= 500 else 30
    if tier(category) == 1 and heldout >= 100:
        base = min(C_CAP, base + HIGH_CONSEQUENCE_BONUS)
    return base


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with open(args.plan, newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    out = []
    for row in rows:
        held = int(row["heldout_required"])
        items = items_for(row["verification_mode"], held, row["category"])
        out.append({
            "rule_id": row["rule_id"], "category": row["category"], "consequence_tier": tier(row["category"]),
            "verification_mode": row["verification_mode"], "heldout_required": held,
            "items_v1": int(row["human_items_this_design"]), "items_v2": items,
            "reportable": "yes" if items >= 20 or (held and items == held) else "descriptive-only",
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(out[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)
    total_v1, total_v2 = sum(r["items_v1"] for r in out), sum(r["items_v2"] for r in out)
    hours = 0.0
    for mode, minutes in MINUTES.items():
        n = sum(r["items_v2"] for r in out if r["verification_mode"] == mode)
        hours += n * minutes * 2 / 60
        print(f"{mode}: {n} items")
    duplicates = round(total_v2 * DUPLICATE_SHARE)
    adjudicated = round(total_v2 * ADJUDICATION_SHARE)
    hours += duplicates * 4 * 1 / 60 + adjudicated * 5 / 60
    print(f"items v1 {total_v1} -> v2 {total_v2}; duplicates {duplicates}; adjudicated {adjudicated}")
    print(f"main-label hours (2 raters + duplicates + adjudication, excluding pilots/recall/secondary): {hours:.0f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
