#!/usr/bin/env python3
"""Descriptive analysis of the v0.0.7 run by category, family, rule, and repository.

Reads the aggregate occurrence exports of a run package and writes small CSV
tables (no source content). All shares are of the stated population; counts
are detector output, not validated defects.

Populations:
- ``internal``: AnsibleGuard static-source occurrences (206 analyzable
  repositories). ``required`` and ``optional`` follow the rule catalog policy.
- ``complete-provider repositories``: the 171 repositories where AnsibleGuard,
  ansible-lint, and GitLeaks all completed; the only valid population for any
  cross-provider comparison.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from pathlib import Path

import numpy as np

csv.field_size_limit(1 << 30)


def gini(values) -> float:
    v = np.sort(np.asarray(values, dtype=float))
    n = len(v)
    if n == 0 or v.sum() == 0:
        return 0.0
    return float((2 * np.arange(1, n + 1) - n - 1).dot(v) / (n * v.sum()))


def ranks(values) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    result = np.empty(len(values))
    sorted_values = values[order]
    start = 0
    for end in range(1, len(values) + 1):
        if end == len(values) or sorted_values[end] != sorted_values[start]:
            result[order[start:end]] = (start + end - 1) / 2 + 1
            start = end
    return result


def spearman(x, y) -> float:
    rx, ry = ranks(x), ranks(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def read(path: Path):
    with open(path, newline="", encoding="utf-8") as stream:
        yield from csv.DictReader(stream)


def tier(heldout_required: int) -> str:
    if heldout_required == 0:
        return "none"
    if heldout_required <= 30:
        return "census"
    return "large" if heldout_required >= 500 else "mid"


def write(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True, help="study/runs/v007-full-repro-2026")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    aggregate = args.run / "aggregate"
    human = args.root / "study/validation-v007-human"
    split = {r["repository"]: r["split"] for r in read(human / "splits/repository-split.csv")}
    family = {r["rule_id"]: r for r in read(human / "mappings/rule-family-map.csv")}
    summaries = {r["project"]: r for r in read(aggregate / "repository-summary.csv") if r["project"] != "__ALL__"}
    status = {r["project"]: r for r in read(args.run / "status/validation.csv")}
    loc = {p: float(r.get("selected_loc") or 0) for p, r in summaries.items()}
    analyzable = sorted(p for p, r in summaries.items() if r.get("scan_status") != "timeout")
    complete = {p for p in analyzable if status.get(p, {}).get("status") == "complete"}

    per_rule_repo: dict[tuple[str, str], Counter] = defaultdict(Counter)
    cells: Counter = Counter()
    meta: dict[str, dict] = {}
    for r in read(aggregate / "all-internal-source-occurrences.csv"):
        rule, project = r["rule_id"], r["project"]
        meta.setdefault(rule, {"category": r["category"]})
        per_rule_repo[(rule, "all")][project] += 1
        # Policy is decided per occurrence by the tool's resolution state (for
        # example an undecidable dynamic no_log makes an occurrence optional),
        # so it must be counted per occurrence, never taken from a rule.
        per_rule_repo[(rule, "policy:" + r["policy"])][project] += 1
        cells[(r["category"], r["policy"], r["severity"], r["confidence"], r["certainty"])] += 1
        per_rule_repo[(rule, "sev:" + r["severity"])][project] += 1
        per_rule_repo[(rule, "conf:" + r["confidence"])][project] += 1
        per_rule_repo[(rule, "cert:" + r["certainty"])][project] += 1

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    def counts_vector(counter: Counter) -> np.ndarray:
        return np.array([counter.get(p, 0) for p in analyzable], dtype=float)

    # ---- rule profile -------------------------------------------------------
    rule_rows = []
    for rule, m in sorted(meta.items()):
        counter = per_rule_repo[(rule, "all")]
        vector = counts_vector(counter)
        total = int(vector.sum())
        affected = vector[vector > 0]
        top_repo, top_n = counter.most_common(1)[0]
        required_counter = per_rule_repo[(rule, "policy:required")]
        optional_counter = per_rule_repo[(rule, "policy:optional")]
        policy = "mixed" if required_counter and optional_counter else ("required" if required_counter else "optional")
        held = sum(n for p, n in required_counter.items() if split.get(p) == "heldout")
        held_all = sum(n for p, n in counter.items() if split.get(p) == "heldout")
        cal = total - held_all
        held_repos = sum(1 for p in required_counter if split.get(p) == "heldout")
        info = family.get(rule, {})
        row = {
            "rule_id": rule, "category": m["category"], "policy": policy,
            "required_occurrences": sum(required_counter.values()), "optional_occurrences": sum(optional_counter.values()),
            "family": info.get("family_id", ""), "catalog_status": info.get("catalog_status", ""),
            "taxonomy": info.get("catalog_taxonomy", ""), "occurrences": total,
            "repositories": int((vector > 0).sum()), "prevalence_pct": round(100 * (vector > 0).mean(), 1),
            "median_per_affected_repo": float(np.median(affected)), "p90_per_affected_repo": float(np.quantile(affected, 0.9)),
            "top_repository": top_repo, "top_repository_share": round(top_n / total, 3), "gini_across_repos": round(gini(vector), 3),
            "calibration_occurrences": cal, "heldout_occurrences": held_all,
            "heldout_required_occurrences": held, "heldout_required_repositories": held_repos,
            "heldout_tier": tier(held) if required_counter else "optional-only",
        }
        for kind in ("sev", "conf", "cert"):
            tallies = {k.split(":", 1)[1]: sum(c.values()) for (rl, k), c in per_rule_repo.items() if rl == rule and k.startswith(kind + ":")}
            row[f"{kind}_mix"] = "; ".join(f"{k}={v}" for k, v in sorted(tallies.items(), key=lambda kv: -kv[1]))
        rule_rows.append(row)
    write(out / "rule-profile.csv", rule_rows)

    # ---- category overview ---------------------------------------------------
    by_category: dict[str, list[dict]] = defaultdict(list)
    for row in rule_rows:
        by_category[row["category"]].append(row)
    total_all = sum(r["occurrences"] for r in rule_rows)
    category_rows = []
    for category, rows in sorted(by_category.items(), key=lambda kv: -sum(r["occurrences"] for r in kv[1])):
        occurrences = sum(r["occurrences"] for r in rows)
        required = sum(r["required_occurrences"] for r in rows)
        per_repo = Counter()
        for r in rows:
            per_repo.update(per_rule_repo[(r["rule_id"], "all")])
        vector = counts_vector(per_repo)
        affected = vector[vector > 0]
        top = max(rows, key=lambda r: r["occurrences"])
        shares = np.array([r["occurrences"] for r in rows], dtype=float) / occurrences
        severity = Counter()
        uncertain = 0
        for (c, pol, sev, conf, cert), n in cells.items():
            if c == category:
                severity[sev] += n
                uncertain += n if cert in ("UNCERTAIN", "UNRESOLVED") else 0
        density = np.array([per_repo.get(p, 0) / (loc[p] / 1000) for p in analyzable if loc.get(p, 0) > 0])
        category_rows.append({
            "category": category, "occurrences": occurrences, "share_pct": round(100 * occurrences / total_all, 1),
            "required": required, "optional": occurrences - required,
            "rules": len(rows), "rules_with_required": sum(1 for r in rows if r["required_occurrences"]),
            "repositories": int((vector > 0).sum()), "prevalence_pct": round(100 * (vector > 0).mean(), 1),
            "median_per_affected_repo": float(np.median(affected)), "p90_per_affected_repo": float(np.quantile(affected, 0.9)),
            "top_rule": top["rule_id"].split("/")[-1], "top_rule_share_pct": round(100 * top["occurrences"] / occurrences, 1),
            "rule_hhi": round(float((shares ** 2).sum()), 3), "gini_across_repos": round(gini(vector), 3),
            "top10_repo_share_pct": round(100 * np.sort(vector)[::-1][:10].sum() / vector.sum(), 1),
            "median_per_kloc": round(float(np.median(density)), 2), "p25_per_kloc": round(float(np.quantile(density, 0.25)), 2),
            "p75_per_kloc": round(float(np.quantile(density, 0.75)), 2),
            "spearman_loc_vs_count": round(spearman([loc[p] for p in analyzable], counts_vector(per_repo)), 2),
            "error": severity["error"], "warning": severity["warning"], "note": severity["note"],
            "uncertain_pct": round(100 * uncertain / occurrences, 1),
            "calibration_occurrences": sum(r["calibration_occurrences"] for r in rows),
            "heldout_occurrences": sum(r["heldout_occurrences"] for r in rows),
            "heldout_required": sum(r["heldout_required_occurrences"] for r in rows),
        })
    write(out / "category-overview.csv", category_rows)

    # ---- family overview (required rules only) ------------------------------
    family_rows = []
    for fam in sorted({r["family"] for r in rule_rows}):
        rows = [r for r in rule_rows if r["family"] == fam]
        req = [r for r in rows if r["required_occurrences"]]
        family_rows.append({
            "family": fam, "rules": len(rows), "rules_with_required": len(req),
            "required_occurrences": sum(r["required_occurrences"] for r in req),
            "optional_occurrences": sum(r["optional_occurrences"] for r in rows),
            "heldout_required": sum(r["heldout_required_occurrences"] for r in req),
            "large_rules": sum(1 for r in req if r["heldout_tier"] == "large"),
            "mid_rules": sum(1 for r in req if r["heldout_tier"] == "mid"),
            "census_rules": sum(1 for r in req if r["heldout_tier"] == "census"),
        })
    write(out / "family-overview.csv", family_rows)

    # ---- cross-tabulation ----------------------------------------------------
    write(out / "crosstab-category-policy-severity-confidence-certainty.csv", [
        {"category": c, "policy": p, "severity": s, "confidence": cf, "certainty": ce, "occurrences": n}
        for (c, p, s, cf, ce), n in sorted(cells.items())
    ])

    # ---- repository profile --------------------------------------------------
    required_by_repo, optional_by_repo, uncertain_by_repo = Counter(), Counter(), Counter()
    for r in read(aggregate / "all-internal-source-occurrences.csv"):
        (required_by_repo if r["policy"] == "required" else optional_by_repo)[r["project"]] += 1
        if r["certainty"] in ("UNCERTAIN", "UNRESOLVED"):
            uncertain_by_repo[r["project"]] += 1
    repo_rows = []
    for p in analyzable:
        kloc = loc[p] / 1000 or float("nan")
        repo_rows.append({
            "repository": p, "split": split.get(p, "?"), "selected_loc": int(loc[p]),
            "selected_files": summaries[p].get("selected_files", ""), "required": required_by_repo[p],
            "optional": optional_by_repo[p], "uncertain": uncertain_by_repo[p],
            "required_per_kloc": round(required_by_repo[p] / kloc, 2) if kloc == kloc else "",
            "all_per_kloc": round((required_by_repo[p] + optional_by_repo[p]) / kloc, 2) if kloc == kloc else "",
            "provider_complete": p in complete,
        })
    write(out / "repository-profile.csv", repo_rows)

    # ---- provider comparison on complete repositories ------------------------
    internal_cat, internal_req = Counter(), Counter()
    for r in read(aggregate / "all-internal-source-occurrences.csv"):
        if r["project"] in complete:
            internal_cat[r["category"]] += 1
            internal_req[r["category"]] += r["policy"] == "required"
    lint_cat = Counter(r["category"] for r in read(aggregate / "all-ansible-lint-occurrences.csv") if r["project"] in complete)
    leak_cat = Counter(r["category"] for r in read(aggregate / "all-gitleaks-occurrences.csv") if r["project"] in complete)
    review = Counter(r["category"] for r in read(aggregate / "all-review-occurrences.csv"))
    write(out / "provider-by-category-complete-repositories.csv", [
        {"category": c, "internal_all": internal_cat[c], "internal_required": internal_req[c],
         "ansible_lint": lint_cat[c], "gitleaks": leak_cat[c], "review_range_not_comparable": review[c]}
        for c in sorted(set(internal_cat) | set(lint_cat) | set(leak_cat) | set(review))
    ])

    # ---- headline figures ----------------------------------------------------
    req_total = sum(r["required_occurrences"] for r in rule_rows)
    vec_all = counts_vector(sum((per_rule_repo[(r["rule_id"], "all")] for r in rule_rows), Counter()))
    print(f"internal occurrences {total_all}; required {req_total}; repositories analyzable {len(analyzable)}; "
          f"provider-complete {len(complete)}; repo Gini {gini(vec_all):.3f}; top10 repo share "
          f"{np.sort(vec_all)[::-1][:10].sum() / vec_all.sum():.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
