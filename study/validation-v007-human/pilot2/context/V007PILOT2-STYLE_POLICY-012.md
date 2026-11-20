# Frozen source context: V007PILOT2-STYLE_POLICY-012

- Repository: `gdcc/dataverse-ansible`
- Commit: `ae29ce65dd4cddd5187c2bc00aefd319b6bb4484`
- Family: style_policy
- Rule: `ansibleguard/unnamed-task`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `tasks/main.yml` (reported anchor line 106)
- Flagged construct: not named by the finding; the anchor line 106 lies in the task at line 106, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–213 of 213:

```text
    1 | ---
    2 | # dataverse/tasks/main.yml
    3 | 
    4 | - name: begin dataverse ansible role
    5 |   debug:
    6 |     msg: '##### BEGIN ANSIBLE ROLE #####'
    7 | 
    8 | - ansible.builtin.import_tasks: sanity-checks.yml
    9 |   tags:
   10 |   - prereqs
   11 | 
   12 | - ansible.builtin.import_tasks: dataverse-prereqs.yml
   13 |   tags: 
   14 |   - prereqs
   15 | 
   16 | - ansible.builtin.import_tasks: dataverse-required-variables.yml
   17 |   tags:
   18 |    - always
   19 | 
   20 | - ansible.builtin.import_tasks: ansible-scripts.yml
   21 |   tags:
   22 |    - always
   23 |    - scripts
   24 | 
   25 | - ansible.builtin.import_tasks: rserve.yml
   26 |   when: rserve.install == true
   27 |   tags:
   28 |   - rserve
   29 | 
   30 | - ansible.builtin.import_tasks: dataverse-fqdn.yml
   31 |   tags:
   32 |    - prereqs
   33 |    - apache
   34 |    - fqdn
   35 |    - dataverse
   36 | 
   37 | - ansible.builtin.import_tasks: sshkeys.yml
   38 |   when: sshkeys.enabled == True
   39 |   tags:
   40 |   - sshkeys
   41 | 
   42 | - ansible.builtin.import_tasks: postfix.yml
   43 |   when: postfix.enabled == true
   44 |   tags:
   45 |   - postfix
   46 | 
   47 | - ansible.builtin.import_tasks: dataverse-apache.yml
   48 |   when: apache.enabled == True
   49 |   tags:
   50 |   - apache
   51 | 
   52 | - ansible.builtin.import_tasks: postgres.yml
   53 |   when: db.postgres.enabled == True
   54 |   tags:
   55 |   - postgres
   56 | 
   57 | - ansible.builtin.import_tasks: dataverse-branch.yml
   58 |   when: dataverse_branch != "release"
   59 |   tags:
   60 |   - dataverse
   61 | 
   62 | - ansible.builtin.import_tasks: jacoco-download.yml
   63 |   when: dataverse.jacoco.enabled == true and
   64 |         dataverse_repo != "release"
   65 | 
   66 | - ansible.builtin.import_tasks: dataverse-installer.yml
   67 |   tags:
   68 |   - payara
   69 | 
   70 | - ansible.builtin.import_tasks: payara.yml
   71 |   tags:
   72 |   - payara
   73 | 
   74 | - ansible.builtin.import_tasks: tasks/extra-certificate-authorities.yml
   75 |   when:
   76 |    - extra_certificates is defined
   77 |    - extra_certificates.files is defined
   78 |    - extra_certificates.files
   79 |   tags:
   80 |    - extracerts
   81 | 
   82 | - ansible.builtin.import_tasks: solr.yml
   83 |   tags:
   84 |   - solr
   85 | 
   86 | - ansible.builtin.import_tasks: localstack.yml
   87 |   when: localstack.enabled == true
   88 |   tags:
   89 |   - localstack
   90 | 
   91 | - ansible.builtin.import_tasks: s3.yml
   92 |   when: s3.enabled == true
   93 |   tags:
   94 |   - s3
   95 | 
   96 | - ansible.builtin.import_tasks: localstack_create.yml
   97 |   when: localstack.enabled == true
   98 |   tags:
   99 |   - localstack 
  100 | 
  101 | - ansible.builtin.import_tasks: minio.yml
  102 |   when: minio.enabled == true
  103 |   tags:
  104 |   - minio
  105 | 
  106 | - ansible.builtin.import_tasks: dataverse-install.yml
  107 |   tags:
  108 |   - dataverse
  109 | 
  110 | - ansible.builtin.import_tasks: dataverse-storage.yml
  111 |   when: dataverse.filesdirs[0] is defined
  112 |   tags:
  113 |   - storage
  114 | 
  115 | - ansible.builtin.import_tasks: dataverse-postinstall.yml
  116 |   tags:
  117 |   - postinstall
  118 | 
  119 | - ansible.builtin.import_tasks: dataverse-frontend.yml
  120 |   tags:
  121 |   - frontend
  122 |   when: dataverse.frontend.enabled
  123 | 
  124 | - ansible.builtin.import_tasks: dataverse-gui.yml
  125 |   tags:
  126 |   - gui
  127 |   when: dataverse.branding.enabled
  128 | 
  129 | - ansible.builtin.import_tasks: shibboleth.yml
  130 |   when: shibboleth.enabled == True
  131 |   tags:
  132 |   - shibboleth
  133 | 
  134 | - ansible.builtin.import_tasks: orcid.yml
  135 |   when: orcid.enabled == "true"
  136 |   tags:
  137 |   - orcid
  138 | 
  139 | - ansible.builtin.import_tasks: sampledata.yml
  140 |   when: dataverse.sampledata.enabled == true
  141 |   tags:
  142 |   - sampledata
  143 | 
  144 | - ansible.builtin.import_tasks: custom_sampledata.yml
  145 |   when: dataverse.custom_sampledata.enabled == true
  146 |   tags:
  147 |   - custom_sampledata
  148 | 
  149 | - ansible.builtin.import_tasks: dataverse-counter.yml
  150 |   when: dataverse.counter.enabled == true
  151 |   tags:
  152 |   - counter
  153 | 
  154 | - ansible.builtin.import_tasks: dataverse-previewers.yml
  155 |   when: dataverse.previewers.enabled == true
  156 |   tags:
  157 |   - previewers
  158 | 
  159 | - ansible.builtin.import_tasks: dataverse-languages.yml
  160 |   when: dataverse.language.enabled == true
  161 |   tags:
  162 |   - languages
  163 | 
  164 | - ansible.builtin.import_tasks: dataverse-licenses.yml
  165 |   when: dataverse.licenses.enabled == true
  166 |   tags:
  167 |   - licenses
  168 | 
  169 | - ansible.builtin.import_tasks: dataverse-externaltools.yml
  170 |   tags:
  171 |   - externaltools
  172 | 
  173 | - ansible.builtin.import_tasks: prometheus.yml
  174 |   when: prometheus.install == true
  175 |   tags:
  176 |   - prometheus
  177 | 
  178 | - ansible.builtin.import_tasks: dataverse-api-testsuite.yml
  179 |   when: dataverse.api.test_suite == true
  180 |   tags:
  181 |   - apitestsuite
  182 | 
  183 | - ansible.builtin.import_tasks: postgresql_perl_party.yml
  184 |   when: db.postgres.query_counts == true
  185 |   tags:
  186 |   - query_counts
  187 | 
  188 | - ansible.builtin.import_tasks: jacoco-generate_report.yml
  189 |   when: dataverse.jacoco.enabled == true and
  190 |         dataverse_repo != "release"
  191 | 
  192 | - ansible.builtin.import_tasks: build_guides.yml
  193 |   when: build_guides == true
  194 |   tags:
  195 |   - build_guides
  196 | 
  197 | - ansible.builtin.import_tasks: munin.yml
  198 |   when: munin.install == true
  199 |   tags:
  200 |   - munin
  201 | 
  202 | - ansible.builtin.import_tasks: pg_backups.yml
  203 |   when: db.backups.enabled == true
  204 |   tags:
  205 |   - pg_backups
  206 | 
  207 | - ansible.builtin.import_tasks: schemaspy.yml
  208 |   when: schemaspy.enabled == true
  209 |   tags:
  210 |   - schemaspy
  211 | 
  212 | - ansible.builtin.import_tasks: fin.yml
  213 |   
```
