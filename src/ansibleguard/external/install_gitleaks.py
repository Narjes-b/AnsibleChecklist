import os
import platform
import subprocess
import tarfile
import shutil
import requests
import json
from pathlib import Path

GITLEAKS_VERSION = "8.30.1"

GITLEAKS_DIR = Path.home() / ".ansibleguard" / "gitleaks-bin"
GITLEAKS_PATH = GITLEAKS_DIR / "gitleaks"


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

    print(f"[+] Extracting {filename}...")
    if ext == "tar.gz":
        with tarfile.open(local_archive, "r:gz") as tar:
            tar.extractall(path=GITLEAKS_DIR)
    elif ext == "zip":
        import zipfile

        with zipfile.ZipFile(local_archive, "r") as zip_ref:
            zip_ref.extractall(GITLEAKS_DIR)
    else:
        raise RuntimeError("Unsupported archive type")

    os.remove(local_archive)
    GITLEAKS_PATH.chmod(0o755)
    print(f"[✓] Gitleaks installed at: {GITLEAKS_PATH}")


def ensure_gitleaks_installed():
    if not GITLEAKS_PATH.exists():
        download_and_install_gitleaks()


# Example usage
if __name__ == "__main__":
    ensure_gitleaks_installed()
    # findings = scan_ansible_playbook("example_playbook.yml")
    # for f in findings:
    #   print(f"🔒 {f['rule']} in {f['file']} at line {f['line']}")
