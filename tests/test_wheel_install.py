import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def test_wheel_exposes_schema_and_writes_output_artifact_outside_checkout(tmp_path):
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            str(ROOT),
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir",
            str(wheelhouse),
        ],
        check=True,
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    wheel = next(wheelhouse.glob("ansibleguard-*.whl"))
    environment = tmp_path / "environment"
    subprocess.run(
        [sys.executable, "-m", "venv", "--system-site-packages", str(environment)],
        check=True,
        capture_output=True,
        text=True,
    )
    python = environment / "bin" / "python"
    subprocess.run(
        [python, "-m", "pip", "install", "--no-deps", str(wheel)],
        check=True,
        capture_output=True,
        text=True,
    )
    outside = tmp_path / "outside-checkout"
    outside.mkdir()
    clean_environment = os.environ.copy()
    clean_environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [
            python,
            "-c",
            "from pathlib import Path; "
            "from ansibleguard.report.output_contract import "
            "load_contract_schema, write_contract_schema; "
            "schema = load_contract_schema(); "
            "target = write_contract_schema(Path('scan-output')); "
            "assert schema['$id'] == 'ansibleguard://schemas/output-v3.json'; "
            "assert target.is_file(); "
            "print(target)",
        ],
        check=True,
        cwd=outside,
        env=clean_environment,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "scan-output/schemas/output-v3.json"
