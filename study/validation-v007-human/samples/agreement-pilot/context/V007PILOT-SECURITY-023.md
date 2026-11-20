# Frozen source context: V007PILOT-SECURITY-023

- Repository: `cradle8810/ansible_hayaworld`
- Commit: `d458c0db8fe44340eb3ecd3ce9dee58ebc6e0597`
- Family: Security
- Rule: `ansibleguard/credentials-leaking-in-log`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/gui/tasks/packages/install_rdp.yml` (reported anchor line 68)
- Object: `task` `122764dede194ba89e18dbfe8f0866c9d73314deaed9b9997b123fdd2d9546aa`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–86 of 86:

```text
    1 | ---
    2 | - name: "RDP / Installing RDP (X11/For Not Ubuntu 25.10)"
    3 |   when: not gui_wayland
    4 |   ansible.builtin.apt:
    5 |     install_recommends: false
    6 |     update_cache: true
    7 |     cache_valid_time: "{{ common_apt.cache_valid_time }}"
    8 |     pkg:
    9 |       - xorgxrdp
   10 |       - xrdp
   11 |       - xserver-xorg-video-intel
   12 |   notify: "Restart xrdp"
   13 | 
   14 | # https://github.com/rustdesk/rustdesk/discussions/10016
   15 | - name: "RDP / Installing RDP (Wayland/For Ubuntu 25.04 or more)"
   16 |   when: gui_wayland
   17 |   block:
   18 |     - name: "Remove xrdp"
   19 |       ansible.builtin.apt:
   20 |         state: absent
   21 |         cache_valid_time: "{{ common_apt.cache_valid_time }}"
   22 |         pkg:
   23 |           - xorgxrdp
   24 |           - xrdp
   25 |           - xserver-xorg-video-intel
   26 | 
   27 |     - name: "Installing RDP server for Wayland"
   28 |       ansible.builtin.apt:
   29 |         install_recommends: false
   30 |         update_cache: true
   31 |         cache_valid_time: "{{ common_apt.cache_valid_time }}"
   32 |         pkg:
   33 |           - gnome-remote-desktop
   34 |           - winpr-utils
   35 | 
   36 |     - name: Create Certdir
   37 |       ansible.builtin.file:
   38 |         path: "/etc/gnome-remote-desktop"
   39 |         state: directory
   40 |         owner: "root"
   41 |         group: "root"
   42 |         mode: '0755'
   43 | 
   44 |     - name: "Check rdp is already configurated"
   45 |       ansible.builtin.stat:
   46 |         path: "/etc/gnome-remote-desktop/configurated"
   47 |       register: gui_wayland_rdp_configurated
   48 | 
   49 |     - name: "RDP Configurations"
   50 |       when: not gui_wayland_rdp_configurated.stat.exists
   51 |       notify: "Restart gnome-remote-desktop.service"
   52 |       become: true
   53 |       block:
   54 |         - name: "Ensure certificates directory exists"
   55 |           ansible.builtin.file:
   56 |             path: "/etc/gnome-remote-desktop/certificates"
   57 |             state: directory
   58 |             owner: root
   59 |             group: root
   60 |             mode: '0755'
   61 | 
   62 |         - name: "Create WinPR makecert"
   63 |           ansible.builtin.command:
   64 |             cmd: "winpr-makecert -silent -rdp -y 2 -path /etc/gnome-remote-desktop/certificates rdp-tls"
   65 |           register: retval
   66 |           changed_when: retval.rc == 0
   67 | 
   68 |         - name: "Configure System RDP"
   69 |           ansible.builtin.shell:
   70 |             cmd: |
   71 |               grdctl --system rdp enable
   72 |               grdctl --system rdp disable-view-only
   73 |               grdctl --system rdp set-credentials "{{ gui_wayland_user }}" "{{ gui_wayland_passwd }}"
   74 |               grdctl --system rdp set-tls-cert /etc/gnome-remote-desktop/certificates/rdp-tls.crt
   75 |               grdctl --system rdp set-tls-key /etc/gnome-remote-desktop/certificates/rdp-tls.key
   76 |           register: retval
   77 |           changed_when: retval.rc == 0
   78 | 
   79 |     - name: "Mark as rdp is already configurated"
   80 |       ansible.builtin.file:
   81 |         path: "/etc/gnome-remote-desktop/configurated"
   82 |         state: touch
   83 |         owner: root
   84 |         group: root
   85 |         mode: '0644'
   86 |       become: true
```
