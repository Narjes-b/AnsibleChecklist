from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]


def test_research_requirements_are_clean_utf8():
    raw = (ROOT / "requirements.txt").read_bytes()
    text = raw.decode("utf-8")

    assert not raw.startswith((b"\xff\xfe", b"\xfe\xff", b"\xef\xbb\xbf"))
    assert "\x00" not in text
    assert "\r" not in text
    assert "ruamel.yaml==0.19.1" in text.splitlines()


def test_research_docker_builds_in_ci():
    dockerfile = (ROOT / "Dockerfile.research").read_text(encoding="utf-8")
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(
        encoding="utf-8"
    )

    assert "iconv" not in dockerfile
    assert "pip install --no-cache-dir -r requirements.txt" in dockerfile
    assert "docker build" in workflow
    assert "--build-arg ANSIBLEGUARD_BUILD_GIT_SHA" in workflow
    assert "-f Dockerfile.research" in workflow


def test_v004_release_checksums_verify():
    completed = subprocess.run(
        ["sha256sum", "--check", "checksums.sha256"],
        cwd=ROOT / "study" / "releases" / "v004",
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
