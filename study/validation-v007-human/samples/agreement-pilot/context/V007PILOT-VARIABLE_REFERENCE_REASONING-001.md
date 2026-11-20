# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-001

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/missing-bool-filters`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `ansible/roles/biocache-properties/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `ee487ac17048dbdf0b28f80a9fe274173ed188772718fd2119a26db51db74d2b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–70 of 70:

```text
    1 | - include_tasks: ../../common/tasks/setfacts.yml
    2 |   tags:
    3 |     - properties
    4 |     - biocache-properties
    5 |     - biocache-layers    
    6 | 
    7 | - name: ensure target directories exist
    8 |   file: path={{item}} state=directory
    9 |   with_items:
   10 |     - "{{data_dir}}/biocache/layers"
   11 |     - "{{data_dir}}/biocache/config"    
   12 |   tags:
   13 |     - properties
   14 |     - biocache-properties
   15 | 
   16 | - name: copy biocache config properties template 
   17 |   template: src={{item}} dest={{data_dir}}/biocache/config/{{item}} mode=0644 output_encoding=iso-8859-1
   18 |   with_items:
   19 |     - biocache-config.properties
   20 |   tags:
   21 |     - properties
   22 |     - properties-file
   23 |     - biocache-properties
   24 | 
   25 | - name: Download SDS layers
   26 |   get_url: url={{ sds_layers_url | default('https://archives.ala.org.au/archives/layers/sds-layers.tgz') }} dest="{{data_dir}}/biocache/layers/sds-layers.tgz" force=yes
   27 |   when: sds_enabled is defined and sds_enabled == "true"
   28 |   tags:
   29 |     - properties
   30 |     - biocache-properties
   31 |     - biocache-layers   
   32 | 
   33 | - name: Extract SDS layers
   34 |   unarchive: src="{{data_dir}}/biocache/layers/sds-layers.tgz" dest="{{data_dir}}/biocache/layers/" copy=no owner=root group=root extra_opts=--no-same-owner
   35 |   when: sds_enabled is defined and sds_enabled == "true"
   36 |   tags:
   37 |     - properties
   38 |     - biocache-properties
   39 |     - biocache-layers    
   40 | 
   41 | - name: copy biocache subgroups config
   42 |   copy: src=subgroups.json dest={{data_dir}}/biocache/config/subgroups.json
   43 |   tags:
   44 |     - properties
   45 |     - biocache-properties
   46 | 
   47 | - name: ensure target directories exist [data subdirectories etc.
   48 |   file: path={{ item }} state=directory mode=0775
   49 |   with_items:
   50 |     - "{{data_dir}}/biocache-load"
   51 |     - "{{data_dir}}/biocache-media"
   52 |     - "{{data_dir}}/biocache-upload"
   53 |     - "{{data_dir}}/biocache-upload/status"
   54 |     - "{{data_dir}}/biocache-upload/temp"
   55 |     - "{{data_dir}}/biocache-delete"
   56 |     - "{{data_dir}}/cache"
   57 |     - "{{data_dir}}/tmp"
   58 |     - "{{data_dir}}/offline/exports"    
   59 |     - "{{data_dir}}/tool"
   60 |   tags:
   61 |     - properties
   62 |     - biocache-properties
   63 | 
   64 | # - name: set data ownership [all data is owned by tomcat]
   65 | #   file: path={{data_dir}}/{{item}} owner={{tomcat_user}} group={{tomcat_user}} recurse=true
   66 | #   with_items:
   67 | #     - biocache 
   68 | #   tags:
   69 | #     - biocache-properties
   70 | #     - biocache-layers
```
