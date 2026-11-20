import copy
import csv
import json
from pathlib import Path

import pytest
import yaml

from scripts import llm_quality_study as study
from scripts import llm_participant_study as participants
from scripts.llm_behavior_checks import bounded_task


@pytest.fixture
def package(tmp_path, monkeypatch):
    original_load = study.load
    dev = study.base.controlled_cases("development")
    held = study.base.controlled_cases("evaluation")[:2]
    original = {"development": dev, "evaluation": held, "cases_sha256": study.digest([dev, held])}
    monkeypatch.setattr(study, "load", lambda p: original if str(p).endswith("evaluation/cases.json") else original_load(p))
    target = tmp_path / "package"
    study.prepare(target)
    monkeypatch.setattr(study, "implementation", lambda: {"fixture": "frozen"})
    monkeypatch.setattr(study.llm.llm_runtime, "model_identity", lambda *a, **k: "model-digest")
    frozen = {"manifest_sha256": study.read_package(target)["sha256"], "implementation": study.implementation(),
              "model_digest": "model-digest", "instrument_hashes": {},
              "assignments_sha256": __import__("hashlib").sha256((target / "assignments-private.json").read_bytes()).hexdigest()}
    frozen["sha256"] = study.digest(frozen)
    study.save(target / "freeze.json", frozen)
    return target


def complete_sources(package, ids=None):
    for name in ("source-reviewer-A.csv", "source-reviewer-B.csv", "source-adjudication.csv"):
        with (package / name).open() as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        for row in rows:
            if ids is None or row["case_id"] in ids:
                row.update(condition="supported", evidence_sufficient="yes", actionability="actionable",
                           acceptable_change="bounded edit", condition_rubric="literal predicate", evidence_rubric="cite lines",
                           action_rubric="bounded justified action", notes="Independent fixture judgment")
        study.table(package / name, fields, rows)


def run_fake(package, tmp_path, monkeypatch, panel="explanation"):
    monkeypatch.setattr(study.llm, "explain_occurrence", lambda *a, **k:
                        {"llm_status": "ok", "llm_assessment": "supported"})
    output = tmp_path / (panel + "-run")
    study.run(package, output, panel)
    return output


def test_prepare_blank_forms_original_preserved_and_safe_repeated_output(package):
    for name in ("source-reviewer-A.csv", "source-reviewer-B.csv", "source-adjudication.csv"):
        with (package / name).open() as stream:
            rows = list(csv.DictReader(stream))
        assert all(not row["condition"] and not row["notes"] for row in rows)
    assert len(study.read_package(package)["panels"]["repair"]) == 12
    assert not any("engineering_expectation" in p.read_text() for p in (package / "source-review").glob("*.json"))
    with pytest.raises(FileExistsError):
        study.prepare(package)


def test_schedule_balances_order_and_covers_every_pair_once():
    cases = study.base.controlled_cases("evaluation")
    schedule = study.schedule(cases, True)
    assert len(schedule) == 48
    assert len({(c["case_id"], mode) for c, mode in schedule}) == 48
    assert sum(schedule[i][1] == "window" for i in range(0, 48, 2)) == 12
    assert [(c["case_id"], m) for c, m in schedule] == [(c["case_id"], m) for c, m in study.schedule(cases, True)]


def test_participant_schedules_no_repetition_balanced_arms_and_task_exposure(package):
    schedules = study.load(package / "assignments-private.json")
    for assignment in schedules:
        assert len({t["case_id"] for t in assignment["tasks"]}) == 12
        assert all(sum(t["arm"] == a for t in assignment["tasks"]) == 4 for a in study.ARMS)
    for block in range(3):
        tasks = [t for a in schedules[block * 6:(block + 1) * 6] for t in a["tasks"]]
        for case_id in {t["case_id"] for t in tasks}:
            assert all(sum(t["case_id"] == case_id and t["arm"] == arm for t in tasks) == 2 for arm in study.ARMS)


@pytest.mark.parametrize("panel", ["repair", "comprehension"])
def test_human_source_gate_before_repair_and_participant_inference(package, tmp_path, monkeypatch, panel):
    with pytest.raises(ValueError, match="incomplete"):
        study.run(package, tmp_path / "run", panel)
    assert not (tmp_path / "run").exists()


def test_freeze_or_model_drift_rejected_before_inference(package, tmp_path, monkeypatch):
    monkeypatch.setattr(study, "implementation", lambda: {"fixture": "changed"})
    with pytest.raises(ValueError, match="changed"):
        study.run(package, tmp_path / "run", "explanation")


def test_recorded_failure_retained_on_resume(package, tmp_path, monkeypatch):
    calls = []
    def fail(*args, **kwargs):
        calls.append(1)
        return {"llm_status": "error", "llm_error": "fixture failure"}
    monkeypatch.setattr(study.llm, "explain_occurrence", fail)
    output = tmp_path / "run"
    study.run(package, output, "explanation")
    assert len(calls) == 4
    study.run(package, output, "explanation", resume=True)
    assert len(calls) == 4
    _, records = study.records_for(package, output)
    assert all(r["result"]["llm_status"] == "error" for r in records)


def test_interrupted_unknown_outcome_not_retried(package, tmp_path, monkeypatch):
    output = tmp_path / "run"
    calls = []
    def interrupted(*a, **k):
        calls.append(1)
        raise KeyboardInterrupt()
    monkeypatch.setattr(study.llm, "explain_occurrence", interrupted)
    with pytest.raises(KeyboardInterrupt):
        study.run(package, output, "explanation")
    monkeypatch.setattr(study.llm, "explain_occurrence", lambda *a, **k: {"llm_status": "ok"})
    study.run(package, output, "explanation", resume=True)
    _, records = study.records_for(package, output)
    assert sum(r["result"]["llm_status"] == "interrupted-unknown" for r in records) == 1


def test_output_export_waits_for_independent_source_review(package, tmp_path, monkeypatch):
    run = run_fake(package, tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="incomplete"):
        study.export_review(package, run, tmp_path / "review")
    complete_sources(package)
    study.export_review(package, run, tmp_path / "review")
    packet = study.load(tmp_path / "review/packets/O001.json")
    assert "mode" not in packet and "engineering_expectation" not in json.dumps(packet)


def test_quality_analysis_hand_calculated_all_scheduled_denominator(package, tmp_path, monkeypatch):
    run = run_fake(package, tmp_path, monkeypatch)
    complete_sources(package)
    review = tmp_path / "review"
    study.export_review(package, run, review)
    mapping = study.load(review / "mapping-private.json")
    for name in ("reviewer-A", "reviewer-B", "adjudication"):
        rows = []
        for entry in mapping:
            correct = entry["mode"] == "scoped"
            rows.append({"output_id": entry["output_id"], "factually_correct": "yes" if correct else "no",
                "evidence_supported": "yes", "contradiction": "no", "assessment_correct": "yes",
                "uncertainty_appropriate": "yes", "fix_judgment": "not-proposed", "notes": "fixture adjudication"})
        study.table(review / f"{name}.csv", rows[0].keys(), rows)
    study.quality_summary(package, run, review, tmp_path / "summary.json")
    summary = study.load(tmp_path / "summary.json")
    assert summary["groups"]["all/scoped"]["success_rate"] == 1
    assert summary["groups"]["all/window"]["success_rate"] == 0
    assert summary["paired_counts"] == {"window=False,scoped=True": 2}
    assert summary["reviewer_agreement"]["factually_correct"] == 1
    assert summary["fix_judgments"] == {"not-proposed": 4}


def test_blank_output_adjudication_refused(package, tmp_path, monkeypatch):
    run = run_fake(package, tmp_path, monkeypatch)
    complete_sources(package)
    study.export_review(package, run, tmp_path / "review")
    with pytest.raises(ValueError, match="incomplete"):
        study.quality_summary(package, run, tmp_path / "review", tmp_path / "summary.json")


def test_failed_outputs_remain_in_primary_denominator(package, tmp_path, monkeypatch):
    monkeypatch.setattr(study.llm, "explain_occurrence", lambda *a, **k: {"llm_status": "error", "llm_error": "timeout fixture"})
    run = tmp_path / "run"
    study.run(package, run, "explanation")
    complete_sources(package)
    review = tmp_path / "review"
    study.export_review(package, run, review)
    mapping = study.load(review / "mapping-private.json")
    rows = [{"output_id": m["output_id"], "factually_correct": "not-assessable", "evidence_supported": "not-assessable",
             "contradiction": "not-assessable", "assessment_correct": "not-assessable", "uncertainty_appropriate": "not-assessable",
             "fix_judgment": "not-proposed", "notes": "Unavailable output, retained failure"} for m in mapping]
    for name in ("reviewer-A", "reviewer-B", "adjudication"):
        study.table(review / f"{name}.csv", rows[0].keys(), rows)
    study.quality_summary(package, run, review, tmp_path / "summary.json")
    summary = study.load(tmp_path / "summary.json")
    assert summary["groups"]["all/scoped"]["scheduled"] == 2
    assert summary["groups"]["all/scoped"]["success_rate"] == 0
    assert summary["groups"]["all/scoped"]["failures"] == 2


def test_duplicate_csv_key_refused(tmp_path):
    path = tmp_path / "duplicate.csv"
    path.write_text("case_id,condition\na,supported\na,unsupported\n")
    with pytest.raises(ValueError, match="duplicate"):
        study.keyed_rows(path, ("case_id",))


@pytest.mark.parametrize("family", ["missing-validate-certs", "credential-log-exposure"])
def test_behavior_boundary_accepts_only_supported_edit(family):
    case = next(c for c in study.repair_cases() if c["family"] == family)
    before = case["files"]["tasks.yml"]
    task = yaml.safe_load(before)[0]
    if family == "missing-validate-certs":
        task["ansible.builtin.get_url"]["validate_certs"] = True
    else:
        task["no_log"] = True
    after = yaml.safe_dump([task], sort_keys=False)
    bounded_task(before, after, family)
    task["ansible.builtin.shell"] = "echo unexpected"
    with pytest.raises(ValueError, match="boundary"):
        bounded_task(before, yaml.safe_dump([task]), family)


def test_tls_fixture_rejects_external_endpoint():
    case = study.repair_cases()[0]
    before = case["files"]["tasks.yml"].replace("localhost:4443", "external.invalid")
    after = before.replace("validate_certs: false", "validate_certs: true")
    with pytest.raises(ValueError, match="TLS fixture"):
        bounded_task(before, after, case["family"])


def response_fixture(package):
    assignment = study.load(package / "assignments-private.json")[0]
    return {"participant_id": "P01", "manifest_sha256": study.read_package(package)["sha256"],
            "freeze_sha256": study.load(package / "freeze.json")["sha256"], "consent_version": "1",
            "consented_at": "2026-11-14T10:00:00Z", "experience_years": 2,
            "answers": [{"case_id": t["case_id"], "condition": "fixture", "evidence": "line 1", "action": "review",
                         "confidence": 3, "elapsed_seconds": 40, "timeout": False} for t in assignment["tasks"]]}


@pytest.mark.parametrize("problem", ["duplicate-task", "missing-task", "negative-time", "nan-time", "missing-consent", "wrong-hash", "false-timeout"])
def test_participant_import_rejects_invalid_responses(package, tmp_path, problem):
    payload = response_fixture(package)
    if problem == "duplicate-task":
        payload["answers"][1] = payload["answers"][0]
    elif problem == "missing-task":
        payload["answers"].pop()
    elif problem == "negative-time":
        payload["answers"][0]["elapsed_seconds"] = -1
    elif problem == "nan-time":
        payload["answers"][0]["elapsed_seconds"] = float("nan")
    elif problem == "missing-consent":
        payload["consented_at"] = ""
    elif problem == "wrong-hash":
        payload["manifest_sha256"] = "changed"
    else:
        payload["answers"][0]["timeout"] = True
    path = tmp_path / "responses.json"
    study.save(path, payload)
    with pytest.raises(ValueError):
        participants.import_responses(package, [path], tmp_path / "import")


def test_participant_duplicate_and_blinded_grading(package, tmp_path):
    path = tmp_path / "responses.json"
    study.save(path, response_fixture(package))
    with pytest.raises(ValueError, match="duplicate participant"):
        participants.import_responses(package, [path, path], tmp_path / "bad")
    result = participants.import_responses(package, [path], tmp_path / "import")
    assert result["responses"] == 12
    packet = study.load(tmp_path / "import/grading-packets/G0001.json")
    assert "arm" not in packet and "participant_id" not in packet and "elapsed_seconds" not in packet


def test_recruitment_gate_blocks_unapproved_pages(package, tmp_path):
    with pytest.raises(ValueError, match="institutional"):
        participants.pages(package, tmp_path / "unused", tmp_path / "pages")


def test_partial_sessions_are_explicitly_preserved_not_scored_as_completions(package, tmp_path):
    payload = response_fixture(package)
    payload["answers"] = payload["answers"][:3]
    path = tmp_path / "partial.json"
    study.save(path, payload)
    result = participants.import_responses(package, [path], tmp_path / "import", allow_partial=True)
    assert result["complete_sessions"] == 0 and result["partial_sessions"] == 1
    assert study.load(tmp_path / "import/responses-private.json") == []
    assert len(study.load(tmp_path / "import/partial-sessions-private.json")[0]["answers"]) == 3


def test_real_source_hash_mismatch_rejected_before_use(tmp_path, monkeypatch):
    root = tmp_path / "owner/repo"
    root.mkdir(parents=True)
    (root / "tasks.yml").write_text("- name: changed\n")
    monkeypatch.setattr(study.base, "git", lambda root, *args: "commit" if args[0] == "rev-parse" else "")
    case = {"case_id": "real-fixture", "kind": "real", "repository": "owner/repo", "sha": "commit",
            "source_sha256": "old-source-hash", "occurrence": {"file": "tasks.yml"}}
    with pytest.raises(ValueError, match="source mismatch"):
        with study.case_root(case, tmp_path):
            pytest.fail("must reject before yielding source")


def test_participant_grading_hand_calculated_and_blank_grades_rejected(package, tmp_path):
    complete_sources(package)
    path = tmp_path / "responses.json"
    study.save(path, response_fixture(package))
    output = tmp_path / "import"
    participants.import_responses(package, [path], output)
    with pytest.raises(ValueError, match="incomplete"):
        participants.summarize(package, output, output, tmp_path / "bad.json")
    mapping = study.load(output / "grading-mapping-private.json")
    rows = [{"response_id": m["response_id"], "condition_score": "1", "evidence_score": "0",
             "action_score": "1", "harmful_decision": "no", "notes": "Fixture grade, not participant data"} for m in mapping]
    for name in ("grader-A", "grader-B", "adjudication"):
        study.table(output / f"{name}.csv", rows[0].keys(), rows)
    participants.summarize(package, output, output, tmp_path / "summary.json")
    summary = study.load(tmp_path / "summary.json")
    assert summary["status"] == "feasibility-only" and summary["participants"] == 1
    assert all(group["mean_score_out_of_3"] == 2 for group in summary["groups"].values())
    assert summary["participant_differences"][0]["score_difference_llm_minus_evidence"] == 0
