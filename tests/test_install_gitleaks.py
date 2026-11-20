import pytest


class FakeResponse:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def raise_for_status(self):
        return None

    def iter_content(self, chunk_size):
        yield self.payload


def test_installer_rejects_archive_that_does_not_match_pinned_hash(
    tmp_path, monkeypatch
):
    from ansibleguard.external import install_gitleaks

    filename = "gitleaks_8.30.1_linux_x64.tar.gz"
    monkeypatch.setattr(install_gitleaks, "GITLEAKS_DIR", tmp_path)
    monkeypatch.setattr(
        install_gitleaks, "GITLEAKS_PATH", tmp_path / "gitleaks"
    )
    monkeypatch.setattr(
        install_gitleaks,
        "get_gitleaks_download_url",
        lambda: ("https://example.invalid/gitleaks", filename, "tar.gz"),
    )
    monkeypatch.setattr(
        install_gitleaks.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(b"not-the-reviewed-archive"),
    )

    with pytest.raises(RuntimeError, match="checksum mismatch"):
        install_gitleaks.download_and_install_gitleaks()

    assert not (tmp_path / filename).exists()
