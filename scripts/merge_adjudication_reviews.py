#!/usr/bin/env python3
"""
Merge adjudication reviews into study/validation-v6/sample.csv.

Reads all batch_NNN.json files from study/validation-v6/adjudication_reviews/,
matches each adjudicated item back to its sample.csv row by occurrence_id
(or project+path for clean-file-review items), and sets consensus_label /
consensus_reason on disagreement rows.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
from collections import Counter

SAMPLE   = Path("study/validation-v6/sample.csv")
ADJ_DIR  = Path("study/validation-v6/adjudication_reviews")


def load_adjudications() -> tuple[dict, dict, dict]:
    """Return (by_occ, by_idx, by_cfr).

    by_occ  — {full_occurrence_id: {label, reason}}
    by_idx  — {item_idx: {label, reason}}  (fallback for truncated occurrence_ids)
    by_cfr  — {(project, path): {label, reason}}
    """
    by_occ: dict[str, dict] = {}
    by_idx: dict[int, dict] = {}
    by_cfr: dict[tuple, dict] = {}

    batch_files = sorted(ADJ_DIR.glob("batch_*.json"))
    if not batch_files:
        sys.exit(f"No batch files found in {ADJ_DIR}")
    print(f"Loading {len(batch_files)} batch files...")

    # idx → full occurrence_id and (project, path) from the adjudication items file.
    items_path = SAMPLE.parent / "adjudication_items.json"
    idx_to_meta: dict[int, dict] = {}
    if items_path.exists():
        for item in json.loads(items_path.read_text()):
            idx_to_meta[item["idx"]] = item

    for bf in batch_files:
        try:
            reviews = json.loads(bf.read_text())
        except Exception as e:
            print(f"  WARNING: could not parse {bf.name}: {e}", file=sys.stderr)
            continue
        for r in reviews:
            idx  = r.get("idx")
            occ  = r.get("occurrence_id", "")
            lbl  = r.get("label", "uncertain")
            rsn  = r.get("reason", "")
            meta = idx_to_meta.get(idx, {})

            payload = {"label": lbl, "reason": rsn}

            # Primary: full occurrence_id from the review (may be truncated by the agent).
            if occ:
                by_occ[occ] = payload

            # Secondary: resolve the full occurrence_id from the items file using idx.
            if idx is not None:
                by_idx[idx] = payload
                full_occ = meta.get("occurrence_id", "")
                if full_occ and full_occ not in by_occ:
                    by_occ[full_occ] = payload

            # Clean-file-review: match by (project, path).
            if not meta.get("occurrence_id") and meta.get("project") and meta.get("path"):
                key = (meta["project"], meta["path"])
                by_cfr[key] = payload

    print(f"  {len(by_occ)} occurrence adjudications, {len(by_cfr)} clean-file-review adjudications")
    return by_occ, by_idx, by_cfr


def main():
    by_occ, by_idx, by_cfr = load_adjudications()

    # Build idx lookup from adjudication_items.json for fallback matching.
    items_path = SAMPLE.parent / "adjudication_items.json"
    occ_to_idx: dict[str, int] = {}
    if items_path.exists():
        for item in json.loads(items_path.read_text()):
            if item.get("occurrence_id"):
                occ_to_idx[item["occurrence_id"]] = item["idx"]

    rows = list(csv.DictReader(SAMPLE.open()))
    updated = 0
    skipped = 0

    for row in rows:
        if row.get("consensus_label") != "disagreement":
            continue

        adj = None
        occ = row.get("occurrence_id", "")

        # 1. Full occurrence_id match.
        if occ and occ in by_occ:
            adj = by_occ[occ]

        # 2. Idx-based fallback (handles truncated occurrence_ids written by agents).
        if adj is None and occ in occ_to_idx:
            idx = occ_to_idx[occ]
            if idx in by_idx:
                adj = by_idx[idx]

        # 3. Clean-file-review: match by (project, path).
        if adj is None:
            key = (row.get("project", ""), row.get("path", ""))
            if key in by_cfr:
                adj = by_cfr[key]

        if adj is None:
            skipped += 1
            continue

        row["consensus_label"]  = adj["label"]
        row["consensus_reason"] = adj["reason"]
        updated += 1

    print(f"Updated {updated} rows, skipped {skipped} (no adjudication found)")

    fieldnames = list(rows[0].keys())
    with SAMPLE.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print("Wrote updated sample.csv")

    # Summary stats
    all_rows = rows
    label_counts = Counter(r["consensus_label"] for r in all_rows)
    print("\nconsensus_label distribution after merge:")
    for lbl, n in label_counts.most_common():
        print(f"  {lbl}: {n}")

    # Precision (excl. uncertain / out-of-scope / clean-file)
    occ_rows = [r for r in all_rows if r["validation_unit"] == "occurrence"]
    tp = sum(1 for r in occ_rows if r["consensus_label"] == "true-positive")
    fp = sum(1 for r in occ_rows if r["consensus_label"] == "false-positive")
    unc = sum(1 for r in occ_rows if r["consensus_label"] == "uncertain")
    total_dec = tp + fp
    prec = f"{tp / total_dec:.1%}" if total_dec else "n/a"
    print(f"\nOverall precision (occurrences, decidable): {prec}  ({tp} TP / {total_dec} decidable, {unc} uncertain)")


if __name__ == "__main__":
    main()
