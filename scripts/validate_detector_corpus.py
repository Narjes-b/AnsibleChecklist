"""Run source-level detectors over a YAML corpus and print a review baseline."""

from __future__ import annotations

from collections import defaultdict
import argparse
import json
from pathlib import Path

from ansibleguard.cli import collect_yaml_files
from ansibleguard.detectors.deprecated_modules import detect_deprecated_modules
from ansibleguard.detectors.handler_issues import detect_handler_issues
from ansibleguard.detectors.missing_tags import detect_missing_tags
from ansibleguard.detectors.missing_validate_certs import detect_missing_validate_certs
from ansibleguard.detectors.paper_candidates import detect_paper_candidates
from ansibleguard.detectors.partial_checklist import detect_partial_checklist_smells
from ansibleguard.detectors.review_checklist import detect_review_checklist_smells
from ansibleguard.detectors.shell_instead_of_module import detect_shell_instead_of_module


def validate(root):
    files = collect_yaml_files(Path(root))
    counts = defaultdict(int)
    affected_files = defaultdict(set)
    samples = defaultdict(list)
    parseable = 0
    for path in files:
        metrics = {}
        for detector in (
            detect_paper_candidates,
            detect_review_checklist_smells,
            detect_partial_checklist_smells,
        ):
            metrics.update(detector(path))
        missing_handlers, missing_details, unused_handlers, unused_details = (
            detect_handler_issues(path)
        )
        legacy = {
            "missing_tags": detect_missing_tags(path),
            "deprecated_modules": detect_deprecated_modules(path),
            "missing_validate_certs": detect_missing_validate_certs(path),
            "shell_instead_of_module": detect_shell_instead_of_module(path),
            "missing_handlers": (missing_handlers, missing_details),
            "unused_handlers": (unused_handlers, unused_details),
        }
        if any(key in metrics for key in ("complex_expressions", "insecure_permissions")):
            parseable += 1
        for metric, (count, details) in legacy.items():
            metrics[metric] = count
            metrics[f"{metric}_details"] = details
        for metric, count in metrics.items():
            if metric.endswith("_details") or not isinstance(count, int) or count <= 0:
                continue
            counts[metric] += count
            affected_files[metric].add(str(path.relative_to(root)))
            detail_key = f"{metric}_details"
            for detail in metrics.get(detail_key, [])[: 5 - len(samples[metric])]:
                samples[metric].append(
                    {
                        "file": str(path.relative_to(root)),
                        "line": detail.get("line", 1),
                        "issue": detail.get("issue") or detail.get("message", ""),
                    }
                )
    return {
        "corpus": str(Path(root).resolve()),
        "yaml_files": len(files),
        "files_processed_by_detector_bundles": parseable,
        "rules": {
            metric: {
                "findings": counts[metric],
                "affected_files": len(affected_files[metric]),
                "samples": samples[metric],
            }
            for metric in sorted(counts)
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.corpus), indent=2))


if __name__ == "__main__":
    main()
