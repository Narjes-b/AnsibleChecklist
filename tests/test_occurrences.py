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

    reversed_occurrences = build_occurrences(
        list(reversed(findings)), repo_root=tmp_path
    )
    assert reversed_occurrences == occurrences


def test_gitleaks_and_plaintext_variable_merge_only_with_same_subject(tmp_path):
    source = tmp_path / "vars.yml"
    base = {
        "file": str(source), "line": 2, "severity": "error",
        "concept_id": "hardcoded-secret", "scan_mode": "source",
    }
    findings = [
        {
            **base, "rule_id": "hardcoded-credentials", "provider": "gitleaks",
            "native_rule_id": "generic-api-key", "finding_id": "g",
            "semantic_subject": "variable:api_token", "message": "secret",
        },
        {
            **base, "rule_id": "plaintext-sensitive-variable", "provider": "ansibleguard",
            "native_rule_id": "plaintext-sensitive-variable", "finding_id": "a",
            "semantic_subject": "variable:api_token", "message": "plaintext",
        },
    ]
    occurrence = build_occurrences(findings, repo_root=tmp_path)
    assert len(occurrence) == 1
    assert occurrence[0]["detector_count"] == 2


def test_exact_duplicate_detector_evidence_is_removed(tmp_path):
    source = tmp_path / "tasks.yml"
    finding = {
        "file": str(source),
        "line": 7,
        "rule_id": "unguarded-variable",
        "severity": "warning",
        "message": "Variable 'value' is unguarded",
        "provider": "ansibleguard",
        "native_rule_id": "unguarded-variable",
        "concept_id": "unguarded-variable",
        "finding_id": "same-finding",
    }
    occurrence = build_occurrences([finding, dict(finding)], repo_root=tmp_path)[0]
    assert occurrence["detector_count"] == 1
    assert len(occurrence["detectors"]) == 1


def test_provider_evidence_changes_without_changing_semantic_identity(tmp_path):
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
    assert old["occurrence_id"] == new["occurrence_id"]
    assert old["semantic_key"] == new["semantic_key"]
    assert (
        old["provider_evidence_fingerprint"]
        != new["provider_evidence_fingerprint"]
    )


def test_provider_wording_changes_without_changing_semantic_identity(tmp_path):
    base = {
        "file": str(tmp_path / "tasks.yml"),
        "line": 2,
        "rule_id": "ansible-lint-issue",
        "severity": "warning",
        "provider": "ansible-lint",
        "native_rule_id": "fqcn[action-core]",
        "concept_id": "fqcn-migration",
        "finding_id": "raw",
        "semantic_subject": "module:copy",
    }
    old = build_occurrences([{**base, "message": "Use FQCN"}], tmp_path)[0]
    new = build_occurrences(
        [{**base, "message": "Use fully qualified collection names"}], tmp_path
    )[0]

    assert old["occurrence_id"] == new["occurrence_id"]
    assert old["provider_evidence_fingerprint"] != new[
        "provider_evidence_fingerprint"
    ]


def test_task_fingerprint_disambiguates_same_subject_in_different_tasks(tmp_path):
    base = {
        "file": str(tmp_path / "tasks.yml"),
        "line": 2,
        "rule_id": "unguarded-variable",
        "severity": "warning",
        "message": "Variable 'result' is unguarded",
        "provider": "ansibleguard",
        "concept_id": "unguarded-variable",
        "semantic_subject": "variable:result",
    }

    first = build_occurrences(
        [{**base, "finding_id": "one", "task_fingerprint": "task-one"}], tmp_path
    )[0]
    second = build_occurrences(
        [{**base, "finding_id": "two", "task_fingerprint": "task-two"}], tmp_path
    )[0]

    assert first["semantic_key"] != second["semantic_key"]


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

    base = {
        item["semantic_subject"]: item
        for item in build_occurrences(findings(base_root, "a", "z"), base_root)
    }
    head = {
        item["semantic_subject"]: item
        for item in build_occurrences(findings(head_root, "z", "a"), head_root)
    }

    assert set(base) == set(head) == {"variable:k", "variable:v"}
    assert {
        subject: item["occurrence_id"] for subject, item in base.items()
    } == {
        subject: item["occurrence_id"] for subject, item in head.items()
    }


def test_long_yaml_line_deduplication_when_both_providers_fire(tmp_path):
    """Both the internal long-statement detector (concept_id=long-yaml-line) and
    ansible-lint yaml[line-length] (also concept_id=long-yaml-line after mapping)
    should be merged into exactly one occurrence per (file, line) pair."""
    source = tmp_path / "tasks.yml"
    findings = [
        {
            "file": str(source),
            "line": 15,
            "rule_id": "long-yaml-line",
            "severity": "warning",
            "message": "Line exceeds 120 characters (internal)",
            "provider": "ansibleguard",
            "native_rule_id": "long-statement",
            "concept_id": "long-yaml-line",
            "finding_id": "internal",
        },
        {
            "file": str(source),
            "line": 15,
            "rule_id": "ansible-lint-issue",
            "severity": "warning",
            "message": "Line too long (160)",
            "provider": "ansible-lint",
            "native_rule_id": "yaml[line-length]",
            "concept_id": "long-yaml-line",
            "finding_id": "lint",
        },
    ]
    occurrences = build_occurrences(findings, repo_root=tmp_path)
    assert len(occurrences) == 1, (
        "Both providers found the same long line — must be deduplicated to 1 occurrence"
    )
    assert occurrences[0]["detector_count"] == 2
    assert occurrences[0]["concept_id"] == "long-yaml-line"
    # ansible-lint is canonical provider for long-yaml-line
    assert occurrences[0]["canonical_provider"] == "ansible-lint"
    native_rules = occurrences[0]["native_rules"]
    assert "ansibleguard/long-statement" in native_rules
    assert "ansible-lint/yaml[line-length]" in native_rules


def test_long_yaml_line_different_lines_are_not_merged(tmp_path):
    """Findings on different lines for the same concept must NOT be merged."""
    source = tmp_path / "tasks.yml"
    findings = [
        {
            "file": str(source),
            "line": 10,
            "rule_id": "long-yaml-line",
            "severity": "warning",
            "message": "Line 10 too long",
            "provider": "ansibleguard",
            "native_rule_id": "long-statement",
            "concept_id": "long-yaml-line",
            "finding_id": "f10",
        },
        {
            "file": str(source),
            "line": 20,
            "rule_id": "ansible-lint-issue",
            "severity": "warning",
            "message": "Line 20 too long",
            "provider": "ansible-lint",
            "native_rule_id": "yaml[line-length]",
            "concept_id": "long-yaml-line",
            "finding_id": "f20",
        },
    ]
    occurrences = build_occurrences(findings, repo_root=tmp_path)
    assert len(occurrences) == 2, "Different lines must produce separate occurrences"
    assert {o["line"] for o in occurrences} == {10, 20}


def test_same_line_distinct_semantic_subjects_are_not_merged(tmp_path):
    findings = [
        {
            "file": str(tmp_path / "tasks.yml"),
            "line": 4,
            "rule_id": "unguarded-variable",
            "concept_id": "unguarded-variable",
            "severity": "warning",
            "message": "Variable 'first_value' is unresolved.",
        },
        {
            "file": str(tmp_path / "tasks.yml"),
            "line": 4,
            "rule_id": "unguarded-variable",
            "concept_id": "unguarded-variable",
            "severity": "warning",
            "message": "Variable 'second_value' is unresolved.",
        },
    ]

    occurrences = build_occurrences(findings, tmp_path)

    assert len(occurrences) == 2
    assert {item["semantic_subject"] for item in occurrences} == {
        "variable:first_value", "variable:second_value"
    }


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


def test_semantic_identity_preserves_meaningful_numbers(tmp_path):
    finding = {
        "file": str(tmp_path / "vars.yml"),
        "line": 1,
        "rule_id": "invalid-numeric-value",
        "severity": "warning",
        "provider": "ansibleguard",
        "native_rule_id": "invalid-numeric-value",
        "concept_id": "invalid-numeric-value",
        "finding_id": "raw",
    }
    port_80 = build_occurrences(
        [{**finding, "message": "Invalid port 80", "semantic_subject": "port:80"}],
        tmp_path,
    )[0]
    port_443 = build_occurrences(
        [
            {
                **finding,
                "message": "Invalid port 443",
                "semantic_subject": "port:443",
            }
        ],
        tmp_path,
    )[0]

    assert port_80["semantic_key"] != port_443["semantic_key"]


def test_warn_list_policy_adjusts_canonical_confidence(tmp_path):
    finding = {
        "file": str(tmp_path / "tasks.yml"),
        "line": 3,
        "rule_id": "ansible-lint-issue",
        "severity": "warning",
        "message": "Use FQCN",
        "provider": "ansible-lint",
        "native_rule_id": "fqcn[action]",
        "concept_id": "fqcn-migration",
        "finding_id": "lint",
        "native_policy": "warn-list",
        "policy_adjusted": True,
    }

    occurrence = build_occurrences([finding], tmp_path)[0]

    assert occurrence["native_policies"] == ["warn-list"]
    assert occurrence["policy_adjusted"] is True
    assert occurrence["confidence"] == "low"
    assert occurrence["taxonomy"] == "STYLE_POLICY"
    assert occurrence["actionability"] == "advisory"
    assert occurrence["rule_maturity"] == "stable"


def test_uncertain_semantic_evidence_is_low_confidence_and_informational(
    tmp_path,
):
    finding = {
        "file": str(tmp_path / "tasks.yml"),
        "line": 3,
        "rule_id": "unguarded-variable",
        "severity": "warning",
        "message": "Variable 'runtime_value' is unresolved.",
        "provider": "ansibleguard",
        "native_rule_id": "unguarded-variable",
        "concept_id": "unguarded-variable",
        "finding_id": "uncertain",
        "semantic_status": "UNCERTAIN",
        "uncertainty_sources": ["dynamic_include"],
        "confidence": "low",
        "confidence_factors": {
            "positive": ["no_visible_static_definition"],
            "negative": ["dynamic_include"],
        },
        "resolution_status": "RUNTIME_CONTEXT_UNCERTAIN",
        "resolution_scope": "repository-static",
        "resolution_evidence": {
            "proved": ["no_visible_static_definition"],
            "blockers": ["dynamic_include"],
        },
    }

    occurrence = build_occurrences([finding], tmp_path)[0]

    assert occurrence["semantic_status"] == "UNCERTAIN"
    assert occurrence["uncertainty_sources"] == ["dynamic_include"]
    assert occurrence["resolution_status"] == "RUNTIME_CONTEXT_UNCERTAIN"
    assert occurrence["resolution_scope"] == "repository-static"
    assert occurrence["confidence"] == "low"
    assert occurrence["actionability"] == "advisory"
    assert occurrence["policy"] == "optional"
    assert occurrence["taxonomy"] == "OPTIONAL_PRACTICE"
