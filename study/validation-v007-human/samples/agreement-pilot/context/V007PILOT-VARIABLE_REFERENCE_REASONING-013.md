# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-013

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/role-variable-precedence-collision`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/solr9cloud/vars/main.yml` (reported anchor line 3)
- Object: `variable` `ef8f55309b3c1208dbae897eac111c9eec4b0d2dc4d4981762be1d15f99285cd`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–28 of 28:

```text
    1 | ---
    2 | solr_cloud_build_name: "solr-{{ solr_cloud_download_version }}"
    3 | solr_cloud_package: "{{ solr_cloud_build_name }}.tgz"
    4 | solr_config_xml: "<str name=\"lucene-spec-version\">{{ solr_cloud_version }}</str>"
    5 | plugin_jars:
    6 |   - asm-7.3.1.jar
    7 |   - asm-commons-7.3.1.jar
    8 |   - asm-tree-7.3.1.jar
    9 |   - asm-util-7.3.1.jar
   10 |   - CJKFilterUtils-v4.0.jar
   11 |   - icu4j-74.2.jar
   12 |   - jolokia-agent-jvm-{{ jolokia_agent_version }}-javaagent.jar
   13 |   - jts-core-1.15.1.jar
   14 |   - lucene-analysis-icu-9.12.2.jar
   15 |   - lucene-umich-solr-filters-2.0-solr-9.0.0.jar
   16 |   - nashorn-core-15.4.jar
   17 | analysis_extra_jardirectory: "{{ solr_installation }}/modules/analysis-extras/lib"
   18 | analysis_extras_jars:
   19 |   - lucene-analysis-morfologik-9.12.2.jar
   20 |   - lucene-analysis-opennlp-9.12.2.jar
   21 |   - lucene-analysis-smartcn-9.12.2.jar
   22 |   - lucene-analysis-stempel-9.12.2.jar
   23 |   - morfologik-fsa-2.1.9.jar
   24 |   - morfologik-polish-2.1.9.jar
   25 |   - morfologik-stemming-2.1.9.jar
   26 |   - morfologik-ukrainian-search-4.9.1.jar
   27 |   - opennlp-tools-1.9.4.jar
   28 |   - solr-analysis-extras-9.9.0.jar
```

## Visible variable references

```text
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/defaults/main.yml:4:solr_cloud_package: "{{ solr_cloud_build_name }}.tgz"
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/defaults/main.yml:8:solr_cloud_url: "https://pulmirror.princeton.edu/mirror/solr/{{ solr_cloud_download_version }}/{{ solr_cloud_package }}"
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/tasks/install.yml:14:    src: "/tmp/{{ solr_cloud_package }}"
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/tasks/main.yml:74:    dest: "/tmp/{{ solr_cloud_package }}"
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/tasks/main.yml:88:    src: "local_files/solr/{{ solr_cloud_package }}"
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/tasks/main.yml:89:    dest: "/tmp/{{ solr_cloud_package }}"
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/tasks/main.yml:166:    path: "/tmp/{{ solr_cloud_package }}"
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/tasks/main.yml:176:    - "/tmp/{{ solr_cloud_package }}"
5f01e9a8e80ce332b7c3710302ed1e5af00ebe91:roles/solr9cloud/vars/main.yml:3:solr_cloud_package: "{{ solr_cloud_build_name }}.tgz"
```
