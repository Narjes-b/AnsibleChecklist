from ansibleguard.parser import mainn
from ansibleguard.detectors.high_coupling import high_coupling


def test_mainn_handles_vars_file_gracefully(fixtures_dir):
    """Real-world regression test: a genuine Ansible vars file (flat dict,
    no hosts:/tasks: anywhere) must never crash the full pipeline, even
    though every prior test used either a list-shaped playbook or a
    vault-encrypted STRING. This is the first test against a legitimately
    parsed, populated DICT — confirmed against a real file from a
    downloaded OpenStack-style project structure."""
    fixture = fixtures_dir / "vars_file_not_a_playbook.yml"
    result = mainn(str(fixture))
    # Vars files are valid YAML, but they are not playbooks/task files.
    # The classifier now deliberately keeps them out of structural detectors;
    # content-only scanners such as gitleaks still run at the CLI layer.
    assert result is None


def test_high_coupling_returns_none_for_dict_shaped_yaml(fixtures_dir):
    """high_coupling.py's isinstance(playbook, list) guard (added earlier
    this session to fix the vault-string bug) correctly generalizes to
    ALSO catch a genuine populated dict, not just a parsed-string edge
    case — confirmed against real content, not just an empty file."""
    fixture = fixtures_dir / "vars_file_not_a_playbook.yml"
    assert high_coupling(str(fixture)) is None
