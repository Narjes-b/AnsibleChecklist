# Frozen source context: V007PILOT-STYLE_POLICY-022

- Repository: `AtlasOfLivingAustralia/ala-install`
- Commit: `aa2070a840f5debc3b78095c31b58004d04d2063`
- Family: Style/policy
- Rule: `ansibleguard/variable-naming-convention`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `ansible/roles/web2pyApps/vars/main.yml` (reported anchor line 23)
- Object: `variable` `f58073c8ef5d966ad7916a2b2d242f0a187fd41ffd39e6994fccc06fc133294c`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–29 of 29:

```text
    1 | parentDir: /data
    2 | web2pyAppDir: "{{web2pyDir}}/applications"
    3 | apiDir: "{{web2pyAppDir}}/api"
    4 | peyotlDir: "{{parentDir}}/peyotl"
    5 | phylesystemDir: "{{parentDir}}/phylesystem"
    6 | phylesystemDir0: "{{phylesystemDir}}/phylesystem-0"
    7 | phylesystemDir1: "{{phylesystemDir}}/phylesystem-1"
    8 | nclDir: "{{parentDir}}/ncl"
    9 | configDest: "{{apiDir}}/private/"
   10 | opentreeDir: "{{parentDir}}/opentree"
   11 | curatorDir: "{{opentreeDir}}/curator"
   12 | webappDir: "{{opentreeDir}}/webapp"
   13 | opentreeApp: opentree
   14 | curatorApp: curator
   15 | curatorAppDir: "{{web2pyAppDir}}/{{curatorApp}}"
   16 | opentreeAppDir: "{{web2pyAppDir}}/{{opentreeApp}}"
   17 | opentreeToolsDir: "{{parentDir}}/opentree-tools"
   18 | toNexmlDir: "{{parentDir}}/2nexml"
   19 | 
   20 | apiUrl: https://github.com/OpenTreeOfLife/phylesystem-api.git
   21 | peyotlUrl: https://github.com/OpenTreeOfLife/peyotl.git
   22 | nclGit: https://github.com/OpenTreeOfLife/ncl.git
   23 | phylesystemUrl0: https://github.com/OpenTreeOfLife/phylesystem.git
   24 | toNexmlGit: https://github.com/OpenTreeOfLife/2nexml.git
   25 | #phylesystemUrl1: https://github.com/OpenTreeOfLife/phylesystem-1.git
   26 | opentreeUrl: https://github.com/OpenTreeOfLife/opentree.git
   27 | opentreeVersion: 511c1184eff1184ff32b2b63338b01e89bc23223
   28 | apiVersion: 2facf54d170084b6777154490d1947b7395e324c
   29 | peyotlVersion: d8a164e907c3960f654b5356fb1fa4e60fb65522
```
