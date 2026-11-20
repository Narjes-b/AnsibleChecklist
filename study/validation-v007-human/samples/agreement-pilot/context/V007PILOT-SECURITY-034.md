# Frozen source context: V007PILOT-SECURITY-034

- Repository: `JenswBE/setup`
- Commit: `18c39275cc08ae3f7bea8b7ee0624876b8fa72fe`
- Family: Security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `radio/physical_and_tts/jingles.yml` (reported anchor line 1)
- Object: `source_location` `09a18a770752308076dcf73702fd06d295299eaa49d24752e30d71dde4790363`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–57 of 57:

```text
    1 | - name: Setup Jingles
    2 |   hosts: jingles
    3 |   remote_user: jens
    4 |   become: true
    5 | 
    6 |   tasks:
    7 |     - name: Upgrade system
    8 |       ansible.builtin.apt:
    9 |         update_cache: true
   10 |         upgrade: dist
   11 | 
   12 |     - name: Install dependencies
   13 |       ansible.builtin.package:
   14 |         name:
   15 |           - espeak
   16 |           - mpd
   17 |           - mpc
   18 | 
   19 |     - name: Copy mpd config file
   20 |       ansible.builtin.copy:
   21 |         src: mpd.conf
   22 |         dest: /etc/mpd.conf
   23 |         owner: mpd
   24 |         group: audio
   25 |         mode: "640"
   26 |         backup: true
   27 | 
   28 |     - name: Grant users pulse access
   29 |       command: adduser {{ item }} pulse-access
   30 |       with_items:
   31 |         - root
   32 |         - willemsensj
   33 |         - mpd
   34 | 
   35 |     - name: Install alsa-utils
   36 |       apt: pkg=alsa-utils state=installed
   37 | 
   38 |     - name: Unmute ALSA
   39 |       command: amixer sset Master {{ item }}
   40 |       with_items:
   41 |         - unmute
   42 |         - 100%
   43 |         - 75%
   44 | 
   45 |     - name: Copy radio program
   46 |       ansible.builtin.copy:
   47 |         src: radio.py
   48 |         dest: /usr/bin/radio
   49 |         owner: root
   50 |         group: root
   51 |         mode: "555"
   52 | 
   53 |     - name: restart machine
   54 |       shell: sleep 2 && shutdown -r now "Ansible updates triggered"
   55 |       async: 1
   56 |       poll: 0
   57 |       ignore_errors: true
```
