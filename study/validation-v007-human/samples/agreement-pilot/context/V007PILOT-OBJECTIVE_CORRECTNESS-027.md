# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-027

- Repository: `igou-io/igou-ansible`
- Commit: `5dac3e63735e0e15407c172e0abd56d431fe4e47`
- Family: Objective correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `playbooks/rpi-image/build.yml` (reported anchor line 114)
- Object: `source_location` `f09fecbbcd4141b69b4f10b09047004fc3264387607a815ac3cc3541c85e5a86`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–143 of 143:

```text
    1 | ---
    2 | # Build, verify and publish a Raspberry Pi OS image with rpi-image-gen.
    3 | #
    4 | #   ansible-playbook playbooks/rpi-image/build.yml \
    5 | #     -i ../igou-inventory/inventory.yaml
    6 | #
    7 | # Useful overrides:
    8 | #   -e rpi_image_hostname=foo        host-specific image
    9 | #   -e rpi_image_config=bar          alternate config/publish name
   10 | #   -e rpi_image_user1passhash=[REDACTED_LITERAL]
   11 | #
   12 | # Stages: render config -> build (async) -> verify (loop-mount
   13 | # assertions against the produced image) -> publish (xz + sha256 +
   14 | # latest symlink + retention prune). A build that fails verification
   15 | # is not published.
   16 | 
   17 | - name: Build a Raspberry Pi OS image with rpi-image-gen
   18 |   hosts: rpi_image_builders
   19 |   become: false
   20 |   gather_facts: false
   21 | 
   22 |   vars:
   23 |     rpi_image_config: "{{ rpi_image_default_config }}"
   24 |     rpi_image_workdir: "{{ rpi_image_root }}/rpi-image-gen/work"
   25 |     rpi_image_publish_config_dir: >-
   26 |       {{ rpi_image_publish_dir }}/{{ rpi_image_config }}
   27 | 
   28 |   tasks:
   29 |     # set_fact evaluates the lookup exactly once. As a lazy play var,
   30 |     # every reference would re-run `date` and the publish path, latest
   31 |     # symlink and set_stats could disagree (seen on the first live run).
   32 |     - name: Pin build id
   33 |       ansible.builtin.set_fact:
   34 |         rpi_image_build_id: >-
   35 |           {{ lookup('ansible.builtin.pipe', 'date -u +%Y%m%dT%H%M%SZ') }}
   36 | 
   37 |     - name: Assert pinned rpi-image-gen checkout is present
   38 |       ansible.builtin.command: # noqa: command-instead-of-module (read-only describe)
   39 |         cmd: git describe --tags --exact-match
   40 |         chdir: "{{ rpi_image_root }}/rpi-image-gen"
   41 |       register: rpi_image_gen_tag
   42 |       changed_when: false
   43 |       # A mismatch means the host was never converged (or the pin moved):
   44 |       # run converge.yml first.
   45 |       failed_when: >-
   46 |         rpi_image_gen_tag.rc != 0
   47 |         or rpi_image_gen_tag.stdout != rpi_image_gen_version
   48 | 
   49 |     - name: Render image config {{ rpi_image_config }}
   50 |       ansible.builtin.template:
   51 |         src: templates/config.yaml.j2
   52 |         dest: "{{ rpi_image_root }}/configs/{{ rpi_image_config }}.yaml"
   53 |         mode: "0644"
   54 | 
   55 |     - name: Mark build start (for artifact discovery)
   56 |       ansible.builtin.file:
   57 |         path: "{{ rpi_image_root }}/.build-start"
   58 |         state: touch
   59 |         mode: "0644"
   60 | 
   61 |     # Serialise builds (scheduled vs manual) and log to the workspace so
   62 |     # failures are diagnosable after the fact. sbin dirs must be on PATH:
   63 |     # rpi-image-gen's dependency check resolves tools like mkdosfs with
   64 |     # `command -v`, and non-login SSH sessions don't get sbin by default.
   65 |     - name: Run rpi-image-gen build (async, logged)
   66 |       environment:
   67 |         PATH: /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
   68 |       ansible.builtin.shell: |
   69 |         set -o pipefail
   70 |         exec 200>{{ rpi_image_root }}/build.lock
   71 |         flock -n 200 || { echo "another build is running" >&2; exit 75; }
   72 |         ./rpi-image-gen build \
   73 |           -c {{ rpi_image_root }}/configs/{{ rpi_image_config }}.yaml \
   74 |           2>&1 | tee {{ rpi_image_root }}/logs/{{ rpi_image_build_id }}.log
   75 |       args:
   76 |         executable: /bin/bash
   77 |         chdir: "{{ rpi_image_root }}/rpi-image-gen"
   78 |       async: 7200
   79 |       poll: 30
   80 |       register: rpi_image_build
   81 |       changed_when: true
   82 | 
   83 |     - name: Locate produced image
   84 |       ansible.builtin.command:
   85 |         cmd: >-
   86 |           find {{ rpi_image_workdir }} -name '{{ rpi_image_config }}.img'
   87 |           -newer {{ rpi_image_root }}/.build-start
   88 |       register: rpi_image_find
   89 |       changed_when: false
   90 |       failed_when: rpi_image_find.stdout_lines | length != 1
   91 | 
   92 |     - name: Verify image contents (loop-mount assertions)
   93 |       become: true
   94 |       ansible.builtin.shell: |
   95 |         set -euo pipefail
   96 |         img='{{ rpi_image_find.stdout_lines[0] }}'
   97 |         mnt=$(mktemp -d)
   98 |         dev=$(losetup -fP --show "$img")
   99 |         trap 'umount -q "$mnt" 2>/dev/null || true; losetup -d "$dev"; rmdir "$mnt"' EXIT
  100 |         mount -o ro "${dev}p2" "$mnt"
  101 |         grep -qF '{{ rpi_image_ssh_pubkey }}' \
  102 |           "$mnt/home/{{ rpi_image_user }}/.ssh/authorized_keys"
  103 |         grep -qF '{{ rpi_image_user }} ALL=(ALL) NOPASSWD: [REDACTED_LITERAL]
  104 |           "$mnt/etc/sudoers.d/010_rpi-nopasswd"
  105 |         grep -q '^PasswordAuthentication no' \
  106 |           "$mnt/etc/ssh/sshd_config.d/01pubkey-only.conf"
  107 |         chroot "$mnt" /usr/bin/systemctl is-enabled ssh
  108 |         echo VERIFY_OK
  109 |       args:
  110 |         executable: /bin/bash
  111 |       register: rpi_image_verify
  112 |       changed_when: false
  113 | 
  114 |     - name: Publish image {{ rpi_image_build_id }}
  115 |       ansible.builtin.shell: |
  116 |         set -euo pipefail
  117 |         dest='{{ rpi_image_publish_config_dir }}/{{ rpi_image_build_id }}'
  118 |         mkdir -p "$dest"
  119 |         xz -T0 -c '{{ rpi_image_find.stdout_lines[0] }}' \
  120 |           > "$dest/{{ rpi_image_config }}.img.xz"
  121 |         cd "$dest" && sha256sum ./*.img.xz > SHA256SUMS
  122 |         ln -sfn "$dest" '{{ rpi_image_publish_config_dir }}/latest'
  123 |         cd '{{ rpi_image_publish_config_dir }}'
  124 |         ls -1d 20*/ | sort | head -n -{{ rpi_image_publish_retain }} \
  125 |           | xargs -r rm -rf
  126 |       args:
  127 |         executable: /bin/bash
  128 |       register: rpi_image_publish
  129 |       changed_when: true
  130 | 
  131 |     - name: Record artifact location
  132 |       ansible.builtin.set_stats:
  133 |         data:
  134 |           rpi_image_artifact: >-
  135 |             {{ rpi_image_publish_config_dir }}/{{ rpi_image_build_id
  136 |             }}/{{ rpi_image_config }}.img.xz
  137 | 
  138 |     - name: Report
  139 |       ansible.builtin.debug:
  140 |         msg: >-
  141 |           published {{ rpi_image_publish_config_dir }}/{{ rpi_image_build_id
  142 |           }}/{{ rpi_image_config }}.img.xz (latest ->
  143 |           {{ rpi_image_build_id }})
```
