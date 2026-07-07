from overriding_facts import overriding_facts


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
