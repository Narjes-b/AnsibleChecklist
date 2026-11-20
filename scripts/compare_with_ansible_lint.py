#!/usr/bin/env python3
"""Compare AnsibleGuard rules with their closest ansible-lint counterparts.

For each related rule pair, counts occurrences found by
both tools, only by AnsibleGuard, and only by ansible-lint, on repositories
where every provider completed. Two findings are "both" when AnsibleGuard's
canonical model merged them into one occurrence (``native_rules`` lists both
rules) or when both tools report the same file and line in the same run and
repository revision. Each occurrence can match at most once per rule pair.
These are evidence-overlap counts, not precision or recall estimates.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

PAIRS = [
    ("non-idempotent-command", "no-changed-when"),
    ("shell-instead-of-module", "command-instead-of-module"),
    ("silent-error-suppression", "ignore-errors"),
    ("unnamed-task", "name[missing]"),
    ("unnamed-play", "name[play]"),
    ("long-statement", "yaml[line-length]"),
    ("deprecated-modules", "deprecated-module"),
    ("credentials-leaking-in-log", "no-log-password"),
    ("variable-naming-convention", "var-naming[pattern]"),
]

# Occurrence IDs are local to a repository snapshot. Shared files in different
# repositories can have the same ID, and an ID can recur in another run/ref.
OccurrenceKey = tuple[str, str, str, str]
Location = tuple[str, str, str, str, str]


def natives(row: dict) -> set[str]:
    value = row["native_rules"].strip()
    rules = set(json.loads(value)) if value.startswith("[") else ({value} if value else set())
    return rules | {row["rule_id"]}


def compare_rule_pair(
    ag_items: dict[OccurrenceKey, Location],
    al_items: dict[OccurrenceKey, Location],
) -> dict[str, int]:
    # Reserve canonical matches before location matching so a same-line
    # candidate cannot consume evidence already shared by the two tools.
    shared = ag_items.keys() & al_items.keys()
    al_locations: dict[Location, list[OccurrenceKey]] = defaultdict(list)
    for key in sorted(al_items.keys() - shared, reverse=True):
        al_locations[al_items[key]].append(key)

    both = len(shared)
    for key in sorted(ag_items.keys() - shared):
        candidates = al_locations.get(ag_items[key])
        if candidates:
            candidates.pop()
            both += 1

    return {
        "ansibleguard_total": len(ag_items),
        "ansible_lint_total": len(al_items),
        "both": both,
        "both_merged_by_ansibleguard": len(shared),
        "ansibleguard_only": len(ag_items) - both,
        "ansible_lint_only": len(al_items) - both,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aggregate", type=Path, required=True, help="run's aggregate/ directory")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    complete = set()
    with (args.aggregate / "repository-summary.csv").open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            if (row["scan_status"] in {"completed", "existing"} and row["ansible_lint_status"] == "completed"
                    and row["gitleaks_status"] == "completed"):
                complete.add(row["project"])

    wanted = {f"ansibleguard/{a}" for a, _ in PAIRS} | {f"ansible-lint/{b}" for _, b in PAIRS}
    # A canonical occurrence may appear in more than one export. Count its
    # native-rule evidence once, using the full snapshot identity.
    found: dict[str, dict[OccurrenceKey, Location]] = defaultdict(dict)
    locations: dict[OccurrenceKey, Location] = {}
    for name in ("all-internal-source-occurrences.csv", "all-ansible-lint-occurrences.csv"):
        with (args.aggregate / name).open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                if row["project"] not in complete:
                    continue
                rules = natives(row) & wanted
                if not rules:
                    continue
                snapshot = (row["run_id"], row["project"], row["commit_sha"])
                key = (*snapshot, row["occurrence_id"])
                location = (*snapshot, row["file"], row["line"])
                if key in locations and locations[key] != location:
                    raise ValueError(f"conflicting locations for occurrence {key!r}")
                locations[key] = location
                for rule in rules:
                    found[rule][key] = location

    rows = []
    for ag, al in PAIRS:
        ag_id, al_id = f"ansibleguard/{ag}", f"ansible-lint/{al}"
        rows.append({
            "ansibleguard_rule": ag, "ansible_lint_rule": al,
            **compare_rule_pair(found.get(ag_id, {}), found.get(al_id, {})),
        })
    with args.output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"repositories: {len(complete)}")
    for row in rows:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
