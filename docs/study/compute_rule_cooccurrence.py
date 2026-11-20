# -*- coding: utf-8 -*-
"""RQ2 data: rule-violation co-occurrence within the same file, mirroring
Bessghaier et al. (SANER'24)'s IaC-smell co-occurrence methodology (Apriori-
style support/confidence/lift, plus Chi-squared/Cramer's V for association
strength), applied to AnsibleGuard's own v0.0.7.1 occurrence data instead of
Puppet IaC smells.

Transaction unit: one (project, file). The "items" in each transaction are
the set of distinct rule_ids with at least one occurrence in that file.
Required (defect-claiming) rules only, per the already-established policy
distinction in docs/study/v007-research-report-and-validation-plan.md --
pooling optional-policy rules like missing-tags would let them dominate
purely on volume, same reasoning as that doc's own RQ1 discussion.

Input data (not committed -- 166MB, exceeds GitHub's file size limit):
copy study/runs/v0071-final-2026/aggregate/all-internal-source-occurrences.csv
from the WSL v0.0.7.1 reproduction checkout to
docs/study/v0071-all-internal-source-occurrences.csv before running this.
Output (rq2-cooccurrence-pairs.csv, 709 rows, ~92KB) IS committed.
"""
import csv
from collections import defaultdict
from itertools import combinations


def chi2_2x2(table):
    """Pearson chi-squared for a 2x2 contingency table, no scipy dependency.
    Returns (chi2, p_value) using the standard formula and a direct
    regularized-incomplete-gamma based chi-squared survival function for
    dof=1 (p = erfc(sqrt(chi2/2)))."""
    import math
    (a, b), (c, d) = table
    n = a + b + c + d
    row1, row2 = a + b, c + d
    col1, col2 = a + c, b + d
    if n == 0 or row1 == 0 or row2 == 0 or col1 == 0 or col2 == 0:
        return float("nan"), float("nan")
    expected = [[row1 * col1 / n, row1 * col2 / n], [row2 * col1 / n, row2 * col2 / n]]
    observed = [[a, b], [c, d]]
    chi2 = sum(
        (observed[i][j] - expected[i][j]) ** 2 / expected[i][j]
        for i in range(2) for j in range(2)
        if expected[i][j] > 0
    )
    # dof=1: p-value = erfc(sqrt(chi2/2)) (survival function of chi2 dist, df=1)
    p = math.erfc(math.sqrt(chi2 / 2))
    return chi2, p

IN_CSV = "v0071-all-internal-source-occurrences.csv"
OUT_PAIRS_CSV = "rq2-cooccurrence-pairs.csv"

# Optional-policy rules per the research report (missing-tags, unguarded-variable,
# variable-naming-convention and similar are not defect claims) -- excluded so
# they cannot dominate pair counts purely on volume. We read "policy" directly
# from the data instead of hardcoding, since that's exactly what the column is for.


def main():
    transactions = defaultdict(set)  # (project, file) -> {rule_id, ...}
    required_only = 0
    total_rows = 0
    with open(IN_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            total_rows += 1
            if row.get("policy") != "required":
                continue
            required_only += 1
            key = (row["project"], row["file"])
            transactions[key].add(row["rule_id"])

    print(f"total internal occurrences: {total_rows}")
    print(f"required (defect-claiming) occurrences: {required_only}")
    print(f"transactions (project,file pairs) with >=1 required occurrence: {len(transactions)}")

    multi_rule_transactions = [t for t in transactions.values() if len(t) >= 2]
    print(f"transactions with >=2 distinct required rules (co-occurrence possible): {len(multi_rule_transactions)}")
    print(f"share of transactions with co-occurring distinct rules: {len(multi_rule_transactions)/len(transactions)*100:.2f}%")

    # Per-rule support (fraction of transactions containing that rule)
    rule_counts = defaultdict(int)
    for items in transactions.values():
        for r in items:
            rule_counts[r] += 1
    n = len(transactions)

    # Pairwise support/confidence/lift
    pair_counts = defaultdict(int)
    for items in transactions.values():
        if len(items) < 2:
            continue
        for a, b in combinations(sorted(items), 2):
            pair_counts[(a, b)] += 1

    results = []
    for (a, b), both in pair_counts.items():
        support_ab = both / n
        support_a = rule_counts[a] / n
        support_b = rule_counts[b] / n
        conf_ab = both / rule_counts[a]  # P(b|a)
        conf_ba = both / rule_counts[b]  # P(a|b)
        lift = support_ab / (support_a * support_b)

        # Chi-squared + Cramer's V on the 2x2 contingency table for this pair
        a_yes_b_yes = both
        a_yes_b_no = rule_counts[a] - both
        a_no_b_yes = rule_counts[b] - both
        a_no_b_no = n - rule_counts[a] - rule_counts[b] + both
        table = [[a_yes_b_yes, a_yes_b_no], [a_no_b_yes, a_no_b_no]]
        chi2, p = chi2_2x2(table)
        cramers_v = (chi2 / n) ** 0.5 if chi2 == chi2 else float("nan")  # 2x2: Cramer's V = sqrt(chi2/n)

        results.append({
            "rule_a": a, "rule_b": b,
            "both_count": both,
            "support": round(support_ab, 4),
            "confidence_a_to_b": round(conf_ab, 4),
            "confidence_b_to_a": round(conf_ba, 4),
            "lift": round(lift, 2),
            "chi2": round(chi2, 2),
            "p_value": p,
            "cramers_v": round(cramers_v, 3),
        })

    results.sort(key=lambda r: -r["lift"])

    with open(OUT_PAIRS_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    print(f"\ndistinct rule pairs that ever co-occur: {len(results)}")
    print(f"wrote {OUT_PAIRS_CSV}")

    print("\nTop 10 pairs by Lift:")
    for r in results[:10]:
        print(f"  {r['rule_a']} <-> {r['rule_b']}: support={r['support']} conf(a->b)={r['confidence_a_to_b']} "
              f"conf(b->a)={r['confidence_b_to_a']} lift={r['lift']} chi2_p={r['p_value']:.2e} cramers_v={r['cramers_v']}")

    # Support-threshold calibration: smallest threshold s.t. >=80% of observed
    # pairs are covered, mirroring SANER24's calibration approach for the
    # support threshold.
    supports_sorted = sorted((r["support"] for r in results), reverse=True)
    cutoff_idx = int(len(supports_sorted) * 0.8)
    print(f"\nsupport threshold covering 80% of observed pairs: >= {supports_sorted[min(cutoff_idx, len(supports_sorted)-1)]}")

    sig = [r for r in results if r["p_value"] < 0.05 and r["lift"] >= 1]
    print(f"\npairs with lift>=1 and p<0.05 (statistically significant positive association): {len(sig)} of {len(results)}")


if __name__ == "__main__":
    main()
