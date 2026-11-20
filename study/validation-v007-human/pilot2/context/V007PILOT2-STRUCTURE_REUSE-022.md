# Frozen source context: V007PILOT2-STRUCTURE_REUSE-022

- Repository: `wonderbird/ansible-all-my-things`
- Commit: `4993019d9dfb175eef6cb40fce4ea56138e6a374`
- Family: structure_reuse
- Rule: `ansibleguard/missing-abstraction`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `roles/android_studio/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`roles/android_studio/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–112 of 112:

```text
    1 | #SPDX-License-Identifier: MIT-0
    2 | ---
    3 | - name: Install Android Studio via snap
    4 |   community.general.snap:
    5 |     name: android-studio
    6 |     classic: true
    7 |     state: present
    8 | 
    9 | - name: Download Android SDK command-line tools
   10 |   ansible.builtin.get_url:
   11 |     url: "https://dl.google.com/android/repository/commandlinetools-linux-{{ android_cmdlinetools_build }}_latest.zip"
   12 |     dest: "/tmp/commandlinetools-linux-{{ android_cmdlinetools_build }}_latest.zip"
   13 |     checksum: "sha1:{{ android_cmdlinetools_sha1 }}"
   14 | 
   15 | - name: Create ANDROID_HOME directory
   16 |   ansible.builtin.file:
   17 |     path: "/home/{{ item }}/Android/Sdk"
   18 |     state: directory
   19 |     owner: "{{ item }}"
   20 |     group: "{{ item }}"
   21 |     mode: "0755"
   22 |   loop: "{{ login_user_names }}"
   23 | 
   24 | - name: Create cmdline-tools parent directory
   25 |   ansible.builtin.file:
   26 |     path: "/home/{{ item }}/Android/Sdk/cmdline-tools"
   27 |     state: directory
   28 |     owner: "{{ item }}"
   29 |     group: "{{ item }}"
   30 |     mode: "0755"
   31 |   loop: "{{ login_user_names }}"
   32 | 
   33 | - name: Extract cmdline-tools
   34 |   ansible.builtin.unarchive:
   35 |     src: "/tmp/commandlinetools-linux-{{ android_cmdlinetools_build }}_latest.zip"
   36 |     dest: "/home/{{ item }}/Android/Sdk/cmdline-tools/"
   37 |     remote_src: true
   38 |     creates: "/home/{{ item }}/Android/Sdk/cmdline-tools/cmdline-tools/bin/sdkmanager"
   39 |   become_user: "{{ item }}"
   40 |   loop: "{{ login_user_names }}"
   41 | 
   42 | - name: Rename cmdline-tools to latest
   43 |   ansible.builtin.command:
   44 |     cmd: >
   45 |       mv
   46 |       /home/{{ item }}/Android/Sdk/cmdline-tools/cmdline-tools
   47 |       /home/{{ item }}/Android/Sdk/cmdline-tools/latest
   48 |     creates: "/home/{{ item }}/Android/Sdk/cmdline-tools/latest/bin/sdkmanager"
   49 |   become_user: "{{ item }}"
   50 |   loop: "{{ login_user_names }}"
   51 | 
   52 | - name: Detect latest Android API level
   53 |   ansible.builtin.shell:
   54 |     cmd: >
   55 |       /home/{{ item }}/Android/Sdk/cmdline-tools/latest/bin/sdkmanager --list --channel=0
   56 |       | grep -oP 'platforms;android-\K[0-9]+(?:\.[0-9]+)?(?=\s)'
   57 |       | sort -V
   58 |       | tail -1
   59 |   environment:
   60 |     JAVA_HOME: "/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}"
   61 |   become_user: "{{ item }}"
   62 |   loop: "{{ login_user_names }}"
   63 |   register: detected_api_levels
   64 |   changed_when: false
   65 |   failed_when: detected_api_levels.rc != 0 or detected_api_levels.stdout | trim | length == 0
   66 | 
   67 | - name: Detect latest build-tools version
   68 |   ansible.builtin.shell:
   69 |     cmd: >
   70 |       /home/{{ item }}/Android/Sdk/cmdline-tools/latest/bin/sdkmanager --list --channel=0
   71 |       | grep -oP 'build-tools;\K[0-9]+\.[0-9]+\.[0-9]+'
   72 |       | sort -V
   73 |       | tail -1
   74 |   environment:
   75 |     JAVA_HOME: "/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}"
   76 |   become_user: "{{ item }}"
   77 |   loop: "{{ login_user_names }}"
   78 |   register: detected_buildtools_versions
   79 |   changed_when: false
   80 |   failed_when: detected_buildtools_versions.rc != 0 or detected_buildtools_versions.stdout | trim | length == 0
   81 | 
   82 | - name: Assert detected API level is a valid version
   83 |   ansible.builtin.assert:
   84 |     that:
   85 |       - item.stdout | trim is match('^[0-9]+(\.[0-9]+)?$')
   86 |     fail_msg: "Detected API level '{{ item.stdout | trim }}' is not a valid version for user '{{ item.item }}'."
   87 |   loop: "{{ detected_api_levels.results }}"
   88 | 
   89 | - name: Assert detected build-tools version matches X.Y.Z
   90 |   ansible.builtin.assert:
   91 |     that:
   92 |       - item.stdout | trim is match('^[0-9]+\.[0-9]+\.[0-9]+$')
   93 |     fail_msg: "Detected build-tools version '{{ item.stdout | trim }}' does not match X.Y.Z for user '{{ item.item }}'."
   94 |   loop: "{{ detected_buildtools_versions.results }}"
   95 | 
   96 | - name: Install SDK components
   97 |   community.general.android_sdk:
   98 |     name:
   99 |       - platform-tools
  100 |       - "platforms;android-{{ detected_api_levels.results[idx].stdout }}"
  101 |       - "build-tools;{{ detected_buildtools_versions.results[idx].stdout }}"
  102 |       - emulator
  103 |     state: present
  104 |     accept_licenses: true
  105 |     sdk_root: "/home/{{ item }}/Android/Sdk"
  106 |   environment:
  107 |     JAVA_HOME: "/home/{{ item }}/.sdkman/candidates/java/{{ java_sdkman_identifier }}"
  108 |     PATH: "/home/{{ item }}/Android/Sdk/cmdline-tools/latest/bin:{{ ansible_facts['env']['PATH'] }}"
  109 |   become_user: "{{ item }}"
  110 |   loop: "{{ login_user_names }}"
  111 |   loop_control:
  112 |     index_var: idx
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `roles/android_studio`; 5 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: yes
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: yes
- molecule/ directory: no

roles/android_studio/DESIGN.md
roles/android_studio/README.md
roles/android_studio/defaults/main.yml
roles/android_studio/meta/main.yml
roles/android_studio/tasks/main.yml
```

## Computed facts

```text
Computed facts (from the parsed file, independent of the detector):
- leaf tasks (not counting block containers): 11 (the rule needs more than 10)
- include/import task or role, or play-level roles, present: no
```
