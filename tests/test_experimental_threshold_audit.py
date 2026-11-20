from scripts.audit_experimental_thresholds import audit_paths


def test_threshold_audit_reports_monotonic_candidate_rates(tmp_path):
    source = tmp_path / "site.yml"
    source.write_text(
        "- name: Audit\n  hosts: all\n  tasks:\n"
        + "".join(
            f"    - name: Import {index}\n      include_tasks: task_{index}.yml\n"
            for index in range(7)
        )
        + "    - name: Complex condition\n      debug: {msg: ok}\n"
        "      when: a and b or c and d\n",
        encoding="utf-8",
    )

    result = audit_paths([source])

    assert result["high_coupling"] == {"4": 1, "6": 1, "8": 0}
    assert result["undocumented_complex_task"] == {"3": 1, "4": 0, "5": 0}
    assert result["not_applicable_or_unreadable_files"] == 0
