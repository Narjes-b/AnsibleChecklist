# Frozen source context: V007PILOT-STYLE_POLICY-012

- Repository: `redhat-openstack/infrared`
- Commit: `d00a414759c83765e8fd2e19d48f06d492736a93`
- Family: Style/policy
- Rule: `ansibleguard/duplicate-task-names`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `plugins/virsh/snapshot_upload.yml` (reported anchor line 1)
- Object: `source_location` `aa339be9098aca9bb4cd4ffd70d7a3f1aa34f144c06da1e1a8f6753e9d0480fb`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–104 of 104:

```text
    1 | ---
    2 | - name: Upload snapshots of virtual machines
    3 |   hosts: "{{ (_run_condition | bool) | ternary('hypervisor', 'none') }}"
    4 |   gather_facts: yes
    5 |   any_errors_fatal: true
    6 |   vars:
    7 |     _object_storage_client_venv_path: "{{ provision.virsh.snapshot.path | dirname }}/.awsclientvenv"
    8 |   tasks:
    9 |     - name: Check that the required environment variables are set
   10 |       fail:
   11 |         msg: >-
   12 |           The environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
   13 |           must be set on the Ansible controller.
   14 |       when:
   15 |         - lookup('env', 'AWS_ACCESS_KEY_ID') == ""
   16 |         - lookup('env', 'AWS_SECRET_ACCESS_KEY') == ""
   17 | 
   18 |     - name: Ensure a usable object storage client is available
   19 |       include_role:
   20 |         name: create_venv
   21 |       vars:
   22 |         venv_destination_path: "{{ _object_storage_client_venv_path }}"
   23 |         venv_owner_match_to_parent: yes
   24 |         venv_pip_packages:
   25 |           - "awscli"
   26 |         venv_shebang_relocate: yes
   27 | 
   28 |     - name: Upload the image set and cleanup afterwards
   29 |       environment:
   30 |         AWS_ACCESS_KEY_ID: "{{ lookup('env', 'AWS_ACCESS_KEY_ID') }}"
   31 |         AWS_SECRET_ACCESS_KEY: "{{ lookup('env', 'AWS_SECRET_ACCESS_KEY') }}"
   32 |       vars:
   33 |         _cli_aws_endpoint_url: "{{ (lookup('env', 'AWS_ENDPOINT_URL') != '') | ternary('--endpoint-url ' ~ lookup('env', 'AWS_ENDPOINT_URL'), '') }}"
   34 |       block:
   35 |         - name: Detect whether an image set exists (but may not be complete)
   36 |           shell: >-
   37 |             source {{ _object_storage_client_venv_path | basename }}/bin/activate;
   38 |             aws {{ _cli_aws_endpoint_url }}
   39 |             s3 ls {{ provision.virsh.snapshot.container }}/{{ provision.virsh.snapshot.path | basename }}/status
   40 |           args:
   41 |             executable: "/bin/bash"
   42 |             chdir: "{{ provision.virsh.snapshot.path | dirname }}"
   43 |           register: _virsh_snapshot_upload_aws_status
   44 |           failed_when: false
   45 | 
   46 |         - name: Upload the image set if one does not exist yet
   47 |           when: _virsh_snapshot_upload_aws_status.rc == 1
   48 |           block:
   49 |             - name: Update status and timestamp to enable status tracking
   50 |               lineinfile:
   51 |                 path: "{{ provision.virsh.snapshot.path }}/status"
   52 |                 line: "upload-start {{ lookup('pipe', 'date --utc +%FT%T%Z') }}"
   53 |                 create: yes
   54 | 
   55 |             - &upload_status_file
   56 |               name: Upload the status file to object storage
   57 |               shell: >-
   58 |                 source {{ _object_storage_client_venv_path | basename }}/bin/activate;
   59 |                 aws {{ _cli_aws_endpoint_url }}
   60 |                 s3 cp {{ provision.virsh.snapshot.path }}/status
   61 |                 {{ provision.virsh.snapshot.container }}/{{ provision.virsh.snapshot.path | basename }}/
   62 |               args:
   63 |                 executable: "/bin/bash"
   64 |                 chdir: "{{ provision.virsh.snapshot.path | dirname }}"
   65 |               register: _virsh_snapshot_upload_aws_result
   66 |               retries: 10
   67 |               delay: 30
   68 |               until: _virsh_snapshot_upload_aws_result is success
   69 | 
   70 |             # The ansible s3_sync module does not currently support the s3_url parameter
   71 |             # which would allow it to work with Ceph RGW.
   72 |             # The ansible aws_s3 module supports the s3_url, but requires the upload of
   73 |             # each object to be done in a loop which is highly inefficient.
   74 |             # We use the 'aws s3 sync' option due to it being able to work on the whole
   75 |             # folder at once with a high level of efficiency.
   76 |             - name: Upload the snapshot path folder to object storage
   77 |               shell: >-
   78 |                 source {{ _object_storage_client_venv_path | basename }}/bin/activate;
   79 |                 aws {{ _cli_aws_endpoint_url }}
   80 |                 s3 sync --no-progress --delete
   81 |                 {{ provision.virsh.snapshot.path | basename }}
   82 |                 {{ provision.virsh.snapshot.container }}/{{ provision.virsh.snapshot.path | basename }}
   83 |               args:
   84 |                 executable: "/bin/bash"
   85 |                 chdir: "{{ provision.virsh.snapshot.path | dirname }}"
   86 |               register: _virsh_snapshot_upload_aws_result
   87 |               retries: 10
   88 |               delay: 30
   89 |               until: _virsh_snapshot_upload_aws_result is success
   90 | 
   91 |             - name: Update status and timestamp to enable status tracking
   92 |               lineinfile:
   93 |                 path: "{{ provision.virsh.snapshot.path }}/status"
   94 |                 line: "upload-complete {{ lookup('pipe', 'date --utc +%FT%T%Z') }}"
   95 |                 create: yes
   96 | 
   97 |             - *upload_status_file
   98 |       always:
   99 |         - name: Clean up the snapshot path
  100 |           file:
  101 |             path: "{{ provision.virsh.snapshot.path }}"
  102 |             state: absent
  103 |           when:
  104 |             - provision.virsh.snapshot.cleanup | bool
```
