# Frozen Git review context: V007PILOT-REVIEW_HISTORY-008

- Repository: `CMSgov/bluebutton-web-deployment`
- Target commit: `ef2da5200c4d70c9db49e682ae28cd52ca92c995`
- Actual first parent: `7b51c2c8a691e22742517d395df865589c778802`
- Evidence type: actual first-parent diff
- Family: Review/history
- Rule: `ansibleguard/missing-test-update`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: `7b51c2c8a691e22742517d395df865589c778802..ef2da5200c4d70c9db49e682ae28cd52ca92c995` (from frozen Git objects)
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
disable splunk service (#1564)

* disable splunk service

* Uninstall splunkforwarder from base AMI during build

* Uninstall splunkforwarder in app_prep phase for complete removal

* Robust splunkforwarder uninstallation: stop, disable, and remove

* Update main.yml
```

## Changed paths (9)

- `M` `playbook/build_app_ami_amzn2/main.yml`
- `M` `playbook/build_platinum_ami_amzn2/main.yml`
- `M` `roles/amzn2_base/tasks/main.yml`
- `M` `roles/env_config/files/env_config.yml`
- `D` `roles/splunk/tasks/main.yml`
- `D` `roles/splunk/templates/splunk_deployment_conf.j2`
- `D` `roles/splunk/vars/main.yml`
- `M` `terraform/modules/asg/templates/user_data.tpl`
- `M` `vars/all_var.yml`

## Relevant first-parent diff

```diff
diff --git a/playbook/build_app_ami_amzn2/main.yml b/playbook/build_app_ami_amzn2/main.yml
index 520c09d0d..ea578c3ca 100644
--- a/playbook/build_app_ami_amzn2/main.yml
+++ b/playbook/build_app_ami_amzn2/main.yml
@@ -7,11 +7,10 @@
     ansible_ssh_pipelining: no
     azone: "az1"
     sub_zone: "app"
     sg_zone: "appserver"
     env_az: "{{ env }}-{{ azone }}"
-    splunk_target_layer: "app"
   vars_files:
     - "./../../vars/common.yml"
     - "./../../vars/env/{{ env }}/env.yml"
     - "./../../vars/all_var.yml"
   roles:
diff --git a/playbook/build_platinum_ami_amzn2/main.yml b/playbook/build_platinum_ami_amzn2/main.yml
index 6e096bd0f..7b1cbf6b8 100644
--- a/playbook/build_platinum_ami_amzn2/main.yml
+++ b/playbook/build_platinum_ami_amzn2/main.yml
@@ -6,11 +6,10 @@
   vars:
     ansible_ssh_pipelining: no
     azone: "az1"
     sub_zone: "app"
     sg_zone: "appserver"
-    splunk_target_layer: "app"
      # Disable SSH users
   vars_files:
     - "./../../vars/common.yml"
     - "./../../vars/env/shared/env.yml"
     - "./../../vars/all_var.yml"
diff --git a/roles/amzn2_base/tasks/main.yml b/roles/amzn2_base/tasks/main.yml
index 0407c6195..a0d962864 100644
--- a/roles/amzn2_base/tasks/main.yml
+++ b/roles/amzn2_base/tasks/main.yml
@@ -56,5 +56,12 @@
       - boto3
       - botocore
       - psycopg2-binary==2.9.10
     executable: pip3.12
     umask: "0022"
+
+- name: Remove Splunk Universal Forwarder
+  become: yes
+  become_user: "{{ remote_admin_account }}"
+  dnf:
+    name: splunkforwarder
+    state: absent
diff --git a/roles/env_config/files/env_config.yml b/roles/env_config/files/env_config.yml
index 8ad44ec8c..183219a81 100644
--- a/roles/env_config/files/env_config.yml
+++ b/roles/env_config/files/env_config.yml
@@ -6,11 +6,10 @@
   vars:
     ansible_ssh_pipelining: no
     env: "dev"
     sub_zone: "app"
     sg_zone: "appserver"
-    splunk_target_layer: "app"
     var_files:
       - "vars/common.yml"
       - "vars/env/{{ env }}/env.yml"
       - "vars/all_var.yml"
 
diff --git a/roles/splunk/tasks/main.yml b/roles/splunk/tasks/main.yml
deleted file mode 100644
index eb5081b11..000000000
--- a/roles/splunk/tasks/main.yml
+++ /dev/null
@@ -1,19 +0,0 @@
----
-- name: "configure splunk"
-  become_user: "{{ remote_admin_account }}"
-  become: yes
-  template:
-    src: "../templates/splunk_deployment_conf.j2"
-    dest: "/opt/splunkforwarder/etc/system/local/deploymentclient.conf"
-
-- name: "Stop and initialize splunk configuration"
-  become_user: "{{ remote_admin_account }}"
-  become: yes
-  shell: |
-    systemctl stop splunk
-    /opt/splunkforwarder/bin/splunk clone-prep-clear-config
-
-- name: "Start splunk"
-  become_user: "{{ remote_admin_account }}"
-  shell: |
-    systemctl start splunk
diff --git a/roles/splunk/vars/main.yml b/roles/splunk/vars/main.yml
deleted file mode 100644
index 786bca673..000000000
--- a/roles/splunk/vars/main.yml
+++ /dev/null
@@ -1,4 +0,0 @@
----
-# File: main.yml 
-# Created: 5/6/17
-# Author: '@ekivemark'
diff --git a/vars/all_var.yml b/vars/all_var.yml
index 0de21c640..6cc3e0770 100644
--- a/vars/all_var.yml
+++ b/vars/all_var.yml
@@ -118,13 +118,10 @@
 
   mon_nessus_user: "{{ env_mon_nessus_user }}"
   mon_nessus_pwd: "{{ env_mon_nessus_pwd }}"
   mon_nessus_pub_key: "{{ env_mon_nessus_pub_key }}"
 
-  # splunk configuration
-  # Group name = BBAPI
-
   #
   # SLSx / Medicare.gov Authentication Integration
   #
   slsx_client_id: "{{ env_slsx_client_id }}"
   slsx_client_secret: "{{ env_slsx_client_secret }}"

```
