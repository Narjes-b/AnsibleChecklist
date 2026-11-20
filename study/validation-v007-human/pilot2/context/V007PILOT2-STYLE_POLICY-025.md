# Frozen source context: V007PILOT2-STYLE_POLICY-025

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: style_policy
- Rule: `ansibleguard/missing-file-extension`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `onecloud/roles/utils/eip-ha/tasks/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`onecloud/roles/utils/eip-ha/tasks/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–98 of 98:

```text
    1 | ---
    2 | - name: EIP HA
    3 |   when:
    4 |     - vrrp_interface is defined
    5 |     - vrrp_vip is defined
    6 |   become: true
    7 |   block:
    8 |     - name: install sdnagent rpm
    9 |       package:
   10 |         name: yunion-sdnagent
   11 |         state: latest
   12 |       when:
   13 |       - is_centos_x86 is defined
   14 |       notify: restart eipgw
   15 | 
   16 |     - name: get vars
   17 |       shell: |
   18 |         /opt/yunion/bin/fetch-rcadmin.sh | sed \
   19 |         -e 's#export ##' \
   20 |         -e 's#OS_REGION_NAME#oc_region#' \
   21 |         -e 's#OS_AUTH_URL#oc_auth_url#' \
   22 |         -e 's#OS_USERNAME#oc_admin_user#' \
   23 |         -e 's#OS_PASSWORD#oc_admin_password#' \
   24 |         -e 's#OS_PROJECT_NAME#oc_admin_project#' \
   25 |         -e 's#=#: "#' \
   26 |         -e 's#$#"#' | \
   27 |         grep '^oc_'
   28 |       register: oc_vars
   29 |       delegate_to: "{{ k8s_controlplane_host }}"
   30 | 
   31 |     - name: write oc vars
   32 |       copy:
   33 |         content: "{{ oc_vars.stdout }}"
   34 |         dest: /tmp/oc_vars
   35 | 
   36 |     - name: get oc vars
   37 |       run_once: yes
   38 |       fetch:
   39 |         src: /tmp/oc_vars
   40 |         dest: /tmp/oc_vars
   41 |         flat: yes
   42 | 
   43 |     - name: load vars
   44 |       run_once: yes
   45 |       include_vars: /tmp/oc_vars
   46 | 
   47 |     - name: clean tmp files
   48 |       file:
   49 |         path: /tmp/oc_vars
   50 |         state: absent
   51 | 
   52 |     - name: enable ip forwarding
   53 |       sysctl:
   54 |         name: net.ipv4.ip_forward
   55 |         value: '1'
   56 |         sysctl_set: yes
   57 |         state: present
   58 |         reload: yes
   59 | 
   60 |     - name: make sdnagent.conf
   61 |       template:
   62 |         src: sdnagent.conf.j2
   63 |         dest: /etc/yunion/sdnagent.conf
   64 |       notify: restart eipgw
   65 | 
   66 |     - name: install keepalived
   67 |       package:
   68 |         name: keepalived
   69 |         state: present
   70 | 
   71 |     - name: mkdir /etc/keepalived
   72 |       file:
   73 |         name: /etc/keepalived
   74 |         state: directory
   75 |         owner: root
   76 |         group: root
   77 | 
   78 |     - name: make keepalived eipgw.conf
   79 |       template:
   80 |         src: keepalived-eipgw.conf.j2
   81 |         dest: /etc/keepalived/eipgw.conf
   82 |       vars:
   83 |         vrrp_notify_script: /etc/keepalived/eipgw-notify.sh
   84 |       notify: restart eipgw
   85 | 
   86 |     - name: copy keepalived notify script
   87 |       copy:
   88 |         src: keepalived-eipgw-notify.sh
   89 |         dest: /etc/keepalived/eipgw-notify.sh
   90 |         owner: root
   91 |         group: root
   92 |         mode: 0700
   93 | 
   94 |     - name: enable yunion-sdnagent-eipgw service
   95 |       service:
   96 |         name: yunion-sdnagent-eipgw
   97 |         state: started
   98 |         enabled: yes
```
