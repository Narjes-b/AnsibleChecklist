"""Summarize the two recorded timing datasets used by the paper. Read-only."""
from pathlib import Path
import csv
import json
from collections import Counter
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
SCAN = "study/analysis-v0071-rerun-2026-10-22/run/tables/runtimes.csv"
PR = "study/pr-replay-v007-2026-10-15/prs.csv"

def summarize(root=ROOT):
    with (root / SCAN).open(newline="") as stream:
        scans = list(csv.DictReader(stream))
    with (root / PR).open(newline="") as stream:
        comparisons = list(csv.DictReader(stream))
    return {
        "sources": {"scan": SCAN, "pr": PR},
        "scan_attempts": len(scans),
        "scan_statuses": dict(sorted(Counter(row["overall_status"] for row in scans).items())),
        "scan_median_seconds": median(float(row["duration_seconds"]) for row in scans),
        "pr_comparisons": len(comparisons),
        "pr_median_seconds": median(float(row["pr_seconds"]) for row in comparisons),
        "pr_maximum_seconds": max(float(row["pr_seconds"]) for row in comparisons),
        "interpretation": "Observed separate runs; not controlled comparative speed measurements. Scan median includes partial and failed attempts.",
    }

if __name__ == "__main__":
    print(json.dumps(summarize(), indent=2))
