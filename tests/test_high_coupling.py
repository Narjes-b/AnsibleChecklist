from high_coupling import high_coupling


def test_singular_role_does_not_crash(fixtures_dir):
    """Regression test: 'role:' (singular) with no matching 'roles:' key
    used to raise KeyError, since the old code checked
    'roles' in play or 'role' in play but always indexed play['roles']."""
    fixture = fixtures_dir / "high_coupling_singular_role.yml"
    result = high_coupling(str(fixture))
    assert result is not None
    assert result["Num_Roles"] == 0


def test_dict_style_roles_counted_correctly(fixtures_dir):
    """Confirms roles: [{role: x, vars: {...}}, {role: y}] counts as 2 —
    this was suspected broken but testing showed len(roles) already
    handled dicts fine regardless of item type."""
    fixture = fixtures_dir / "high_coupling_dict_style_roles.yml"
    result = high_coupling(str(fixture))
    assert result["Num_Roles"] == 2


def test_nested_import_tasks_detected(fixtures_dir):
    """Regression test for the real detection gap: import_tasks/
    include_tasks nested inside a play's tasks: list (the common real-world
    form) used to be invisible — only a bare top-level import_tasks: was
    ever caught."""
    fixture = fixtures_dir / "high_coupling_nested_import_tasks.yml"
    result = high_coupling(str(fixture))
    assert result["Num_Imports"] == 2


def test_fully_vault_encrypted_file_returns_none(fixtures_dir):
    """Regression test: a fully vault-encrypted file parses via
    yaml.safe_load() as a plain string (not a list, not an error). The old
    code had no type guard, so 'for play in playbook:' silently iterated
    the string character by character and confidently returned all-zero
    results for a file it never actually read."""
    fixture = fixtures_dir / "high_coupling_full_vault.yml"
    result = high_coupling(str(fixture))
    assert result is None
