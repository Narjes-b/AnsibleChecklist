import os
import platform
import subprocess
import tarfile
import shutil
import requests
import json
import hashlib
from pathlib import Path

GITLEAKS_VERSION = "8.30.1"

GITLEAKS_DIR = Path.home() / ".ansibleguard" / "gitleaks-bin"
GITLEAKS_PATH = GITLEAKS_DIR / "gitleaks"
GITLEAKS_ARCHIVE_SHA256 = {
    "gitleaks_8.30.1_darwin_arm64.tar.gz": "b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5",
    "gitleaks_8.30.1_darwin_x64.tar.gz": "dfe101a4db2255fc85120ac7f3d25e4342c3c20cf749f2c20a18081af1952709",
    "gitleaks_8.30.1_linux_arm64.tar.gz": "e4a487ee7ccd7d3a7f7ec08657610aa3606637dab924210b3aee62570fb4b080",
    "gitleaks_8.30.1_linux_x64.tar.gz": "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb",
    "gitleaks_8.30.1_windows_x64.zip": "d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e",
}


def get_gitleaks_download_url(version=GITLEAKS_VERSION):
    system = platform.system().lower()
    arch = platform.machine().lower()

    if system == "darwin":
        if "arm" in arch:
            tag = "darwin_arm64"
        else:
            tag = "darwin_x64"
        ext = "tar.gz"
    elif system == "linux":
        if "arm" in arch or "aarch64" in arch:
            tag = "linux_arm64"
        else:
            tag = "linux_x64"
        ext = "tar.gz"
    elif system == "windows":
        tag = "windows_x64"
        ext = "zip"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")

    filename = f"gitleaks_{version}_{tag}.{ext}"
    url = (
        f"https://github.com/gitleaks/gitleaks/releases/download/v{version}/{filename}"
    )
    return url, filename, ext


def download_and_install_gitleaks():
    GITLEAKS_DIR.mkdir(parents=True, exist_ok=True)
    url, filename, ext = get_gitleaks_download_url()

    local_archive = GITLEAKS_DIR / filename
    print(f"[+] Downloading Gitleaks: {url}")
    with requests.get(url, stream=True) as r:
        if r.status_code != 200:
            raise RuntimeError(
                f"Failed to download gitleaks from {url} (HTTP {r.status_code}). "
                f"Check GITLEAKS_VERSION and your OS/architecture detection."
            )
        r.raise_for_status()
        with open(local_archive, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    expected = GITLEAKS_ARCHIVE_SHA256.get(filename)
    if expected is None:
        local_archive.unlink(missing_ok=True)
        raise RuntimeError(f"No pinned SHA-256 is available for {filename}.")
    actual = hashlib.sha256(local_archive.read_bytes()).hexdigest()
    if actual != expected:
        local_archive.unlink(missing_ok=True)
        raise RuntimeError(
            f"GitLeaks archive checksum mismatch for {filename}: "
            f"expected {expected}, got {actual}."
        )

    print(f"[+] Extracting {filename}...")
    if ext == "tar.gz":
        with tarfile.open(local_archive, "r:gz") as tar:
            root = GITLEAKS_DIR.resolve()
            for member in tar.getmembers():
                destination = (GITLEAKS_DIR / member.name).resolve()
                try:
                    destination.relative_to(root)
                except ValueError as exc:
                    raise RuntimeError(
                        f"Unsafe path in GitLeaks archive: {member.name}"
                    ) from exc
                if member.issym() or member.islnk():
                    raise RuntimeError(
                        f"Links are not allowed in GitLeaks archive: {member.name}"
                    )
            tar.extractall(path=GITLEAKS_DIR)
    elif ext == "zip":
        import zipfile

        with zipfile.ZipFile(local_archive, "r") as zip_ref:
            root = GITLEAKS_DIR.resolve()
            for member in zip_ref.infolist():
                destination = (GITLEAKS_DIR / member.filename).resolve()
                try:
                    destination.relative_to(root)
                except ValueError as exc:
                    raise RuntimeError(
                        f"Unsafe path in GitLeaks archive: {member.filename}"
                    ) from exc
            zip_ref.extractall(GITLEAKS_DIR)
    else:
        raise RuntimeError("Unsupported archive type")

    local_archive.unlink()
    GITLEAKS_PATH.chmod(0o755)
    print(f"[ok] Gitleaks installed at: {GITLEAKS_PATH}")


def ensure_gitleaks_installed():
    if not GITLEAKS_PATH.exists():
        download_and_install_gitleaks()


# Example usage
if __name__ == "__main__":
    ensure_gitleaks_installed()
    # findings = scan_ansible_playbook("example_playbook.yml")
    # for f in findings:
    #   print(f"{f['rule']} in {f['file']} at line {f['line']}")
