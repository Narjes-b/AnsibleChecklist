from pathlib import Path

# Default output folder name is excluded too — otherwise a second run
# against the same target directory could, in principle, later start
# picking up its own previous output as input if that ever changed shape.
# Costs nothing to guard against now.
EXCLUDE_DIRS = {"molecule", ".github", ".git", ".venv", "venv", "ansibleguard-output"}


def collect_yaml_files(target: Path) -> list[Path]:
    """Find every .yml/.yaml file under target, recursively, skipping
    directories that contain real YAML but aren't Ansible production
    content (Molecule test scenarios, CI config, etc.)."""
    target = Path(target)
    if target.is_file():
        return [target]

    files = []
    for pattern in ("*.yml", "*.yaml"):
        files.extend(target.rglob(pattern))

    return sorted(f for f in files if not any(part in EXCLUDE_DIRS for part in f.parts))


def output_dir_for(scan_root: Path, yaml_file: Path, output_root: Path) -> Path:
    """
    Build a collision-safe output directory for one analyzed file.

    Using just the file's stem (e.g. "main") breaks the moment a real
    project has more than one identically-named file in different
    directories -- roles/apache/tasks/main.yml and roles/nginx/tasks/main.yml
    both stem to "main" and would silently overwrite each other's results.
    Confirmed this collision is real, not theoretical, against a synthetic
    two-role fixture before writing this function.

    Instead, mirror the file's path *relative to the scan root* underneath
    the output directory (extension dropped), so directory structure is
    preserved and collisions are structurally impossible rather than
    merely unlikely.
    """
    scan_root = Path(scan_root)
    yaml_file = Path(yaml_file)
    try:
        rel = yaml_file.resolve().relative_to(scan_root.resolve())
    except ValueError:
        # yaml_file isn't actually under scan_root (e.g. an absolute path
        # passed as a single file target with no directory context) --
        # fall back to just its own name rather than crashing.
        rel = Path(yaml_file.name)
    return Path(output_root) / rel.with_suffix("")


def _relative_or_self(path: Path, root: Path) -> str:
    """Best-effort relative path for the summary CSV -- falls back to the
    original path string if it isn't actually under root (e.g. a
    single-file target passed with no shared directory)."""
    path = Path(path).resolve()
    root = Path(root).resolve()
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def analyze_path(target: Path, output_root: Path) -> tuple[int, int]:
    """
    Run the existing per-file analysis + report-writing pipeline
    (smellsDetector.py's execute_for_single_file + the ansible-lint/gitleaks
    text writers) against every YAML file found under target, writing
    results under output_root instead of config.py's hardcoded RESULTS_DIR.

    In addition to everything already written per-file (unchanged), also
    accumulates a flat findings list across every file and writes three
    project-wide rollups once at the end: summary.csv (one row per file,
    for "which files are worst" at a glance), findings.json (the flat
    findings shape, our own readable format), and findings.sarif (the
    industry-standard shape GitHub Code Scanning natively renders as
    inline PR annotations).

    Returns (num_succeeded, num_files) so a caller (or a future PR bot) can
    tell at a glance whether anything failed without re-parsing print output.
    """
    from smellsDetector import (
        execute_for_single_file,
        format_ansible_lint_results,
    )
    from write_to_text import (
        write_AnsibleLint_results_to_txt,
        write_GitLeaks_results_to_txt,
    )
    from findings import build_findings_list
    from sarif_writer import write_sarif

    target = Path(target)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    yaml_files = collect_yaml_files(target)
    print(f"Found {len(yaml_files)} YAML file(s) to analyze.")

    if not yaml_files:
        print("Nothing to analyze.")
        return 0, 0

    scan_root = target if target.is_dir() else target.parent
    succeeded = 0
    all_findings = []
    summary_rows = []

    for yaml_file in yaml_files:
        out_dir = output_dir_for(scan_root, yaml_file, output_root)
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔍 Processing file: {yaml_file}")

        findings, lint_results, result, metrics = execute_for_single_file(
            yaml_file, None, None, out_dir
        )

        formatted = format_ansible_lint_results(lint_results)
        write_AnsibleLint_results_to_txt(
            formatted, out_dir / "ansiblelint.txt", yaml_file
        )
        write_GitLeaks_results_to_txt(findings, out_dir / "gitleaks.txt")

        file_findings = build_findings_list(
            metrics, result, findings, lint_results, yaml_file
        )
        all_findings.extend(file_findings)

        summary_rows.append(
            {
                "file": _relative_or_self(yaml_file, scan_root),
                "errors": sum(1 for f in file_findings if f["severity"] == "error"),
                "warnings": sum(1 for f in file_findings if f["severity"] == "warning"),
                "notes": sum(1 for f in file_findings if f["severity"] == "note"),
                "total": len(file_findings),
            }
        )

        succeeded += 1

    _write_rollups(all_findings, summary_rows, output_root, scan_root)

    print(
        f"[✔] {succeeded}/{len(yaml_files)} file(s) analyzed. Results under {output_root}"
    )
    print(f"[✔] {len(all_findings)} total finding(s) across all files.")
    return succeeded, len(yaml_files)


def _write_rollups(all_findings, summary_rows, output_root, scan_root):
    import csv
    import json as _json
    from sarif_writer import write_sarif

    # summary.csv -- one row per file, ranked worst-first, for "which files
    # actually need attention" at a glance instead of opening N CSVs by hand.
    summary_rows_sorted = sorted(
        summary_rows, key=lambda r: (-r["errors"], -r["warnings"], -r["total"])
    )
    summary_csv_path = output_root / "summary.csv"
    with open(summary_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["file", "errors", "warnings", "notes", "total"]
        )
        writer.writeheader()
        writer.writerows(summary_rows_sorted)

    # findings.json -- the flat shape itself, in our own readable format.
    findings_json_path = output_root / "findings.json"
    with open(findings_json_path, "w", encoding="utf-8") as f:
        _json.dump(all_findings, f, indent=2)

    # findings.sarif -- GitHub Code Scanning-native shape.
    sarif_path = output_root / "findings.sarif"
    write_sarif(all_findings, sarif_path, repo_root=scan_root)

    print(
        f"[✔] Rollups written: {summary_csv_path}, {findings_json_path}, {sarif_path}"
    )


def main(argv=None):
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="ansibleguard",
        description="Analyze Ansible playbooks/roles for IaC code smells.",
    )
    parser.add_argument(
        "target",
        type=Path,
        help="A playbook file OR a project directory (searched recursively)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("./ansibleguard-output"),
        help="Where to write reports (default: ./ansibleguard-output)",
    )
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"Error: target path does not exist: {args.target}", file=sys.stderr)
        sys.exit(1)

    succeeded, total = analyze_path(args.target, args.output)
    if total and succeeded < total:
        sys.exit(1)  # non-zero exit if anything failed, useful for CI/bot use


if __name__ == "__main__":
    main()

