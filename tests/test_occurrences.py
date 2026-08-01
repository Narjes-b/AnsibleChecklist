from ansibleguard.report.occurrences import build_occurrences


def test_overlapping_detectors_are_grouped_without_losing_evidence(tmp_path):
    source = tmp_path / "tasks.yml"
    findings = [
        {
            "file": str(source),
            "line": 7,
            "rule_id": "overriden-keys",
            "severity": "error",
            "message": "duplicate key",
            "provider": "ansibleguard",
            "native_rule_id": "overriden-keys",
            "concept_id": "duplicate-mapping-key",
            "finding_id": "internal",
        },
        {
            "file": str(source),
            "line": 7,
            "rule_id": "ansible-lint-issue",
            "severity": "warning",
            "message": "key-duplicates",
            "provider": "ansible-lint",
            "native_rule_id": "yaml[key-duplicates]",
            "concept_id": "duplicate-mapping-key",
            "finding_id": "lint",
        },
    ]
    occurrences = build_occurrences(findings, repo_root=tmp_path)
    assert len(occurrences) == 1
    assert occurrences[0]["detector_count"] == 2
    assert occurrences[0]["canonical_provider"] == "ansible-lint"
    assert {item["finding_id"] for item in occurrences[0]["detectors"]} == {
        "internal",
        "lint",
    }


def test_occurrence_identity_changes_when_native_evidence_changes(tmp_path):
    base = {
        "file": str(tmp_path / "vars.yml"),
        "line": 2,
        "rule_id": "hardcoded-credentials",
        "severity": "error",
        "message": "secret",
        "provider": "gitleaks",
        "native_rule_id": "generic-api-key",
        "concept_id": "hardcoded-secret",
        "finding_id": "raw",
        "native_fingerprint": "old",
        "scan_mode": "dir",
    }
    old = build_occurrences([base], repo_root=tmp_path)[0]
    new = build_occurrences(
        [{**base, "native_fingerprint": "new"}], repo_root=tmp_path
    )[0]
    assert old["occurrence_id"] != new["occurrence_id"]


def test_occurrence_identity_is_stable_across_checkout_roots(tmp_path):
    base_root = tmp_path / "base"
    head_root = tmp_path / "head"

    def findings(root, first_id, second_id):
        source = root / "tasks" / "main.yml"
        return [
            {
                "file": str(source),
                "line": 8,
                "rule_id": "unguarded-variable",
                "severity": "warning",
                "message": "Variable 'v' is unguarded",
                "provider": "ansibleguard",
                "native_rule_id": "unguarded-variable",
                "concept_id": "unguarded-variable",
                "finding_id": first_id,
            },
            {
                "file": str(source),
                "line": 8,
                "rule_id": "unguarded-variable",
                "severity": "warning",
                "message": "Variable 'k' is unguarded",
                "provider": "ansibleguard",
                "native_rule_id": "unguarded-variable",
                "concept_id": "unguarded-variable",
                "finding_id": second_id,
            },
        ]

    base = build_occurrences(findings(base_root, "a", "z"), base_root)[0]
    head = build_occurrences(findings(head_root, "z", "a"), head_root)[0]

    assert base["message"] == head["message"] == "Variable 'k' is unguarded"
    assert base["occurrence_id"] == head["occurrence_id"]


def test_occurrence_identity_removes_checkout_root_from_tool_messages(tmp_path):
    def occurrence(root):
        message = f"Role not found in {root}/molecule/default/roles"
        return build_occurrences(
            [
                {
                    "file": str(root / "molecule" / "default" / "converge.yml"),
                    "line": 6,
                    "rule_id": "ansible-lint-issue",
                    "severity": "warning",
                    "message": message,
                    "provider": "ansible-lint",
                    "native_rule_id": "syntax-check[specific]",
                    "concept_id": "ansible-lint-issue",
                    "finding_id": message,
                }
            ],
            root,
        )[0]

    assert occurrence(tmp_path / "base")["occurrence_id"] == occurrence(
        tmp_path / "head"
    )["occurrence_id"]
