# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-040

- Repository: `pulibrary/princeton_ansible`
- Commit: `5f01e9a8e80ce332b7c3710302ed1e5af00ebe91`
- Family: Objective correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/studio_proc/tasks/main.yml` (reported anchor line 34)
- Object: `task` `d51b1410bfb5f109980ff242983c43bd161cb04aacc2d361488fe2806688825f`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–74 of 74:

```text
    1 | ---
    2 | # tasks file for lib_proc4
    3 | - name: Create mount directories
    4 |   file:
    5 |     path: "/mnt/{{ item }}"
    6 |     state: "directory"
    7 |     mode: 0755
    8 |   loop:
    9 |     - libimages
   10 |     - diglibdata
   11 |     - hydra_sources
   12 | 
   13 | - name: Copy smb credentials
   14 |   copy:
   15 |     src: "files/{{ item }}"
   16 |     dest: "/etc/{{ item }}"
   17 |     mode: 0644
   18 |   when:
   19 |     - running_on_server
   20 |   loop:
   21 |     - libimages.smb.credentials
   22 |     - bluemountain.smb.credentials
   23 |     - archives.smb.credentials
   24 |     - archives_bd.smb.credentials
   25 |     - historicalperiodicals.smb.credentials
   26 |     - princetonperiodicals.smb.credentials
   27 |     - pudl.smb.credentials
   28 |     - ddd.smb.credentials
   29 |     - pul_store.smb.credentials
   30 |     - ingest_scratch.smb.credentials
   31 |     - studio.new.smb.credentials
   32 | 
   33 | - name: Create mount to diglibdata shares
   34 |   mount:
   35 |     path: "/mnt/diglibdata/{{ item.path }}"
   36 |     src: "//diglibdata1.princeton.edu/{{ item.src }}"
   37 |     fstype: cifs
   38 |     opts: "credentials=[REDACTED_LITERAL]
   39 |     state: mounted
   40 |   when:
   41 |     - running_on_server
   42 |   loop:
   43 |     - {path: "bluemountain", src: "bluemountain", opts: "bluemountain"}
   44 |     - {path: "archives", src: "archives", opts: "archives"}
   45 |     - {path: "archives_bd", src: "archives_bd", opts: "archives_bd"}
   46 |     - {path: "ddd", src: "ddd", opts: "ddd"}
   47 |     - {path: "historicalperiodicals", src: "historicalperiodicals", opts: "historicalperiodicals"}
   48 |     - {path: "princetonperiodicals", src: "princetonperiodicals", opts: "princetonperiodicals"}
   49 |     - {path: "pudl", src: "pudl", opts: "pudl"}
   50 |     - {path: "pul_store", src: "pul_store", opts: "pul_store"}
   51 |     - {path: "ingest_scratch", src: "hydra/binaries/ingest_scratch", opts: "ingest_scratch"}
   52 |   become: true
   53 | 
   54 | - name: Create mount to libimages shares
   55 |   mount:
   56 |     path: "/mnt/libimages/data"
   57 |     src: "//libimages.princeton.edu/data"
   58 |     fstype: cifs
   59 |     opts: "credentials=[REDACTED_LITERAL]
   60 |     state: mounted
   61 |   when:
   62 |     - running_on_server
   63 |   become: true
   64 | 
   65 | - name: Create mount to new studio shares
   66 |   mount:
   67 |     path: "/mnt/hydra_sources/studio_new"
   68 |     src: "//lib-dps-server.princeton.edu/studio"
   69 |     fstype: cifs
   70 |     opts: "credentials=[REDACTED_LITERAL]
   71 |     state: mounted
   72 |   when:
   73 |     - running_on_server
   74 |   become: true
```
