# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-007

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unscoped-shell-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `onecloud/roles/utils/ai-env/tasks/install-container-toolkit-Debian.yml` (reported anchor line 32)
- Object: `source_location` `400165339b7c1a3a2f615e245f8fe9df1f08923bd9a01d3d7b037ec7f66bcc1a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–44 of 44:

```text
    1 | - name: Install curl and gpg prerequisites (Debian)
    2 |   apt:
    3 |     name:
    4 |       - curl
    5 |       - gpg
    6 |     state: present
    7 |     update_cache: yes
    8 |   become: true
    9 | 
   10 | - name: Add NVIDIA Container Toolkit GPG key (Debian)
   11 |   shell: |
   12 |     curl -fsSL https://mirrors.ustc.edu.cn/libnvidia-container/gpgkey | \
   13 |       gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   14 |   become: true
   15 |   args:
   16 |     executable: /bin/bash
   17 | 
   18 | - name: Add NVIDIA Container Toolkit apt repository (Debian)
   19 |   shell: |
   20 |     curl -s -L https://mirrors.ustc.edu.cn/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
   21 |       sed 's#deb https://nvidia.github.io#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://mirrors.ustc.edu.cn#g' | \
   22 |       tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   23 |   become: true
   24 |   args:
   25 |     executable: /bin/bash
   26 | 
   27 | - name: Update apt cache (Debian)
   28 |   apt:
   29 |     update_cache: yes
   30 |   become: true
   31 | 
   32 | - name: Install NVIDIA Container Toolkit (Debian)
   33 |   shell: |
   34 |     export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.17.8-1
   35 |     apt install -y \
   36 |       nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
   37 |       nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
   38 |       libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
   39 |       libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}
   40 |   become: true
   41 |   args:
   42 |     executable: /bin/bash
   43 |   environment:
   44 |     DEBIAN_FRONTEND: noninteractive
```
