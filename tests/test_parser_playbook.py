from ansibleguard.parser import mainn
from ansibleguard.analysis_context import build_repository_analysis_context
import pytest


def test_mainn_pairs_each_play_with_its_own_tasks(fixtures_dir):
    """End-to-end regression test for the play_id desync bug: detect_large_task.py
    and detect_large_play.py used to disagree on what counts as a "play"
    boundary (whether a top-level task-with-a-block counts), silently pairing
    every real play with a DIFFERENT play's tasks throughout the pipeline.
    This fixture has two top-level task-with-block entries preceding the real
    plays — exactly the shape that used to desync the numbering."""
    fixture = fixtures_dir / "parser_playbook_main3.yml"
    result = mainn(str(fixture))

    plays_by_name = {
        p["play_metrics"]["Play_name"]: p
        for p in result["plays"]
        if p["play_metrics"] is not None
    }

    example_playbook_tasks = {
        t["task_name"] for t in plays_by_name["Example Playbook"]["task_metrics"]
    }
    assert example_playbook_tasks == {
        "Include some vars from a file (used)",
        "Include some vars from another file (unused)",
        "Use a variable from the first included file",
    }

    # play1 must have its real nested block tasks (task4/5/6), NOT the
    # block-wrapper names (Notconsideredtask3/4) and NOT another play's tasks
    play1_tasks = {t["task_name"] for t in plays_by_name["play1"]["task_metrics"]}
    assert play1_tasks == {"task4", "task5", "task6"}

    play2_tasks = {t["task_name"] for t in plays_by_name["play2"]["task_metrics"]}
    assert play2_tasks == {"task7"}

    # Global leaf tasks keep their own group; wrappers and real-play tasks
    # must not enter the measured population (declared-leaf-tasks-v2+).
    global_group = next(p for p in result["plays"] if p["play_metrics"] is None)
    global_task_names = {t["task_name"] for t in global_group["task_metrics"]}
    assert global_task_names == {"task1", "task2", "task3", "task20"}


def test_mainn_task_only_playbook_single_global_entry(fixtures_dir):
    """A role-style tasks/main.yml file (no hosts:/tasks: anywhere) must take
    the is_task_only_playbook branch: metrics_play stays None, and 'plays'
    ends up with exactly one entry covering every task in the file."""
    fixture = fixtures_dir / "parser_playbook_task_only.yml"
    result = mainn(str(fixture))

    assert len(result["plays"]) == 1
    assert result["plays"][0]["play_metrics"] is None
    task_names = {t["task_name"] for t in result["plays"][0]["task_metrics"]}
    assert task_names == {"task1", "task2"}


def test_mainn_can_skip_optional_cohesion_model(fixtures_dir, monkeypatch):
    def should_not_run(*args, **kwargs):
        raise AssertionError("cohesion model was loaded for a profile without cohesion rules")

    monkeypatch.setattr("ansibleguard.parser.calculate_similarity", should_not_run)
    monkeypatch.setattr("ansibleguard.parser.calculate_similarity_plays", should_not_run)

    result = mainn(
        str(fixtures_dir / "credentials_in_real_play.yml"),
        include_cohesion=False,
    )

    assert result["similarity"] is None
    assert result["similarityPlays"] is None


def test_detector_exception_is_isolated_and_other_evidence_survives(
    fixtures_dir, monkeypatch
):
    monkeypatch.setattr(
        "ansibleguard.parser.calculate_metrics_playbook",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    result = mainn(
        str(fixtures_dir / "credentials_in_real_play.yml"),
        include_cohesion=False,
    )

    assert result is not None
    assert result["unnamed_tasks"] >= 0
    assert result["_detector_diagnostics"] == [
        {
            "category": "INTERNAL_DETECTOR_EXCEPTION",
            "detector": "large-playbook",
            "stage": "internal-detectors",
            "exception_type": "RuntimeError",
            "message": "boom",
            "file": str(fixtures_dir / "credentials_in_real_play.yml"),
        }
    ]
    assert result["_detector_timings"]["large-playbook"] >= 0


def test_strict_detector_mode_reraises_first_exception(fixtures_dir, monkeypatch):
    monkeypatch.setattr(
        "ansibleguard.parser.calculate_metrics_playbook",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("strict boom")),
    )

    with pytest.raises(RuntimeError, match="strict boom"):
        mainn(
            str(fixtures_dir / "credentials_in_real_play.yml"),
            include_cohesion=False,
            fail_on_detector_error=True,
        )


def test_enabled_rules_skip_audited_unrelated_detector_families(
    fixtures_dir, monkeypatch
):
    def unrelated(*_args, **_kwargs):
        raise AssertionError("unrelated detector executed")

    for detector in (
        "high_coupling",
        "duplicate_code",
        "unnecessary_set_fact_details",
        "overriding_facts",
        "detect_credentials_leaking_in_log",
    ):
        monkeypatch.setattr(f"ansibleguard.parser.{detector}", unrelated)
    monkeypatch.setattr(
        "ansibleguard.parser.detect_missing_validate_certs",
        lambda *_args, **_kwargs: (1, [{"line": 1, "issue": "test"}]),
    )

    result = mainn(
        str(fixtures_dir / "credentials_in_real_play.yml"),
        enabled_rules={"missing-validate-certs"},
        include_cohesion=False,
    )

    assert result["missing_validate_certs"] == 1
    assert {
        "high-coupling",
        "duplicated-code",
        "unnecessary-set-fact",
        "overriding-facts",
        "credential-log-exposure",
    } <= set(result["_detectors_skipped"])
    assert result["_detector_service_requirements"][
        "missing-validate-certs"
    ] == ["parsed_yaml"]


def test_detector_rule_dependency_registry_uses_catalogued_rules():
    from ansibleguard.parser import DETECTOR_RULE_REQUIREMENTS
    from ansibleguard.report.findings import RULE_CATALOG

    declared = set().union(*DETECTOR_RULE_REQUIREMENTS.values())
    assert declared <= set(RULE_CATALOG)


def test_mainn_injects_repository_module_metadata(tmp_path, monkeypatch):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: Configure user\n"
        "  user:\n"
        "    password: '{{ service_password }}'\n",
        encoding="utf-8",
    )
    metadata = {"user": {"options": {"password": {"no_log": True}}}}
    context = build_repository_analysis_context(
        tmp_path, [playbook], module_metadata=metadata
    )
    observed = {}

    def credential_detector(path, module_metadata=None):
        observed["path"] = path
        observed["metadata"] = module_metadata
        return [], 0, []

    monkeypatch.setattr(
        "ansibleguard.parser.detect_credentials_leaking_in_log",
        credential_detector,
    )

    mainn(
        playbook,
        parsed_document=context.document_for(playbook),
        repository_context=context,
        enabled_rules={"credentials-leaking-in-log"},
        include_cohesion=False,
    )

    assert observed["path"] == playbook
    assert observed["metadata"] == context.module_metadata
