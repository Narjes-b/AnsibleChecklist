# Frozen source context: V007PILOT-SECURITY-043

- Repository: `ansible/instruqt`
- Commit: `e23435acd50f1f645c88958c8dee4fe2929014b6`
- Family: Security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `images/ansible/devops-controller-setup.yml` (reported anchor line 548)
- Object: `source_location` `59867d7b8fc597eccc9d2ab766b52ff80679e306b140dd89ba6b2b98a496c608`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 513–583 of 831:

```text
  513 |           loop:
  514 |             - absent
  515 |             - directory
  516 | 
  517 |         - name: Extract initial repo files
  518 |           ansible.builtin.unarchive:
  519 |             src: "/opt/setup-scripts/{{ track_slug }}/files/acme_repo.tar.gz"
  520 |             dest: "~{{ student_username }}/{{ gitea_repo_name }}"
  521 |             creates: "~{{ student_username }}/{{ gitea_repo_name }}/app"
  522 |             remote_src: true
  523 |             owner: "{{ student_username }}"
  524 |             group: "{{ student_username }}"
  525 | 
  526 |         - name: Fix directory permissions - {{ gitea_repo_name }}
  527 |           ansible.builtin.file:
  528 |             path: "~{{ student_username }}/{{ gitea_repo_name }}"
  529 |             state: directory
  530 |             owner: "{{ student_username }}"
  531 |             group: "{{ student_username }}"
  532 |             mode: "755"
  533 | 
  534 |         - name: Initialise track repo - {{ gitea_repo_name }} # noqa command-instead-of-module
  535 |           ansible.builtin.command:
  536 |             cmd: /usr/bin/git init
  537 |             chdir: "~{{ student_username }}/{{ gitea_repo_name }}"
  538 |             creates: "~{{ student_username }}/{{ gitea_repo_name }}/.git"
  539 | 
  540 |         - name: Add git configurations - {{ gitea_repo_name }}
  541 |           ansible.builtin.template:
  542 |             src: gitconfig.j2
  543 |             owner: "{{ student_username }}"
  544 |             group: "{{ student_username }}"
  545 |             mode: '644'
  546 |             dest: "~{{ student_username }}/{{ gitea_repo_name }}/.git/config"
  547 | 
  548 |         - name: Store repo credentials in git-creds file
  549 |           ansible.builtin.copy:
  550 |             dest: "~{{ student_username }}/.git-creds"
  551 |             content: "{{ gitea_protocol }}://{{ student_username | urlencode }}:{{ student_password | urlencode }}@{{ gitea_hostname }}:{{ gitea_http_port }}"
  552 |             owner: "{{ student_username }}"
  553 |             group: "{{ student_username }}"
  554 |             mode: "644"
  555 | 
  556 |         - name: Push initial commit to repo
  557 |           ansible.builtin.command:
  558 |             cmd: "{{ item }}"
  559 |             chdir: "~{{ student_username }}/{{ gitea_repo_name }}"
  560 |           register: __output
  561 |           changed_when: __output.rc == 0
  562 |           loop:
  563 |             - "git checkout -b main"
  564 |             - "git add ."
  565 |             - "git commit -m'Initial commit'"
  566 |             - "git push -u origin main --force"
  567 | 
  568 |     # Jenkins
  569 |     - name: Configure Jenkins
  570 |       when: ('"containers" in groups' and '"jenkins" in inventory_hostnames["containers"]')
  571 |       module_defaults:
  572 |         ansible.builtin.uri:
  573 |           url_username: "{{ student_username }}"
  574 |           url_password: "{{ student_password }}"
  575 |           force_basic_auth: true
  576 |           return_content: true
  577 |           validate_certs: false
  578 |       tags:
  579 |         - jenkins
  580 |       block:
  581 |         - name: Generate Jenkins CSRF token - {{ student_username }}
  582 |           ansible.builtin.uri:
  583 |             method: GET
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.
