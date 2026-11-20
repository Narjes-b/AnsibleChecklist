# Frozen source context: V007PILOT-STYLE_POLICY-020

- Repository: `rtdevx/homelab`
- Commit: `a23266aa968127747db1aa91d544ab60ce402f55`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-play`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `ansible/site/configure_k3s.yml` (reported anchor line 23)
- Object: `source_location` `6e9408285ad3d58aa0666f08ee82d351514f0f7bd0812f6d8b95e95a8c187531`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–120 of 120:

```text
    1 | ---
    2 | # K3s prerequisuites
    3 | - hosts: k3s
    4 |   become: true
    5 |   roles:
    6 |     - k3s_configure_prereq
    7 | 
    8 | # K3s HA Proxy LB
    9 | - hosts: k3slb
   10 |   become: true
   11 |   roles:
   12 |     - k3s_configure_haproxy
   13 | 
   14 | # Initialize K3s Control Plane
   15 | - hosts: k3ssvr[0]
   16 |   become: true
   17 |   roles:
   18 |     - k3s_initialize_control_plane
   19 |   vars_files:
   20 |     - roles/k3s_initialize_control_plane/vars/secrets.encrypted
   21 | 
   22 | # Join K3s Control Plane Servers
   23 | - hosts: k3ssvr[1:2]
   24 |   become: true
   25 |   roles:
   26 |     - k3s_initialize_join_svr
   27 |   vars_files:
   28 |     - roles/k3s_initialize_control_plane/vars/secrets.encrypted
   29 | # note: vars_files (encrypted secrets) are not stored in this role but in the role where the cluster is being initialized (k3s_initialize_control_plane).
   30 | 
   31 | # Join K3s Agent Nodes
   32 | - hosts: k3sagt
   33 |   become: true
   34 |   roles:
   35 |     - k3s_initialize_join_agt
   36 |   vars_files:
   37 |     - roles/k3s_initialize_control_plane/vars/secrets.encrypted    
   38 | # note: vars_files (encrypted secrets) are not stored in this role but in the role where the cluster is being initialized (k3s_initialize_control_plane).
   39 | 
   40 | # info: Configure K3s Manager
   41 | 
   42 | # Execute k3s_configure_mgr role on the K3s manager server (Install and configure kubectl,k9s)
   43 | - hosts: k3smgr
   44 |   become: true
   45 |   roles:
   46 |     - k3s_configure_mgr
   47 | 
   48 | # Check if k3s.yaml file exists on the K3s server and fetch it to the temporary location if it does not exist
   49 | 
   50 | # @high Should /tmp be changed to something else so the file is not lost after reboot and is only accessible by root?
   51 | # @low Can the checksum of the downloaded file be verified to ensure integrity?
   52 | 
   53 | - name: Check if /tmp/k3s.yaml exists on the K3s server
   54 |   tags: k3s,mgr
   55 |   hosts: k3ssvr[0]
   56 |   tasks:
   57 |   - name: Check if /tmp/k3s.yaml exists on the K3s server
   58 |     stat:
   59 |       path: /tmp/k3s.yaml
   60 |     register: k3syaml_stat
   61 |   become: true
   62 | 
   63 | - name: Fetch /etc/rancher/k3s/k3s.yaml from the K3s server to Temporary location
   64 |   hosts: k3ssvr[0]
   65 |   tasks:
   66 |     - name: Fetch file from source server
   67 |       fetch:
   68 |         src: /etc/rancher/k3s/k3s.yaml
   69 |         dest: /tmp/k3s.yaml
   70 |         flat: yes
   71 |       become: true
   72 |       when: k3syaml_stat.stat.exists == false
   73 | 
   74 | # Check if /home/k3s/.kube/config exists on the manager server, copy and rename it if it does not exist
   75 | - name: Check if /home/k3s/.kube/config exists on the manager server
   76 |   tags: k3s,mgr
   77 |   hosts: k3smgr 
   78 |   tasks:
   79 |   - name: Check if kubeconfig file exists
   80 |     stat:
   81 |       path: /home/k3s/.kube/config
   82 |     register: kubeconfig_stat
   83 |   become: true
   84 | 
   85 | - name: Copy file to destination server
   86 |   hosts: k3smgr
   87 |   tasks:
   88 |     - name: Copy k3s.yaml file to the manager server
   89 |       copy:
   90 |         src: /tmp/k3s.yaml
   91 |         dest: /home/k3s/.kube/config
   92 |         owner: k3s
   93 |         group: k3s
   94 |         mode: '0600'
   95 |       become: true
   96 |       when: kubeconfig_stat.stat.exists == false  
   97 | 
   98 | # Configure K3s Manager kubeconfig file
   99 | - name: Check if "/home/k3s/.kube/config" is already configured
  100 |   tags: k3s,lb
  101 |   hosts: k3smgr
  102 |   tasks:
  103 |     - name: Check if kubeconfig file exists
  104 |       command: 'grep "    server: https://127.0.0.1:6443" /home/k3s/.kube/config'
  105 |       register: kubeconfig_vip_check
  106 |       ignore_errors: true
  107 |       changed_when: false  # Ensure task is marked as "ok" instead of "changed" in the output
  108 |       failed_when: false  # Suppress output error if grep doesn't find a match
  109 | 
  110 | - name: Update /home/k3s/.kube/config LB address
  111 |   tags: k3s,lb
  112 |   hosts: k3smgr
  113 |   tasks:
  114 |     - name: Update LB address in kubeconfig
  115 |       lineinfile:
  116 |         path: /home/k3s/.kube/config
  117 |         regexp: "^    server"
  118 |         line: "    server: https://{{ lb_vip }}:6443"
  119 |       when: kubeconfig_vip_check.rc != 0 
  120 |   become: true          
```
