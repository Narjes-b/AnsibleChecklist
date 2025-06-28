import subprocess
import json

def run_ansible_lint(target_path, output_format="json"):
    """
    Run ansible-lint on a given file or directory and return parsed results.

    Args:
        target_path (str): Path to a playbook file or Ansible role directory.
        output_format (str): 'json' or 'plain'

    Returns:
        list or str: Parsed lint results or raw output.
    """
    try:
        cmd = ["ansible-lint", target_path]
        if output_format == "json":
            cmd += ["-f", "json"]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode not in (0, 2):  # 0 = no issues, 2 = lint warnings
            print("❌ Error running ansible-lint:")
            print(result.stderr)
            return []

        if output_format == "json":
            return json.loads(result.stdout)
        else:
            return result.stdout.strip()

    except Exception as e:
        print(f"Exception while running ansible-lint: {e}")
        return []
