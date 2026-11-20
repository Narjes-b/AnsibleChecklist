from ansibleguard.detectors.overriding_facts import overriding_facts


def test_conflicting_fact_values_detected(fixtures_dir):
    """Same fact name (environment_type), two different values set
    elsewhere in the file — this is the actual smell being detected."""
    fixture = fixtures_dir / "overriding_facts_conflict.yml"
    assert overriding_facts(str(fixture)) == 1


def test_different_fact_names_not_flagged(fixtures_dir):
    """Two different fact names, no actual override — must not
    false-positive."""
    fixture = fixtures_dir / "overriding_facts_none.yml"
    assert overriding_facts(str(fixture)) == 0


def test_vault_encrypted_file_does_not_crash(fixtures_dir):
    """A vault-encrypted file parses as a plain string, not a dict/list.
    find_facts_in_data()'s isinstance checks correctly fall through with
    no match, so this returns 0 rather than crashing."""
    fixture = fixtures_dir / "vault_encrypted_full.yml"
    assert overriding_facts(str(fixture)) == 0


def test_same_fact_in_separate_plays_is_not_cross_play_override(tmp_path):
    playbook = tmp_path / "plays.yml"
    playbook.write_text(
        "- hosts: staging\n"
        "  tasks:\n"
        "    - set_fact: {environment_type: staging}\n"
        "- hosts: production\n"
        "  tasks:\n"
        "    - set_fact: {environment_type: production}\n",
        encoding="utf-8",
    )

    assert overriding_facts(playbook) == 0


def test_templated_fact_reassignment_is_uncertain_not_override(tmp_path):
    playbook = tmp_path / "templated.yml"
    playbook.write_text(
        "- hosts: all\n"
        "  tasks:\n"
        "    - set_fact:\n"
        "        environment_type: '{{ requested_environment }}'\n"
        "    - set_fact:\n"
        "        environment_type: '{{ detected_environment }}'\n",
        encoding="utf-8",
    )

    assert overriding_facts(playbook) == 0


def test_fqcn_set_fact_conflict_is_detected(tmp_path):
    playbook = tmp_path / "fqcn.yml"
    playbook.write_text(
        "- ansible.builtin.set_fact: {environment_type: staging}\n"
        "- ansible.builtin.set_fact: {environment_type: production}\n",
        encoding="utf-8",
    )

    assert overriding_facts(playbook) == 1


def test_set_fact_cacheable_option_is_not_a_fact(tmp_path):
    playbook = tmp_path / "cacheable.yml"
    playbook.write_text(
        "- set_fact: {cacheable: true, environment_type: staging}\n"
        "- set_fact: {cacheable: false, environment_type: staging}\n",
        encoding="utf-8",
    )

    assert overriding_facts(playbook) == 0
