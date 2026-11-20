# Frozen source context: V007PILOT-SECURITY-030

- Repository: `cfpb/aurora`
- Commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Family: Security
- Rule: `ansibleguard/default-credentials`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `deploy/roles/eod/defaults/main.yaml` (reported anchor line 32)
- Object: `source_location` `1a9552c87931b8dd998120decc9c4a688550de8de726fc9c52701ee759b500b8`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–53 of 53:

```text
    1 | ---
    2 | #==================#
    3 | ### EoD SETTINGS ###
    4 | #==================#
    5 | install_desktop: False
    6 | eod_restart: False
    7 | eod_install: False
    8 | eod_upgrade: False
    9 | eod_installer: ecs-13.8.5-linux-x64.bin
   10 | eod_upgrader:
   11 | eod_installer_directory: '/artifacts'
   12 | 
   13 | eod_client_ports:
   14 |   - 5500
   15 |   - 8406
   16 |   - 8407
   17 |   - 6000:6025
   18 | 
   19 | eod_client_ports_udp:
   20 |   - 177
   21 | 
   22 | eod_admins:
   23 |   - vagrant
   24 | 
   25 | eod_install_directory: '/usr/local/eod'
   26 | eod_cm_password: PASSWORD
   27 | 
   28 | # Define this variable to setup a cluster with a common datastore
   29 | # The datastore must be a shared volume accessible by all EOD nodes.
   30 | # eod_datastore_directory:
   31 | 
   32 | eod_datastore_password: PASSWORD
   33 | eod_cm_preferred_pcm: "{{ ansible_ssh_host }}"
   34 | eod_cluster_name: "{{ ansible_ssh_host }}"
   35 | xdmc_query_host:  "{{ ansible_ssh_host }}"
   36 | 
   37 | eod_use_license_server: 0
   38 | eod_license_server_host:
   39 | eod_license_server_cache:
   40 | 
   41 | # TODO: you can put all the keys you want to here
   42 | eod_license_keys:
   43 |   - AAAA-BBBBBB-CCCCCC-DDDD-EEEEEE-FFF -0123456789 123
   44 | 
   45 | # GDM Settings
   46 | # This example disables the login user list
   47 | gconf_settings:
   48 |   -
   49 |     setting: "/apps/gdm/simple-greeter/disable_user_list"
   50 |     type: "bool"
   51 |     value: "true"
   52 | 
   53 | eod_greeter_include: false
```
