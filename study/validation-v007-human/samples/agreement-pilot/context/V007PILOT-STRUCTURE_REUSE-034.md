# Frozen source context: V007PILOT-STRUCTURE_REUSE-034

- Repository: `snowdrop/k8s-infra`
- Commit: `0a9fe0fb57bd9759833bb9974d5022d945b2647c`
- Family: Structure/reuse
- Rule: `ansibleguard/role-readme-absent`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible/roles/install_jenkins/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `44fddf1f7b533b842b07e3e454f9ec83fc214539842adccc4747d123f91d535e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–61 of 61:

```text
    1 | - assert:
    2 |     that:
    3 |       - "openshift_env.config_dir != ''"
    4 |     msg: "Unable to determine the Openshift configuration directory -> You are probably running an unsupported Openshift version or in an unsupported environment"
    5 | 
    6 | - name: Set master config file
    7 |   set_fact:
    8 |     config_file: "{{ openshift_env.config_dir }}/master/master-config.yaml"
    9 | 
   10 | - name: Generate patch using template
   11 |   template:
   12 |     src: "templates/jenkins_patch.json.j2"
   13 |     dest: /tmp/jenkins_patch.json
   14 | 
   15 | - name: Get patch file
   16 |   command: cat /tmp/jenkins_patch.json
   17 |   register: patch
   18 | 
   19 | - name: Patch master-config file
   20 |   command: "oc {{ openshift_env.oc_admin_kubeconfig_arg }} ex config patch {{ openshift_env.config_dir }}/master/master-config.yaml --patch '{{ patch.stdout }}'"
   21 |   register: r
   22 | 
   23 | - name: Copy patch to new master config file
   24 |   copy: content="{{ r.stdout }}" dest={{ openshift_env.master_config_file }}
   25 | 
   26 | - name: Restart master
   27 |   include_role:
   28 |     name: restart_master
   29 | 
   30 | - set_fact:
   31 |     namespace: "{{ infra_project | default('infra') }}"
   32 | 
   33 | - name: Create namespace
   34 |   command: "oc {{ openshift_env.oc_admin_kubeconfig_arg }} new-project {{ namespace }}"
   35 |   ignore_errors: true
   36 | 
   37 | - name: Set Jenkins app name
   38 |   set_fact:
   39 |     jenkins_app: jenkins-persistent
   40 | 
   41 | - name: Change scc permission to allow jenkins pod to run within the docker container using its userid
   42 |   shell: "oc {{ openshift_env.oc_admin_kubeconfig_arg }} adm policy add-scc-to-group anyuid system:authenticated -n {{ namespace }}"
   43 | 
   44 | - name: Install {{ jenkins_app }}
   45 |   command: "oc {{ openshift_env.oc_admin_kubeconfig_arg }} new-app JENKINS_PASSWORD=[REDACTED_LITERAL]
   46 | 
   47 | - name: Add role cluster admin to the jenkins service account
   48 |   command: "oc {{ openshift_env.oc_admin_kubeconfig_arg }} policy add-role-to-user admin system:serviceaccount:{{ namespace }}:jenkins"
   49 | 
   50 | - name: Get Jenkins Service Account Token
   51 |   command: "oc {{ openshift_env.oc_admin_kubeconfig_arg }} serviceaccounts get-token jenkins -n {{ namespace }}"
   52 |   register: sa_jenkins_token
   53 |   until: sa_jenkins_token.rc =[REDACTED_LITERAL]
   54 |   retries: 12
   55 |   delay: 10
   56 | 
   57 | - name: Print token
   58 |   debug:
   59 |     msg:
   60 |       - "Jenkins ServiceAccount token is"
   61 |       - "{{sa_jenkins_token.stdout}}"
```

## Frozen tracked paths in the relevant role/scope

```text
ansible/roles/install_jenkins/files/pvc-jenkins.yml
ansible/roles/install_jenkins/files/sa.yml
ansible/roles/install_jenkins/meta/main.yml
ansible/roles/install_jenkins/tasks/main.yml
ansible/roles/install_jenkins/templates/jenkins_patch.json.j2
```
