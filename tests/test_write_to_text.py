import json
from ansibleguard.report.text_writer import (
    write_GitLeaks_results_to_txt,
    write_unused_vars_to_txt,
    write_duplicates_to_txt,
    write_results_to_txt,
)


def test_global_tasks_section_has_a_clear_header(tmp_path):
    """Regression test: tasks outside any play used to be printed with no
    header at all — visually indistinguishable from belonging to whatever
    play happened to print immediately before them in the report."""
    out_path = tmp_path / "out.txt"
    all_results = {
        "/fake/path.yml": {
            "playbook": {
                "plays": [
                    {
                        "exist_play": 0,
                        "play_name": "Global",
                        "metrics": {},
                        "tasks": [{"task_name": "a stray task", "metrics": {}}],
                    }
                ]
            }
        }
    }
    write_results_to_txt(all_results, str(out_path))
    content = out_path.read_text()
    assert "Tasks outside any play (Global):" in content


def test_gitleaks_writer_produces_valid_json(tmp_path):
    out_path = tmp_path / "gitleaks.json"
    findings = [{"rule": "aws-key", "file": "x.yml"}]
    write_GitLeaks_results_to_txt(findings, str(out_path))
    with open(out_path) as f:
        data = json.load(f)
    assert data == findings


def test_unused_vars_empty_case(tmp_path):
    out_path = tmp_path / "vars.txt"
    write_unused_vars_to_txt([], str(out_path))
    assert "No unnecessary dependencies found." in out_path.read_text()


def test_unused_vars_with_warnings(tmp_path):
    out_path = tmp_path / "vars.txt"
    write_unused_vars_to_txt(["Warning: some var"], str(out_path))
    assert "Warning: some var" in out_path.read_text()


def test_duplicates_writer_append_mode_preserves_prior_content(tmp_path):
    """Documents a real fragility, not a bug: write_duplicates_to_txt
    (and write_results_to_txt) open their target file in append mode
    ('a'), not write mode ('w'). This is by design — the real pipeline
    calls multiple writers against the same Play_Level_Analysis.txt in
    sequence, each appending its own section. But it means correctness
    depends on an UNSTATED call order: whichever writer runs first must
    use 'w' to start the file fresh, and every writer after it must use
    'a'. This test locks in that append behavior is real and intentional,
    so a future refactor can't silently change it without this test
    catching the shift."""
    out_path = tmp_path / "out.txt"
    out_path.write_text("PRE-EXISTING CONTENT\n")
    write_duplicates_to_txt([], str(out_path))
    content = out_path.read_text()
    assert "PRE-EXISTING CONTENT" in content
    assert "No duplicate keys found." in content
