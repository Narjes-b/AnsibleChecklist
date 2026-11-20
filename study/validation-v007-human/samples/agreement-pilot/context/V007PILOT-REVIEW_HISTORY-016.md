# Frozen Git review context: V007PILOT-REVIEW_HISTORY-016

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Target commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Actual first parent: `99c63c980f58850c1c7dd4d41b9523138513f650`
- Evidence type: actual first-parent diff
- Family: Review/history
- Rule: `ansibleguard/missing-test-update`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: `99c63c980f58850c1c7dd4d41b9523138513f650..6e9fdebea0d9a7e66563ea3595d9eff160986d25` (from frozen Git objects)
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
Merge pull request #1041 from rajan-mis/mainfix600

Fixed remote mount role for shell commands that need quoting
```

## Changed paths (4)

- `M` `roles/remotemount_configure/defaults/main.yml`
- `M` `roles/remotemount_configure/tasks/cleanup_remote_mount_api_cli.yml`
- `M` `roles/remotemount_configure/tasks/mount_filesystem_api_cli.yml`
- `M` `roles/remotemount_configure/tasks/remotecluster_api_cli.yml`

## Relevant first-parent diff

```diff
diff --git a/roles/remotemount_configure/defaults/main.yml b/roles/remotemount_configure/defaults/main.yml
index 109ae4b..8dfee07 100644
--- a/roles/remotemount_configure/defaults/main.yml
+++ b/roles/remotemount_configure/defaults/main.yml
@@ -13,10 +13,11 @@ scale_remotemount_storage_cluster_gui_port: 443
 scale_remotemount_scalemgmt_endpoint: "scalemgmt/v2"
 scale_remotemount_endpoint: "{{ scale_remotemount_scalemgmt_endpoint }}/remotemount"
 
 
 scale_remotemount_validate_certs_uri: 'no'
+scale_remotemount_ca_bundle_path: ''  # Optional: path to custom CA bundle for certificate validation
 
 scale_cluster_authorization_cleanup: [REDACTED_LITERAL]
 
 # Temporary Storage for Public Key, Only used when debuging
 scale_remotemount_client_access_key: [REDACTED_LITERAL]
diff --git a/roles/remotemount_configure/tasks/cleanup_remote_mount_api_cli.yml b/roles/remotemount_configure/tasks/cleanup_remote_mount_api_cli.yml
index cc88085..9090bc0 100644
--- a/roles/remotemount_configure/tasks/cleanup_remote_mount_api_cli.yml
+++ b/roles/remotemount_configure/tasks/cleanup_remote_mount_api_cli.yml
@@ -2,10 +2,11 @@
 # Get some cluster information before starting Cleanup
 #
 - name: Cleanup Remote Mount - API-CLI | Storage Cluster (owner) | GET the Owning Cluster Information
   uri:
     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+    ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
     force_basic_auth: yes
     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/cluster
     method: GET
     user: "{{ scale_remotemount_storage_gui_username }}"
     password: "{{ scale_remotemount_storage_gui_password }}"
@@ -104,17 +105,17 @@
 #
 
 - name: Cleanup Remote Mount - API-CLI | Client Cluster (Access) | Check if the Storage Cluster ('{{ owning_cluster_name }}') is already defined on Client"
   run_once: True
   shell: |
-    /usr/lpp/mmfs/bin/mmremotecluster show {{ owning_cluster_name }}
+    /usr/lpp/mmfs/bin/mmremotecluster show {{ owning_cluster_name | quote }}
   register: remote_cluster_check_owning_cluster
   ignore_errors: true
   changed_when: false
 
 - name: Cleanup Remote Mount - API-CLI | Client Cluster (access) | Remove the connection of Storage Cluster (Owning) from Client Cluster (Access)
-  shell: "/usr/lpp/mmfs/bin/mmremotecluster delete {{ owning_cluster_name }}"
+  shell: "/usr/lpp/mmfs/bin/mmremotecluster delete {{ owning_cluster_name | quote }}"
   register: access_cluster_remove_remote_cluster
   run_once: True
   #ignore_errors: true
   when: remote_cluster_check_owning_cluster.rc == 0
 
@@ -124,10 +125,11 @@
 #
 
 - name: "Cleanup Remote Mount - API-CLI | Storage Cluster (owner) | Check if the Client Cluster ('{{ access_cluster_name }}') is already defined"
   uri:
     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+    ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
     force_basic_auth: yes
     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}
     method: GET
     user: "{{ scale_remotemount_storage_gui_username }}"
     password: "{{ scale_remotemount_storage_gui_password }}"
@@ -143,10 +145,11 @@
 - name: Cleanup Remote Mount - API-CLI | Storage Cluster (owner) | Delete the Client Cluster, if it exists.
   block:
     - name: "DELETE: {{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}"
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: true
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}
         method: DELETE
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
@@ -155,10 +158,11 @@
       register: delete_call
 
     - name: "Cleanup Remote Mount - API-CLI | Checking results from the job: {{ delete_call.json.jobs[0].jobId }}"
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: true
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/jobs/{{ delete_call.json.jobs[0].jobId }}
         method: GET
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
diff --git a/roles/remotemount_configure/tasks/mount_filesystem_api_cli.yml b/roles/remotemount_configure/tasks/mount_filesystem_api_cli.yml
index aef036b..62d9b0f 100644
--- a/roles/remotemount_configure/tasks/mount_filesystem_api_cli.yml
+++ b/roles/remotemount_configure/tasks/mount_filesystem_api_cli.yml
@@ -8,10 +8,11 @@
   run_once: True
 
 - name: Mount Filesystem - Rest-API | Storage Cluster (owner) | GET the Cluster Information
   uri:
     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+    ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
     force_basic_auth: yes
     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/cluster
     method: GET
     user: "{{ scale_remotemount_storage_gui_username }}"
     password: "{{ scale_remotemount_storage_gui_password }}"
@@ -56,10 +57,11 @@
   run_once: True
 
 - name: "Mount Filesystem - Rest-API | Storage Cluster (owner) | Check if filesystems is already accessible for Client Cluster  ('{{ access_cluster_name }}')"
   uri:
     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+    ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
     force_basic_auth: yes
     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}
     method: GET
     user: "{{ scale_remotemount_storage_gui_username }}"
     password: "{{ scale_remotemount_storage_gui_password }}"
@@ -91,10 +93,11 @@
    - 'item.scale_remotemount_storage_filesystem_name not in current_scale_remotemount_storage_filesystem_name'
 
 - name: Mount Filesystem - Rest-API | Storage Cluster (owning) | Allow and Set the client cluster filesystem access attributes on the Storage Cluster
   uri:
     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+    ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
     force_basic_auth: true
     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}/access/{{ item.scale_remotemount_storage_filesystem_name }}
     method: POST
     user: "{{ scale_remotemount_storage_gui_username }}"
     password: "{{ scale_remotemount_storage_gui_password }}"
@@ -120,10 +123,11 @@
    - 'item.item.scale_remotemount_storage_filesystem_name not in current_scale_remotemount_storage_filesystem_name'
 
 - name: Mount Filesystem - Rest-API | Storage Cluster (owning) | Check the result of setting the access attributes on the Storage Cluster ##"{{ completed_check.json.jobs[0].jobId }}"
   uri:
     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+    ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
     force_basic_auth: true
     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/jobs/{{ item.json.jobs.0['jobId'] }}
     method: GET
     user: "{{ scale_remotemount_storage_gui_username }}"
     password: "{{ scale_remotemount_storage_gui_password }}"
@@ -169,11 +173,11 @@
     msg: "Add the remotefileystem and mount it on the Client Side"
 
 - name: Mount Filesystem - Rest-API | Client Cluster (access) | Add remote filesystem - Output is from check.
   run_once: True
   shell: |
-    /usr/lpp/mmfs/bin/mmremotefs add {{ item.item.scale_remotemount_client_filesystem_name }} -f {{ item.item.scale_remotemount_storage_filesystem_name }} -C {{ owning_cluster_name }} -T {{ item.item.scale_remotemount_client_remotemount_path }} -o  {{ item.item.scale_remotemount_access_mount_attributes | default ('rw') }} -A {{ item.item.scale_remotemount_client_mount_fs | default ('yes') }} --mount-priority {{ item.item.scale_remotemount_client_mount_priority | default ('0') }}
+    /usr/lpp/mmfs/bin/mmremotefs add {{ item.item.scale_remotemount_client_filesystem_name | quote }} -f {{ item.item.scale_remotemount_storage_filesystem_name | quote }} -C {{ owning_cluster_name | quote }} -T {{ item.item.scale_remotemount_client_remotemount_path | quote }} -o {{ item.item.scale_remotemount_access_mount_attributes | default('rw') | quote }} -A {{ item.item.scale_remotemount_client_mount_fs | default('yes') | quote }} --mount-priority {{ item.item.scale_remotemount_client_mount_priority | default('0') | quote }}
   register: client_cluster_add_remotefs
   loop: "{{ remote_filesystem_results_cli.results }}"
   when:
     - item.rc != 0 or scale_remotemount_forceRun | bool
   failed_when:
diff --git a/roles/remotemount_configure/tasks/remotecluster_api_cli.yml b/roles/remotemount_configure/tasks/remotecluster_api_cli.yml
index 1d18ce0..60c77ee 100644
--- a/roles/remotemount_configure/tasks/remotecluster_api_cli.yml
+++ b/roles/remotemount_configure/tasks/remotecluster_api_cli.yml
@@ -8,10 +8,11 @@
   run_once: True
 
 - name: Remote Cluster Config - API-CLI | Storage Cluster (owner) | GET the Cluster Information
   uri:
     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+    ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
     force_basic_auth: yes
     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/cluster
     method: GET
     user: "{{ scale_remotemount_storage_gui_username }}"
     password: "{{ scale_remotemount_storage_gui_password }}"
@@ -56,10 +57,11 @@
     msg: "Check if the Remote Cluster is already configured"
 
 - name: "Remote Cluster Config - API-CLI | Storage Cluster (owner) | Check if the Client Cluster ('{{ access_cluster_name }}') is already defined"
   uri:
     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+    ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
     force_basic_auth: yes
     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}
     method: GET
     user: "{{ scale_remotemount_storage_gui_username }}"
     password: "{{ scale_remotemount_storage_gui_password }}"
@@ -72,20 +74,21 @@
   run_once: true
 
 - name: Remote Cluster Config - API-CLI | Client Cluster (access) | Check if the Storage Cluster ('{{ owning_cluster_name }}') is already defined on Client"
   run_once: True
   shell: |
-    /usr/lpp/mmfs/bin/mmremotecluster show {{ owning_cluster_name }}
+    /usr/lpp/mmfs/bin/mmremotecluster show {{ owning_cluster_name | quote }}
   register: remote_cluster_check_owning_cluster
   ignore_errors: true
   changed_when: false
 
 - name: Remote Cluster Config - API-CLI | Storage Cluster (owner) | Delete the Client Cluster, if it exists
   block:
     - name: "DELETE: {{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}"
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: true
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}
         method: DELETE
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
@@ -95,10 +98,11 @@
       register: delete_call
 
     - name: "Checking results from the job: {{ delete_call.json.jobs[0].jobId }}"
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: true
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/jobs/{{ delete_call.json.jobs[0].jobId }}
         method: GET
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
@@ -196,10 +200,11 @@
 #  Read also the documentation of CLI command 'mmauth'.
 
     - name: Remote Cluster Config - API-CLI | Storage Cluster (owner) | Send the Public Key of the Client Cluster (access) to Storage Cluster (Owner)
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: true
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters
         method: POST
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
@@ -218,10 +223,11 @@
         - (remote_clusters_results.status == 400) or (scale_remotemount_forceRun | bool)
 
     - name: "Remote Cluster Config - API-CLI | Storage Cluster (owner) | Check the result of adding the Client Cluster {{ send_key.json.jobs[0].jobId }}"
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: true
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/jobs/{{ send_key.json.jobs[0].jobId }}
         method: GET
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
@@ -234,10 +240,11 @@
         - (remote_clusters_results.status == 400) or (scale_remotemount_forceRun | bool)
 
     - name: Remote Cluster Config - API-CLI | Storage Cluster (owner) | Get the Public Key
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: yes
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/authenticationkey/
         method: GET
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
@@ -274,10 +281,11 @@
 # This Section is gather the nodenames and adminNodeName
 #
     - name: "Remote Cluster Config - API-CLI | Storage Cluster (owner) | GET adminNodeName Info - GET {{ scale_remotemount_scalemgmt_endpoint }}/nodes"
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: yes
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/nodes{{ scale_remotemount_storage_contactnodes_filter }}
         method: GET
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
@@ -300,10 +308,11 @@
 # This Section is when using daemonNodeName
 #
     - name: "Remote Cluster Config - API-CLI | Storage Cluster (owner) | GET daemonNodeName Info - GET {{ scale_remotemount_scalemgmt_endpoint }}/nodes/"
       uri:
         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
+        ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
         force_basic_auth: yes
         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/nodes/{{item}}
         method: GET
         user: "{{ scale_remotemount_storage_gui_username }}"
         password: "{{ scale_remotemount_storage_gui_password }}"
@@ -335,11 +344,11 @@
       run_once: True
 
     - name: Remote Cluster Config - API-CLI | Client Cluster (Access) | Install storage cluster (owner) public key in remote cluster with adminNodeName
       run_once: True
       shell: |
-        /usr/lpp/mmfs/bin/mmremotecluster add {{ owning_cluster_name }} -n {{ owning_nodes_name | list | join(',') }} -k {{ scale_remotemount_storage_pub_key_location }}
+        /usr/lpp/mmfs/bin/mmremotecluster add {{ owning_cluster_name | quote }} -n {{ owning_nodes_name | map('quote') | join(',') }} -k {{ scale_remotemount_storage_pub_key_location | quote }}
       register: remote_cluster_add_ssh
       failed_when:
         - "remote_cluster_add_ssh.rc != 0 and 'is already defined' not in remote_cluster_add_ssh.stderr"
       when: scale_remotemount_storage_adminnodename is defined and scale_remotemount_storage_adminnodename | bool
 #
@@ -352,11 +361,11 @@
       run_once: True
 
     - name: Remote Cluster Config - API-CLI | Client Cluster (Access) |  Install storage cluster (owner) public key in remote cluster with daemonNodeName
       run_once: True
       shell: |
-        /usr/lpp/mmfs/bin/mmremotecluster add {{ owning_cluster_name }} -n {{ owning_daemon_nodes_name | list | join(',') }} -k {{ scale_remotemount_storage_pub_key_location }}
+        /usr/lpp/mmfs/bin/mmremotecluster add {{ owning_cluster_name | quote }} -n {{ owning_daemon_nodes_name | map('quote') | join(',') }} -k {{ scale_remotemount_storage_pub_key_location | quote }}
       register: remote_cluster_add_ssh
       failed_when:
         - "remote_cluster_add_ssh.rc != 0 and 'is already defined' not in remote_cluster_add_ssh.stderr"
       when: not scale_remotemount_storage_adminnodename
 

```
