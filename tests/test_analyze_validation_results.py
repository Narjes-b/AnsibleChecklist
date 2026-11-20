import csv
import json

from scripts.analyze_validation_results import summarize_result


def test_summary_counts_selected_loc_and_provider_overlap(tmp_path):
    root = tmp_path / "results"
    result = root / "example__project" / "abc123"
    result.mkdir(parents=True)
    manifest = tmp_path / "classification.csv"
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("path", "loc", "included"))
        writer.writeheader()
        writer.writerows(
            [
                {"path": "included.yml", "loc": 12, "included": "true"},
                {"path": "excluded.yml", "loc": 50, "included": "false"},
            ]
        )
    (result / "run_metadata.json").write_text(
        json.dumps(
            {
                "target": "/tmp/example",
                "file_selection": {
                    "manifest": str(manifest),
                    "included_files": 1,
                },
                "tools": {
                    "ansible_lint": "completed",
                    "gitleaks": "completed",
                },
            }
        ),
        encoding="utf-8",
    )
    (result / "occurrences.json").write_text(
        json.dumps(
            [
                {
                    "concept_id": "one-provider",
                    "detectors": [
                        {"provider": "ansibleguard"},
                        {"provider": "ansibleguard"},
                    ],
                },
                {
                    "concept_id": "cross-provider",
                    "detectors": [
                        {"provider": "ansibleguard"},
                        {"provider": "ansible-lint"},
                    ],
                },
            ]
        ),
        encoding="utf-8",
    )

    row, rules, _ = summarize_result("test", root, result)

    assert row["included_loc"] == 12
    assert row["raw_detectors"] == 4
    assert row["canonical_occurrences"] == 2
    assert row["same_provider_multi_detector_occurrences"] == 1
    assert row["cross_provider_occurrences"] == 1
    assert rules == {"one-provider": 1, "cross-provider": 1}
