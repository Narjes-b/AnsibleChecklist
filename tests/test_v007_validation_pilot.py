from pathlib import Path

import pytest

from scripts import v007_validation_pilot
from scripts.v007_validation_pilot import (
    REVIEWER_DECISION_COLUMNS,
    _numbered_excerpt,
    pilot_rank,
    redact_sensitive_text,
    REVIEW_MESSAGE_ONLY_RULE_IDS,
    select_family,
    stable_review_occurrence_id,
)


def _candidate(rule, repo, occurrence):
    return {
        "rule_id": rule,
        "repository": repo,
        "occurrence_id": occurrence,
        "selection_rank_sha256": pilot_rank("objective_correctness", rule, occurrence),
    }


def test_pilot_selection_is_deterministic_round_robin_and_repository_diverse_first():
    candidates = [
        _candidate("rule-a", f"org/repo-{index}", f"a-{index}") for index in range(3)
    ] + [
        _candidate("rule-b", f"org/repo-{index}", f"b-{index}") for index in range(3)
    ]
    population = {"rule-a": 6, "rule-b": 6}
    first, rare = select_family(candidates, population, target=4)
    second, _ = select_family(candidates, population, target=4)
    assert [row["occurrence_id"] for row in first] == [row["occurrence_id"] for row in second]
    assert not rare
    assert len(first) == 4
    assert len({row["repository"] for row in first}) == 3
    assert {row["rule_id"] for row in first} == {"rule-a", "rule-b"}


def test_rare_rules_are_protected_when_enough_nonrare_candidates_exist():
    candidates = [
        _candidate("common-a", f"org/a-{index}", f"a-{index}") for index in range(30)
    ] + [
        _candidate("common-b", f"org/b-{index}", f"b-{index}") for index in range(30)
    ] + [_candidate("rare-rule", "org/rare", "rare-1")]
    selected, rare = select_family(
        candidates,
        {"common-a": 30, "common-b": 30, "rare-rule": 1},
        target=50,
    )
    assert len(selected) == 50
    assert "rare-rule" in rare
    assert all(row["rule_id"] != "rare-rule" for row in selected)


def test_when_fewer_than_target_are_usable_selection_is_a_census_of_nonrare_rows():
    candidates = [
        _candidate("rule-a", f"org/a-{index}", f"a-{index}") for index in range(4)
    ] + [
        _candidate("rule-b", f"org/b-{index}", f"b-{index}") for index in range(3)
    ]
    selected, _rare = select_family(candidates, {"rule-a": 10, "rule-b": 10}, target=50)
    assert {row["occurrence_id"] for row in selected} == {
        row["occurrence_id"] for row in candidates
    }


def test_review_identity_is_namespaced_by_repository_commit_and_rule():
    one = stable_review_occurrence_id("org/a", "a" * 40, "ansibleguard", "rule-a", "raw")
    two = stable_review_occurrence_id("org/b", "a" * 40, "ansibleguard", "rule-a", "raw")
    three = stable_review_occurrence_id("org/a", "a" * 40, "ansibleguard", "rule-b", "raw")
    assert len({one, two, three}) == 3


def test_review_message_only_rule_uses_exact_commit_message_without_parent(monkeypatch):
    class Result:
        stdout = "Fix the documented issue\n\nRefs: #42\n"

    monkeypatch.setattr(v007_validation_pilot, "_git", lambda *_args, **_kwargs: Result())
    candidate = {
        "_parent_sha": "",
        "commit_sha": "a" * 40,
        "rule_id": "ansibleguard/missing-bug-reference",
        "sample_id": "pilot-1",
        "repository": "org/repo",
    }
    context, inline = v007_validation_pilot._review_context(
        candidate, "Review/history", "codebooks/FAMILY_REVIEW_HISTORY.md", Path("/unused")
    )
    assert candidate["rule_id"] in REVIEW_MESSAGE_ONLY_RULE_IDS
    assert "Evidence type: exact target commit message only" in context
    assert "Actual first parent: unavailable locally and not required" in context
    assert "Diff range: not used for this message-only rule" in context
    assert "Fix the documented issue" in context and "Refs: #42" in context
    assert "Message-only evidence" in inline


def test_diff_dependent_review_rule_still_requires_actual_parent(monkeypatch):
    class Result:
        stdout = "Update tests"

    monkeypatch.setattr(v007_validation_pilot, "_git", lambda *_args, **_kwargs: Result())
    candidate = {
        "_parent_sha": "",
        "commit_sha": "b" * 40,
        "rule_id": "ansibleguard/missing-test-update",
        "sample_id": "pilot-2",
        "repository": "org/repo",
    }
    with pytest.raises(RuntimeError, match="lacks its actual first parent"):
        v007_validation_pilot._review_context(
            candidate, "Review/history", "codebooks/FAMILY_REVIEW_HISTORY.md", Path("/unused")
        )


def test_context_redaction_masks_secrets_but_preserves_templates_and_public_defaults():
    source = (
        "password: hunter2\n"
        "admin_password: changeme\n"
        "api_token: {{ vault_api_token }}\n"
        '\"client_secret\": \"high-entropy-secret\"\n'
    )
    redacted = redact_sensitive_text(source)
    assert "hunter2" not in redacted and "high-entropy-secret" not in redacted
    assert "[REDACTED_LITERAL]" in redacted
    assert "admin_password: changeme" in redacted
    assert "{{ vault_api_token }}" in redacted
    assert REVIEWER_DECISION_COLUMNS


def test_context_redaction_covers_prefixed_keys_and_multiline_secret_blocks():
    source = (
        "  ipaadmin_password: SomeAdminSecretValue\n"
        "  gateway_token: SomeGatewaySecretValue\n"
        "  aws_access_key_id: AKIA1234567890ABCDEF\n"
        "  api_credentials: | # secret document\n"
        "    username: private-user\n"
        "    password: nested-secret-value\n"
        "  next_setting: retained\n"
    )

    redacted = redact_sensitive_text(source)

    for secret in (
        "SomeAdminSecretValue",
        "SomeGatewaySecretValue",
        "AKIA1234567890ABCDEF",
        "private-user",
        "nested-secret-value",
    ):
        assert secret not in redacted
    assert "  ipaadmin_password: [REDACTED_LITERAL]" in redacted
    assert "  gateway_token: [REDACTED_LITERAL]" in redacted
    assert "  api_credentials: [REDACTED VALUE BLOCK]" in redacted
    assert "    [REDACTED ENCRYPTED VALUE]" in redacted
    assert "  next_setting: retained" in redacted

    numbered = _numbered_excerpt(
        ["before", "api_credentials: |", "  username: private-user", "  password: nested-secret-value", "after", ""],
        2,
        6,
    )
    assert "    2 | api_credentials: [REDACTED VALUE BLOCK]" in numbered
    assert "    3 |   [REDACTED ENCRYPTED VALUE]" in numbered
    assert "    4 |   [REDACTED ENCRYPTED VALUE]" in numbered
    assert "    5 | after" in numbered
    assert "    6 | " in numbered
    assert "private-user" not in numbered and "nested-secret-value" not in numbered

    private_key = (
        "before\n-----BEGIN RSA PRIVATE KEY-----\nprivate-key-material\n"
        "-----END RSA PRIVATE KEY-----\nafter\n"
    )
    redacted_key = redact_sensitive_text(private_key)
    assert "private-key-material" not in redacted_key
    assert len(redacted_key.split("\n")) == len(private_key.split("\n"))
    assert redact_sensitive_text(redacted_key) == redacted_key
