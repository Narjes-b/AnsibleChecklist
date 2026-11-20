# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-012

- Repository: `packit/deployment`
- Commit: `0c6bf4b0fead603fc6872739b20a73c6858dcb83`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/redundant-default-value`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/deploy/tasks/main.yml` (reported anchor line 281)
- Object: `variable` `afe3c6267a9e74d4da64b05ec61321e62053b7db6779f68a6667e6082a9fa852`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–401 of 401:

```text
    1 | ---
    2 | - name: Include project-dir.yml
    3 |   ansible.builtin.include_tasks: project-dir.yml
    4 |   tags:
    5 |     - always
    6 | 
    7 | - name: Include variables
    8 |   ansible.builtin.include_vars: "{{ project_dir }}/vars/{{ service }}/{{ deployment }}.yml"
    9 |   tags:
   10 |     - always
   11 | 
   12 | - name: Include check-up-to-date.yml
   13 |   ansible.builtin.include_tasks: check-up-to-date.yml
   14 |   tags:
   15 |     - always
   16 | 
   17 | - name: Include deployment facts
   18 |   ansible.builtin.include_tasks: set-deployment-facts.yml
   19 |   tags:
   20 |     - always
   21 | 
   22 | - name: Include set-facts.yml
   23 |   ansible.builtin.include_tasks: set-facts.yml
   24 |   tags:
   25 |     - always
   26 | 
   27 | - name: Include extra secret vars
   28 |   ansible.builtin.include_vars:
   29 |     file: "{{ path_to_secrets }}/extra-vars.yml"
   30 |     name: vault
   31 |   tags:
   32 |     - always
   33 | 
   34 | - name: Get k8s token and check it
   35 |   tags:
   36 |     - always
   37 |   block:
   38 |     - name: Get kubeconfig token
   39 |       ansible.builtin.command: oc whoami -t
   40 |       register: kubeconfig_token
   41 |       changed_when: false
   42 |     - name: Check if tokens match
   43 |       ansible.builtin.assert:
   44 |         that:
   45 |           - kubeconfig_token.stdout =[REDACTED_LITERAL]
   46 |         msg: "OpenShift API token defined in vars/ does not match token from your current environment."
   47 | 
   48 | - name: Push dev images to local registry
   49 |   when: push_dev_images
   50 |   tags:
   51 |     - packit-service
   52 |     - packit-worker
   53 |     - packit-service-beat
   54 |   block:
   55 |     - name: Set tls-verify to false if podman is used
   56 |       ansible.builtin.set_fact:
   57 |         tls_verify_false: "{{ '--tls-verify=false' if 'podman' in container_engine else '' }}"
   58 |       changed_when: false
   59 |     - name: Login to local cluster
   60 |       ansible.builtin.shell: "{{ container_engine }} login -u {{ registry_user }} -p $(oc whoami -t) {{ registry }} {{ tls_verify_false }}"
   61 |       changed_when: false
   62 |     - name: Inspect service image
   63 |       ansible.builtin.command: "{{ container_engine }} inspect {{ image }}"
   64 |       changed_when: false
   65 |     - name: Tag the image with :dev
   66 |       ansible.builtin.command: "{{ container_engine }} tag {{ image }} {{ registry }}/myproject/packit-service:dev"
   67 |       changed_when: true
   68 |     - name: Push the image
   69 |       ansible.builtin.command: "{{ container_engine }} push {{ registry }}/myproject/packit-service:dev {{ tls_verify_false }}"
   70 |       changed_when: true
   71 |     - name: Inspect worker image
   72 |       ansible.builtin.command: "{{ container_engine }} inspect {{ image_worker }}"
   73 |       changed_when: false
   74 |     - name: Tag the image with :dev
   75 |       ansible.builtin.command: "{{ container_engine }} tag {{ image_worker }} {{ registry }}/myproject/packit-worker:dev"
   76 |       changed_when: true
   77 |     - name: Push the image
   78 |       ansible.builtin.command: "{{ container_engine }} push {{ registry }}/myproject/packit-worker:dev {{ tls_verify_false }}"
   79 |       changed_when: true
   80 |     - name: Inspect fedmsg image
   81 |       ansible.builtin.command: "{{ container_engine }} inspect {{ image_fedmsg }}"
   82 |       changed_when: false
   83 |     - name: Tag the image with :dev
   84 |       ansible.builtin.command: "{{ container_engine }} tag {{ image_fedmsg }} {{ registry }}/myproject/packit-service-fedmsg:dev"
   85 |       changed_when: true
   86 |     - name: Push the image
   87 |       ansible.builtin.command: "{{ container_engine }} push {{ registry }}/myproject/packit-service-fedmsg:dev {{ tls_verify_false }}"
   88 |       changed_when: true
   89 |     - name: Inspect dashboard image
   90 |       ansible.builtin.command: "{{ container_engine }} inspect {{ image_dashboard }}"
   91 |       changed_when: false
   92 |     - name: Tag the image with :dev
   93 |       ansible.builtin.command: "{{ container_engine }} tag {{ image_dashboard }} {{ registry }}/myproject/packit-dashboard:dev"
   94 |       changed_when: true
   95 |     - name: Push the image
   96 |       ansible.builtin.command: "{{ container_engine }} push {{ registry }}/myproject/packit-dashboard:dev {{ tls_verify_false }}"
   97 |       changed_when: true
   98 |     - name: Inspect tokman image
   99 |       ansible.builtin.command: "{{ container_engine }} inspect {{ image_tokman }}"
  100 |       changed_when: false
  101 |     - name: Tag the image with :dev
  102 |       ansible.builtin.command: "{{ container_engine }} tag {{ image_tokman }} {{ registry }}/myproject/tokman:dev"
  103 |       changed_when: true
  104 |     - name: Push the image
  105 |       ansible.builtin.command: "{{ container_engine }} push {{ registry }}/myproject/tokman:dev {{ tls_verify_false }}"
  106 |       changed_when: true
  107 | 
  108 | - name: Deploy secrets
  109 |   ansible.builtin.include_tasks: k8s.yml
  110 |   loop:
  111 |     - "{{ lookup('template', '{{ project_dir }}/openshift/secret-packit-ssh.yml.j2') }}"
  112 |     - "{{ lookup('template', '{{ project_dir }}/openshift/secret-packit-secrets.yml.j2') }}"
  113 |     - "{{ lookup('template', '{{ project_dir }}/openshift/secret-packit-config.yml.j2') }}"
  114 |     - "{{ lookup('template', '{{ project_dir }}/openshift/secret-sentry.yml.j2') }}"
  115 |     - "{{ lookup('template', '{{ project_dir }}/openshift/secret-postgres.yml.j2') }}"
  116 |     - "{{ lookup('template', '{{ project_dir }}/openshift/secret-aws.yml.j2') }}"
  117 |     - "{{ lookup('template', '{{ project_dir }}/openshift/secret-splunk.yml.j2') }}"
  118 |     - "{{ lookup('template', '{{ project_dir }}/openshift/secret-centpkg-sig.yml.j2') }}"
  119 |     - "{{ lookup('template', '{{ project_dir }}/openshift/github-app-private-key.yml.j2') }}"
  120 |   tags:
  121 |     - secrets
  122 | 
  123 | - name: Set up sandbox namespace
  124 |   when: with_sandbox
  125 |   block:
  126 |     - name: Create sandbox namespace
  127 |       k8s:
  128 |         resource_definition: "{{ lookup('template', '{{ project_dir }}/openshift/sandbox-namespace.yml.j2') }}"
  129 |         host: "{{ host }}"
  130 |         api_key: "{{ api_key }}"
  131 |         validate_certs: "{{ validate_certs }}"
  132 |     - name: Add edit role to service account in sandbox namespace
  133 |       ansible.builtin.command: oc adm policy add-role-to-user edit system:serviceaccount:{{ project }}:default -n {{ sandbox_namespace }}
  134 |       register: rolebinding
  135 |       changed_when: "'added:' in rolebinding.stdout"
  136 | 
  137 | - name: Deploy postgres
  138 |   ansible.builtin.include_tasks: k8s.yml
  139 |   loop:
  140 |     - "{{ lookup('template', '{{ project_dir }}/openshift/postgres.yml.j2') }}"
  141 |   tags:
  142 |     - postgres
  143 | 
  144 | - name: Deploy key-value database ({{ kv_database }})
  145 |   ansible.builtin.include_tasks: k8s.yml
  146 |   loop:
  147 |     - "{{ lookup('file', '{{ project_dir }}/openshift/configmap-redis_like_config.yml') }}"
  148 |     - "{{ lookup('template', '{{ project_dir }}/openshift/{{ kv_database }}.yml.j2') }}"
  149 |   when: with_kv_database
  150 |   tags:
  151 |     - kv_database
  152 | 
  153 | - name: Deploy fluentd image stream and config
  154 |   ansible.builtin.include_tasks: k8s.yml
  155 |   loop:
  156 |     - "{{ lookup('template', '{{ project_dir }}/openshift/fluentd.yml.j2') }}"
  157 |   tags:
  158 |     - packit-service
  159 |     - packit-worker
  160 |   when: with_fluentd_sidecar
  161 | 
  162 | - name: Deploy packit-service
  163 |   ansible.builtin.include_tasks: k8s.yml
  164 |   loop:
  165 |     - "{{ lookup('template', '{{ project_dir }}/openshift/packit-service.yml.j2') }}"
  166 |   tags:
  167 |     - packit-service
  168 | 
  169 | - name: Deploy repository cache PVCs for packit-workers that serves both queues
  170 |   vars:
  171 |     component: "packit-worker-{{ item }}"
  172 |   k8s:
  173 |     namespace: "{{ sandbox_namespace }}"
  174 |     definition: "{{ lookup('template', '{{ project_dir }}/openshift/sandcastle-volumes-for-cache.yml.j2') }}"
  175 |     host: "{{ host }}"
  176 |     api_key: "{{ api_key }}"
  177 |     validate_certs: "{{ validate_certs }}"
  178 |   loop: "{{ range(0, workers_all_tasks) | list }}"
  179 |   tags:
  180 |     - packit-worker
  181 |   when: workers_all_tasks > 0 and with_repository_cache
  182 | 
  183 | - name: Deploy packit-worker to serve all queues
  184 |   vars:
  185 |     component: packit-worker
  186 |     queues: "short-running,long-running,rate-limited"
  187 |     worker_replicas: "{{ workers_all_tasks }}"
  188 |     worker_requests_memory: "384Mi"
  189 |     worker_requests_cpu: "100m"
  190 |     worker_limits_memory: "1024Mi"
  191 |     worker_limits_cpu: "400m"
  192 |   ansible.builtin.include_tasks: k8s.yml
  193 |   loop:
  194 |     - "{{ lookup('template', '{{ project_dir }}/openshift/packit-worker.yml.j2') }}"
  195 |   tags:
  196 |     - packit-worker
  197 |   when: workers_all_tasks > 0
  198 | 
  199 | - name: Deploy packit-worker to serve short-running queue
  200 |   vars:
  201 |     component: packit-worker-short-running
  202 |     queues: "short-running"
  203 |     worker_replicas: "{{ workers_short_running }}"
  204 |     # Short-running tasks are just interactions with different services.
  205 |     # They should not require a lot of memory/cpu.
  206 |     worker_requests_memory: "768Mi"
  207 |     worker_requests_cpu: "80m"
  208 |     worker_limits_memory: "2048Mi"
  209 |     worker_limits_cpu: "2"
  210 |   ansible.builtin.include_tasks: k8s.yml
  211 |   loop:
  212 |     - "{{ lookup('template', '{{ project_dir }}/openshift/packit-worker.yml.j2') }}"
  213 |   tags:
  214 |     - packit-worker
  215 |   when: workers_short_running > 0
  216 | 
  217 | - name: Deploy repository cache PVCs for packit-workers that serves long-running queue
  218 |   vars:
  219 |     component: "packit-worker-long-running-{{ item }}"
  220 |   k8s:
  221 |     namespace: "{{ sandbox_namespace }}"
  222 |     definition: "{{ lookup('template', '{{ project_dir }}/openshift/sandcastle-volumes-for-cache.yml.j2') }}"
  223 |     host: "{{ host }}"
  224 |     api_key: "{{ api_key }}"
  225 |     validate_certs: "{{ validate_certs }}"
  226 |   loop: "{{ range(0, workers_long_running) | list }}"
  227 |   tags:
  228 |     - packit-worker
  229 |   when: workers_long_running > 0 and with_repository_cache
  230 | 
  231 | - name: Deploy packit-worker to serve long-running and rate-limited queue
  232 |   vars:
  233 |     component: packit-worker-long-running
  234 |     queues: "long-running,rate-limited"
  235 |     worker_replicas: "{{ workers_long_running }}"
  236 |     # cloning repos is memory intensive: glibc needs 300M+, kernel 600M+
  237 |     # during cloning, we need to account for git and celery worker processes
  238 |     worker_requests_memory: "768Mi"
  239 |     worker_requests_cpu: "100m"
  240 |     worker_limits_memory: "2048Mi"
  241 |     worker_limits_cpu: "2"
  242 |   ansible.builtin.include_tasks: k8s.yml
  243 |   loop:
  244 |     - "{{ lookup('template', '{{ project_dir }}/openshift/packit-worker.yml.j2') }}"
  245 |   tags:
  246 |     - packit-worker
  247 |   when: workers_long_running > 0
  248 | 
  249 | - name: Deploy packit-service-beat
  250 |   ansible.builtin.include_tasks: k8s.yml
  251 |   loop:
  252 |     - "{{ lookup('template', '{{ project_dir }}/openshift/packit-service-beat.yml.j2') }}"
  253 |   when: with_beat
  254 |   tags:
  255 |     - packit-service-beat
  256 | 
  257 | - name: Deploy dashboard
  258 |   ansible.builtin.include_tasks: k8s.yml
  259 |   loop:
  260 |     - "{{ lookup('template', '{{ project_dir }}/openshift/dashboard.yml.j2') }}"
  261 |   when: with_dashboard
  262 |   tags:
  263 |     - dashboard
  264 | 
  265 | - name: Create redis-commander secrets
  266 |   k8s:
  267 |     namespace: "{{ project }}"
  268 |     definition: "{{ lookup('template', '{{ project_dir }}/openshift/secret-redis-commander.yml.j2') }}"
  269 |     host: "{{ host }}"
  270 |     api_key: "{{ api_key }}"
  271 |     validate_certs: "{{ validate_certs }}"
  272 |     apply: true
  273 |   tags:
  274 |     - redis-commander
  275 |   notify:
  276 |     - Restart redis-commander deployment
  277 |   when: with_redis_commander
  278 | 
  279 | - name: Deploy redis-commander
  280 |   vars:
  281 |     k8s_apply: true
  282 |   ansible.builtin.include_tasks: k8s.yml
  283 |   loop:
  284 |     - "{{ lookup('template', '{{ project_dir }}/openshift/redis-commander.yml.j2') }}"
  285 |   when: with_redis_commander
  286 |   tags:
  287 |     - redis-commander
  288 |   register: redis_commander
  289 | 
  290 | - name: Deploy flower
  291 |   ansible.builtin.include_tasks: k8s.yml
  292 |   loop:
  293 |     - "{{ lookup('template', '{{ project_dir }}/openshift/flower.yml.j2') }}"
  294 |   when: with_flower
  295 |   tags:
  296 |     - flower
  297 | 
  298 | - name: Deploy packit-service-fedmsg
  299 |   ansible.builtin.include_tasks: k8s.yml
  300 |   loop:
  301 |     - "{{ lookup('template', '{{ project_dir }}/openshift/packit-service-fedmsg.yml.j2') }}"
  302 |   tags:
  303 |     - fedmsg
  304 |   when: with_fedmsg
  305 | 
  306 | - name: Deploy GitHub App Private Key
  307 |   k8s:
  308 |     namespace: "{{ project }}"
  309 |     resource_definition: "{{ lookup('template', '{{ project_dir }}/openshift/github-app-private-key.yml.j2') }}"
  310 |     host: "{{ host }}"
  311 |     api_key: "{{ api_key }}"
  312 |     validate_certs: "{{ validate_certs }}"
  313 |   tags:
  314 |     - tokman
  315 |   notify:
  316 |     - Restart tokman deployment
  317 |   when: with_tokman
  318 | 
  319 | - name: Deploy tokman
  320 |   k8s:
  321 |     namespace: "{{ project }}"
  322 |     definition: "{{ lookup('template', '{{ project_dir }}/openshift/tokman.yml.j2') }}"
  323 |     host: "{{ host }}"
  324 |     api_key: "{{ api_key }}"
  325 |     validate_certs: "{{ validate_certs }}"
  326 |   tags:
  327 |     - tokman
  328 |   register: tokman
  329 |   when: with_tokman
  330 | 
  331 | - name: Deploy aggregating pushgateway
  332 |   ansible.builtin.include_tasks: k8s.yml
  333 |   loop:
  334 |     - "{{ lookup('template', '{{ project_dir }}/openshift/pushgateway.yml.j2') }}"
  335 |   tags:
  336 |     - pushgateway
  337 |   when: with_pushgateway
  338 | 
  339 | - name: Create htpasswd file and deploy it as a secret
  340 |   tags:
  341 |     - flower
  342 |   when: with_flower
  343 |   block:
  344 |     - name: Create htpasswd file
  345 |       htpasswd:[REDACTED VALUE BLOCK]
  346 |         [REDACTED ENCRYPTED VALUE]
  347 |         [REDACTED ENCRYPTED VALUE]
  348 |         [REDACTED ENCRYPTED VALUE]
  349 |         [REDACTED ENCRYPTED VALUE]
  350 |     - name: Deploy flower-htpasswd secret
  351 |       # Don't use k8s.yml here because the loop item is always evaluated
  352 |       k8s:
  353 |         namespace: "{{ project }}"
  354 |         resource_definition: "{{ lookup('template', '{{ project_dir }}/openshift/secret-flower-htpasswd.yml.j2') }}"
  355 |         host: "{{ host }}"
  356 |         api_key: "{{ api_key }}"
  357 |         validate_certs: "{{ validate_certs }}"
  358 |       notify:
  359 |         - Restart nginx deployment
  360 | 
  361 | - name: Deploy nginx to reverse proxy the pushgateway and flower
  362 |   k8s:
  363 |     namespace: "{{ project }}"
  364 |     definition: "{{ lookup('template', '{{ project_dir }}/openshift/nginx.yml.j2') }}"
  365 |     host: "{{ host }}"
  366 |     api_key: "{{ api_key }}"
  367 |     validate_certs: "{{ validate_certs }}"
  368 |   tags:
  369 |     - pushgateway
  370 |   register: nginx
  371 |   when: with_pushgateway and with_flower
  372 | 
  373 | - name: Wait for worker-0 to be running
  374 |   vars:
  375 |     pod_name: packit-worker-0
  376 |   ansible.builtin.include_tasks: wait_for_pod.yml
  377 |   when: workers_all_tasks > 0
  378 | 
  379 | - name: Wait for worker-short-running-0 to be running
  380 |   vars:
  381 |     pod_name: packit-worker-short-running-0
  382 |   ansible.builtin.include_tasks: wait_for_pod.yml
  383 |   when: workers_short_running > 0
  384 | 
  385 | - name: Wait for worker-long-running-0 to be running
  386 |   vars:
  387 |     pod_name: packit-worker-long-running-0
  388 |   ansible.builtin.include_tasks: wait_for_pod.yml
  389 |   when: workers_long_running > 0
  390 | 
  391 | - name: Select project to check status on command line
  392 |   ansible.builtin.command: "oc project {{ project }}"
  393 |   changed_when: false
  394 | 
  395 | - name: Wait for deploymentconfig rollouts to complete
  396 |   # timeout 10min to not wait indefinitely in case of a problem
  397 |   ansible.builtin.command: timeout 15m oc rollout status -w deploy/{{ item }}
  398 |   register: oc_rollout_status
  399 |   changed_when: false
  400 |   failed_when: '"successfully rolled out" not in oc_rollout_status.stdout'
  401 |   loop: "{{ deploymentconfigs }}"
```

## Visible variable references

```text
0c6bf4b0fead603fc6872739b20a73c6858dcb83:playbooks/deploy.yml:57:    k8s_apply: true
0c6bf4b0fead603fc6872739b20a73c6858dcb83:roles/deploy/defaults/main.yml:50:k8s_apply: true
0c6bf4b0fead603fc6872739b20a73c6858dcb83:roles/deploy/tasks/main.yml:281:    k8s_apply: true
0c6bf4b0fead603fc6872739b20a73c6858dcb83:tasks/k8s.yml:23:    apply: "{{ k8s_apply }}"
```
