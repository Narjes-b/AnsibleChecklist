from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # .../AnsibleChecklist/AnsibleGuard
PROJECT_ROOT = BASE_DIR.parent  # .../AnsibleChecklist  <-- was missing

## ---------------------------------------------------------------
## Analysis fixtures (test/sample data shipped with the repo)
## ---------------------------------------------------------------
TEST_PLAYBOOK = PROJECT_ROOT / "TestData" / "tasks" / "main.yml"
THRESHOLDS_FILE = (
    BASE_DIR / "thresholds.csv"
)  # correct as-is, lives inside AnsibleGuard/

# Used as the default single-file analysis target in parser_playbook.py's __main__.
yaml_file_path = (
    PROJECT_ROOT
    / "TestData"
    / "projects"
    / "adriagalin"
    / "ansible.motd"
    / "adriagalin"  # yes, this repeats — confirmed against the real tree
    / "ansible.motd"
    / "tasks"
    / "main.yml"
)

# No matching sample data exists in the tree yet — leave as None until you add a fixture.
varsfiles_folder = None

# Folder of .yml/.yaml files smellsDetector.py iterates over in batch mode.
yaml_files_folder = PROJECT_ROOT / "TestData" / "tasks"

## ---------------------------------------------------------------
## Results files (output — created automatically if missing)
## ---------------------------------------------------------------
RESULTS_DIR = PROJECT_ROOT / "TestData" / "Results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

csvfile = RESULTS_DIR / "IaC_Smells.csv"
textfile = RESULTS_DIR / "Play_Level_Analysis.txt"
Ansiblelintfile = RESULTS_DIR / "AnsibleLint_Analysis.txt"
Gitleaksfile = RESULTS_DIR / "GitLeaks_Analysis.json"
JSONfile = RESULTS_DIR / "Technical_Analysis.json"
