# Frozen source context: V007PILOT-SECURITY-016

- Repository: `IBM/ibm-spectrum-scale-install-infra`
- Commit: `6e9fdebea0d9a7e66563ea3595d9eff160986d25`
- Family: Security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/remotemount_configure/tasks/remotecluster_api_cli.yml` (reported anchor line 225)
- Object: `task` `6a0e7eb3ec33f6ab726e5a0c62c1740a9d3a61f854380ec3f6730236d7eb0ef0`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–383 of 383:

```text
    1 | ---
    2 | #
    3 | # Gather cluster information
    4 | #
    5 | - name: Step 1 - Remote Cluster Config - API-CLI
    6 |   debug:
    7 |     msg: Gather some information about cluster and state
    8 |   run_once: True
    9 | 
   10 | - name: Remote Cluster Config - API-CLI | Storage Cluster (owner) | GET the Cluster Information
   11 |   uri:
   12 |     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
   13 |     ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
   14 |     force_basic_auth: yes
   15 |     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/cluster
   16 |     method: GET
   17 |     user: "{{ scale_remotemount_storage_gui_username }}"
   18 |     password: "{{ scale_remotemount_storage_gui_password }}"
   19 |     body_format: json
   20 |     status_code:
   21 |       - 200
   22 |   register: owning_cluster_info
   23 |   run_once: True
   24 | 
   25 | - name: Remote Cluster Config - API-CLI |  Storage Cluster (owner) | scale_remotemount_debug | Print the Cluster Information
   26 |   debug:
   27 |     msg: "{{ owning_cluster_info }}"
   28 |   when: scale_remotemount_debug is defined and scale_remotemount_debug | bool
   29 |   run_once: True
   30 | 
   31 | - name: Remote Cluster Config - API-CLI | Client Cluster (access) | GET the Cluster Information
   32 |   shell: /usr/lpp/mmfs/bin/mmlscluster -Y | grep -v HEADER | grep clusterSummary | cut -d ':' -f 9
   33 |   register: access_cluster_info
   34 |   changed_when: false
   35 |   failed_when: false
   36 |   run_once: True
   37 | 
   38 | - name: Remote Cluster Config - API-CLI | Client Cluster (access) | scale_remotemount_debug | Print the Cluster Information
   39 |   debug:
   40 |     msg: "{{ access_cluster_info }}"
   41 |   when: scale_remotemount_debug is defined and scale_remotemount_debug | bool
   42 |   run_once: True
   43 | 
   44 | - set_fact:
   45 |     access_cluster_name: "{{ access_cluster_info.stdout }}"
   46 |     owning_cluster_name: "{{ owning_cluster_info.json.cluster.clusterSummary.clusterName }}"
   47 |   run_once: True
   48 | 
   49 | #
   50 | # When scale_remotemount_forceRun, do some cleanup to properly unmount and remove things
   51 | #
   52 | - import_tasks: cleanup_filesystem_api_cli.yml
   53 |   when: scale_remotemount_forceRun | bool
   54 | 
   55 | - name: Step 2 - Remote Cluster Config - API-CLI
   56 |   debug:
   57 |     msg: "Check if the Remote Cluster is already configured"
   58 | 
   59 | - name: "Remote Cluster Config - API-CLI | Storage Cluster (owner) | Check if the Client Cluster ('{{ access_cluster_name }}') is already defined"
   60 |   uri:
   61 |     validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
   62 |     ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
   63 |     force_basic_auth: yes
   64 |     url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}
   65 |     method: GET
   66 |     user: "{{ scale_remotemount_storage_gui_username }}"
   67 |     password: "{{ scale_remotemount_storage_gui_password }}"
   68 |     body_format: json
   69 |     status_code:
   70 |       - 200
   71 |       - 400
   72 |   register: remote_clusters_results
   73 |   ignore_errors: true
   74 |   run_once: true
   75 | 
   76 | - name: Remote Cluster Config - API-CLI | Client Cluster (access) | Check if the Storage Cluster ('{{ owning_cluster_name }}') is already defined on Client"
   77 |   run_once: True
   78 |   shell: |
   79 |     /usr/lpp/mmfs/bin/mmremotecluster show {{ owning_cluster_name | quote }}
   80 |   register: remote_cluster_check_owning_cluster
   81 |   ignore_errors: true
   82 |   changed_when: false
   83 | 
   84 | - name: Remote Cluster Config - API-CLI | Storage Cluster (owner) | Delete the Client Cluster, if it exists
   85 |   block:
   86 |     - name: "DELETE: {{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}"
   87 |       uri:
   88 |         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
   89 |         ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
   90 |         force_basic_auth: true
   91 |         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters/{{ access_cluster_name }}
   92 |         method: DELETE
   93 |         user: "{{ scale_remotemount_storage_gui_username }}"
   94 |         password: "{{ scale_remotemount_storage_gui_password }}"
   95 |         status_code:
   96 |           - 202
   97 |       run_once: true
   98 |       register: delete_call
   99 | 
  100 |     - name: "Checking results from the job: {{ delete_call.json.jobs[0].jobId }}"
  101 |       uri:
  102 |         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
  103 |         ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
  104 |         force_basic_auth: true
  105 |         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/jobs/{{ delete_call.json.jobs[0].jobId }}
  106 |         method: GET
  107 |         user: "{{ scale_remotemount_storage_gui_username }}"
  108 |         password: "{{ scale_remotemount_storage_gui_password }}"
  109 |       register: completed_check
  110 |       until: completed_check.json.jobs[0].status == "COMPLETED"
  111 |       retries: "{{ scale_remotemount_restapi_retries_count }}"
  112 |       delay: "{{ scale_remotemount_restapi_retries_delay }}"
  113 |       run_once: True
  114 |   when:
  115 |     - not remote_clusters_results.failed and scale_remotemount_forceRun | bool
  116 | 
  117 | - name: "Remote Cluster Config - API-CLI | If remote cluster (access) connection is already configured, nothing to do."
  118 |   debug:
  119 |     msg: "Remote Cluster connection ('{{ access_cluster_name }}') is already configured proceeding to filesystem mounting."
  120 |   run_once: True
  121 |   when:
  122 |     - (remote_clusters_results.status == 200) or (scale_remotemount_forceRun | bool)
  123 | 
  124 | # Get node names and check if gpfs deamon is running.
  125 | 
  126 | - name: Remote Cluster Config - API-CLI | Client Cluster (access) | GET the cluster nodes name information
  127 |   shell: /usr/lpp/mmfs/bin/mmlscluster -Y | grep -v HEADER | grep clusterNode |  cut -d ':' -f 8
  128 |   register: access_node_names
  129 |   changed_when: false
  130 |   failed_when: false
  131 |   run_once: True
  132 | 
  133 | - name: Remote Cluster Config - API-CLI | Client Cluster (access) | scale_remotemount_debug | Print the Cluster Information
  134 |   debug:
  135 |     msg: "{{ access_node_names.stdout_lines |  join(',') }}"
  136 |   when: scale_remotemount_debug is defined and scale_remotemount_debug | bool
  137 |   run_once: True
  138 | 
  139 | - set_fact:
  140 |     accessing_nodes_name: []
  141 |   run_once: True
  142 | 
  143 | - set_fact:
  144 |     accessing_nodes_name: "{{ access_node_names.stdout_lines |  join(',')  }}"
  145 |   run_once: True
  146 | 
  147 | - name: Remote Cluster Config - API-CLI | Client Cluster (access) | Check if GPFS deamon is started
  148 |   shell: /usr/lpp/mmfs/bin/mmgetstate -Y -N {{ accessing_nodes_name }} | grep -v HEADER | cut -d ':' -f 9
  149 |   register: gpfs_deamon_state
  150 |   changed_when: false
  151 |   run_once: true
  152 | 
  153 | - name: Remote Cluster Config - API-CLI | Client Cluster (access) | Fail if GPFS deamon is not started
  154 |   fail:
  155 |     msg: "Scale/GPFS deamon is NOT running on one or serveral of your client cluster node. Check and run mmount manually"
  156 |   when: "'down' in gpfs_deamon_state.stdout"
  157 |   ignore_errors: true
  158 |   run_once: true
  159 | 
  160 | #
  161 | # Section for doing the configuration of remote cluster.
  162 | #
  163 | - name: Remote Cluster Config - API-CLI | Exchange the keys between Storage and Client Clusters (access)
  164 |   block:
  165 |     - name: Step 3 - Remote Cluster Config - API-CLI
  166 |       debug:
  167 |         msg: "Configure remote Cluster connection between Storage Cluster (owner) and Client Cluster (access)"
  168 |       run_once: True
  169 |       when:
  170 |         - (remote_clusters_results.status == 400) or (scale_remotemount_forceRun | bool)
  171 | 
  172 |     - name: Remote Cluster Config - API-CLI | Remote Cluster connection status
  173 |       debug:
  174 |         msg: "Remote Cluster connection to ('{{ access_cluster_name }}') is not configured, procceding with configuration"
  175 |       run_once: True
  176 |       when:
  177 |         - (remote_clusters_results.status == 400) or (scale_remotemount_forceRun | bool)
  178 | 
  179 |     - name: Remote Cluster Config - API-CLI | Client Cluster (Access) | Get the Public key from CLI and register
  180 |       shell: "cat /var/mmfs/ssl/id_rsa_committed.pub"
  181 |       register: accesskey_result
  182 |       run_once: True
  183 |       when:
  184 |         - (remote_clusters_results.status == 400) or (scale_remotemount_forceRun | bool)
  185 | 
  186 |     - name: Remote Cluster Config - API-CLI |  Client Cluster (accesing) | scale_remotemount_debug | Print out the Client Cluster (access) Public Key results
  187 |       debug:
  188 |         msg: "{{ accesskey_result }}"
  189 |       when: scale_remotemount_debug is defined and scale_remotemount_debug | bool
  190 |       run_once: True
  191 | 
  192 |     - name: Remote Cluster Config - API-CLI | Client Cluster (accesing) | scale_remotemount_debug | Print out the Client Cluster (access) Public Key results to file ("{{ scale_remotemount_client_access_key }}")
  193 |       copy:
  194 |         dest: "{{ scale_remotemount_client_access_key }}"
  195 |         content: "{{ accesskey_result }}\n"
  196 |       when: scale_remotemount_debug is defined and scale_remotemount_debug | bool
  197 |       run_once: True
  198 | 
  199 | #  Register the Client Cluster (Access) on the Storage Cluster (owner) with RestAPI
  200 | #  Read also the documentation of CLI command 'mmauth'.
  201 | 
  202 |     - name: Remote Cluster Config - API-CLI | Storage Cluster (owner) | Send the Public Key of the Client Cluster (access) to Storage Cluster (Owner)
  203 |       uri:
  204 |         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
  205 |         ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
  206 |         force_basic_auth: true
  207 |         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/remoteclusters
  208 |         method: POST
  209 |         user: "{{ scale_remotemount_storage_gui_username }}"
  210 |         password: "{{ scale_remotemount_storage_gui_password }}"
  211 |         body_format: json
  212 |         body: |
  213 |           {
  214 |             "remoteCluster": "{{ access_cluster_name }}",
  215 |             "ciphers": ["{{ scale_remotemount_remotecluster_chipers }}"],
  216 |             "key": {{ accesskey_result.stdout_lines }}
  217 |           }
  218 |         status_code:
  219 |           - 202
  220 |       register: send_key
  221 |       run_once: True
  222 |       when:
  223 |         - (remote_clusters_results.status == 400) or (scale_remotemount_forceRun | bool)
  224 | 
  225 |     - name: "Remote Cluster Config - API-CLI | Storage Cluster (owner) | Check the result of adding the Client Cluster {{ send_key.json.jobs[0].jobId }}"
  226 |       uri:
  227 |         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
  228 |         ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
  229 |         force_basic_auth: true
  230 |         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/jobs/{{ send_key.json.jobs[0].jobId }}
  231 |         method: GET
  232 |         user: "{{ scale_remotemount_storage_gui_username }}"
  233 |         password: "{{ scale_remotemount_storage_gui_password }}"
  234 |       register: completed_check
  235 |       until: completed_check.json.jobs[0].status != "FAILED"
  236 |       retries: "{{ scale_remotemount_restapi_retries_count }}"
  237 |       delay: "{{ scale_remotemount_restapi_retries_delay }}"
  238 |       run_once: True
  239 |       when:
  240 |         - (remote_clusters_results.status == 400) or (scale_remotemount_forceRun | bool)
  241 | 
  242 |     - name: Remote Cluster Config - API-CLI | Storage Cluster (owner) | Get the Public Key
  243 |       uri:
  244 |         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
  245 |         ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
  246 |         force_basic_auth: yes
  247 |         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_endpoint }}/authenticationkey/
  248 |         method: GET
  249 |         user: "{{ scale_remotemount_storage_gui_username }}"
  250 |         password: "{{ scale_remotemount_storage_gui_password }}"
  251 |         body_format: raw
  252 |         status_code:
  253 |           - 200
  254 |       register: owningkey_result
  255 |       run_once: True
  256 | 
  257 |     - name: Remote Cluster Config - API-CLI | Remote Mount Handshake | Copy the Storage Cluster (owning) Public key content to local file on Client Cluster (access)
  258 |       copy:
  259 |         content: "{{ owningkey_result | json_query('json.key[]') }}"
  260 |         dest: "{{ scale_remotemount_storage_pub_key_location_json }}"
  261 |       run_once: true
  262 | #
  263 | # Trouble getting the JSON to be a proper pub_key in ansible, using SED and TR insted
  264 | # sed replaces , with a linebreak
  265 | # "tr -d"  delete  those characters (escaped with a backslash, so only dobbelfnutt, [ and ] is replaced)
  266 | # SED: S for substitute. That is first after / and with that after second /.. and "g"  does is several time per line.
  267 | #
  268 |     - name: Remote Cluster Config - API-CLI | Client Cluster (Access) | Remove json spesific information to a plain pub key file.
  269 |       shell:
  270 |         cmd: sed 's/,/\n/g' {{ scale_remotemount_storage_pub_key_location_json }} | tr -d '"\[\]' | sed 's/^ //' > {{ scale_remotemount_storage_pub_key_location }}
  271 |       run_once: true
  272 | 
  273 |     - name: Step 3 - Remote Cluster Config - API-CLI
  274 |       debug:
  275 |         msg: "Add the storage cluster (mmremotecluster add)"
  276 |       run_once: True
  277 | 
  278 | #
  279 | # After a feature improvements we want to grab adminnodename and deamonnode name after where we want the remote mount traffic going over.
  280 | #
  281 | # This Section is gather the nodenames and adminNodeName
  282 | #
  283 |     - name: "Remote Cluster Config - API-CLI | Storage Cluster (owner) | GET adminNodeName Info - GET {{ scale_remotemount_scalemgmt_endpoint }}/nodes"
  284 |       uri:
  285 |         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
  286 |         ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
  287 |         force_basic_auth: yes
  288 |         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/nodes{{ scale_remotemount_storage_contactnodes_filter }}
  289 |         method: GET
  290 |         user: "{{ scale_remotemount_storage_gui_username }}"
  291 |         password: "{{ scale_remotemount_storage_gui_password }}"
  292 |         body_format: json
  293 |         status_code:
  294 |           - 200
  295 |       register: owning_cluster_nodes
  296 |       run_once: True
  297 | 
  298 |     - set_fact:
  299 |         owning_nodes_name: []
  300 |       run_once: True
  301 | 
  302 |     - set_fact:
  303 |         owning_nodes_name: "{{ owning_nodes_name }} + [ '{{ item.adminNodeName }}' ]"
  304 |       with_items: "{{ owning_cluster_nodes.json.nodes }}"
  305 |       run_once: True
  306 | 
  307 | #
  308 | # This Section is when using daemonNodeName
  309 | #
  310 |     - name: "Remote Cluster Config - API-CLI | Storage Cluster (owner) | GET daemonNodeName Info - GET {{ scale_remotemount_scalemgmt_endpoint }}/nodes/"
  311 |       uri:
  312 |         validate_certs: "{{ scale_remotemount_validate_certs_uri }}"
  313 |         ca_path: "{{ scale_remotemount_ca_bundle_path | default(omit) }}"
  314 |         force_basic_auth: yes
  315 |         url: https://{{ scale_remotemount_storage_gui_hostname }}:{{ scale_remotemount_storage_cluster_gui_port }}/{{ scale_remotemount_scalemgmt_endpoint }}/nodes/{{item}}
  316 |         method: GET
  317 |         user: "{{ scale_remotemount_storage_gui_username }}"
  318 |         password: "{{ scale_remotemount_storage_gui_password }}"
  319 |         body_format: json
  320 |         status_code:
  321 |          - 200
  322 |       register: owning_cluster_daemonnodes
  323 |       with_items: "{{ owning_nodes_name }}"
  324 |       run_once: True
  325 | 
  326 |     - set_fact:
  327 |         owning_daemon_nodes_name: []
  328 |       run_once: True
  329 | 
  330 | 
  331 |     - set_fact:
  332 |         owning_daemon_nodes_name: "{{ owning_daemon_nodes_name }} + [ '{{ item.json.nodes.0.network.daemonNodeName }}' ]"
  333 |       with_items: "{{ owning_cluster_daemonnodes.results }}"
  334 |       run_once: True
  335 | 
  336 | 
  337 | #
  338 | # adminNodeName section
  339 | #
  340 |     - name: Remote Cluster Config - API-CLI | scale_remotemount_debug | Print out the array storing the AdminNodeNames from the Storage Cluster (owning)
  341 |       debug:
  342 |         msg: "{{ owning_nodes_name }}"
  343 |       when: scale_remotemount_debug is defined and scale_remotemount_debug | bool
  344 |       run_once: True
  345 | 
  346 |     - name: Remote Cluster Config - API-CLI | Client Cluster (Access) | Install storage cluster (owner) public key in remote cluster with adminNodeName
  347 |       run_once: True
  348 |       shell: |
  349 |         /usr/lpp/mmfs/bin/mmremotecluster add {{ owning_cluster_name | quote }} -n {{ owning_nodes_name | map('quote') | join(',') }} -k {{ scale_remotemount_storage_pub_key_location | quote }}
  350 |       register: remote_cluster_add_ssh
  351 |       failed_when:
  352 |         - "remote_cluster_add_ssh.rc != 0 and 'is already defined' not in remote_cluster_add_ssh.stderr"
  353 |       when: scale_remotemount_storage_adminnodename is defined and scale_remotemount_storage_adminnodename | bool
  354 | #
  355 | # deamonNodeName section
  356 | #
  357 |     - name: Remote Cluster Config - API-CLI | scale_remotemount_debug | Print out the array storing the DeamonNodeNames from the Storage Cluster (owning)
  358 |       debug:
  359 |         msg: "{{ owning_daemon_nodes_name }}"
  360 |       when: scale_remotemount_debug is defined and scale_remotemount_debug | bool
  361 |       run_once: True
  362 | 
  363 |     - name: Remote Cluster Config - API-CLI | Client Cluster (Access) |  Install storage cluster (owner) public key in remote cluster with daemonNodeName
  364 |       run_once: True
  365 |       shell: |
  366 |         /usr/lpp/mmfs/bin/mmremotecluster add {{ owning_cluster_name | quote }} -n {{ owning_daemon_nodes_name | map('quote') | join(',') }} -k {{ scale_remotemount_storage_pub_key_location | quote }}
  367 |       register: remote_cluster_add_ssh
  368 |       failed_when:
  369 |         - "remote_cluster_add_ssh.rc != 0 and 'is already defined' not in remote_cluster_add_ssh.stderr"
  370 |       when: not scale_remotemount_storage_adminnodename
  371 | 
  372 |     - name: Remote Cluster Config - API-CLI | Client Cluster (Access) | Cleanup temporary keys.
  373 |       file:
  374 |         path: "{{ item }}"
  375 |         state: absent
  376 |       when:
  377 |         - scale_remotemount_storage_pub_key_delete | bool
  378 |       with_items:
  379 |        - "{{ scale_remotemount_storage_pub_key_location }}"
  380 |        - "{{ scale_remotemount_storage_pub_key_location_json }}"
  381 | 
  382 |   when:
  383 |     - (remote_clusters_results.status == 400) or (remote_cluster_check_owning_cluster.rc != 0) or (scale_remotemount_forceRun | bool)
```
