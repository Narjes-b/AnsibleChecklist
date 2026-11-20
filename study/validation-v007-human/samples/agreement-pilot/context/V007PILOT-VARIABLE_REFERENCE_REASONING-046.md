# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-046

- Repository: `kubevirt/project-infra`
- Commit: `2b204a6ee9bcf983613baf20f122fe2272dbcf3e`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unscoped-shell-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `github/ci/prow-deploy/tasks/main.yml` (reported anchor line 19)
- Object: `source_location` `0e567d4686533effdd9db4053df2177ed139c9876da6d5d24ea8e68fa423599d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–106 of 106:

```text
    1 | ---
    2 | - name: set deploy environment
    3 |   set_fact:
    4 |     deploy_environment: '{{ lookup("env", "DEPLOY_ENVIRONMENT") }}'
    5 |   when: deploy_environment is undefined
    6 | 
    7 | - name: Check deploy_environment
    8 |   fail:
    9 |     msg: DEPLOY_ENVIRONMENT must be set
   10 |   when: deploy_environment is undefined or deploy_environment == ""
   11 | 
   12 | - name: load deploy config from environment
   13 |   include_vars:
   14 |     dir: "./{{ deploy_environment }}"
   15 | 
   16 | - name: prepare docker proxy CA if needed
   17 |   when: dockerMirrorProxyCA is not defined
   18 |   block:
   19 |     - name: create docker mirror proxy CA files
   20 |       shell: |
   21 |         set -eo pipefail
   22 | 
   23 |         # testing keypair generated following https://github.com/rpardini/docker-registry-proxy/blob/master/create_ca_cert.sh
   24 |         CA_KEY_FILE=/tmp/ca.key
   25 |         CA_CRT_FILE=/tmp/ca.crt
   26 | 
   27 |         openssl genrsa -des3 -passout pass:[REDACTED_LITERAL]
   28 | 
   29 |         openssl req -new -x509 -days 1300 -sha256 -key ${CA_KEY_FILE} -out ${CA_CRT_FILE} -passin pass:[REDACTED_LITERAL]
   30 |         cat <<-EOF
   31 |         [req]
   32 |         distinguished_name = dn
   33 |         [dn]
   34 |         [IA]
   35 |         basicConstraints = critical,CA:TRUE
   36 |         keyUsage = critical, digitalSignature, cRLSign, keyCertSign
   37 |         subjectKeyIdentifier = hash
   38 |         EOF
   39 |         )
   40 | 
   41 |       args:
   42 |         executable: /bin/bash
   43 | 
   44 |     - name: get CA key file contents
   45 |       slurp:
   46 |         src: /tmp/ca.key
   47 |       register: caKey
   48 |     - name: get CA crt file contents
   49 |       slurp:
   50 |         src: /tmp/ca.crt
   51 |       register: caCrt
   52 | 
   53 |     - name: set docker mirror proxy tmp var
   54 |       set_fact:
   55 |         # we use a different variable here to let the loop iterate over all the
   56 |         # items, otherwise, given that the block executes if dockerMirrorProxyCA
   57 |         # is empty, after the first iteration (when dockerMirrorProxyCA is defined)
   58 |         # the loop stops
   59 |         dockerMirrorProxyCATmp: "{{ dockerMirrorProxyCATmp | default({}) | combine ({ item.key : item.value }) }}"
   60 |       with_items:
   61 |         - {'key': 'crt', 'value': '{{ caCrt["content"] | b64decode }}'}
   62 |         - {'key': 'key', 'value': '{{ caKey["content"] | b64decode }}'}
   63 | 
   64 |     - name: set docker mirror proxy var
   65 |       set_fact:
   66 |         dockerMirrorProxyCA: '{{ dockerMirrorProxyCATmp }}'
   67 | 
   68 | - name: create secret files
   69 |   include_tasks: secrets.yml
   70 | 
   71 | - name: create config files
   72 |   include_tasks: configs.yml
   73 | 
   74 | - name: patch test resources
   75 |   include_tasks: patch_test_resources.yml
   76 |   when: deploy_environment == "kubevirtci-testing"
   77 | 
   78 | - name: create templated resources
   79 |   include_tasks: resources.yml
   80 | 
   81 | - name: set kubectl context if needed
   82 |   when: remote_cluster_prow_jobs_context is defined
   83 |   block:
   84 |     - name: switch context
   85 |       shell: |
   86 |         kubectl config use-context {{ remote_cluster_prow_jobs_context }}
   87 |         kubectl config current-context
   88 | 
   89 |       environment:
   90 |         KUBECONFIG: "{{ kubeconfig_path }}"
   91 |       register: result
   92 | 
   93 |     - debug:
   94 |         var: result
   95 | 
   96 | - name: Launch deployment
   97 |   when: "'deploy' in main_actions"
   98 |   include_tasks: deploy.yml
   99 | 
  100 | - name: Run tests when in test environment
  101 |   include_tasks: tests.yml
  102 |   when: deploy_environment == "kubevirtci-testing"
  103 | 
  104 | - name: Launch cleanup
  105 |   include_tasks: cleanup.yml
  106 |   when: "'cleanup' in main_actions"
```
