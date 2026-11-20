"""Draw a calibration-only, rule-stratified sample of AnsibleGuard findings with source context."""
import csv, random, subprocess, sys
from collections import defaultdict
from pathlib import Path
csv.field_size_limit(1 << 30)
occ, root, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
per_rule = int(sys.argv[4]) if len(sys.argv) > 4 else 2
split = {r["repository"]: r["split"] for r in csv.DictReader(open(root / "study/validation-v007-human/splits/repository-split.csv"))}
pilot = {(r["repository"], r["path"], r["line_start"], r["rule_id"]) for r in csv.DictReader(open(root / "study/validation-v007-human/samples/agreement-pilot/agreement-pilot-master.csv"))}
by_rule = defaultdict(list)
with open(occ, newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if split.get(r["project"]) != "calibration" or r["policy"] == "optional":
            continue
        if (r["project"], r["file"], r["line"], r["rule_id"]) in pilot:
            continue
        by_rule[r["rule_id"]].append(r)
rng = random.Random("v007-audit-2026-10-15-fp-precheck")
sample = []
for rule in sorted(by_rule):
    rows = by_rule[rule]
    sample += rng.sample(rows, min(per_rule, len(rows)))
cache = root / "study/cache/v007-full-repro-2026/repositories"
out.mkdir(parents=True, exist_ok=True)
with open(out / "sample.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["sample_id", "rule_id", "severity", "population", "project", "commit_sha", "file", "line", "message"])
    w.writeheader()
    md = []
    for i, r in enumerate(sample, 1):
        sid = f"FP-{i:03d}"
        w.writerow({"sample_id": sid, "rule_id": r["rule_id"], "severity": r["severity"], "population": len(by_rule[r["rule_id"]]),
                    "project": r["project"], "commit_sha": r["commit_sha"], "file": r["file"], "line": r["line"], "message": r["message"][:300]})
        text = subprocess.run(["git", "-C", str(cache / r["project"]), "show", f'{r["commit_sha"]}:{r["file"]}'], capture_output=True, text=True, errors="replace").stdout.splitlines()
        line = int(r["line"] or 1)
        lo, hi = max(1, line - 6), min(len(text), line + 14)
        window = "\n".join(f"{n:5d}{'>' if n == line else ' '}| {text[n-1][:160]}" for n in range(lo, hi + 1))
        md.append(f"### {sid} `{r['rule_id']}` ({r['severity']}) — {r['project']} `{r['file']}:{line}` ({len(text)} lines)\n{r['message'][:400]}\n```\n{window}\n```\n")
    (out / "contexts.md").write_text("\n".join(md), encoding="utf-8")
print(f"rules={len(by_rule)} sampled={len(sample)} calibration_only=True")
