# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-027

- Repository: `snowdrop/k8s-infra`
- Commit: `0a9fe0fb57bd9759833bb9974d5022d945b2647c`
- Family: Maintainability/complexity
- Rule: `ansibleguard/deprecated-modules`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `ansible/roles/cluster/tasks/install_oc_client.yml` (reported anchor line 7)
- Object: `task` `28ac9848921f9db678fa15af330544f366ebd3d465a8467ee5abaef11ff6467d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–74 of 74:

```text
    1 | - name: Get the Mac asset 
    2 |   include: get_mac_asset.yml
    3 |   with_items: "{{ assets.json }}"
    4 |   when: assets is defined and ansible_os_family == 'Darwin'
    5 | 
    6 | - name: Get the Linux asset
    7 |   include: get_linux_asset.yml
    8 |   with_items: "{{ assets.json }}"
    9 |   when: "assets is defined and ansible_os_family in ['RedHat', 'Debian']"
   10 | 
   11 | - name: Should have an asset_name
   12 |   assert:
   13 |     that: asset_name is defined
   14 | 
   15 | - name: Create a temp dir
   16 |   command: mktemp -d -t ansible.XXXXXXXXXX
   17 |   register: temp_output
   18 | 
   19 | - name: Show temp dir
   20 |   debug: msg="Temp dir - {{ temp_output.stdout }}"
   21 | 
   22 | - name: Show the asset name
   23 |   debug: msg="Asset name = {{ asset_name }}"
   24 | 
   25 | - name: Download the asset
   26 |   get_url:
   27 |     url: "{{ asset_url }}"
   28 |     dest: "{{ temp_output.stdout }}/{{ asset_name }}" 
   29 | 
   30 | - name: Unzip the archive
   31 |   command: "unzip {{ asset_name }}" 
   32 |   args:
   33 |     chdir: "{{ temp_output.stdout }}"
   34 |   when: "'zip' in asset_name"
   35 | 
   36 | - name: Untar the archive
   37 |   unarchive:
   38 |     src: "{{ temp_output.stdout }}/{{ asset_name }}"
   39 |     dest: "{{ temp_output.stdout }}"
   40 |     remote_src: yes
   41 |   when: "'tar.gz' in asset_name"
   42 | 
   43 | - name: List output dir
   44 |   command: ls -la {{ temp_output.stdout }}
   45 | 
   46 | - name: Set path to the extracted folder for tar.gz archive
   47 |   set_fact:
   48 |     archive_path: "{{ asset_name | regex_replace('\\.tar\\.gz', '') }}"
   49 |   when: "'tar.gz' in asset_name"
   50 | 
   51 | - name: Set path to the extracted folder for zip archive
   52 |   set_fact:
   53 |     archive_path: ""
   54 |   when: "'zip' in asset_name"
   55 | 
   56 | - name: Check if 'oc' client exists within the extracted archive folder
   57 |   stat:
   58 |     path: "{{ temp_output.stdout }}/{{ archive_path }}/oc"
   59 |   register: oc
   60 | 
   61 | - name: Copy 'oc' to the requested directory if it exists within the extracted folder
   62 |   copy:
   63 |     src: "{{ temp_output.stdout }}/{{ archive_path }}/oc"
   64 |     dest: "{{ openshift_client_dest }}/oc"
   65 |     mode: 0775
   66 |     remote_src: true
   67 |   become: yes
   68 |   become_user: root
   69 |   when: oc.stat.exists
   70 | 
   71 | - name: Remove the temp directory
   72 |   file:
   73 |     path: "{{ temp_output.stdout }}"
   74 |     state: absent
```
