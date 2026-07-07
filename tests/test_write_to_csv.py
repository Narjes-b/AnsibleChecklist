import csv

from ansibleguard.report.csv_writer import write_results_to_csv


def test_none_incohesive_playbook_writes_blank(tmp_path):
    """Regression test: incohesive_playbook can legitimately be None
    (cohesion unmeasurable — see sem_cohesion.py's OOV fix). A naive
    .get('incohesive_playbook', '') doesn't catch this, since that
    default only applies to a MISSING key, not one present with value
    None — the CSV would have literally shown the string 'None'."""
    csv_path = tmp_path / "out.csv"
    all_results = {
        "/fake/path.yml": {
            "playbook": {"metrics": {"incohesive_playbook": None, "num_plays": 2}}
        }
    }
    write_results_to_csv(all_results, str(csv_path))
    with open(csv_path) as f:
        row = list(csv.DictReader(f))[0]
    assert row["Incohesive Playbook"] == ""


def test_zero_incohesive_playbook_not_blanked(tmp_path):
    """Confirms the None-fix didn't overcorrect: 0 is a real, legitimate
    'not incohesive' result and must render as '0', not blank. A naive
    `value or ''` would have wrongly blanked this too, since 0 is falsy
    in Python."""
    csv_path = tmp_path / "out.csv"
    all_results = {
        "/fake/path.yml": {
            "playbook": {"metrics": {"incohesive_playbook": 0, "num_plays": 2}}
        }
    }
    write_results_to_csv(all_results, str(csv_path))
    with open(csv_path) as f:
        row = list(csv.DictReader(f))[0]
    assert row["Incohesive Playbook"] == "0"
