Ongoing implementation

To run the tool:
 - run the script 'smellsDetector.py'
 - update the necessary file paths in 'config.py'
 - install AnsibleLint from https://ansible.readthedocs.io/projects/lint/installing/#installing-the-latest-version
 - run the script 'Install_GitLeaks.py' to install GitLeaks
 - to update the rules metrics thresholds: {LOC_playbook,num_plays,avg_play_size,num_tasks_playbook,avg_task_playbook,Num_Imports,Num_Roles,similarity,similarityPlays,LOC_play,num_tasks_play,avg_task_play,special_chars,LOC_task,task_name_len}
       1) In intercative terminal: run 'python edit_cli_thresholds.py --file thresholds.csv'
       2) In CLI: run 'python edit_cli_thresholds.py --file thresholds.csv --set avg_task_play=15'
       3) To put values back to defaut: run 'python edit_cli_thresholds.py --file thresholds.csv --default'

Current features:
- 22 IaC smells adapted from Puppet and EMSE checklist: Overview at https://www.overleaf.com/2736588529tfxqwjmdkmhn#2fc7bc
- All Ansible lint smells
- All GitLeaks secrets violation detection
  
Upcoming features:
 - wrap the tool as a CLI bot
 - make the tool reads a commit
 
