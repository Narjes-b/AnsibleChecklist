# Frozen source context: V007PILOT2-SECURITY-007

- Repository: `igou-io/igou-ansible`
- Commit: `5dac3e63735e0e15407c172e0abd56d431fe4e47`
- Family: security
- Rule: `ansibleguard/unsafe-file-write`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `roles/zfs_pool/tasks/install.yml` (reported anchor line 98)
- Flagged construct: not named by the finding; the anchor line 98 lies in the task at line 98, name `Apply zfs_arc_max live`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–117 of 117:

```text
    1 | ---
    2 | - name: Enable the backports apt suite (zfs lives in contrib)
    3 |   ansible.builtin.deb822_repository:
    4 |     name: debian-backports
    5 |     types: deb
    6 |     uris: http://deb.debian.org/debian
    7 |     suites: "{{ zfs_pool_apt_suite }}"
    8 |     components:
    9 |       - main
   10 |       - contrib
   11 |     signed_by: /usr/share/keyrings/debian-archive-keyring.gpg
   12 |     state: present
   13 |     # minimal Armbian images ship without python3-debian, which this
   14 |     # module needs on the target; let it install it.
   15 |     install_python_debian: true
   16 | 
   17 | # Backports default to Pin-Priority 100 (< 500), so apt would never
   18 | # select them without this. src:zfs-linux pins the whole source package
   19 | # instead of enumerating the shifting libzfs/libzpool binary names.
   20 | - name: Pin src:zfs-linux to the backports suite
   21 |   ansible.builtin.copy:
   22 |     dest: /etc/apt/preferences.d/90-zfs-backports.pref
   23 |     owner: root
   24 |     group: root
   25 |     mode: "0644"
   26 |     content: |
   27 |       Package: src:zfs-linux
   28 |       Pin: release n={{ zfs_pool_apt_suite }}
   29 |       Pin-Priority: 990
   30 | 
   31 | - name: Stat kernel headers for the running kernel
   32 |   ansible.builtin.stat:
   33 |     path: "/usr/src/linux-headers-{{ ansible_facts['kernel'] }}"
   34 |   register: __zfs_pool_headers
   35 | 
   36 | # Catch this before apt: without headers the zfs-dkms postinst "fails"
   37 | # 20 minutes in with a much less obvious error.
   38 | - name: Assert kernel headers are installed (DKMS prerequisite)
   39 |   ansible.builtin.assert:
   40 |     that:
   41 |       - __zfs_pool_headers.stat.exists
   42 |     fail_msg: >-
   43 |       /usr/src/linux-headers-{{ ansible_facts['kernel'] }} is missing —
   44 |       zfs-dkms cannot build against the running kernel. The Armbian
   45 |       image must ship its own headers package: set
   46 |       armbian_build_model.compile_args.INSTALL_HEADERS="yes" for this
   47 |       board (see group_vars/cm3588_nas.yml), rebuild with
   48 |       armbian_build_force=true, and reimage.
   49 | 
   50 | # DKMS build of zfs on the RK3588 takes ~10-15 min; async keeps the
   51 | # task alive across any SSH hiccup instead of dying mid-build.
   52 | - name: Install zfs-dkms + zfsutils-linux from backports (long DKMS build)
   53 |   ansible.builtin.apt:
   54 |     name:
   55 |       - zfs-dkms
   56 |       - zfsutils-linux
   57 |       # ZED is a separate package on Debian; without it
   58 |       # zfs-zed.service does not exist and the enable task fails.
   59 |       - zfs-zed
   60 |     default_release: "{{ zfs_pool_apt_suite }}"
   61 |     update_cache: true
   62 |     state: present
   63 |   environment:
   64 |     DEBIAN_FRONTEND: noninteractive
   65 |   async: 2700
   66 |   poll: 30
   67 | 
   68 | - name: Cap ARC via modprobe options
   69 |   ansible.builtin.copy:
   70 |     dest: /etc/modprobe.d/zfs.conf
   71 |     owner: root
   72 |     group: root
   73 |     mode: "0644"
   74 |     content: |
   75 |       options zfs zfs_arc_max={{ zfs_pool_arc_max_bytes }}
   76 |   when: zfs_pool_arc_max_bytes is defined
   77 | 
   78 | - name: Load the zfs module at boot
   79 |   ansible.builtin.copy:
   80 |     dest: /etc/modules-load.d/zfs.conf
   81 |     owner: root
   82 |     group: root
   83 |     mode: "0644"
   84 |     content: |
   85 |       zfs
   86 | 
   87 | - name: Load the zfs module now
   88 |   community.general.modprobe:
   89 |     name: zfs
   90 |     state: present
   91 | 
   92 | - name: Read live zfs_arc_max
   93 |   ansible.builtin.command: cat /sys/module/zfs/parameters/zfs_arc_max
   94 |   register: __zfs_pool_arc_live
   95 |   changed_when: false
   96 |   when: zfs_pool_arc_max_bytes is defined
   97 | 
   98 | - name: Apply zfs_arc_max live
   99 |   ansible.builtin.copy:
  100 |     dest: /sys/module/zfs/parameters/zfs_arc_max
  101 |     content: "{{ zfs_pool_arc_max_bytes }}"
  102 |     unsafe_writes: true
  103 |     mode: "0644"
  104 |   when:
  105 |     - zfs_pool_arc_max_bytes is defined
  106 |     - __zfs_pool_arc_live.stdout | trim != zfs_pool_arc_max_bytes | string
  107 | 
  108 | - name: Enable ZFS boot-time import/mount services
  109 |   ansible.builtin.systemd_service:
  110 |     name: "{{ item }}"
  111 |     enabled: true
  112 |   loop:
  113 |     - zfs-import-cache.service
  114 |     - zfs-import.target
  115 |     - zfs-mount.service
  116 |     - zfs.target
  117 |     - zfs-zed.service
```
