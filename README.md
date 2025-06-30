Ongoing implementation

22 IaC smells are now detected along with Ansible lint smells: Overview at https://www.overleaf.com/2736588529tfxqwjmdkmhn#2fc7bc

To run the tool:
 - run the script 'smellsDetector.py'
 - update the necessary file paths in 'config.py'
 - install AnsibleLint from https://ansible.readthedocs.io/projects/lint/installing/#installing-the-latest-version

   
Upcoming features:
 - Snyk adaptation for Ansible to detect sensitive credentials vulnerabilities
 - wrap the tool as a Pull-request Github bot
 - support reading a whole ansible project (only 1 playbook and a folder of vars are supported for now)
