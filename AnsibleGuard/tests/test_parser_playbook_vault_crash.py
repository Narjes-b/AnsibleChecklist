from parser_playbook import mainn


def test_mainn_handles_inline_vault_tag_gracefully(fixtures_dir):
    """Regression test found via real-world testing: a genuine file from a
    downloaded Ansible project (env_vars/dev.yml) containing an inline
    !vault | tag crashed mainn() directly with yaml.ConstructorError, since
    mainn()'s own top-level yaml.safe_load() call had no try/except at all
    -- unlike every individual detector it calls, which already handles
    this correctly. Only smellsDetector.py's outer try/except was masking
    this in production; calling mainn() more directly (as a future CLI
    will) crashed immediately."""
    fixture = fixtures_dir / "inline_vault_tag.yml"
    result = mainn(str(fixture))
    assert result is None
