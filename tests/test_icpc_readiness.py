import csv
import json
from pathlib import Path

import pytest

from scripts import icpc_llm_evaluation as evaluation
from scripts.pr_replay_study import load_frozen_pull_requests
from ansibleguard.report import llm_explain as llm
from ansibleguard.report.llm_runtime import write_checkpoint


def test_controlled_panels_are_disjoint_and_cover_four_families():
    dev, held = evaluation.controlled_cases("development"), evaluation.controlled_cases("evaluation")
    assert len(dev) == len(held) == 24
    assert not {case["case_id"] for case in dev} & {case["case_id"] for case in held}
    assert all(sum(case["family"] == rule for case in dev) == 6 for rule in evaluation.RULES)
    assert all(not case["eligible_for_population_scoring"] for case in dev + held)


@pytest.mark.parametrize("case", evaluation.controlled_cases("development") + evaluation.controlled_cases("evaluation"),
                         ids=lambda case: case["case_id"])
def test_controlled_case_evidence_contract_matches_declared_mechanism(tmp_path, case):
    from ansibleguard.report.llm_evidence import build_packet
    from ansibleguard.symbol_index import build_repository_symbol_index
    for name, content in case["files"].items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    packet = build_packet(case["occurrence"], case["files"]["tasks.yml"].splitlines(),
        lambda file: (tmp_path / file).read_text().splitlines(), lambda: build_repository_symbol_index(tmp_path))
    assert packet["unit"] is not None
    if case["engineering_expectation"] == "insufficient-evidence":
        assert packet["missing"]
    else:
        assert packet["complete"], packet["missing"]
        if packet["condition_hint"]:
            assert packet["condition_hint"] == case["engineering_expectation"]


def test_preparation_keeps_review_forms_blank_and_does_not_replace_existing_output(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluation, "real_cases", lambda root: ([], [{"exclusion": "fixture"}]))
    output = tmp_path / "evaluation"
    manifest = evaluation.prepare(tmp_path, output)
    assert not manifest["evaluation_complete"] and manifest["human_review"] == "pending"
    assert manifest["cases_sha256"] == evaluation.digest([manifest["development"], manifest["evaluation"]])
    for reviewer in ("A", "B"):
        with (output / f"reviewer-{reviewer}.csv").open() as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == 24 and all(not row["condition"] for row in rows)
    with pytest.raises(FileExistsError):
        evaluation.prepare(tmp_path, output)


def test_evaluation_rejects_missing_model_without_downloading_or_creating_output(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluation, "real_cases", lambda root: ([], []))
    evaluation.prepare(tmp_path, tmp_path / "cases")
    monkeypatch.setattr(llm.llm_runtime, "model_identity", lambda *a, **k: None)
    with pytest.raises(ValueError, match="never downloads"):
        evaluation.run(tmp_path / "cases/cases.json", tmp_path / "outputs", "development", 1, 1)
    assert not (tmp_path / "outputs").exists()


def test_checkpoint_retains_failed_attempt_when_later_attempt_succeeds(tmp_path):
    for status in ("error", "ok"):
        write_checkpoint(tmp_path, "same-key", {"key": "same-key", "result": {"llm_status": status}})
    history = [json.loads(path.read_text()) for path in (tmp_path / "history").glob("*.json")]
    assert {row["result"]["llm_status"] for row in history} == {"error", "ok"}
    assert json.loads((tmp_path / "same-key.json").read_text())["result"]["llm_status"] == "ok"


def frozen_manifest(tmp_path, repository="owner/repo", sha="a" * 40, split="calibration"):
    folder = tmp_path / "study/validation-v007-human/splits"
    folder.mkdir(parents=True)
    (folder / "repository-split.csv").write_text(f"repository,split\n{repository},{split}\n")
    path = tmp_path / "prs.csv"
    path.write_text("repository,merge_sha,base_sha,files_changed,ansible_yaml_changed\n"
                    f"{repository},{sha},{'b' * 40},2,1\n")
    return path


def test_frozen_pr_loading_keeps_exact_pairs(tmp_path):
    path = frozen_manifest(tmp_path)
    selected, ledger = load_frozen_pull_requests(path, tmp_path)
    assert selected[0]["merge_sha"] == "a" * 40 and selected[0]["base_sha"] == "b" * 40
    assert "frozen pair" in ledger[0]["reason"]


@pytest.mark.parametrize("kwargs", [{"repository": "../repo"}, {"sha": "main"}, {"split": "heldout"}])
def test_frozen_pr_loading_rejects_unsafe_mutable_or_ineligible_inputs(tmp_path, kwargs):
    path = frozen_manifest(tmp_path, **kwargs)
    with pytest.raises(ValueError):
        load_frozen_pull_requests(path, tmp_path)
