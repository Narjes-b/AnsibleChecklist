# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-018

- Repository: `easzlab/kubeasz`
- Commit: `fcb46a47a7fcd3bbc97498ea4aefdd564e16b383`
- Family: objective_correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `roles/cluster-addon/tasks/ingress-nginx.yml` (reported anchor line 18)
- Flagged construct: not named by the finding; the anchor line 18 lies in the task at line 18, name `轮询等待部署 ingress-nginx`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–30 of 30:

```text
    1 | - block:
    2 |     - name: prepare some dirs
    3 |       file: name={{ cluster_dir }}/yml/ingress-nginx state=directory
    4 | 
    5 |     - name: 创建命名空间{{ ingress_nginx_namespace }}
    6 |       shell: "{{ base_dir }}/bin/kubectl create ns {{ ingress_nginx_namespace }} || echo true"
    7 | 
    8 |     - name: 创建chart 个性化设置
    9 |       template: src=ingress-nginx/{{ item }}.j2 dest={{ cluster_dir }}/yml/ingress-nginx/{{ item }}
   10 |       with_items:
   11 |       - "values.yaml"
   12 | 
   13 |     - name: helm 部署 ingress-nginx
   14 |       shell: "{{ base_dir }}/bin/helm upgrade ingress-nginx --install -n {{ ingress_nginx_namespace }} \
   15 |               -f {{ cluster_dir }}/yml/ingress-nginx/values.yaml \
   16 |               {{ base_dir }}/roles/cluster-addon/files/ingress-nginx-{{ ingress_nginx_ver }}.tgz"
   17 | 
   18 |     - name: 轮询等待部署 ingress-nginx
   19 |       shell: "{{ base_dir }}/bin/helm ls -n {{ ingress_nginx_namespace }}|grep ingress-nginx|awk '{print $8}'"
   20 |       register: chart_status
   21 |       until: chart_status.stdout == "deployed"
   22 |       retries: 15
   23 |       delay: 5
   24 |       ignore_errors: true
   25 | 
   26 |     - name: 提示 WARNNING
   27 |       debug:
   28 |         msg: "ingress-nginx 只会部署到有如下标签的节点：ingress-controller/provider=ingress-nginx"
   29 | 
   30 |   when: 'ingress_nginx_install == "yes"'
```
