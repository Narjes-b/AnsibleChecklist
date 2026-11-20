# Frozen Git review context: V007PILOT-REVIEW_HISTORY-007

- Repository: `mageops/ansible-infrastructure`
- Target commit: `5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8`
- Actual first parent: `f43dda320ec66d942b01be0511747854d32a9399`
- Evidence type: actual first-parent diff
- Family: Review/history
- Rule: `ansibleguard/missing-release-note`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: `f43dda320ec66d942b01be0511747854d32a9399..5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8` (from frozen Git objects)
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
Merge pull request #578 from mageops/rocky-develop

Release
```

## Changed paths (103)

- `A` `.python-version`
- `M` `ansible.cfg`
- `M` `group_vars/all.yml`
- `M` `library/cloudfront_distribution.py`
- `A` `library/cloudfront_distribution_info.py`
- `M` `library/ec2_launch_template.py`
- `M` `requirements-galaxy.yml`
- `M` `requirements-python.txt`
- `M` `roles/cs.ansible-plugins/filter_plugins/transform.py`
- `M` `roles/cs.aws-autoscaling-facts/tasks/main.yml`
- `M` `roles/cs.aws-autoscaling-triggers/tasks/main.yml`
- `M` `roles/cs.aws-autoscaling/tasks/create.yml`
- `M` `roles/cs.aws-autoscaling/tasks/delete.yml`
- `M` `roles/cs.aws-cloudfront-facts/tasks/main.yml`
- `M` `roles/cs.aws-cloudfront-post-deploy/tasks/main.yml`
- `M` `roles/cs.aws-cloudfront/tasks/setup-distribution-s3-media.yml`
- `M` `roles/cs.aws-create-ami/tasks/main.yml`
- `M` `roles/cs.aws-ec2-cleanup/tasks/main.yml`
- `M` `roles/cs.aws-iam-employee-access/tasks/main.yml`
- `M` `roles/cs.aws-lambda-import/tasks/main.yml`
- `M` `roles/cs.aws-logs-slack/tasks/main.yml`
- `M` `roles/cs.aws-node-ami-builder/tasks/main.yml`
- `M` `roles/cs.aws-node-facts/tasks/main.yml`
- `M` `roles/cs.aws-node-persistent/tasks/main.yml`
- `M` `roles/cs.aws-node-varnish/tasks/main.yml`
- `M` `roles/cs.aws-rds-facts/tasks/main.yml`
- `M` `roles/cs.aws-rds-gfs-backup/tasks/cluster-db.yml`
- `M` `roles/cs.aws-rds-gfs-backup/tasks/main.yml`
- `M` `roles/cs.aws-rds-gfs-backup/tasks/single-db.yml`
- `M` `roles/cs.aws-rds/tasks/main.yml`
- `M` `roles/cs.aws-rds/tasks/upgrade_iteration.yml`
- `M` `roles/cs.aws-region-facts/tasks/main.yml`
- `M` `roles/cs.aws-s3/tasks/main.yml`
- `M` `roles/cs.aws-security-group/tasks/main.yml`
- `M` `roles/cs.aws-ses/tasks/main.yml`
- `M` `roles/cs.blackfire/tasks/main.yml`
- `M` `roles/cs.deploy-containerized-tasks/tasks/main.yml`
- `M` `roles/cs.deploy/tasks/90-emergency-link-back.yml`
- `M` `roles/cs.deploy/tasks/91-emergency-rename.yml`
- `M` `roles/cs.deploy/tasks/main.yml`
- `M` `roles/cs.firewalld/defaults/main.yml`
- `M` `roles/cs.goaccess/defaults/main.yml`
- `M` `roles/cs.goaccess/tasks/main.yml`
- `M` `roles/cs.magento-configure/defaults/main/general.yml`
- `M` `roles/cs.magento-configure/tasks/000-prepare-runtime-config.yml`
- `M` `roles/cs.magento-configure/tasks/035-clean-old-static-content.yml`
- `M` `roles/cs.magento-configure/tasks/037-wait-for-services.yml`
- `M` `roles/cs.magento-configure/tasks/080-core-config.yml`
- `M` `roles/cs.magento-configure/tasks/action/configure-env.yml`
- `M` `roles/cs.magento-configure/tasks/main.yml`
- `M` `roles/cs.magento-configure/tasks/vagrant.yml`
- `M` `roles/cs.magento-postfix/tasks/main.yml`
- `M` `roles/cs.magento-shared-storage/tasks/main.yml`
- `M` `roles/cs.magerun/defaults/main.yml`
- `M` `roles/cs.new-relic/defaults/main.yml`
- `M` `roles/cs.new-relic/tasks/main.yml`
- `M` `roles/cs.nginx-https-termination/defaults/main.yml`
- `M` `roles/cs.nginx-https-termination/tasks/000-facts.yml`
- `M` `roles/cs.nginx-https-termination/tasks/030-certificates-install.yml`
- `M` `roles/cs.nginx-https-termination/tasks/032-certificates-bootstrap.yml`
- `M` `roles/cs.nginx-https-termination/tasks/034-certificates-acme.yml`
- `M` `roles/cs.nginx-https-termination/tasks/main.yml`
- `M` `roles/cs.nginx-language-redirect-multilevel/defaults/main.yml`
- `M` `roles/cs.nginx-language-redirect-multilevel/meta/main.yml`
- `M` `roles/cs.nginx-language-redirect-multilevel/tasks/main.yml`
- `M` `roles/cs.nginx-language-redirect/defaults/main.yml`
- `M` `roles/cs.nginx-language-redirect/meta/main.yml`
- `M` `roles/cs.nginx-language-redirect/tasks/main.yml`
- `M` `roles/cs.packages/tasks/main.yml`
- `M` `roles/cs.php-fpm/tasks/main.yml`
- `M` `roles/cs.php-tideways/tasks/main.yml`
- `M` `roles/cs.pio/tasks/install_rpm.yml`
- `M` `roles/cs.rabbitmq/defaults/main.yml`
- `M` `roles/cs.rabbitmq/handlers/main.yml`
- `M` `roles/cs.rabbitmq/tasks/main.yml`
- `M` `roles/cs.redis/tasks/configure.yml`
- `M` `roles/cs.repo-mageops/handlers/main.yml`
- `A` `roles/cs.repo-rabbitmq/defaults/main.yml`
- `M` `roles/cs.repo-rabbitmq/tasks/main.yml`
- `M` `roles/cs.repo-rabbitmq/templates/rabbitmq.repo`
- `M` `roles/cs.s3-mount/tasks/002-setup-mounts.yml`
- `M` `roles/cs.s3-mount/tasks/main.yml`
- `M` `roles/cs.ssh-proxy-user/tasks/main.yml`
- `M` `roles/cs.ssh-tunel/tasks/main.yml`
- `M` `roles/cs.sshd/defaults/main.yml`
- `M` `roles/cs.swap/tasks/main.yml`
- `M` `roles/cs.unison/meta/main.yml`
- `M` `roles/cs.unison/tasks/main.yml`
- `M` `roles/cs.varnish/defaults/main.yml`
- `M` `roles/cs.varnish/tasks/000-facts.yml`
- `M` `roles/cs.varnish/templates/vcl/acl.vcl.j2`
- `M` `roles/cs.varnish/vars/main.yml`
- `M` `site.maintenance.aws-remove-all.yml`
- `M` `site.maintenance.aws-start.yml`
- `M` `site.maintenance.aws-stop.yml`
- `M` `site.maintenance.purge-db.yml`
- `M` `site.maintenance.update-certificates.yml`
- `M` `site.step-15-varnish.yml`
- `M` `site.step-20-persistent.yml`
- `M` `site.step-40-app-node.yml`
- `M` `site.step-45-app-deploy.yml`
- `M` `site.step-50-ami.yml`
- `M` `vars_plugins/mageops_vars.py`

## Relevant first-parent diff

```diff
diff --git a/group_vars/all.yml b/group_vars/all.yml
index 29cc338..57c3426 100644
--- a/group_vars/all.yml
+++ b/group_vars/all.yml
@@ -366,11 +366,11 @@ aws_security_group_persistent_rules_tinyproxy:
     ports:
       - "{{ tinyproxy_port }}"
     group_name: "{{ aws_security_group_app_name }}"
 
 aws_security_group_persistant_rules_tpl: [
-  "{{ mageops_ssh_proxy_persistant | ternary(aws_security_group_persistant_rules_ssh_proxy, []) }}",
+  "{{ (mageops_ssh_proxy_persistant | bool) | ternary(aws_security_group_persistant_rules_ssh_proxy, []) }}",
   "{{ mageops_tinyproxy_persistant_enabled | ternary(aws_security_group_persistent_rules_tinyproxy, []) }}"
 ]
 
 aws_security_group_persistant_rules: "{{ aws_security_group_persistant_rules_tpl | flatten }}"
 
@@ -1159,29 +1159,45 @@ magento_core_config_settings_default:
   # if it is already set.
   - name: Set secure media url to cloudfront domain
     path: "web/secure/base_media_url"
     value: "https://{{ aws_cloudfront_distribution_domain | default('') }}/"
     default: "{{ aws_cloudfront_domain_aliases | default([]) | length > 0 }}"
-    enabled: "{{ aws_cloudfront_distribution_domain is string and aws_cloudfront_distribution_create }}"
+    enabled: >-
+      {{
+        (aws_cloudfront_distribution_domain | default('', true) | string | length) > 0
+        and (aws_cloudfront_distribution_create | bool)
+      }}
 
   - name: Set secure static url to cloudfront domain
     path: "web/secure/base_static_url"
     value: "https://{{ aws_cloudfront_distribution_domain | default('') }}/static/"
     default: "{{ aws_cloudfront_domain_aliases | default([]) | length > 0 }}"
-    enabled: "{{ aws_cloudfront_distribution_domain is string and aws_cloudfront_distribution_create }}"
+    enabled: >-
+      {{
+        (aws_cloudfront_distribution_domain | default('', true) | string | length) > 0
+        and (aws_cloudfront_distribution_create | bool)
+      }}
 
   - name: Set unsecure media url to cloudfront domain
     path: "web/secure/base_media_url"
     value: "https://{{ aws_cloudfront_distribution_domain | default('') }}/"
     default: "{{ aws_cloudfront_domain_aliases | default([]) | length > 0 }}"
-    enabled: "{{ aws_cloudfront_distribution_domain is string and aws_cloudfront_distribution_create }}"
+    enabled: >-
+      {{
+        (aws_cloudfront_distribution_domain | default('', true) | string | length) > 0
+        and (aws_cloudfront_distribution_create | bool)
+      }}
 
   - name: Set unsecure static url to cloudfront domain
     path: "web/secure/base_static_url"
     value: "https://{{ aws_cloudfront_distribution_domain | default('') }}/static/"
     default: "{{ aws_cloudfront_domain_aliases | default([]) | length > 0 }}"
-    enabled: "{{ aws_cloudfront_distribution_domain is string and aws_cloudfront_distribution_create }}"
+    enabled: >-
+      {{
+        (aws_cloudfront_distribution_domain | default('', true) | string | length) > 0
+        and (aws_cloudfront_distribution_create | bool)
+      }}
 
 
 # Extra core config settings to be set at deploy,
 # see roles/cs.magento-configure/tasks/080-core-config.yml
 magento_core_config_settings_extra: []
@@ -1505,11 +1521,11 @@ tideways_enable: no
 
 nginx_version: "1.10.3"
 nginx_user: "nginx"
 nginx_group: "nginx"
 
-nginx_worker_processes: "{{ ansible_processor_vcpus|default(ansible_processor_count + 1) }}"
+nginx_worker_processes: "{{ ansible_facts.processor_vcpus | default(ansible_facts.processor_count + 1) }}"
 nginx_worker_connections: "1024"
 
 nginx_multi_accept: "off"
 
 nginx_www_dir: "/var/www"
@@ -1576,11 +1592,11 @@ mageops_elasticsearch_version:
 elasticsearch_cluster_name: "{{ mageops_app_id }}"
 elasticsearch_node_name: master
 
 elasticsearch_http_port: 9200
 elasticsearch_transport_tcp_port: 9300
-elasticsearch_heap_size: "{{ ((ansible_memtotal_mb / 2) | int ) ~ 'm' }}"
+elasticsearch_heap_size: "{{ ((ansible_facts.memtotal_mb / 2) | int ) ~ 'm' }}"
 elasticsearch_plugins:
     - analysis-icu
     - analysis-phonetic
 
 # ---------------------------------
@@ -1884,10 +1900,20 @@ mageops_rabbitmq_create: "{{ magento_rabbitmq_queue }}"
 rabbitmq_amqp_port: 5672
 
 # Whether to enable Management UI
 rabbitmq_enable_management: yes
 
+# RabbitMQ release series to install and keep updated within
+rabbitmq_release: "4.2"
+rabbitmq_versionlock_package: "rabbitmq-server-{{ rabbitmq_release }}.*"
+# Keep aligned with RabbitMQ/Erlang compatibility: https://www.rabbitmq.com/docs/4.2/which-erlang
+erlang_release: "27"
+erlang_versionlock_package: "erlang-{{ erlang_release }}.*"
+# aarch64 uses a direct RPM, so this exact version duplicates erlang_release on purpose.
+# Update from the latest matching erlang-<version>-1.el9.aarch64.rpm at https://github.com/rabbitmq/erlang-rpm/releases
+rabbitmq_erlang_aarch64_rpm_version: "27.3.4.13-1"
+
 # This port will provide an HTTP API and management UI
 # - might be useful for debugging and will be accessible from `mageops_trusted_cidr_blocks`
 rabbitmq_http_port: 15672
 
 # --------------------------
@@ -2027,13 +2053,15 @@ packages_full_update: "{{ mageops_packages_full_update }}"
 packages_mirrorlist_countrycode: "{{ mageops_packages_mirrorlist_countrycode }}"
 packages_remove: "{{ mageops_packages_banned }}"
 
 # Package locks, for more info, check cs.versionlock role
 
-mageops_elasticsearch_version_full: "elasticsearch-{{mageops_elasticsearch_version}}.*"
+mageops_elasticsearch_version_full: "elasticsearch-{{ mageops_elasticsearch_version }}.*"
 versionlock_persistent_packages_base_tpl: [
-  "{{ mageops_elasticsearch_version | ternary( mageops_elasticsearch_version_full, [] ) }}"
+  "{{ mageops_elasticsearch_version | ternary(mageops_elasticsearch_version_full, []) }}",
+  "{{ mageops_rabbitmq_create | ternary(rabbitmq_versionlock_package, []) }}",
+  "{{ mageops_rabbitmq_create | ternary(erlang_versionlock_package, []) }}"
 ]
 
 # Package locks per instance
 versionlock_varnish_packages:
   - varnish-6.0.*
@@ -2087,11 +2115,11 @@ sshd_config_users_base:
 sshd_config_users_ssh_proxy:
   tunel: "{{ sshd_config_allow_all_forwards }}"
 
 sshd_config_users_tpl: [
   "{{ sshd_config_users_base }}",
-  "{{ mageops_ssh_proxy_persistant | ternary(sshd_config_users_ssh_proxy, {}) }}",
+  "{{ (mageops_ssh_proxy_persistant | bool) | ternary(sshd_config_users_ssh_proxy, {}) }}",
 ]
 
 sshd_config_users: "{{ sshd_config_users_tpl | combine }}"
 
 mageops_tinyproxy_persistant_enabled: no
diff --git a/requirements-galaxy.yml b/requirements-galaxy.yml
index 659eec1..81e79ab 100644
--- a/requirements-galaxy.yml
+++ b/requirements-galaxy.yml
@@ -1,34 +1,33 @@
 roles:
-- src: geerlingguy.mysql
-  version: 4.3.5
-- src: geerlingguy.composer
-  version: 1.9.2
-- src: geerlingguy.ntp
-  version: 2.4.0
-- src: zauberpony.mysql-query
-  version: v0.6.1
-
-- src: pinkeen.postfix
-  version: v1.1
+  - src: geerlingguy.mysql
+    version: 6.3.1
+  - src: geerlingguy.composer
+    version: 1.9.2
+  - src: geerlingguy.ntp
+    version: 4.0.0
+  - src: zauberpony.mysql-query
+    version: v0.6.1
+  - src: pinkeen.postfix
+    version: v1.1
 
 collections:
-- name: community.aws
-  version: 5.5.1
-- name: amazon.aws
-  version: 5.5.2
-- name: community.mysql
-  version: 5.0.2
-- name: ansible.utils
-  version: 2.10.3
-- name: community.general
-  version: 7.2.0
-- name: ansible.posix
-  version: 1.5.4
-- name: community.rabbitmq
-  version: 1.2.3
-- name: community.crypto
-  version: 2.18.0
-- name: ansible.netcommon
-  version: 5.1.2
-- name: containers.podman
-  version: 1.20.2
+  - name: community.aws
+    version: 11.0.0
+  - name: amazon.aws
+    version: 11.0.0
+  - name: community.mysql
+    version: 4.1.0
+  - name: ansible.utils
+    version: 6.0.1
+  - name: community.general
+    version: 12.4.0
+  - name: ansible.posix
+    version: 2.1.0
+  - name: community.rabbitmq
+    version: 1.6.0
+  - name: community.crypto
+    version: 3.1.1
+  - name: ansible.netcommon
+    version: 8.4.0
+  - name: containers.podman
+    version: 1.19.0
diff --git a/roles/cs.aws-autoscaling-facts/tasks/main.yml b/roles/cs.aws-autoscaling-facts/tasks/main.yml
index 55a5ca1..8939e76 100644
--- a/roles/cs.aws-autoscaling-facts/tasks/main.yml
+++ b/roles/cs.aws-autoscaling-facts/tasks/main.yml
@@ -1,7 +1,7 @@
 - name: Get ASG app information
-  ec2_asg_info:
+  amazon.aws.autoscaling_group_info:
     region: "{{ aws_region }}"
     tags: >-
         {{
             aws_tags_default | combine(
               aws_tags_role_app,
@@ -16,11 +16,11 @@
             )
         }}
   register: _aws_asg_app
 
 - name: Get ASG app-extra information
-  ec2_asg_info:
+  amazon.aws.autoscaling_group_info:
     region: "{{ aws_region }}"
     tags: >-
       {{
         aws_tags_default | combine(
           aws_tags_role_app,
@@ -36,11 +36,11 @@
        )
       }}
   register: _aws_asg_app_extra
 
 - name: Get ASG app-pio information
-  ec2_asg_info:
+  amazon.aws.autoscaling_group_info:
     region: "{{ aws_region }}"
     tags: >-
       {{ aws_tags_default | combine(
            aws_tags_pio_only,
            aws_tags_node_pio,
diff --git a/roles/cs.aws-autoscaling-triggers/tasks/main.yml b/roles/cs.aws-autoscaling-triggers/tasks/main.yml
index 4386e0a..58d817c 100644
--- a/roles/cs.aws-autoscaling-triggers/tasks/main.yml
+++ b/roles/cs.aws-autoscaling-triggers/tasks/main.yml
@@ -6,19 +6,30 @@
 - name: Normalize event target ARNs
   set_fact:
     aws_autoscaling_trigger_targets: >-
       {{
         aws_autoscaling_trigger_targets | default([])
-          + [ target | combine({'arn': normalized_arn}) ]
+          + [ target | combine({'arn': normalized_arn, 'id': normalized_target_id}) ]
       }}
   loop: "{{ aws_autoscaling_triggers_list }}"
   loop_control:
     loop_var: target
-    label: "{{ target.arn }} -> {{ normalized_arn }}"
+    label: "{{ target.id }} -> {{ normalized_target_id }}"
   vars:
     # When lambda is created ansible returns function arn containing $LATEST, while when it's already present it's returned without it
     normalized_arn: "{{ target.arn | regex_replace('^(.*lambda:.*:function:.*):[0-9]+$', '\\1') | regex_replace(':\\$LATEST$', '') }}"
+    # Keep this compatible with existing EventBridge target IDs created by earlier deployments.
+    normalized_target_id: >-
+      {{
+        (
+          target.id | length <= 64
+        )
+        | ternary(
+            target.id,
+            ((target.id | regex_replace('-target$', ''))[:54] ~ '-' ~ ((target.id | hash('sha1'))[:8]))
+          )
+      }}
 
 - name: Setup autoscaling event trigger
   cloudwatchevent_rule:
     name: "trigger-autoscaling-lambda-{{ mageops_app_name }}"
     region: "{{ aws_region }}"
diff --git a/roles/cs.aws-autoscaling/tasks/create.yml b/roles/cs.aws-autoscaling/tasks/create.yml
index 1220443..3374abf 100644
--- a/roles/cs.aws-autoscaling/tasks/create.yml
+++ b/roles/cs.aws-autoscaling/tasks/create.yml
@@ -19,11 +19,11 @@
     ebs_optimized: true
   vars:
     aws_ec2_user_launch_script: "{{ autoscaling_instance_start_script }}"
 
 - name: Create AutoScaling Group
-  ec2_asg:
+  amazon.aws.autoscaling_group:
     state: present
     name: "{{ autoscaling_asg_name }}"
     region: "{{ aws_region }}"
     availability_zones: "{{ aws_app_asg_availability_zones | join(',') }}"
     launch_template:
@@ -38,14 +38,10 @@
     # The 300s default we had is waaaay too long for our setup and makes the
     # deploy much, much longer (at least 300s long).
     health_check_period: "{{ autoscaling_healthcheck_grace_period }}"
     termination_policies: "{{ autoscaling_asg_termination_policies }}"
     tags: "{{ aws_tags_default | combine(asg_name_tags, aws_tags_trait_immutable, autoscaling_instance_tags) | dict_to_tag_list }}"
-    # This ansible module does not handle instance replacement properly
-    # so we just update the ASG configuration here and will perform the
-    # replacement via AWS API in the next steps.
-    replace_instances: []
   vars:
     asg_name_tags:
       - Name: "{{ autoscaling_asg_name }}"
   register: _aws_asg
 
@@ -54,11 +50,11 @@
   when: >-
     _aws_asg is changed
       and autoscaling_asg_desired_capacity > 0
 
 - name: Create ASG Termination Lifecycle Hook
-  ec2_asg_lifecycle_hook:
+  community.aws.autoscaling_lifecycle_hook:
     state: present
     region: "{{ aws_region }}"
     autoscaling_group_name: "{{ autoscaling_asg_name }}"
     lifecycle_hook_name: "{{ autoscaling_webnodedown_hook_name }}"
     transition: "autoscaling:EC2_INSTANCE_TERMINATING"
diff --git a/roles/cs.aws-autoscaling/tasks/delete.yml b/roles/cs.aws-autoscaling/tasks/delete.yml
index 34ece28..d18ec12 100644
--- a/roles/cs.aws-autoscaling/tasks/delete.yml
+++ b/roles/cs.aws-autoscaling/tasks/delete.yml
@@ -1,5 +1,5 @@
 - name: Remove AutoScaling Group
-  ec2_asg:
+  amazon.aws.autoscaling_group:
     state: absent
     name: "{{ autoscaling_asg_name }}"
     region: "{{ aws_region }}"
diff --git a/roles/cs.aws-cloudfront-facts/tasks/main.yml b/roles/cs.aws-cloudfront-facts/tasks/main.yml
index 52e78c9..d10c21e 100644
--- a/roles/cs.aws-cloudfront-facts/tasks/main.yml
+++ b/roles/cs.aws-cloudfront-facts/tasks/main.yml
@@ -1,7 +1,7 @@
 - name: Get list of cloudfront distributions
-  community.aws.cloudfront_distribution_info:
+  cloudfront_distribution_info:
     region: "{{ aws_region }}"
     summary: yes
   register: cloudfront_distributions_info
 
 - name: Set list of cloudfront distributions
diff --git a/roles/cs.aws-cloudfront-post-deploy/tasks/main.yml b/roles/cs.aws-cloudfront-post-deploy/tasks/main.yml
index bc4d41b..fc7ef5a 100644
--- a/roles/cs.aws-cloudfront-post-deploy/tasks/main.yml
+++ b/roles/cs.aws-cloudfront-post-deploy/tasks/main.yml
@@ -4,9 +4,9 @@
 # cached at the new urls (basically the static asset version in the url is ignored by magento).
 
 - name: Invalidate cloudfront magento static assets
   cloudfront_invalidation:
     distribution_id: "{{ aws_cloudfront_distribution_id }}"
-    caller_reference: "deploy-{{ ansible_date_time.iso8601_basic_short }}"
+    caller_reference: "deploy-{{ ansible_facts.date_time.iso8601_basic_short }}"
     target_paths:
         - '/static/*'
-  when: aws_cloudfront_distribution_id is defined and aws_cloudfront_distribution_id != ''
\ No newline at end of file
+  when: aws_cloudfront_distribution_id is defined and aws_cloudfront_distribution_id != ''
diff --git a/roles/cs.aws-cloudfront/tasks/setup-distribution-s3-media.yml b/roles/cs.aws-cloudfront/tasks/setup-distribution-s3-media.yml
index 653e49c..965e676 100644
--- a/roles/cs.aws-cloudfront/tasks/setup-distribution-s3-media.yml
+++ b/roles/cs.aws-cloudfront/tasks/setup-distribution-s3-media.yml
@@ -13,16 +13,18 @@
     src: s3-media-distribution-config.json
     dest: "{{ aws_cloudfront_distribution_temp_dir.path }}/config.json"
 
 - name: Create cloudfront distribution
   shell: "aws cloudfront create-distribution --distribution-config=file://{{ aws_cloudfront_distribution_temp_dir.path }}/config.json"
-  when: not aws_cloudfront_distribution | default(false, true)
+  when: (aws_cloudfront_distribution | default(false, true)) is sameas false
   register: aws_cloudfront_create_distribution_cmd
 
 - name: Update cloudfront distribution
   shell: "aws cloudfront update-distribution --distribution-config=file://{{ aws_cloudfront_distribution_temp_dir.path }}/config.json --id={{ aws_cloudfront_distribution.Id }} --if-match={{ aws_cloudfront_distribution.ETag }}"
-  when: aws_cloudfront_distribution | default(false, true)
+  when:
+    - aws_cloudfront_distribution is defined
+    - aws_cloudfront_distribution is not sameas false
   register: aws_cloudfront_update_distribution_cmd
 
 - name: Set cloudfront distribution id fact
   set_fact:
     aws_cloudfront_distribution_id: "{{ (aws_cloudfront_create_distribution_cmd.stdout | from_json).Distribution.Id }}"
@@ -31,6 +33,6 @@
 - name: Ensure distribution is tagged
   cloudfront_distribution:
     state: present
     distribution_id: "{{ aws_cloudfront_distribution_id }}"
     tags: "{{ aws_cloudfront_ditribution_tags }}"
-  when: aws_cloudfront_distribution_id is defined
\ No newline at end of file
+  when: aws_cloudfront_distribution_id is defined
diff --git a/roles/cs.aws-create-ami/tasks/main.yml b/roles/cs.aws-create-ami/tasks/main.yml
index c0e1a06..27494df 100644
--- a/roles/cs.aws-create-ami/tasks/main.yml
+++ b/roles/cs.aws-create-ami/tasks/main.yml
@@ -58,10 +58,10 @@
       image_id: "{{ ami_output.image_id }}"
       build_nr: "{{ aws_ami_release_info.build_nr | default(none) }}"
       release_id: "{{ aws_ami_release_info.release_id | default(none) }}"
 
 - name: Save built AMI info into a file
-  when: aws_ami_build_save_info_file_path | default(false, true)
+  when: (aws_ami_build_save_info_file_path | default('', true) | string | length) > 0
   copy:
     dest: "{{ aws_ami_build_save_info_file_path }}"
     content: "{{ aws_create_ami_info | to_nice_json }}"
   delegate_to: localhost
diff --git a/roles/cs.aws-ec2-cleanup/tasks/main.yml b/roles/cs.aws-ec2-cleanup/tasks/main.yml
index 6acad51..658cbe6 100644
--- a/roles/cs.aws-ec2-cleanup/tasks/main.yml
+++ b/roles/cs.aws-ec2-cleanup/tasks/main.yml
@@ -55,11 +55,11 @@
     _ami_to_keep: "{{ _ami_to_keep + [item.LaunchTemplateData.ImageId ] }}"
   when: item.LaunchTemplateData.ImageId not in _ami_to_keep
   loop: "{{ _to_keep }}"
 
 - name: Get available Launch Configurations (TEMPORARY STEP)
-  ec2_lc_info:
+  community.aws.autoscaling_launch_config_info:
     region: "{{ aws_region }}"
   register: _aws_ec2_cleanup_all_lcs
 
 - name: Keep amis required for all launch configurations (TEMPORARY STEP)
   set_fact:
diff --git a/roles/cs.aws-iam-employee-access/tasks/main.yml b/roles/cs.aws-iam-employee-access/tasks/main.yml
index ed72c62..f3179bb 100644
--- a/roles/cs.aws-iam-employee-access/tasks/main.yml
+++ b/roles/cs.aws-iam-employee-access/tasks/main.yml
@@ -37,6 +37,6 @@
         assume_role_policy_document: "{{ lookup('template', 'trust_main_account_to_grant_assume_role_policy_document.json') }}"
         name: "{{ aws_iam_role_employee_root_access }}"
         state: present
         managed_policy:
           - arn:aws:iam::aws:policy/AdministratorAccess
-  when: aws_iam_master_account_id | default(false, true)
\ No newline at end of file
+  when: (aws_iam_master_account_id | default('', true) | string | length) > 0
diff --git a/roles/cs.aws-lambda-import/tasks/main.yml b/roles/cs.aws-lambda-import/tasks/main.yml
index 748bd01..93b7497 100644
--- a/roles/cs.aws-lambda-import/tasks/main.yml
+++ b/roles/cs.aws-lambda-import/tasks/main.yml
@@ -20,11 +20,11 @@
 
 - name: Register import scaling handler lambda
   lambda:
     name: "{{ aws_lambda_handle_import_scaling_name }}"
     state: "{% if magento_aws_ondemand_import_instance_enable %}present{% else %}absent{% endif %}"
-    zip_file: "{% if magento_aws_ondemand_import_instance_enable %}{{ aws_lambda_import_scaling_deploy_package_path }}{% else %}omit{% endif %}"
+    zip_file: "{{ aws_lambda_import_scaling_deploy_package_path if magento_aws_ondemand_import_instance_enable else omit }}"
     runtime: "{{ aws_lambda_handle_import_scaling_runtime }}"
     role: "arn:aws:iam::{{ aws_account_id }}:role/{{ aws_iam_role_import_scaling_lambda_execution }}"
     handler: import_scaling_handler.handle
     region: "{{ aws_region }}"
     timeout: 120
@@ -45,17 +45,17 @@
   cloudwatchevent_rule:
     name: "handle-import-instance-scaling-{{ mageops_app_name }}"
     region: "{{ aws_region }}"
     state: "{% if magento_aws_ondemand_import_instance_enable %}present{% else %}absent{% endif %}"
     schedule_expression: "{{ aws_import_scaling_lambda_schedule }}"
-    targets: "{% if magento_aws_ondemand_import_instance_enable %}{{ handle_import_scaling_lambda_eventrule_targets }}{% else %}[]{% endif %}"
+    targets: "{{ handle_import_scaling_lambda_eventrule_targets if magento_aws_ondemand_import_instance_enable else [] }}"
   register: import_scaling_schedule_event
 
 - name: Allow autoscaling event handler lambda to be executed by CloudWatch Events
   lambda_policy:
     state: "{% if magento_aws_ondemand_import_instance_enable %}present{% else %}absent{% endif %}"
     region: "{{ aws_region }}"
     function_name: "{{ aws_lambda_handle_import_scaling_name }}"
     action: "lambda:InvokeFunction"
     principal: "events.amazonaws.com"
     statement_id: "AWSEvents-importScalingHandler-{{ mageops_app_name }}"
-    source_arn: "{% if magento_aws_ondemand_import_instance_enable %}{{ import_scaling_schedule_event.rule.arn }}{% else %}omit{% endif %}"
+    source_arn: "{{ import_scaling_schedule_event.rule.arn if magento_aws_ondemand_import_instance_enable else omit }}"
diff --git a/roles/cs.aws-logs-slack/tasks/main.yml b/roles/cs.aws-logs-slack/tasks/main.yml
index 08a3b94..a1a0e59 100644
--- a/roles/cs.aws-logs-slack/tasks/main.yml
+++ b/roles/cs.aws-logs-slack/tasks/main.yml
@@ -64,12 +64,12 @@
     source_account: "{{ aws_account_id }}"
   with_items: "{{ aws_logs_slack_log_groups }}"
 
 # Function ARN has to be constructed manually, because the one from register contains version and prohibits the call from working
 - name: Attach function to exception report group
-  local_action:
-    module: "shell aws logs put-subscription-filter --region {{ aws_region }} --log-group-name /{{ mageops_project }}/{{ mageops_environment }}/{{ item.group }} --filter-name send_to_slack --filter-pattern {{ item.filter | default('')|quote }} --destination-arn arn:aws:lambda:{{ aws_region }}:{{ aws_account_id }}:function:{{ aws_lambda_slack_exceptions_forwarder_name }}"
+  shell: "aws logs put-subscription-filter --region {{ aws_region }} --log-group-name /{{ mageops_project }}/{{ mageops_environment }}/{{ item.group }} --filter-name send_to_slack --filter-pattern {{ item.filter | default('')|quote }} --destination-arn arn:aws:lambda:{{ aws_region }}:{{ aws_account_id }}:function:{{ aws_lambda_slack_exceptions_forwarder_name }}"
+  delegate_to: localhost
   with_items: "{{ aws_logs_slack_log_groups }}"
 
 - name: Fetch existing log groups
   shell: "aws logs --region {{ aws_region }} describe-log-groups"
   register: aws_logs_describe
diff --git a/roles/cs.aws-node-ami-builder/tasks/main.yml b/roles/cs.aws-node-ami-builder/tasks/main.yml
index 7e3ca1d..a9eb851 100644
--- a/roles/cs.aws-node-ami-builder/tasks/main.yml
+++ b/roles/cs.aws-node-ami-builder/tasks/main.yml
@@ -31,13 +31,13 @@
     exact_count: 1
     wait: yes
     wait_timeout: "{{ builder_create_instance_timeout }}"
     # This has zero costs on current-gen instances
     ebs_optimized: yes
-    network:
-      assign_public_ip: yes
-    security_groups: "{{ builder_instance_security_groups }}"
+    network_interfaces:
+      - assign_public_ip: yes
+        groups: "{{ builder_instance_security_groups }}"
   vars:
     builder_instance_name_tags:
       Name: "{{ builder_instance_name }}"
   register: builder_ec2
 
diff --git a/roles/cs.aws-node-facts/tasks/main.yml b/roles/cs.aws-node-facts/tasks/main.yml
index 42d0d49..f906ac0 100644
--- a/roles/cs.aws-node-facts/tasks/main.yml
+++ b/roles/cs.aws-node-facts/tasks/main.yml
@@ -1,9 +1,11 @@
 - name: Get EC2 instance information for nodes
-  ec2_instance_info:
+  amazon.aws.ec2_instance_info:
     region: "{{ aws_region }}"
     filters: "{{ aws_node_facts_base_filters | combine(aws_node_facts_base_tags | combine(node.tags) | prefix_keys('tag:')) }}"
+  vars:
+    ansible_python_interpreter: "{{ ansible_playbook_python }}"
   loop:
     - name: app_builder
       tags: "{{ aws_tags_role_app_builder }}"
     - name: persistent
       tags: "{{ aws_tags_role_persistent }}"
@@ -50,33 +52,45 @@
     _dummy: "_"
 
 - name: Set varnish host to varnish loadbalancer
   set_fact:
     mageops_varnish_host: "{{ aws_nodes_info.varnish_loadbalancer.private_ip_address }}"
-  when: varnish_as_loadbalancer and aws_nodes_info.varnish_loadbalancer
+  when:
+    - varnish_as_loadbalancer | bool
+    - aws_nodes_info.varnish_loadbalancer is mapping
 
 - name: Set elasticsearch host if not predefined
   set_fact:
     mageops_elasticsearch_host: "{{ aws_nodes_info.elasticsearch.private_ip_address }}"
-  when: not mageops_elasticsearch_host | default(false, true) and aws_nodes_info.elasticsearch
+  when:
+    - not (mageops_elasticsearch_host | default(false, true))
+    - aws_nodes_info.elasticsearch is mapping
 
 - name: Set opensearch host if not predefined
   set_fact:
     mageops_opensearch_host: "{{ aws_nodes_info.elasticsearch.private_ip_address }}"
-  when: not mageops_opensearch_host | default(false, true) and aws_nodes_info.elasticsearch
+  when:
+    - not (mageops_opensearch_host | default(false, true))
+    - aws_nodes_info.elasticsearch is mapping
 
 
 # TODO: Find RabbitMQ through tags, right now we don't have option to separate it anyway
 - name: Set RabbitMQ host if not predefined
   set_fact:
     mageops_rabbitmq_host: "{{ aws_nodes_info.elasticsearch.private_ip_address }}"
-  when: not mageops_rabbitmq_host | default(false, true) and aws_nodes_info.elasticsearch
+  when:
+    - not (mageops_rabbitmq_host | default(false, true))
+    - aws_nodes_info.elasticsearch is mapping
 
 - name: Set redis host if not predefined
   set_fact:
     mageops_redis_host: "{{ aws_nodes_info.redis.private_ip_address }}"
-  when: not mageops_redis_host | default(false, true) and aws_nodes_info.redis
+  when:
+    - not (mageops_redis_host | default(false, true))
+    - aws_nodes_info.redis is mapping
 
 - name: Set redis sessions host if not predefined
   set_fact:
     mageops_redis_sessions_host: "{{ aws_nodes_info.redis.private_ip_address }}"
-  when: not mageops_redis_sessions_host | default(false, true) and aws_nodes_info.redis
+  when:
+    - not (mageops_redis_sessions_host | default(false, true))
+    - aws_nodes_info.redis is mapping
diff --git a/roles/cs.aws-node-persistent/tasks/main.yml b/roles/cs.aws-node-persistent/tasks/main.yml
index b900a84..32088e2 100644
--- a/roles/cs.aws-node-persistent/tasks/main.yml
+++ b/roles/cs.aws-node-persistent/tasks/main.yml
@@ -34,23 +34,23 @@
           encrypted: "{{ mageops_ebs_encrypt }}"
     wait: yes
     wait_timeout: 1500
     # This has zero costs on current-gen instances
     ebs_optimized: yes
-    network:
-      assign_public_ip: yes
-    security_groups: >-
-      {{
-          aws_persistent_node_security_groups
-          + aws_security_group_redis_id | default(false, true) | ternary([aws_security_group_redis_id], [])
-          + aws_security_group_persistant_id | default(false, true) | ternary([aws_security_group_persistant_id], [])
-          + aws_security_group_elasticsearch_id | default(false, true) | ternary([aws_security_group_elasticsearch_id], [])
-          + varnish_is_in_autoscaling_group | ternary(
-              aws_security_group_varnish_id | default(false, true) | ternary([aws_security_group_varnish_id], []),
-              []
-          )
-      }}
+    network_interfaces:
+      - assign_public_ip: yes
+        groups: >-
+          {{
+              aws_persistent_node_security_groups
+              + aws_security_group_redis_id | default(false, true) | ternary([aws_security_group_redis_id], [])
+              + aws_security_group_persistant_id | default(false, true) | ternary([aws_security_group_persistant_id], [])
+              + aws_security_group_elasticsearch_id | default(false, true) | ternary([aws_security_group_elasticsearch_id], [])
+              + varnish_is_in_autoscaling_group | ternary(
+                  aws_security_group_varnish_id | default(false, true) | ternary([aws_security_group_varnish_id], []),
+                  []
+              )
+          }}
   vars:
     aws_ec2_user_launch_script: "{{ aws_persistent_node_launch_script_extra }}"
     aws_persistent_node_name_tags:
       Name: "{{ aws_persistent_node_instance_name }}"
   register: aws_persistent_ec2
@@ -92,6 +92,6 @@
 - name: Assign elastic IP to persistent node
   ec2_eip:
     region: "{{ aws_region }}"
     device_id: "{{ aws_persistent_ec2.instances[0].instance_id }}"
     ip: "{{ aws_persistent_node_elastic_ip }}"
-  when: aws_persistent_node_elastic_ip | default(false, true)
+  when: (aws_persistent_node_elastic_ip | default('', true) | string | length) > 0
diff --git a/roles/cs.aws-node-varnish/tasks/main.yml b/roles/cs.aws-node-varnish/tasks/main.yml
index 1c7585e..208f890 100644
--- a/roles/cs.aws-node-varnish/tasks/main.yml
+++ b/roles/cs.aws-node-varnish/tasks/main.yml
@@ -32,13 +32,13 @@
           encrypted: "{{ mageops_ebs_encrypt }}"
     wait: yes
     wait_timeout: 1500
     # This has zero costs on current-gen instances
     ebs_optimized: yes
-    network:
-      assign_public_ip: yes
-    security_groups: "{{ aws_varnish_node_security_groups + varnish_as_loadbalancer | ternary([aws_security_group_lb_id], []) }}"
+    network_interfaces:
+      - assign_public_ip: yes
+        groups: "{{ aws_varnish_node_security_groups + varnish_as_loadbalancer | ternary([aws_security_group_lb_id], []) }}"
   vars:
     aws_ec2_user_launch_script: "{{ aws_varnish_node_launch_script_extra }}"
     aws_varnish_node_name_tags:
       Name: "{{ aws_varnish_node_instance_name }}"
   register: aws_varnish_ec2
@@ -82,6 +82,6 @@
 - name: Assign elastic IP to varnish node
   ec2_eip:
     region: "{{ aws_region }}"
     device_id: "{{ aws_varnish_ec2.instances[0].instance_id }}"
     ip: "{{ aws_varnish_node_elastic_ip }}"
-  when: aws_varnish_node_elastic_ip | default(false, true)
+  when: (aws_varnish_node_elastic_ip | default('', true) | string | length) > 0
diff --git a/roles/cs.aws-rds-facts/tasks/main.yml b/roles/cs.aws-rds-facts/tasks/main.yml
index c05f1e5..da3a1f6 100644
--- a/roles/cs.aws-rds-facts/tasks/main.yml
+++ b/roles/cs.aws-rds-facts/tasks/main.yml
@@ -1,8 +1,10 @@
 - name: Get list of RDS instances
-  community.aws.rds_instance_info:
+  amazon.aws.rds_instance_info:
     region: "{{ aws_region }}"
+  vars:
+    ansible_python_interpreter: "{{ ansible_playbook_python }}"
   register: rds_instances_info
 
 - name: Set list of rds instances
   set_fact:
     aws_rds_instances: "{{ rds_instances_info.instances }}"
@@ -32,12 +34,11 @@
     region: "{{ aws_region }}"
     db_cluster_identifier: "{{ aws_rds_instance.db_cluster_identifier }}"
   register: rds_cluster_info
   when:
     - aws_rds_instance is defined
-    - aws_rds_instance.db_cluster_identifier is defined
-    - aws_rds_instance.db_cluster_identifier
+    - (aws_rds_instance.db_cluster_identifier | default('', true) | string | length) > 0
     - aws_rds_instance.engine is match("^aurora")
 
 - name: Set facts about project's RDS cluster
   set_fact:
     aws_rds_cluster: "{{ rds_cluster_info.clusters | first }}"
@@ -60,6 +61,10 @@
   when: aws_rds_cluster is defined
 
 - name: Set MySQL host to the RDS instance
   set_fact:
     mageops_mysql_host: "{{ aws_rds_instance.endpoint.address }}"
-  when: aws_rds_create and aws_rds_instance | default(false, true)
+  when:
+    - aws_rds_create | bool
+    - aws_rds_instance is defined
+    - aws_rds_instance.endpoint is defined
+    - aws_rds_instance.endpoint.address is defined
diff --git a/roles/cs.aws-rds-gfs-backup/tasks/cluster-db.yml b/roles/cs.aws-rds-gfs-backup/tasks/cluster-db.yml
index 6dfea31..4668597 100644
--- a/roles/cs.aws-rds-gfs-backup/tasks/cluster-db.yml
+++ b/roles/cs.aws-rds-gfs-backup/tasks/cluster-db.yml
@@ -8,15 +8,15 @@
   retries: 40
   delay: 15
 
 - name: Create weekly cluster snapshot from the daily one
   shell: "aws rds copy-db-cluster-snapshot --target-db-cluster-snapshot-identifier '{{ rds_gfs_weekly_snapshot_id }}' --source-db-cluster-snapshot-identifier '{{ rds_gfs_daily_snapshot_id }}' --tags '{{ rds_gfs_weekly_snapshot_tags | to_json }}' --region '{{ aws_region }}'"
-  when: ansible_date_time.weekday_number | int == rds_gfs_weekly_snapshot_weekday_nr
+  when: ansible_facts.date_time.weekday_number | int == rds_gfs_weekly_snapshot_weekday_nr
 
 - name: Create monthly cluster snapshot from the daily one
   shell: "aws rds copy-db-cluster-snapshot --target-db-cluster-snapshot-identifier '{{ rds_gfs_monthly_snapshot_id }}' --source-db-cluster-snapshot-identifier '{{ rds_gfs_daily_snapshot_id }}' --tags '{{ rds_gfs_monthly_snapshot_tags | to_json }}' --region '{{ aws_region }}'"
-  when: ansible_date_time.day | int == rds_gfs_monthly_snapshot_monthday_nr
+  when: ansible_facts.date_time.day | int == rds_gfs_monthly_snapshot_monthday_nr
 
 - name: Get current cluster snapshots
   amazon.aws.rds_snapshot_info:
     snapshot_type: manual
     db_cluster_identifier: "{{ rds_gfs_cluster_id }}"
@@ -39,6 +39,6 @@
   set_fact:
     rds_gfs_snapshots_to_remove: "{{ rds_gfs_daily_to_delete + rds_gfs_weekly_to_delete + rds_gfs_monthly_to_delete }}"
 
 - name: Remove old cluster snapshots
   shell: "aws rds delete-db-cluster-snapshot --db-cluster-snapshot-identifier '{{ item }}' --region '{{ aws_region }}'"
-  with_items: "{{ rds_gfs_snapshots_to_remove }}"
\ No newline at end of file
+  with_items: "{{ rds_gfs_snapshots_to_remove }}"
diff --git a/roles/cs.aws-rds-gfs-backup/tasks/main.yml b/roles/cs.aws-rds-gfs-backup/tasks/main.yml
index 7043395..fdf2d8a 100644
--- a/roles/cs.aws-rds-gfs-backup/tasks/main.yml
+++ b/roles/cs.aws-rds-gfs-backup/tasks/main.yml
@@ -19,13 +19,13 @@
     rds_gfs_cluster_id: "{{ rds_gfs_instance_data.instances[0].db_cluster_identifier | default(false) }}"
     rds_gfs_snapshot_name: "{{ rds_gfs_cluster_id | default(rds_gfs_instance_id) }}-gfs"
 
 - name: Set snapshot identifiers
   set_fact:
-    rds_gfs_daily_snapshot_id: "{{ rds_gfs_snapshot_name }}-daily-{{ ansible_date_time.date }}"
-    rds_gfs_weekly_snapshot_id: "{{ rds_gfs_snapshot_name }}-weekly-{{ ansible_date_time.date }}"
-    rds_gfs_monthly_snapshot_id: "{{ rds_gfs_snapshot_name }}-monthly-{{ ansible_date_time.date }}"
+    rds_gfs_daily_snapshot_id: "{{ rds_gfs_snapshot_name }}-daily-{{ ansible_facts.date_time.date }}"
+    rds_gfs_weekly_snapshot_id: "{{ rds_gfs_snapshot_name }}-weekly-{{ ansible_facts.date_time.date }}"
+    rds_gfs_monthly_snapshot_id: "{{ rds_gfs_snapshot_name }}-monthly-{{ ansible_facts.date_time.date }}"
     rds_gfs_daily_snapshot_tags:
         - Key: GfsType
           Value: daily
         - Key: GfsInstanceId
           Value: "{{ rds_gfs_instance_id }}"
diff --git a/roles/cs.aws-rds-gfs-backup/tasks/single-db.yml b/roles/cs.aws-rds-gfs-backup/tasks/single-db.yml
index a271f41..33576cf 100644
--- a/roles/cs.aws-rds-gfs-backup/tasks/single-db.yml
+++ b/roles/cs.aws-rds-gfs-backup/tasks/single-db.yml
@@ -4,15 +4,15 @@
 - name: Wait until daily snapshot is created
   shell: "aws rds wait db-snapshot-completed --db-snapshot-identifier '{{ rds_gfs_daily_snapshot_id }}' --region '{{ aws_region }}'"
 
 - name: Create weekly snapshot from the daily one
   shell: "aws rds copy-db-snapshot --target-db-snapshot-identifier '{{ rds_gfs_weekly_snapshot_id }}' --source-db-snapshot-identifier '{{ rds_gfs_daily_snapshot_id }}' --tags '{{ rds_gfs_weekly_snapshot_tags | to_json }}' --region '{{ aws_region }}'"
-  when: ansible_date_time.weekday_number | int == rds_gfs_weekly_snapshot_weekday_nr
+  when: ansible_facts.date_time.weekday_number | int == rds_gfs_weekly_snapshot_weekday_nr
 
 - name: Create monthly snapshot from the daily one
   shell: "aws rds copy-db-snapshot --target-db-snapshot-identifier '{{ rds_gfs_monthly_snapshot_id }}' --source-db-snapshot-identifier '{{ rds_gfs_daily_snapshot_id }}' --tags '{{ rds_gfs_monthly_snapshot_tags | to_json }}' --region '{{ aws_region }}'"
-  when: ansible_date_time.day | int == rds_gfs_monthly_snapshot_monthday_nr
+  when: ansible_facts.date_time.day | int == rds_gfs_monthly_snapshot_monthday_nr
 
 - name: Get current snapshots
   amazon.aws.rds_snapshot_info:
     snapshot_type: manual
     db_instance_identifier: "{{ rds_gfs_instance_id }}"
@@ -37,6 +37,6 @@
   set_fact:
     rds_gfs_snapshots_to_remove: "{{ rds_gfs_daily_to_delete + rds_gfs_weekly_to_delete + rds_gfs_monthly_to_delete }}"
 
 - name: Remove old snapshots
   shell: "aws rds delete-db-snapshot --db-snapshot-identifier '{{ item }}' --region '{{ aws_region }}'"
-  with_items: "{{ rds_gfs_snapshots_to_remove }}"
\ No newline at end of file
+  with_items: "{{ rds_gfs_snapshots_to_remove }}"
diff --git a/roles/cs.aws-rds/tasks/main.yml b/roles/cs.aws-rds/tasks/main.yml
index 38431a5..069929b 100644
--- a/roles/cs.aws-rds/tasks/main.yml
+++ b/roles/cs.aws-rds/tasks/main.yml
@@ -1,7 +1,7 @@
 - name: Create RDS subnet group
-  rds_subnet_group:
+  amazon.aws.rds_subnet_group:
     state: present
     region: "{{ aws_region }}"
     name: "{{ aws_rds_subnet_group_name }}"
     description: "{{ aws_rds_subnet_group_name }}"
     subnets: "{{ aws_rds_subnet_group_subnets }}"
@@ -11,37 +11,39 @@
     aws_rds_param_group_params: "{{ aws_rds_param_group_params | combine({'slow_query_log': 1, 'long_query_time': aws_rds_slowlog_time}, recursive=True) }}"
     aws_rds_cloudwatch_logs_exports: "{{ aws_rds_cloudwatch_logs_exports + [ 'slowquery' ] }}"
   when: aws_rds_slowlog_enabled
 
 - name: Create RDS parameter group
-  rds_param_group:
+  amazon.aws.rds_instance_param_group:
     state: present
     region: "{{ aws_region }}"
     name: "{{ aws_rds_param_group_name }}"
     description: "{{ aws_rds_param_group_desc }}"
     engine: "{{ aws_rds_param_group_engine }}"
     tags: "{{ aws_tags_default }}"
     params: "{{ aws_rds_param_group_params | default(omit) }}"
 
 - name: Create RDS encryption key
-  aws_kms:
+  amazon.aws.kms_key:
     alias: "{{ aws_rds_encryption_key_name }}"
     region: "{{ aws_region }}"
     tags: "{{ aws_tags_default | combine(aws_tags_kms_database) }}"
-  when: aws_rds_storage_encrypt and aws_rds_dedicated_encryption_key
+  when:
+    - aws_rds_storage_encrypt | bool
+    - aws_rds_dedicated_encryption_key | bool
 
 - name: Wait for active rds modifications to finish
-  rds_instance_info:
+  amazon.aws.rds_instance_info:
     region: "{{ aws_region }}"
     db_instance_identifier: "{{ aws_rds_instance_name }}"
   register: aws_rds_current
   retries: 600
   delay: 5
   until: (aws_rds_current.instances|length) == 0 or aws_rds_current.instances[0].db_instance_status != "modifying"
 
 - name: Check current RDS configuration
-  rds_instance_info:
+  amazon.aws.rds_instance_info:
     region: "{{ aws_region }}"
     db_instance_identifier: "{{ aws_rds_instance_name }}"
   register: aws_rds_current
 
 - name: Update RDS instance class before applying full configuration (workaround)
@@ -53,19 +55,19 @@
             rds modify-db-instance \
               --db-instance-identifier='{{ aws_rds_instance_name }}' \
               --db-instance-class='{{ aws_rds_instance_type }}' \
               --apply-immediately
     - name: Wait for modification to start
-      rds_instance_info:
+      amazon.aws.rds_instance_info:
         region: "{{ aws_region }}"
         db_instance_identifier: "{{ aws_rds_instance_name }}"
       register: aws_rds_wait_start_result
       retries: 20
       delay: 3
       until: aws_rds_wait_start_result.instances[0].db_instance_status == "modifying" or aws_rds_wait_start_result.instances[0].pending_modified_values.db_instance_class is not defined
     - name: Wait for modification to finish
-      rds_instance_info:
+      amazon.aws.rds_instance_info:
         region: "{{ aws_region }}"
         db_instance_identifier: "{{ aws_rds_instance_name }}"
       register: aws_rds_wait_finish_result
       retries: 600
       delay: 5
@@ -110,11 +112,11 @@
 - name: Upgrade MySQL/MariaDB RDS engine
   include_tasks: upgrade_iteration.yml
   loop: "{{ aws_rds_upgrade_plan }}"
 
 - name: Create MySQL/MariaDB RDS
-  rds_instance:
+  amazon.aws.rds_instance:
     region: "{{ aws_region }}"
     publicly_accessible: "{{ aws_rds_publicly_accessible }}"
     db_instance_identifier: "{{ aws_rds_instance_name }}"
     engine: "{{ aws_rds_db_engine }}"
     db_parameter_group_name: "{{ aws_rds_param_group_name }}"
@@ -140,20 +142,20 @@
     enable_cloudwatch_logs_exports: "{{ aws_rds_cloudwatch_logs_exports }}"
     apply_immediately: yes
     wait: yes
 
 - name: Wait for upgrade to finish
-  rds_instance_info:
+  amazon.aws.rds_instance_info:
     region: "{{ aws_region }}"
     db_instance_identifier: "{{ aws_rds_instance_name }}"
   register: _aws_rds_wait_upgrade_result
   retries: 600
   delay: 5
   until: _aws_rds_wait_upgrade_result.instances[0].db_instance_status == "available" or _aws_rds_wait_upgrade_result.instances[0].db_instance_status == "Storage-optimization"
   when: (aws_rds_current.instances|length) > 0 and aws_rds_current.instances[0].engine_version != aws_rds_db_engine_version
 
 - name: Remove temporary parameter groups used for engine upgrade
-  rds_param_group:
+  amazon.aws.rds_instance_param_group:
     state: absent
     name: "{{ item }}"
     region: "{{ aws_region }}"
   loop: "{{ aws_rds_temporary_parameter_groups }}"
diff --git a/roles/cs.aws-rds/tasks/upgrade_iteration.yml b/roles/cs.aws-rds/tasks/upgrade_iteration.yml
index 017418a..93d8d77 100644
--- a/roles/cs.aws-rds/tasks/upgrade_iteration.yml
+++ b/roles/cs.aws-rds/tasks/upgrade_iteration.yml
@@ -10,21 +10,21 @@
   debug:
     msg: |
       Upgrading to {{ aws_rds_db_engine }} {{ item }}
 
 - name: Create temporary RDS parameter group
-  rds_param_group:
+  amazon.aws.rds_instance_param_group:
     state: present
     region: "{{ aws_region }}"
     name: "{{ _aws_rds_upgrade_parameter_group }}"
     description: "{{ aws_rds_param_group_desc }}"
     engine: "{{ aws_rds_db_engine }}{{ item }}"
     tags: "{{ aws_tags_default }}"
     params: "{{ aws_rds_param_group_params | default(omit) }}"
 
 - name: Upgrade RDS
-  rds_instance:
+  amazon.aws.rds_instance:
     region: "{{ aws_region }}"
     publicly_accessible: "{{ aws_rds_publicly_accessible }}"
     db_instance_identifier: "{{ aws_rds_instance_name }}"
     engine: "{{ aws_rds_db_engine }}"
     db_parameter_group_name: "{{ _aws_rds_upgrade_parameter_group }}"
@@ -54,11 +54,11 @@
 - name: Wait for AWS to acknowledge that rds upgrade is happening (workaround)
   pause:
     minutes: 1
 
 - name: Wait for active rds modifications to finish
-  rds_instance_info:
+  amazon.aws.rds_instance_info:
     region: "{{ aws_region }}"
     db_instance_identifier: "{{ aws_rds_instance_name }}"
   register: aws_rds_current
   retries: 600
   delay: 5
diff --git a/roles/cs.aws-region-facts/tasks/main.yml b/roles/cs.aws-region-facts/tasks/main.yml
index 5390e11..ff653bc 100644
--- a/roles/cs.aws-region-facts/tasks/main.yml
+++ b/roles/cs.aws-region-facts/tasks/main.yml
@@ -24,11 +24,11 @@
 
 - name: Set preferred AZ to the first one if not defined
   set_fact:
     aws_preferred_availability_zone: "{{ aws_availability_zone_names | first }}"
   register: aws_selected_preferred_az
-  when: not aws_preferred_availability_zone | default(false, true)
+  when: (aws_preferred_availability_zone | default('', true) | string | length) == 0
 
 - name: Print the chosen availability zone
   debug:
     msg: "No preferred avaialability zone set, selected automatically: {{ aws_preferred_availability_zone }}"
   when: aws_selected_preferred_az is not skipped
diff --git a/roles/cs.aws-s3/tasks/main.yml b/roles/cs.aws-s3/tasks/main.yml
index 922d8f0..8ca860b 100644
--- a/roles/cs.aws-s3/tasks/main.yml
+++ b/roles/cs.aws-s3/tasks/main.yml
@@ -40,19 +40,22 @@
               {{
                   aws_s3_media_bucket_cors_allowed_origins +
                   https_termination_hosts | default([])|selectattr('server_name', 'defined')|map(attribute='server_name')|list +
                   https_termination_hosts | default([])|selectattr('aliases', 'defined')|map(attribute='aliases')|list | flatten
               }}
-          when: mageops_https_termination_enable | default(false)
+          when: mageops_https_termination_enable | default(false) | bool
         - name: Collect load balancer host
           set_fact:
             aws_s3_media_bucket_cors_allowed_origins: "{{ aws_s3_media_bucket_cors_allowed_origins + [lb_domain] }}"
-          when: aws_elb_create | default(false) and lb_domain is defined and lb_domain | length
+          when:
+            - aws_elb_create | default(false) | bool
+            - lb_domain is defined
+            - (lb_domain | string | length) > 0
       when: aws_s3_generate_allowed_origins
 
     - name: Apply CORS configuration for Media bucket
-      aws_s3_cors:
+      community.aws.s3_cors:
         region: "{{ aws_region }}"
         name: "{{ aws_s3_media_bucket }}"
         state: present
         rules:
           - allowed_origins: "{{ aws_s3_media_bucket_cors_allowed_origins | map('regex_replace', '^', 'https://')|list + aws_s3_media_bucket_cors_allowed_origins | map('regex_replace', '^', 'http://')|list  }}"
diff --git a/roles/cs.aws-security-group/tasks/main.yml b/roles/cs.aws-security-group/tasks/main.yml
index 98e3e50..01fe474 100644
--- a/roles/cs.aws-security-group/tasks/main.yml
+++ b/roles/cs.aws-security-group/tasks/main.yml
@@ -45,10 +45,22 @@
   vars:
     ec2_sg_tags:
       Name: "{{ aws_security_group_lb_name }}"
   register: aws_security_group_lb
 
+- name: Ensure security group for webnodes exists
+  ec2_group:
+    name: "{{ aws_security_group_app_name }}"
+    description: "{{ mageops_app_name }} Webnodes security group"
+    region: "{{ aws_region }}"
+    purge_rules: no
+    purge_rules_egress: no
+    vpc_id: "{{ aws_vpc_id }}"
+    tags: "{{ aws_tags_default | combine(ec2_sg_tags) }}"
+  vars:
+    ec2_sg_tags:
+      Name: "{{ aws_security_group_app_name }}"
 
 - name: Create security group for Varnish
   ec2_group:
     name: "{{ aws_security_group_varnish_name }}"
     description: "{{ mageops_app_name }} - allows for connection between Varnish servers"
diff --git a/roles/cs.aws-ses/tasks/main.yml b/roles/cs.aws-ses/tasks/main.yml
index 199dbee..90ecd48 100644
--- a/roles/cs.aws-ses/tasks/main.yml
+++ b/roles/cs.aws-ses/tasks/main.yml
@@ -14,37 +14,35 @@
         region: "{{ aws_region }}"
         display_name: "SES Complaints {{ mageops_project }}"
       register: _aws_sns_complaints
 
 - name: Add e-mail to SES
-  #community.aws.aws_ses_identity:
-  aws_ses_identity:
+  community.aws.ses_identity:
     identity: "{{ ses_email }}"
     region: "{{ aws_region }}"
     state: present
     complaint_notifications:
       topic: "{{ _aws_sns_complaints.sns_arn }}"
       include_headers: True
     bounce_notifications:
       topic: "{{ _aws_sns_bounce.sns_arn }}"
       include_headers: False
     feedback_forwarding: False
-  when: ses_email | default(false, true)
+  when: (ses_email | default('', true) | string | length) > 0
 
 - name: Add domain to SES
-  #community.aws.aws_ses_identity:
-  aws_ses_identity:
+  community.aws.ses_identity:
     identity: "{{ ses_domain }}"
     region: "{{ aws_region }}"
     state: present
     complaint_notifications:
       topic: "{{ _aws_sns_complaints.sns_arn }}"
       include_headers: yes
     bounce_notifications:
       topic: "{{ _aws_sns_bounce.sns_arn }}"
       include_headers: no
     feedback_forwarding: False
-  when: ses_domain | default(false, true)
+  when: (ses_domain | default('', true) | string | length) > 0
 
   # Could be falled back with
   # "{{ ses_domain | default(ses_email.split('@')[1]) }}"
   # but it turns out we do not need domain.
diff --git a/roles/cs.blackfire/tasks/main.yml b/roles/cs.blackfire/tasks/main.yml
index b593097..17ebefa 100644
--- a/roles/cs.blackfire/tasks/main.yml
+++ b/roles/cs.blackfire/tasks/main.yml
@@ -49,6 +49,9 @@
 
     - name: Set feature flag
       shell: "mageopscli set_feature_flag blackfire_apm {{ blackfire_enable_apm | ternary('yes', 'no') }}"
       when: aws_use
 
-  when: blackfire_install and blackfire_server_id and blackfire_server_token
+  when:
+    - blackfire_install | bool
+    - (blackfire_server_id | default('', true) | string | length) > 0
+    - (blackfire_server_token | default('', true) | string | length) > 0
diff --git a/roles/cs.deploy-containerized-tasks/tasks/main.yml b/roles/cs.deploy-containerized-tasks/tasks/main.yml
index 8ece0a9..7d6fb44 100644
--- a/roles/cs.deploy-containerized-tasks/tasks/main.yml
+++ b/roles/cs.deploy-containerized-tasks/tasks/main.yml
@@ -31,17 +31,15 @@
       loop: "{{ containerized_tasks }}"
 
     - name: Execute containerized tasks
       command: >
         docker run
-        {% if item.name is defined %}--name {{ item.name }}-{{ ansible_date_time.iso8601_basic_short }}{% endif %}
+        {% if item.name is defined %}--name {{ item.name }}-{{ ansible_facts.date_time.iso8601_basic_short }}{% endif %}
         --volume {{ item.workdir }}:{{ item.container_workdir | default(containerized_tasks_container_workdir_default) }}:rw
         {% if item.user is defined %}--user {{ item.user }}{% endif %}
         {{ item.image | mandatory }}
         {{ item.commandline | default('') }}
-      args:
-        warn: no
       ignore_errors: "{{ item.ignore_error | bool }}"
       register: containerized_tasks_result
       loop: "{{ containerized_tasks }}"
     - debug: var=containerized_tasks_result
   when: containerized_tasks | length > 0
diff --git a/roles/cs.deploy/tasks/90-emergency-link-back.yml b/roles/cs.deploy/tasks/90-emergency-link-back.yml
index 02e3e4b..214fc29 100644
--- a/roles/cs.deploy/tasks/90-emergency-link-back.yml
+++ b/roles/cs.deploy/tasks/90-emergency-link-back.yml
@@ -5,6 +5,6 @@
     dest: "{{ deploy_current_release_dir }}"
     src: "{{ deploy_current_release_path }}"
   become: yes
   become_user: "{{ deploy_app_user }}"
   ignore_errors: yes
-  when: deploy_current_release_path | default(false, true)
+  when: (deploy_current_release_path | default('', true) | string | length) > 0
diff --git a/roles/cs.deploy/tasks/91-emergency-rename.yml b/roles/cs.deploy/tasks/91-emergency-rename.yml
index 7e99f88..dcf8e1f 100644
--- a/roles/cs.deploy/tasks/91-emergency-rename.yml
+++ b/roles/cs.deploy/tasks/91-emergency-rename.yml
@@ -1,8 +1,6 @@
 - name: "Failed deploy! Damage control: Rename the deployed release directory to indicate it's broken"
   command: "mv '{{ deploy_next_release_path }}' '{{ deploy_next_release_path }}.failed'"
-  args:
-    warn: no
   become: yes
   become_user: "{{ deploy_app_user }}"
   ignore_errors: yes
-  when: deploy_next_release_path | default(false, true)
\ No newline at end of file
+  when: (deploy_next_release_path | default('', true) | string | length) > 0
diff --git a/roles/cs.deploy/tasks/main.yml b/roles/cs.deploy/tasks/main.yml
index 6205728..ad5c412 100644
--- a/roles/cs.deploy/tasks/main.yml
+++ b/roles/cs.deploy/tasks/main.yml
@@ -8,11 +8,11 @@
 
     - include_tasks: hook/hook-actions.yml
       vars:
         deploy_hook_name: "Pre install"
         deploy_hook_actions: "{{ deploy_pre_actions }}"
-      when: deploy_pre_actions | length
+      when: (deploy_pre_actions | length) > 0
 
     - import_tasks: 03-install-artifact.yml
       when: deploy_install_new_release
 
     - import_tasks: 04-link-shared-dirs.yml
@@ -23,39 +23,39 @@
 
     - include_tasks: hook/hook-actions.yml
       vars:
         deploy_hook_name: "Post install"
         deploy_hook_actions: "{{ deploy_install_actions }}"
-      when: deploy_install_actions | length
+      when: (deploy_install_actions | length) > 0
       
   always:
     - import_tasks: 06-cleanup-post-install.yml
       when: deploy_install_new_release
       
     - include_tasks: hook/hook-actions.yml
       vars:
         deploy_hook_name: "Custom cleanup"
         deploy_hook_actions: "{{ deploy_cleanup_actions }}"
-      when: deploy_cleanup_actions | length
+      when: (deploy_cleanup_actions | length) > 0
 
   rescue:
     - import_tasks: 91-emergency-rename.yml
 
     - include_tasks: hook/hook-actions.yml
       vars:
         deploy_hook_name: "Emergency installation abort"
         deploy_hook_actions: "{{ deploy_abort_install_actions }}"
-      when: deploy_abort_install_actions | length
+      when: (deploy_abort_install_actions | length) > 0
       ignore_errors: true
 
     - set_fact:
         deploy_emergency_install_aborted: yes
 
 - name: Force fail if install has been aborted
   fail:
     msg: "{{ deploy_post_install_abort_msg }}"
-  when: deploy_emergency_install_aborted is defined and deploy_emergency_install_aborted
+  when: deploy_emergency_install_aborted is defined and deploy_emergency_install_aborted | bool
 
 - name: Perform release deploy tasks
   block:
     - import_tasks: 07-relink-releases.yml
       become: yes
@@ -64,35 +64,34 @@
 
     - include_tasks: hook/hook-actions.yml
       vars:
         deploy_hook_name: "After release"
         deploy_hook_actions: "{{ deploy_release_actions }}"
-      when: deploy_release_actions | length
+      when: (deploy_release_actions | length) > 0
 
     - import_tasks: 08-post-deploy.yml
 
     - include_tasks: hook/hook-actions.yml
       vars:
         deploy_hook_name: "post"
         deploy_hook_actions: "{{ deploy_post_actions }}"
-      when: deploy_post_actions | length
+      when: (deploy_post_actions | length) > 0
 
   rescue:
     - import_tasks: 90-emergency-link-back.yml
     - import_tasks: 91-emergency-rename.yml
 
     - include_tasks: hook/hook-actions.yml
       vars:
         deploy_hook_name: "Emergency release abort"
         deploy_hook_actions: "{{ deploy_abort_release_actions }}"
-      when: deploy_abort_release_actions | length
+      when: (deploy_abort_release_actions | length) > 0
       ignore_errors: true
 
     - set_fact:
         deploy_emergency_release_aborted: yes
 
 - name: Force fail if release has been aborted
   fail:
     msg: "{{ deploy_post_release_abort_msg }}"
-  when: deploy_emergency_release_aborted is defined and deploy_emergency_release_aborted
-
+  when: deploy_emergency_release_aborted is defined and deploy_emergency_release_aborted | bool
 
diff --git a/roles/cs.firewalld/defaults/main.yml b/roles/cs.firewalld/defaults/main.yml
index 5f950d2..4e4d710 100644
--- a/roles/cs.firewalld/defaults/main.yml
+++ b/roles/cs.firewalld/defaults/main.yml
@@ -10,11 +10,11 @@ firewall_public_ports: []
 # If set to a list of IPs then public zone is stripped of all "guarded" services (if added) for security.
 # Trusted IPs shall be specified using CIDR notation. For single IPs use X.X.X.X/32.
 firewall_trusted_networks: []
 
 # Interface used for the "internal" network, change if not the main public interface
-firewall_internal_interface: "{{ ansible_default_ipv4.interface }}"
+firewall_internal_interface: "{{ ansible_facts.default_ipv4.interface }}"
 # Ansible group name of servers that will be open to themselves forming a fake "VLAN"
 firewall_internal_group: all
 # Services which should be accessible in the "internal" network
 firewall_internal_services: []
 # Ports which should be accessible in the "internal" network (use this if service for selected port is not predefined)
@@ -41,6 +41,5 @@ firewall_guarded_ports:
     - 9200-9300/tcp # elasticsearch
     - 2049/tcp      # nfs
 
 
 
-
diff --git a/roles/cs.goaccess/defaults/main.yml b/roles/cs.goaccess/defaults/main.yml
index a443318..e8d02cd 100644
--- a/roles/cs.goaccess/defaults/main.yml
+++ b/roles/cs.goaccess/defaults/main.yml
@@ -1,5 +1,6 @@
+goaccess_enabled: true
 goaccess_data_dir: /var/lib/goaccess
 goaccess_report_dir: /var/www/goaccess
 goaccess_prerotate_path: /usr/local/bin/goaccess-prerotate
 # nginx vhost will be create if defined
-# goaccess_vhost_port: 6162
\ No newline at end of file
+# goaccess_vhost_port: 6162
diff --git a/roles/cs.goaccess/tasks/main.yml b/roles/cs.goaccess/tasks/main.yml
index dbb1731..e483f6c 100644
--- a/roles/cs.goaccess/tasks/main.yml
+++ b/roles/cs.goaccess/tasks/main.yml
@@ -1,48 +1,50 @@
-- name: Ensure data dir exists
-  file:
-    path: "{{ item }}"
-    state: directory
-  with_items:
-    - "{{ goaccess_data_dir }}"
-    - "{{ goaccess_data_dir }}/daily"
-    - "{{ goaccess_data_dir }}/weekly"
-    - "{{ goaccess_data_dir }}/monthly"
+- block:
+    - name: Ensure data dir exists
+      file:
+        path: "{{ item }}"
+        state: directory
+      with_items:
+        - "{{ goaccess_data_dir }}"
+        - "{{ goaccess_data_dir }}/daily"
+        - "{{ goaccess_data_dir }}/weekly"
+        - "{{ goaccess_data_dir }}/monthly"
 
-- name: Ensure report dir exists
-  file:
-    path: "{{ goaccess_report_dir }}"
-    state: directory
+    - name: Ensure report dir exists
+      file:
+        path: "{{ goaccess_report_dir }}"
+        state: directory
 
-- name: Ensure goaccess is installed
-  dnf:
-    name: goaccess
-    state: present
+    - name: Ensure goaccess is installed
+      dnf:
+        name: goaccess
+        state: present
 
-- name: Install goaccess prerotate script
-  template:
-    src: prerotate.sh
-    dest: "{{ goaccess_prerotate_path }}"
-    mode: 0755
+    - name: Install goaccess prerotate script
+      template:
+        src: prerotate.sh
+        dest: "{{ goaccess_prerotate_path }}"
+        mode: 0755
 
-- name: Add prerotate to nginx logrotate configuration
-  blockinfile:
-    path: /etc/logrotate.d/nginx
-    marker: "# {mark} ANSIBLE MANAGED BLOCK"
-    insertbefore: "postrotate"
-    content: |
-        prerotate
-            # if goaccess fails do not fail the whole rotation
-            {{ goaccess_prerotate_path }} $@ || true
-        endscript
+    - name: Add prerotate to nginx logrotate configuration
+      blockinfile:
+        path: /etc/logrotate.d/nginx
+        marker: "# {mark} ANSIBLE MANAGED BLOCK"
+        insertbefore: "postrotate"
+        content: |
+            prerotate
+                # if goaccess fails do not fail the whole rotation
+                {{ goaccess_prerotate_path }} $@ || true
+            endscript
 
-- name: Install logrotate config for goaccess reports
-  template:
-    src: logrotate.reports
-    dest: /etc/logrotate.d/goaccess
+    - name: Install logrotate config for goaccess reports
+      template:
+        src: logrotate.reports
+        dest: /etc/logrotate.d/goaccess
 
-- name: Install goaccess vhost
-  template:
-    src: vhost.conf
-    dest: "{{ nginx_confd_dir }}/goaccess.conf"
-  notify: Reload nginx
-  when: goaccess_vhost_port is defined
+    - name: Install goaccess vhost
+      template:
+        src: vhost.conf
+        dest: "{{ nginx_confd_dir }}/goaccess.conf"
+      notify: Reload nginx
+      when: goaccess_vhost_port is defined
+  when: goaccess_enabled | bool
diff --git a/roles/cs.magento-configure/defaults/main/general.yml b/roles/cs.magento-configure/defaults/main/general.yml
index 57be31f..f3a0f69 100644
--- a/roles/cs.magento-configure/defaults/main/general.yml
+++ b/roles/cs.magento-configure/defaults/main/general.yml
@@ -80,11 +80,11 @@ magento_deploy_auto_reindex: no
 magento_scd_skip: no
 magento_scd_strategy: quick
 
 # We need a t3.small builder or frequently it will run out of memory
 # So setting the default at 1 upon consideration
-magento_scd_parallel_jobs: "{{ ansible_processor_vcpus }}"
+magento_scd_parallel_jobs: "{{ ansible_facts.processor_vcpus }}"
 magento_scd_excluded_themes: []
 
 # Optional setup:static-content:deploy skip flags
 magento_scd_no_javascript: no
 magento_scd_no_js_bundle: no
diff --git a/roles/cs.magento-configure/tasks/000-prepare-runtime-config.yml b/roles/cs.magento-configure/tasks/000-prepare-runtime-config.yml
index b6c50c7..f683886 100644
--- a/roles/cs.magento-configure/tasks/000-prepare-runtime-config.yml
+++ b/roles/cs.magento-configure/tasks/000-prepare-runtime-config.yml
@@ -19,11 +19,11 @@
 
     - name: Append the bundling task config to the task list
       set_fact:
         magento_scd_containerized_tasks: "{{ magento_scd_containerized_tasks + [magento_magepack_js_bundling_task] }}"
 
-  when: magento_scd_advanced_js_bundling and magento_scd_advanced_js_bundling_strategy == 'magepack'
+  when: (magento_scd_advanced_js_bundling | bool) and magento_scd_advanced_js_bundling_strategy == 'magepack'
 
 - name: Configure baler JS bundling task hook
   block:
     - name: Configure deploy for bundling
       block:
@@ -59,11 +59,11 @@
         magento_scd_containerized_tasks: "{{ magento_scd_containerized_tasks + [magento_baler_js_bundling_task] }}"
 
     - name: Ensure that Magento's js minification, merging and bundling is disabled
       set_fact:
         magento_core_config_settings: "{{ magento_core_config_settings + magento_baler_js_bundling_core_config }}"
-  when: magento_scd_advanced_js_bundling and magento_scd_advanced_js_bundling_strategy == 'baler'
+  when: (magento_scd_advanced_js_bundling | bool) and magento_scd_advanced_js_bundling_strategy == 'baler'
 
 - name: Check if database is initialized
   command: mysql {{ mageops_mysql_require_ssl | ternary("--ssl-mode=REQUIRED", "") }} -N --batch -u {{ mageops_app_mysql_user|quote }} -p{{ mageops_app_mysql_pass|quote }} -h {{ mageops_mysql_host|quote }} -e "SHOW TABLES FROM `{{ mageops_app_mysql_db }}` LIKE 'admin_user';"
   changed_when: false
   register: admins
diff --git a/roles/cs.magento-configure/tasks/035-clean-old-static-content.yml b/roles/cs.magento-configure/tasks/035-clean-old-static-content.yml
index ecdd145..8494608 100644
--- a/roles/cs.magento-configure/tasks/035-clean-old-static-content.yml
+++ b/roles/cs.magento-configure/tasks/035-clean-old-static-content.yml
@@ -4,12 +4,10 @@
 #   performant way, especially that this might be an S3-backed mount.
 # - Caution: This will not remove dotfiles, but we don't care.
 ###
 - name: Make sure previous Mangeto static cache files are gone
   shell: "[[ ! -d '{{ magento_static_cache_dir }}' ]] || find '{{ magento_static_cache_dir }}' -xdev -type f -exec rm -vf {} \\;"
-  args:
-    warn: no
   changed_when: _magento_install_clean_statics.stdout | trim | length > 0
   register: _magento_install_clean_statics
   retries: 5
   delay: 10 
   until: not _magento_install_clean_statics is failed
diff --git a/roles/cs.magento-configure/tasks/037-wait-for-services.yml b/roles/cs.magento-configure/tasks/037-wait-for-services.yml
index 450ecb0..f3d8bb3 100644
--- a/roles/cs.magento-configure/tasks/037-wait-for-services.yml
+++ b/roles/cs.magento-configure/tasks/037-wait-for-services.yml
@@ -1,36 +1,40 @@
 # TODO: This needs to be done on the final app node before setup:upgrade / cache:flush
 
 - name: Wait for Elasticsearch
   shell: curl -u {{ mageops_elasticsearch_username | default('elastic')}}:{{mageops_elasticsearch_password | default('changeme')}} -sfk 'http://{{ mageops_elasticsearch_host }}:{{ elasticsearch_http_port }}'
-  args:
-    warn: no
   retries: 15
   delay: 5
   register: result
   until: result.rc == 0
-  when: mageops_elasticsearch_host | default(false, true) and not mageops_skip_elasticsearch_check and mageops_elasticsearch_opensearch_flavor == "elasticsearch"
+  when:
+    - (mageops_elasticsearch_host | default('', true) | string | length) > 0
+    - not (mageops_skip_elasticsearch_check | bool)
+    - mageops_elasticsearch_opensearch_flavor == "elasticsearch"
 
 - name: Wait for Opensearch
   shell: curl -u {{ mageops_opensearch_username | default('elastic')}}:{{mageops_elasticsearch_password | default('changeme')}} -sfk 'http://{{ mageops_opensearch_host }}:{{ opensearch_http_port }}'
-  args:
-    warn: no
   retries: 15
   delay: 5
   register: result
   until: result.rc == 0
-  when: mageops_openearch_host | default(false, true) and mageops_elasticsearch_opensearch_flavor == "opensearch"
+  when:
+    - (mageops_opensearch_host | default('', true) | string | length) > 0
+    - mageops_elasticsearch_opensearch_flavor == "opensearch"
 
 - name: Wait for Redis cache host
   shell: echo -ne "PING\r\n" | nc {{ mageops_redis_host }} {{ mageops_redis_port }}
   retries: 15
   delay: 5
   register: result
   until: result.rc == 0
-  when: magento_redis_cache
+  when:
+    - magento_redis_cache | bool
+    - (mageops_redis_host | default('', true) | string | length) > 0
 
 - name: Wait for Redis session host
   shell: echo -ne "PING\r\n" | nc {{ mageops_redis_sessions_host }} {{ mageops_redis_sessions_port }}
   retries: 15
   delay: 5
   register: result
   until: result.rc == 0
+  when: (mageops_redis_sessions_host | default('', true) | string | length) > 0
diff --git a/roles/cs.magento-configure/tasks/080-core-config.yml b/roles/cs.magento-configure/tasks/080-core-config.yml
index 371969b..7248462 100644
--- a/roles/cs.magento-configure/tasks/080-core-config.yml
+++ b/roles/cs.magento-configure/tasks/080-core-config.yml
@@ -5,11 +5,11 @@
     - name: Set varnish URI for warmup crawler
       path: "cache_warmer_crawler/general/varnish_uri"
       value: "{% if magento_varnish_host %}http://{{ magento_varnish_host }}:{{ magento_varnish_port }}{% endif %}"
   set_fact:
     magento_core_config_settings: "{{ magento_core_config_settings + _extra_items }}"
-  when: magento_varnish_host | default(false, true)
+  when: (magento_varnish_host | default('', true) | string | length) > 0
 
 - name: Ensure core config database settings values
   delegate_to: localhost
   become: no
   community.mysql.mysql_query:
@@ -24,11 +24,14 @@
         value = "{{ magento_db_setting.value | quote }}",
         scope_id = 0,
         scope = "default"
       ON DUPLICATE KEY UPDATE
         value = "{{ magento_db_setting.value | quote }}"
-  when: not magento_db_setting.default | default(false) and magento_db_setting.value | default(false) is string and magento_db_setting.enabled | default(true)
+  when:
+    - not (magento_db_setting.default | default(false) | bool)
+    - magento_db_setting.value | default(false) is string
+    - magento_db_setting.enabled | default(true) | bool
   loop: "{{ magento_core_config_settings }}"
   loop_control:
     loop_var: magento_db_setting
 
 - name: Ensure core config database default values (no update if exists)
@@ -44,11 +47,14 @@
       SET
         path = "{{ magento_db_setting.path | quote }}",
         value = "{{ magento_db_setting.value | quote }}",
         scope_id = 0,
         scope = "default"
-  when: magento_db_setting.default | default(false) and magento_db_setting.value | default(false) is string and magento_db_setting.enabled | default(true)
+  when:
+    - magento_db_setting.default | default(false) | bool
+    - magento_db_setting.value | default(false) is string
+    - magento_db_setting.enabled | default(true) | bool
   loop: "{{ magento_core_config_settings }}"
   loop_control:
     loop_var: magento_db_setting
 
 - name: Ensure core config database settings are absent (defaults are used)
diff --git a/roles/cs.magento-configure/tasks/action/configure-env.yml b/roles/cs.magento-configure/tasks/action/configure-env.yml
index ceaaa0f..2dc1506 100644
--- a/roles/cs.magento-configure/tasks/action/configure-env.yml
+++ b/roles/cs.magento-configure/tasks/action/configure-env.yml
@@ -1,47 +1,51 @@
 - name: Configure Magento environment (env.php)
   block:
   - name: Enable HTTP cache
-    when: magento_http_cache_enable
+    when: magento_http_cache_enable | bool
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_http_cache, recursive=true) }}
 
   - name: Enable lazy resize configuration
-    when: lazy_resize_secret
+    when: (lazy_resize_secret | default('', true) | string | length) > 0
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_lazy_resize, recursive=true) }}
 
   - name: Enable ElasticSuite configuration
-    when: elasticsuite_version | default(false) and (mageops_elasticsearch_opensearch_flavor == "elasticsearch")
+    when:
+      - (elasticsuite_version | default('', true) | string | length) > 0
+      - mageops_elasticsearch_opensearch_flavor == "elasticsearch"
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_elasticsuite, recursive=true) }}
 
   - name: Enable ElasticSuite configuration with Opensearch
-    when: elasticsuite_version | default(false) and (mageops_elasticsearch_opensearch_flavor == "opensearch")
+    when:
+      - (elasticsuite_version | default('', true) | string | length) > 0
+      - mageops_elasticsearch_opensearch_flavor == "opensearch"
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_opensearch, recursive=true) }}
 
   - name: Configure Redis caching
-    when: magento_redis_cache
+    when: magento_redis_cache | bool
     block:
     - name: Enable default Redis cache
-      when: not magento_redis_cache_l2
+      when: not (magento_redis_cache_l2 | bool)
       set_fact:
         magento_app_etc_config: >-
           {{ magento_app_etc_config
               | combine(magento_app_etc_config_cache_default_redis, recursive=true) }}
 
     - name: Enable 2-level default Redis cache
-      when: magento_redis_cache_l2
+      when: magento_redis_cache_l2 | bool
       set_fact:
         magento_app_etc_config: >-
           {{ magento_app_etc_config
               | combine(magento_app_etc_config_cache_default_redis_l2, recursive=true) }}
 
@@ -50,39 +54,39 @@
         magento_app_etc_config: >-
           {{ magento_app_etc_config
               | combine(magento_app_etc_config_cache_page_redis, recursive=true) }}
 
   - name: Enable RabbitMQ queue configuration
-    when: magento_rabbitmq_queue
+    when: magento_rabbitmq_queue | bool
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_queue_rabbitmq, recursive=true) }}
 
   - name: Adjust configuration for consumer workers
-    when: magento_consumer_workers_enable
+    when: magento_consumer_workers_enable | bool
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_consumer_workers, recursive=true) }}
 
   - name: Adjust configuration for cron consumers
-    when: magento_cron_consumers_enable
+    when: magento_cron_consumers_enable | bool
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_cron_consumers, recursive=true) }}
 
   - name: Configure X-Magento-Vary cookie signing
-    when: magento_vary_sign
+    when: magento_vary_sign | bool
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_cookie_sign, recursive=true) }}
 
   - name: Enable mysql ssl requirement
-    when: mageops_mysql_require_ssl
+    when: mageops_mysql_require_ssl | bool
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_mysql_ssl_required, recursive=true) }}
 
@@ -91,11 +95,11 @@
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_extra, recursive=true) }}
 
   - name: Config graphql salt
-    when: magento_graphql_salt
+    when: (magento_graphql_salt | default('', true) | string | length) > 0
     set_fact:
       magento_app_etc_config: >-
         {{ magento_app_etc_config
             | combine(magento_app_etc_config_graphql_salt, recursive=true) }}
 
diff --git a/roles/cs.magento-configure/tasks/main.yml b/roles/cs.magento-configure/tasks/main.yml
index 8552941..bebb1ba 100644
--- a/roles/cs.magento-configure/tasks/main.yml
+++ b/roles/cs.magento-configure/tasks/main.yml
@@ -23,11 +23,11 @@
         - include_tasks: 075-compile-di.yml
         - include_tasks: 076-optimize-autoload.yml
         - include_tasks: 080-core-config.yml
         - include_tasks: 110-deploy-static-content.yml
           when: not magento_scd_skip
-      when: deploy_install_new_release
+      when: deploy_install_new_release | bool
   become: yes
   become_user: "{{ magento_user }}"
 
 # Refresh magento facts
 - name: Refresh magento facts
@@ -44,8 +44,8 @@
 
 - name: Install final Magento configuration
   include_tasks: 200-config-finalize.yml
 
 - include_tasks: 210-setup-workers.yml
-  when: magento_consumer_workers_enable
+  when: magento_consumer_workers_enable | bool
 
 - include_tasks: 250-setup-services.yml
diff --git a/roles/cs.magento-configure/tasks/vagrant.yml b/roles/cs.magento-configure/tasks/vagrant.yml
index 2546461..941a72c 100644
--- a/roles/cs.magento-configure/tasks/vagrant.yml
+++ b/roles/cs.magento-configure/tasks/vagrant.yml
@@ -15,11 +15,11 @@
     - include_role:
         name: cs.magento-facts
       vars:
         magento_code_directory: "{{ magento_release_dir }}"
     - include_tasks: 050-install-sample-data.yml
-      when: magento_install_sample_data
+      when: magento_install_sample_data | bool
     - include_tasks: 070-setup-modules.yml
     - include_tasks: 080-core-config.yml
     - include_tasks: 090-setup-upgrade.yml
   become: yes
   become_user: "{{ magento_user }}"
diff --git a/roles/cs.magento-postfix/tasks/main.yml b/roles/cs.magento-postfix/tasks/main.yml
index 156a323..1195c80 100644
--- a/roles/cs.magento-postfix/tasks/main.yml
+++ b/roles/cs.magento-postfix/tasks/main.yml
@@ -1,4 +1,3 @@
 - name: Ensure postfix map has Magento bounce address configured
   include_tasks: setup_bounce_address.yml
-  when: magento_bounce_email_address | default(false, true)
-
+  when: (magento_bounce_email_address | default('', true) | string | length) > 0
diff --git a/roles/cs.magento-shared-storage/tasks/main.yml b/roles/cs.magento-shared-storage/tasks/main.yml
index 8cfa8f2..85d79f1 100644
--- a/roles/cs.magento-shared-storage/tasks/main.yml
+++ b/roles/cs.magento-shared-storage/tasks/main.yml
@@ -56,6 +56,6 @@
     efs_mounts: "{{ magento_efs_app_mounts }}"
     # This is a workaround for EFS mounts overlaying the S3-backed mounts.
     efs_mount_watchdog_cron_enable: "{{ magento_media_storage_strategy == 'aws-s3' }}"
 
 - name: Clean up shared Magento asset cache
-  include: cleanup-static-cache-releases.yml
+  include_tasks: cleanup-static-cache-releases.yml
diff --git a/roles/cs.magerun/defaults/main.yml b/roles/cs.magerun/defaults/main.yml
index d697d35..a371daf 100644
--- a/roles/cs.magerun/defaults/main.yml
+++ b/roles/cs.magerun/defaults/main.yml
@@ -1,3 +1,3 @@
-magerun_version: 9.3.0
-magerun_checksum: sha256:15041cdf99466d80691d9f2ed5f37330115ea37b5ca19b4f1883f1c9a18bd26c
+magerun_version: 9.5.1
+magerun_checksum: sha256:9897fe7c2ea108aa30e68e1a2d629ab4b006231eaf6f2a9d380fec1139a31d1d
 
diff --git a/roles/cs.new-relic/defaults/main.yml b/roles/cs.new-relic/defaults/main.yml
index 4251ce5..e3a1a91 100644
--- a/roles/cs.new-relic/defaults/main.yml
+++ b/roles/cs.new-relic/defaults/main.yml
@@ -1,10 +1,10 @@
 new_relic_repo_url: http://yum.newrelic.com/pub/newrelic/el5/x86_64/newrelic-repo-5-3.noarch.rpm
 new_relic_arm_tar_version: "12.8.0.37"
 new_relic_tarball_root: "/usr/local/src"
 new_relic_tarball_filename: "newrelic-php5-{{ new_relic_arm_tar_version }}-linux.tar.gz"
-new_relic_tarball_url: "https://download.newrelic.com/php_agent/release/{{ new_relic_tarball_filename }}"
+new_relic_tarball_url: "https://download.newrelic.com/php_agent/archive/{{ new_relic_arm_tar_version }}/{{ new_relic_tarball_filename }}"
 new_relic_tarball_extract_dir: "{{ new_relic_tarball_root }}/newrelic-php5-{{ new_relic_arm_tar_version }}-linux"
 new_relic_packages:
   - newrelic-php5
 # new_relic_license:
 new_relic_app_name: "New relic app name"
diff --git a/roles/cs.new-relic/tasks/main.yml b/roles/cs.new-relic/tasks/main.yml
index 3d1e8eb..b5aab07 100644
--- a/roles/cs.new-relic/tasks/main.yml
+++ b/roles/cs.new-relic/tasks/main.yml
@@ -1,23 +1,23 @@
 - name: Fail when New Relic architecture is unsupported
   ansible.builtin.fail:
     msg: >-
       New Relic PHP agent role supports only x86_64 and aarch64.
-      Current architecture is {{ ansible_architecture }}.
-  when: ansible_architecture not in ['x86_64', 'aarch64']
+      Current architecture is {{ ansible_facts.architecture }}.
+  when: ansible_facts.architecture not in ['x86_64', 'aarch64']
 
 - name: Fail when New Relic ARM requirements are not met
   ansible.builtin.fail:
     msg: >-
       New Relic PHP agent on ARM64 requires PHP 8.0+.
-      Current php_version is {{ php_version }} on architecture {{ ansible_architecture }}.
+      Current php_version is {{ php_version }} on architecture {{ ansible_facts.architecture }}.
   when:
-    - ansible_architecture == 'aarch64'
+    - ansible_facts.architecture == 'aarch64'
     - php_version is version('8.0', '<')
 
 - name: Install New Relic via RPM on x86_64
-  when: ansible_architecture == 'x86_64'
+  when: ansible_facts.architecture == 'x86_64'
   block:
     - name: Import New Relic GPG key
       ansible.builtin.rpm_key:
         key: https://download.newrelic.com/php_agent/NEWRELIC_RPM_BD2E199C.public
         state: present
@@ -35,11 +35,11 @@
 
     - name: Initialize new relic from RPM install
       shell: "NR_INSTALL_SILENT=1 newrelic-install install"
 
 - name: Install New Relic via tarball on ARM64
-  when: ansible_architecture == 'aarch64'
+  when: ansible_facts.architecture == 'aarch64'
   block:
     - name: Ensure New Relic tarball root exists
       ansible.builtin.file:
         path: "{{ new_relic_tarball_root }}"
         state: directory
diff --git a/roles/cs.nginx-https-termination/defaults/main.yml b/roles/cs.nginx-https-termination/defaults/main.yml
index cf4ebc3..749dedd 100644
--- a/roles/cs.nginx-https-termination/defaults/main.yml
+++ b/roles/cs.nginx-https-termination/defaults/main.yml
@@ -1,6 +1,7 @@
 # Basic configuration
+https_termination_enabled: true
 https_termination_upstream_scheme: http
 https_termination_upstream_port: 80
 https_termination_upstream_host: 127.0.0.1
 https_termination_proxy_read_timeout: 90
 https_termination_conf_cookie_rewrite_path: "{{ nginx_confd_dir }}/000-global-cookie-rewrite.conf"
diff --git a/roles/cs.nginx-https-termination/tasks/000-facts.yml b/roles/cs.nginx-https-termination/tasks/000-facts.yml
index ff33902..38bf320 100644
--- a/roles/cs.nginx-https-termination/tasks/000-facts.yml
+++ b/roles/cs.nginx-https-termination/tasks/000-facts.yml
@@ -61,11 +61,11 @@
       safe_name:              "{{ vhost.name | regex_replace('[^a-z0-9]+', '_') }}"
       upstream:               "{{ vhost.upstream_uri | urlsplit }}"
       conf_fragment_dir:      "{{ nginx_serverd_dir }}/{{ vhost.name }}"
 
       crt_do_install:         "{{ vhost.crt_install_cert_src is string and vhost.crt_install_key_src is string }}"
-      crt_do_acme:            "{{ vhost.params.letsencrypt | default(false, true) }}"
+      crt_do_acme:            "{{ vhost.params.letsencrypt | default(false, true) | bool }}"
 
       crt_live_dir:           "{{ https_termination_crt_live_dir }}"
       crt_archive_dir:        "{{ https_termination_crt_archive_dir }}/{{ vhost.name }}"
 
       crt_acme_live_dir:           "{{ https_termination_crt_acme_live_dir }}/{{ vhost.name }}"
@@ -80,11 +80,11 @@
 - name: Compute tertiary runtime vhost configuration
   set_fact:
     https_termination_vhosts: "{{ https_termination_vhosts | combine({ vhost.name: https_termination_vhosts[vhost.name] | combine(vhost_derived) }) }}"
   vars:
     vhost_derived:
-      crt_do_bootstrap:             "{{ not vhost.crt_do_install or vhost.crt_do_acme }}"
+      crt_do_bootstrap:             "{{ not (vhost.crt_do_install | bool) or (vhost.crt_do_acme | bool) }}"
 
       crt_install_cert_path:        "{{ vhost.crt_archive_dir }}/installed.cert.pem"
       crt_install_key_path:         "{{ vhost.crt_archive_dir }}/installed.privkey.pem"
       crt_install_chain_path:       "{{ vhost.crt_archive_dir }}/installed.chain.pem"
       crt_install_fullchain_path:   "{{ vhost.crt_archive_dir }}/installed.fullchain.pem"
@@ -122,11 +122,11 @@
       and vhost.upstream.port == 80
       and vhost.upstream.hostname in [
         '127.0.0.1',
         '::1',
         'localhost',
-        ansible_hostname,
+        ansible_facts.hostname,
         inventory_hostname
       ]
   loop: "{{ https_termination_vhosts.values() | list }}"
   loop_control:
     label: "{{ vhost.name }}"
diff --git a/roles/cs.nginx-https-termination/tasks/030-certificates-install.yml b/roles/cs.nginx-https-termination/tasks/030-certificates-install.yml
index 65acc13..bf30b77 100644
--- a/roles/cs.nginx-https-termination/tasks/030-certificates-install.yml
+++ b/roles/cs.nginx-https-termination/tasks/030-certificates-install.yml
@@ -6,11 +6,13 @@
     backup: yes
     mode: 0600
   vars:
     vhost: "{{ entry[0] }}"
     key: "{{ entry[1] }}"
-  when: vhost.crt_do_install and vhost[key.src]
+  when:
+    - vhost.crt_do_install | bool
+    - (vhost[key.src] | default('', true) | string | length) > 0
   loop: >-
     {{
       https_termination_vhosts.values() | product([
         { 'src': 'crt_install_cert_src',  'dst': 'crt_install_cert_path' },
         { 'src': 'crt_install_key_src',   'dst': 'crt_install_key_path' },
@@ -30,11 +32,13 @@
     content: |
       {{ lookup('file', vhost.crt_install_cert_src) }}
       {{ lookup('file', vhost.crt_install_chain_src) }}
     mode: 0600
     validate: 'openssl x509 -in %s -text -noout'
-  when: vhost.crt_do_install and vhost.crt_install_chain_src
+  when:
+    - vhost.crt_do_install | bool
+    - (vhost.crt_install_chain_src | default('', true) | string | length) > 0
   loop: "{{ https_termination_vhosts.values() | list }}"
   loop_control:
     label: "{{ vhost.name }} -> {{ vhost.crt_install_fullchain_path }}"
     loop_var: vhost
   notify: Reload nginx
@@ -69,6 +73,6 @@
           ])
         | list
     }}
   loop_control:
     label: "{{ vhost.name }} -> {{ vhost[key.dst] }}"
-    loop_var: entry
\ No newline at end of file
+    loop_var: entry
diff --git a/roles/cs.nginx-https-termination/tasks/032-certificates-bootstrap.yml b/roles/cs.nginx-https-termination/tasks/032-certificates-bootstrap.yml
index c7b18ee..19352ff 100644
--- a/roles/cs.nginx-https-termination/tasks/032-certificates-bootstrap.yml
+++ b/roles/cs.nginx-https-termination/tasks/032-certificates-bootstrap.yml
@@ -6,11 +6,11 @@
 - name: Generate vhost private key
   openssl_privatekey:[REDACTED VALUE BLOCK]
     [REDACTED ENCRYPTED VALUE]
     [REDACTED ENCRYPTED VALUE]
     [REDACTED ENCRYPTED VALUE]
-  when: vhost.crt_do_bootstrap
+  when: vhost.crt_do_bootstrap | bool
   loop: "{{ https_termination_vhosts.values() | list }}"
   loop_control:
     label: "{{ vhost.name }}"
     loop_var: vhost
 
@@ -26,11 +26,11 @@
           | default([])
           | map('regex_replace', '^', 'DNS:')
           | list
       }}
     subject_alt_name_critical: yes
-  when: vhost.crt_do_bootstrap
+  when: vhost.crt_do_bootstrap | bool
   loop: "{{ https_termination_vhosts.values() | list }}"
   loop_control:
     label: "{{ vhost.name }}"
     loop_var: vhost
 
@@ -39,11 +39,11 @@
     select_crypto_backend: cryptography
     path: "{{ vhost.crt_boot_cert_path }}"
     privatekey_path: "{{ vhost.crt_boot_key_path }}"
     csr_path: "{{ vhost.crt_boot_csr_path }}"
     provider: selfsigned
-  when: vhost.crt_do_bootstrap
+  when: vhost.crt_do_bootstrap | bool
   loop: "{{ https_termination_vhosts.values() | list }}"
   loop_control:
     label: "{{ vhost.name }}"
     loop_var: vhost
   notify: Reload nginx
@@ -52,22 +52,22 @@
   file:
     state: link
     force: yes
     src:  "{{ vhost.crt_boot_cert_path }}"
     dest: "{{ vhost.crt_boot_fullchain_path }}"
-  when: vhost.crt_do_bootstrap
+  when: vhost.crt_do_bootstrap | bool
   loop: "{{ https_termination_vhosts.values() | list }}"
   loop_control:
     label: "{{ vhost.name }}"
     loop_var: vhost
   notify: Reload nginx
 
 - name: Check for existing live cert
   stat:
     path: "{{ vhost.crt_live_fullchain_path }}"
     follow: yes
-  when: vhost.crt_do_bootstrap
+  when: vhost.crt_do_bootstrap | bool
   loop: "{{ https_termination_vhosts.values() | list }}"
   loop_control:
     label: "{{ vhost.name }}"
     loop_var: vhost
   register: https_termination_live_check
@@ -76,11 +76,11 @@
   file:
     state: link
     src:  "{{ vhost[key.src] }}"
     dest: "{{ vhost[key.dst] }}"
     force: yes
-  when: vhost.crt_do_bootstrap and not (live_check.stat.exists | default(false))
+  when: (vhost.crt_do_bootstrap | bool) and not (live_check.stat.exists | default(false))
   vars:
     vhost: "{{ entry[0][0] }}"
     live_check: "{{ entry[0][1] }}"
     key: "{{ entry[1] }}"
   loop: >-
diff --git a/roles/cs.nginx-https-termination/tasks/034-certificates-acme.yml b/roles/cs.nginx-https-termination/tasks/034-certificates-acme.yml
index b75b8cd..f5fc146 100644
--- a/roles/cs.nginx-https-termination/tasks/034-certificates-acme.yml
+++ b/roles/cs.nginx-https-termination/tasks/034-certificates-acme.yml
@@ -50,11 +50,11 @@
       --webroot-path,   "{{ vhost.crt_acme_webroot_dir }}",
       --domains,        "{{ ([vhost.server_name] + vhost.server_aliases | default([], true)) | join(',') }}",
       --cert-name,      "{{ vhost.name }}",
       --post-hook,      "/usr/bin/systemctl reload nginx"
     ]
-  when: vhost.crt_do_acme
+  when: vhost.crt_do_acme | bool
   loop: "{{ https_termination_vhosts.values() | list }}"
   loop_control:
     label: "{{ vhost.name }} -> {{ (certbot_args_default + certbot_args_vhost) | join(' ') }}"
     loop_var: vhost
   register: https_termination_certbot_run
@@ -62,11 +62,11 @@
 - name: Symlink latest ACME certificates as live ones
   file:
     state: link
     src:  "{{ vhost[key.src] }}"
     dest: "{{ vhost[key.dst] }}"
-  when: vhost.crt_do_acme
+  when: vhost.crt_do_acme | bool
   vars:
     vhost: "{{ entry[0] }}"
     key: "{{ entry[1] }}"
   loop: >-
     {{
diff --git a/roles/cs.nginx-https-termination/tasks/main.yml b/roles/cs.nginx-https-termination/tasks/main.yml
index e354e25..dfa8aad 100644
--- a/roles/cs.nginx-https-termination/tasks/main.yml
+++ b/roles/cs.nginx-https-termination/tasks/main.yml
@@ -4,24 +4,30 @@
     path: "{{ nginx_confd_dir }}/{{ item }}"
     state: absent
   loop:
     # Renamed to '000-global-cache-miss-log.conf' in 259201d732db79a43acd3
     - "000-logging-extra.conf"
+  when: https_termination_enabled | bool
 
 - name: Prepare effective configuration
   import_tasks: 000-facts.yml
+  when: https_termination_enabled | bool
 
 - name: Setup filesystem structure
   import_tasks: 010-filesystem.yml
+  when: https_termination_enabled | bool
 
 - name: Create filesystem structure
   import_tasks: 020-nginx.yml
+  when: https_termination_enabled | bool
 
 - name: Install user-provided certificates
   import_tasks: 030-certificates-install.yml
+  when: https_termination_enabled | bool
 
 - name: Bootstrap self-signed certificates if not provided
   import_tasks: 032-certificates-bootstrap.yml
+  when: https_termination_enabled | bool
 
 - name: Setup automatically renewed ACME certificates
   import_tasks: 034-certificates-acme.yml
-
+  when: https_termination_enabled | bool
diff --git a/roles/cs.nginx-language-redirect-multilevel/defaults/main.yml b/roles/cs.nginx-language-redirect-multilevel/defaults/main.yml
index f657400..d6f8aba 100644
--- a/roles/cs.nginx-language-redirect-multilevel/defaults/main.yml
+++ b/roles/cs.nginx-language-redirect-multilevel/defaults/main.yml
@@ -1,6 +1,8 @@
 # Choice mode for geoip level
+nginx_language_redirect_multilevel_enabled: true
+
 # geolite2 - use geolite2 location data to determine location
 #   language codes are uppercase 2 letter codes
 #   eg: PL, US
 # none - disable logic
 nginx_language_redirect_multilevel_geoip_mode: geolite2
diff --git a/roles/cs.nginx-language-redirect-multilevel/meta/main.yml b/roles/cs.nginx-language-redirect-multilevel/meta/main.yml
index 429c103..2f0cf43 100644
--- a/roles/cs.nginx-language-redirect-multilevel/meta/main.yml
+++ b/roles/cs.nginx-language-redirect-multilevel/meta/main.yml
@@ -1,6 +1,6 @@
 dependencies:
   - role: cs.nginx
   - role: cs.repo-mageops
-    when: nginx_language_redirect_multilevel_geoip_mode == 'geolite2'
+    when: nginx_language_redirect_multilevel_enabled | bool and nginx_language_redirect_multilevel_geoip_mode == 'geolite2'
   - role: cs.geolite2
-    when: nginx_language_redirect_multilevel_geoip_mode == 'geolite2'
+    when: nginx_language_redirect_multilevel_enabled | bool and nginx_language_redirect_multilevel_geoip_mode == 'geolite2'
diff --git a/roles/cs.nginx-language-redirect-multilevel/tasks/main.yml b/roles/cs.nginx-language-redirect-multilevel/tasks/main.yml
index 3d91316..5bd66f7 100644
--- a/roles/cs.nginx-language-redirect-multilevel/tasks/main.yml
+++ b/roles/cs.nginx-language-redirect-multilevel/tasks/main.yml
@@ -1,6 +1,7 @@
 - name: Install dependencies
   import_tasks: 000-install.yml
+  when: nginx_language_redirect_multilevel_enabled | bool
 
 - name: Configure redirects
   import_tasks: 001-configure.yml
-
+  when: nginx_language_redirect_multilevel_enabled | bool
diff --git a/roles/cs.nginx-language-redirect/defaults/main.yml b/roles/cs.nginx-language-redirect/defaults/main.yml
index 4cb0b5a..42b54b9 100644
--- a/roles/cs.nginx-language-redirect/defaults/main.yml
+++ b/roles/cs.nginx-language-redirect/defaults/main.yml
@@ -1,6 +1,7 @@
 # Name of server.d include
+nginx_language_redirect_enabled: true
 nginx_language_redirect_site: default
 
 # kind of redirect we want to have
 # geofence - blocks access completly
 # home-redirect - redirect is performed only for single url
diff --git a/roles/cs.nginx-language-redirect/meta/main.yml b/roles/cs.nginx-language-redirect/meta/main.yml
index 4b4409f..cbc8728 100644
--- a/roles/cs.nginx-language-redirect/meta/main.yml
+++ b/roles/cs.nginx-language-redirect/meta/main.yml
@@ -1,8 +1,8 @@
 dependencies:
   - role: cs.nginx
   - role: cs.repo-mageops
-    when: nginx_language_redirect_detection_method == 'geolite2'
+    when: nginx_language_redirect_enabled | bool and nginx_language_redirect_detection_method == 'geolite2'
   - role: cs.geolite2
-    when: nginx_language_redirect_detection_method == 'geolite2'
+    when: nginx_language_redirect_enabled | bool and nginx_language_redirect_detection_method == 'geolite2'
   - role: cs.cloudflare
-    when: nginx_language_redirect_detection_method == 'cloudflare'
+    when: nginx_language_redirect_enabled | bool and nginx_language_redirect_detection_method == 'cloudflare'
diff --git a/roles/cs.nginx-language-redirect/tasks/main.yml b/roles/cs.nginx-language-redirect/tasks/main.yml
index 3d91316..6e48516 100644
--- a/roles/cs.nginx-language-redirect/tasks/main.yml
+++ b/roles/cs.nginx-language-redirect/tasks/main.yml
@@ -1,6 +1,7 @@
 - name: Install dependencies
   import_tasks: 000-install.yml
+  when: nginx_language_redirect_enabled | bool
 
 - name: Configure redirects
   import_tasks: 001-configure.yml
-
+  when: nginx_language_redirect_enabled | bool
diff --git a/roles/cs.packages/tasks/main.yml b/roles/cs.packages/tasks/main.yml
index c2b08ee..a9d037a 100644
--- a/roles/cs.packages/tasks/main.yml
+++ b/roles/cs.packages/tasks/main.yml
@@ -10,20 +10,22 @@
   block:
     - name: Make sure banned packages are not present
       dnf:
         name: "{{ packages_remove | default([]) }}"
         state: absent
-      when: packages_remove is defined and packages_remove | length
+      when:
+        - packages_remove is defined
+        - (packages_remove | length) > 0
 
     - name: Store information that package maintenance was done
       copy:
-        content: "{{ ansible_date_time.epoch }}"
+        content: "{{ ansible_facts.date_time.epoch }}"
         dest: "{{ packages_maintenance_marker_path }}"
   when: >-
     packages_maintenance_last_timestamp.content is not defined or (
       (
-        packages_maintenance_last_timestamp.content | int - ansible_date_time.epoch | int
+        packages_maintenance_last_timestamp.content | int - ansible_facts.date_time.epoch | int
       ) > packages_maintenance_interval | int
     )
 
 # Retries here are required because of funky fastly caching
 # and sometimes selected fastly mirror is not resolving some packages (404)
diff --git a/roles/cs.php-fpm/tasks/main.yml b/roles/cs.php-fpm/tasks/main.yml
index 93efd0c..928ec58 100644
--- a/roles/cs.php-fpm/tasks/main.yml
+++ b/roles/cs.php-fpm/tasks/main.yml
@@ -1,22 +1,22 @@
 - debug:
-    msg: "Detected: {{ ansible_memtotal_mb }}M of memory and {{ ansible_processor_vcpus }} vcpus"
+    msg: "Detected: {{ ansible_facts.memtotal_mb }}M of memory and {{ ansible_facts.processor_vcpus }} vcpus"
 
 - name: Calculate workers
   set_fact:
     php_fpm_pm_max_children_by_memory: >-
       {{
           (
             (
-              ( ansible_memtotal_mb * 1024 * 1024 )
+              ( ansible_facts.memtotal_mb * 1024 * 1024 )
               - ( mageops_app_node_reserved_memory | human_to_bytes )
             )
             / ( php_http_request_memory_limit | human_to_bytes )
           ) | int
       }}
 
-    php_fpm_pm_max_children_by_cpu: "{{ ansible_processor_vcpus * 8 | int }}"
+    php_fpm_pm_max_children_by_cpu: "{{ ansible_facts.processor_vcpus * 8 | int }}"
 
 - name: Calculate default workers
   set_fact:
     # At least 4 workers, but limit by memory and CPU capacity
     php_fpm_pm_max_children_default: "{{
diff --git a/roles/cs.php-tideways/tasks/main.yml b/roles/cs.php-tideways/tasks/main.yml
index e3ceefb..6c34bc2 100644
--- a/roles/cs.php-tideways/tasks/main.yml
+++ b/roles/cs.php-tideways/tasks/main.yml
@@ -1,7 +1,9 @@
 - name: Enable tideways
-  when: tideways_enable and tideways_api_key | default(false, true)
+  when:
+    - tideways_enable | bool
+    - (tideways_api_key | default('', true) | string | length) > 0
   block:
     - name: Install tideways repo GPG keys
       rpm_key:
         state: present
         key: "{{ key_url }}"
diff --git a/roles/cs.pio/tasks/install_rpm.yml b/roles/cs.pio/tasks/install_rpm.yml
index 13c6863..60c97a1 100644
--- a/roles/cs.pio/tasks/install_rpm.yml
+++ b/roles/cs.pio/tasks/install_rpm.yml
@@ -4,11 +4,11 @@
     suffix: pio-worker-install
   register: _temp_dir
 
 - name: Download pio-worker rpm
   get_url:
-    url: "{{ pio_package_url_rpm[ansible_architecture] }}"
+    url: "{{ pio_package_url_rpm[ansible_facts.architecture] }}"
     dest: "{{ _temp_dir.path }}/pio-worker.rpm"
 
 - name: Install pio-worker rpm
   dnf:
     name: "{{ _temp_dir.path }}/pio-worker.rpm"
diff --git a/roles/cs.rabbitmq/defaults/main.yml b/roles/cs.rabbitmq/defaults/main.yml
index f8b47da..f25758a 100644
--- a/roles/cs.rabbitmq/defaults/main.yml
+++ b/roles/cs.rabbitmq/defaults/main.yml
@@ -8,10 +8,15 @@ rabbitmq_amqp_port: 5672
 rabbitmq_http_port: 15672
 
 # Whether to enable the web management API+UI plugin
 rabbitmq_enable_management: no
 
+# RabbitMQ release series to install. Keeps installs and updates within this
+# minor release while still allowing patch releases, e.g. 4.2.x.
+rabbitmq_release: "4.2"
+rabbitmq_server_package_name: "rabbitmq-server-{{ rabbitmq_release }}.*"
+
 # List of plugins to be enabled besides the management UI
 rabbitmq_plugins: []
 
 # These are kind of a "namespaces" that can be used
 # to separate multiple apps on one RMQ instance
diff --git a/roles/cs.rabbitmq/handlers/main.yml b/roles/cs.rabbitmq/handlers/main.yml
index b36776a..c103f8b 100644
--- a/roles/cs.rabbitmq/handlers/main.yml
+++ b/roles/cs.rabbitmq/handlers/main.yml
@@ -1,4 +1,4 @@
 - name: Restart rabbitmq
   service:
     name: rabbitmq-server
-    state: restarted
\ No newline at end of file
+    state: restarted
diff --git a/roles/cs.rabbitmq/tasks/main.yml b/roles/cs.rabbitmq/tasks/main.yml
index 474fe33..e21736b 100644
--- a/roles/cs.rabbitmq/tasks/main.yml
+++ b/roles/cs.rabbitmq/tasks/main.yml
@@ -1,22 +1,35 @@
 - name: Install RabbitMQ Erlang Package
+  when: ansible_facts.architecture == 'x86_64'
   dnf:
     allow_downgrade: no
     name: "erlang"
   notify: Restart rabbitmq
 
+- name: Install RabbitMQ Erlang RPM for aarch64
+  when: ansible_facts.architecture == 'aarch64'
+  dnf:
+    allow_downgrade: no
+    # RabbitMQ's direct aarch64 Erlang RPM is not signed.
+    disable_gpg_check: yes
+    name: "{{ rabbitmq_erlang_aarch64_rpm_url }}"
+    state: present
+  notify: Restart rabbitmq
+
 - name: Install RabbitMQ Package
   dnf:
     allow_downgrade: no
-    name: "rabbitmq-server"
+    name: "{{ rabbitmq_server_package_name }}"
+    state: present
   notify: Restart rabbitmq
 
 - name: Install rabbitmq configuration file
   template:
     src: config.j2
     dest: /etc/rabbitmq/rabbitmq.conf
     backup: yes
+    mode: "0644"
   notify: Restart rabbitmq
 
 - name: Add management plugin to the list if needed
   set_fact:
     rabbitmq_plugins: "{{ rabbitmq_plugins + ['rabbitmq_management', 'rabbitmq_management_agent'] }}"
@@ -28,16 +41,18 @@
 - name: Configure enabled plugins
   copy:
     force: yes
     content: "[{{ rabbitmq_plugins | join(',') }}]." # The dot must stay
     dest: /etc/rabbitmq/enabled_plugins
+    mode: "0644"
   notify: Restart rabbitmq
 
 - name: Configure node name
   copy:
     content: "NODENAME={{ rabbitmq_nodename }}"
     dest: /etc/rabbitmq/rabbitmq-env.conf
+    mode: "0644"
 
 - name: Ensure the rabbitmq service is started and enabled
   service:
     name: rabbitmq-server
     state: started
diff --git a/roles/cs.redis/tasks/configure.yml b/roles/cs.redis/tasks/configure.yml
index f5e7e2f..1dafdab 100644
--- a/roles/cs.redis/tasks/configure.yml
+++ b/roles/cs.redis/tasks/configure.yml
@@ -117,20 +117,19 @@
 - name: Stop {{ redis_uninstalling_flavor }} in case of migration
   service:
     name: "{{ redis_uninstalling_flavor }}"
     state: stopped
     enabled: false
-  when: services[redis_uninstalling_flavor+'.service']['status'] | default('not-found') != 'not-found'
+  when: ansible_facts.services.get(redis_uninstalling_flavor ~ '.service', {}).status | default('not-found') != 'not-found'
 
 - name: Stop {{ redis_uninstalling_flavor }} session in case of migration
   service:
     name: "{{ redis_uninstalling_flavor }}-sessions"
     state: stopped
     enabled: false
-  when: mageops_redis_sessions_create and services[redis_uninstalling_flavor+'-sessions.service']['status'] | default('not-found') != 'not-found'
+  when: mageops_redis_sessions_create and ansible_facts.services.get(redis_uninstalling_flavor ~ '-sessions.service', {}).status | default('not-found') != 'not-found'
 
 - name: Ensure Redis/valkey service is started
   service:
     name: "{{ redis_daemon }}"
     state: started
     enabled: yes
-
diff --git a/roles/cs.repo-mageops/handlers/main.yml b/roles/cs.repo-mageops/handlers/main.yml
index 802f665..27daa98 100644
--- a/roles/cs.repo-mageops/handlers/main.yml
+++ b/roles/cs.repo-mageops/handlers/main.yml
@@ -1,5 +1,3 @@
 - name: Regenerate dnf cache for MageOps repo
   command: dnf --disablerepo="*" --enablerepo="mageops" makecache
-  args:
-    warn: no
-  changed_when: false
\ No newline at end of file
+  changed_when: false
diff --git a/roles/cs.repo-rabbitmq/defaults/main.yml b/roles/cs.repo-rabbitmq/defaults/main.yml
new file mode 100644
index 0000000..5fa6d2a
--- /dev/null
+++ b/roles/cs.repo-rabbitmq/defaults/main.yml
@@ -0,0 +1,7 @@
+# RabbitMQ release series used by repository and package installs.
+rabbitmq_release: "4.2"
+
+# Erlang RPM used on aarch64 where the RabbitMQ Erlang repo does not provide ARM packages.
+rabbitmq_erlang_aarch64_rpm_version: "27.3.4.13-1"
+rabbitmq_erlang_aarch64_release_tag: "{{ rabbitmq_erlang_aarch64_rpm_version | regex_replace('-.*$', '') }}"
+rabbitmq_erlang_aarch64_rpm_url: "https://github.com/rabbitmq/erlang-rpm/releases/download/v{{ rabbitmq_erlang_aarch64_release_tag }}/erlang-{{ rabbitmq_erlang_aarch64_rpm_version }}.el9.aarch64.rpm"
diff --git a/roles/cs.repo-rabbitmq/tasks/main.yml b/roles/cs.repo-rabbitmq/tasks/main.yml
index 6bba0a5..11c20fb 100644
--- a/roles/cs.repo-rabbitmq/tasks/main.yml
+++ b/roles/cs.repo-rabbitmq/tasks/main.yml
@@ -1,9 +1,16 @@
 - name: Check if architecture is supported
   fail:
-    msg: "You cannot install RabbitMQ on this architecture. Please use an x86_64 machine."
-  when: ansible_architecture not in ['x86_64']
+    msg: "You cannot install RabbitMQ on this architecture. Supported architectures: x86_64, aarch64."
+  when: ansible_facts.architecture not in ['x86_64', 'aarch64']
 
 - name: Install rabbitmq repo
   template:
     src: rabbitmq.repo
     dest: /etc/yum.repos.d/rabbitmq.repo
+    mode: "0644"
+
+- name: Import RabbitMQ release signing key for ARM package repositories
+  when: ansible_facts.architecture == 'aarch64'
+  rpm_key:
+    state: present
+    key: https://github.com/rabbitmq/signing-keys/releases/download/3.0/rabbitmq-release-signing-key.asc
diff --git a/roles/cs.s3-mount/tasks/002-setup-mounts.yml b/roles/cs.s3-mount/tasks/002-setup-mounts.yml
index 85c88b0..287be94 100644
--- a/roles/cs.s3-mount/tasks/002-setup-mounts.yml
+++ b/roles/cs.s3-mount/tasks/002-setup-mounts.yml
@@ -1,13 +1,13 @@
 - name: Create S3 mount remote source dirs
   become: no
-  local_action:
-    module: aws_s3
+  amazon.aws.s3_object:
     bucket: "{{ s3_mount_bucket.bucket.split(':')[0] }}"
     object: "{{ s3_mount_bucket.bucket.split(':')[1] }}"
     mode: create
     region: "{{ aws_region }}"
+  delegate_to: localhost
   when: s3_mount_bucket.bucket is search(':/')
   loop: "{{ s3_mount_buckets_resolved }}"
   loop_control:
     loop_var: s3_mount_bucket
 
diff --git a/roles/cs.s3-mount/tasks/main.yml b/roles/cs.s3-mount/tasks/main.yml
index 8954ff3..1fc8776 100644
--- a/roles/cs.s3-mount/tasks/main.yml
+++ b/roles/cs.s3-mount/tasks/main.yml
@@ -7,8 +7,8 @@
   block:
     - include_tasks: 002-setup-mounts.yml
     - include_tasks: 003-setup-watchdog.yml
       when: s3_mount_backend == 's3fs'
     - include_tasks: 004-restore-premount-backups.yml
-      when: s3fs_premount_bind_mounts | length
+      when: (s3fs_premount_bind_mounts | length) > 0
   always:
     - include_tasks: 005-cleanup.yml
diff --git a/roles/cs.ssh-proxy-user/tasks/main.yml b/roles/cs.ssh-proxy-user/tasks/main.yml
index ba4eae3..d47e195 100644
--- a/roles/cs.ssh-proxy-user/tasks/main.yml
+++ b/roles/cs.ssh-proxy-user/tasks/main.yml
@@ -1,12 +1,20 @@
+- name: Validate SSH tunnel private key secret
+  assert:
+    that:
+      - (ssh_tunel_private_key_secret | default('', true) | string | length) > 0
+    fail_msg: "ssh_tunel_private_key_secret must be set when mageops_ssh_proxy_persistant is enabled."
+    quiet: true
+
 - name: Generate public key
-  shell: "ssh-keygen -y -f /dev/stdin <<< \"$( echo {{ ssh_tunel_private_key_secret }} | base64 -d )\""
-  args:
-    executable: /bin/bash
+  command:
+    cmd: ssh-keygen -y -f /dev/stdin
+    stdin: "{{ ssh_tunel_private_key_secret | b64decode }}"
   register: _ssh_tunel_public_key
   delegate_to: localhost
   become: no
+  no_log: true
 
 - name: Create tunel user
   user:
     name: tunel
     state: present
diff --git a/roles/cs.ssh-tunel/tasks/main.yml b/roles/cs.ssh-tunel/tasks/main.yml
index 7c36152..7d6ec95 100644
--- a/roles/cs.ssh-tunel/tasks/main.yml
+++ b/roles/cs.ssh-tunel/tasks/main.yml
@@ -1,5 +1,12 @@
+- name: Validate SSH tunnel private key secret
+  assert:
+    that:
+      - (ssh_tunel_private_key_secret | default('', true) | string | length) > 0
+    fail_msg: "ssh_tunel_private_key_secret must be set when mageops_ssh_proxy_persistant is enabled."
+    quiet: true
+
 - name: Install private key
   file:
     path: /etc/ssh_tunel
     state: directory
     owner: root
@@ -11,10 +18,11 @@
     dest: /etc/ssh_tunel/key
     mode: 0600
     owner: root
     group: root
     content: "{{ ssh_tunel_private_key_secret | b64decode }}"
+  no_log: true
 
 - name: Install tunel service
   template:
     dest: /etc/systemd/system/ssh_proxy.service
     src: ssh_proxy.service
diff --git a/roles/cs.sshd/defaults/main.yml b/roles/cs.sshd/defaults/main.yml
index 9a098e4..e6279a1 100644
--- a/roles/cs.sshd/defaults/main.yml
+++ b/roles/cs.sshd/defaults/main.yml
@@ -21,11 +21,11 @@ sshd_max_auth_tries: "{{ sshd_password_auth | ternary(1, 20) }}"
 
 # List of values to set for directive `PermitListen` in the for "host:port"
 # We could allow everything (sshd default) since user has shell anyway so
 # he can forward any port using other means, however, lets stick only to
 # the local network.
-sshd_permit_open: "127.0.0.1:* {{ ansible_default_ipv4.network | default('0.0.0.0') }}:*"
+sshd_permit_open: "127.0.0.1:* {{ ansible_facts.default_ipv4.network | default('0.0.0.0') }}:*"
 
 # PITA: There is no `PermitListen` directive in OpenSSH 7.4 (latest on CentOS 7)
 # This option should be present since OpenSSH 7.8, so maybe in CentOS 8...
 # So we have to rely on the firewall / virtual network restrictions for the the
 # publicly bindable ports. Anyway if user connects as root it doesn't really matter.
diff --git a/roles/cs.swap/tasks/main.yml b/roles/cs.swap/tasks/main.yml
index ffa854b..1e52578 100644
--- a/roles/cs.swap/tasks/main.yml
+++ b/roles/cs.swap/tasks/main.yml
@@ -32,8 +32,7 @@
       sysctl:
         name: vm.swappiness
         value: "{{ swap_swappiness }}"
         reload: yes
         state: present
-  when: ansible_swaptotal_mb < 1
-
+  when: ansible_facts.swaptotal_mb < 1
 
diff --git a/roles/cs.unison/meta/main.yml b/roles/cs.unison/meta/main.yml
index ef2dda3..668caae 100644
--- a/roles/cs.unison/meta/main.yml
+++ b/roles/cs.unison/meta/main.yml
@@ -1,3 +1,3 @@
 dependencies:
   - role: cs.repo-mageops
-    when: ansible_distribution | lower == 'rocky'
+    when: ansible_facts.distribution | lower == 'rocky'
diff --git a/roles/cs.unison/tasks/main.yml b/roles/cs.unison/tasks/main.yml
index 0d4b09e..0c4e204 100644
--- a/roles/cs.unison/tasks/main.yml
+++ b/roles/cs.unison/tasks/main.yml
@@ -1,22 +1,22 @@
 - name: Fail with warning about unspported OS
-  when: ansible_distribution | lower not in ['macosx', 'rocky']
+  when: ansible_facts.distribution | lower not in ['macosx', 'rocky']
   debug:
     msg: |
 
       ====================================================================
       =              WARNING! Unison will not be installed!              =
       ====================================================================
 
       Automated installation is supported only on macOS and Rocky and your
-      system has been identified as: {{ ansible_distribution }}
+      system has been identified as: {{ ansible_facts.distribution }}
 
       You will have to install unison and fsmonitor manually yourself
       to get continous file sync.
 
 - name: Install unison client for macOS
   import_tasks: install-macos.yml
-  when: ansible_distribution | lower == 'macosx'
+  when: ansible_facts.distribution | lower == 'macosx'
 
 - name: Install unison client for Rocky
   import_tasks: install-rocky.yml
-  when: ansible_distribution | lower == 'rocky'
+  when: ansible_facts.distribution | lower == 'rocky'
diff --git a/roles/cs.varnish/defaults/main.yml b/roles/cs.varnish/defaults/main.yml
index 25bbb89..d9eb8bc 100644
--- a/roles/cs.varnish/defaults/main.yml
+++ b/roles/cs.varnish/defaults/main.yml
@@ -65,11 +65,11 @@ varnish_workspace_thread: 4k
 # As of varnish 6.0 the default is 48k and lower values cause segfault with our VCL
 varnish_thread_pool_stack: 128k
 
 # Max. number of thread pools that should be at most the number of vCPUs
 # See: https://varnish-cache.org/docs/6.0/reference/varnishd.html#thread-pool-max
-varnish_thread_pools: "{{ ansible_processor_vcpus }}"
+varnish_thread_pools: "{{ ansible_facts.processor_vcpus }}"
 
 # The min/max number of threads per pool
 varnish_thread_pool_max: "{{ [(varnish_thread_mem_quota | int / varnish_thread_mem_est | int / varnish_thread_pools | int) | int, 20] | max }}"
 varnish_thread_pool_min: "{{ [[(varnish_thread_pool_max | int / 5) | int, 20] | max, varnish_thread_pool_max | int] | min }}"
 
diff --git a/roles/cs.varnish/tasks/000-facts.yml b/roles/cs.varnish/tasks/000-facts.yml
index 755fd33..99732f3 100644
--- a/roles/cs.varnish/tasks/000-facts.yml
+++ b/roles/cs.varnish/tasks/000-facts.yml
@@ -7,12 +7,12 @@
 
       Dynamically computed parameters for target node.
 
       ---
 
-      Total target system vCPUs: {{ ansible_processor_vcpus }}
-      Total target system memory: {{ ( ansible_memtotal_mb ~ 'MB' ) | human_to_bytes | human_readable }}
+      Total target system vCPUs: {{ ansible_facts.processor_vcpus }}
+      Total target system memory: {{ ( ansible_facts.memtotal_mb ~ 'MB' ) | human_to_bytes | human_readable }}
 
       ---
 
       Approx. max. total memory usage: {{ varnish_full_mem_usage | int | human_readable }}
       Approx. reserved (left) system memory: {{ (varnish_total_sys_mem | int - varnish_full_mem_usage | int) | human_readable }}
@@ -32,13 +32,15 @@
 - name: Get Varnish backends - running EC2 app instances (AWS)
   block:
     - name: Get VPC IP addresses of backend app instances
       delegate_to: localhost
       become: no
-      ec2_instance_info:
+      amazon.aws.ec2_instance_info:
         region: "{{ aws_region }}"
         filters: "{{ varnish_backend_instances_filter_base | combine(varnish_backend_instances_aws_tags | prefix_keys('tag:')) }}"
+      vars:
+        ansible_python_interpreter: "{{ ansible_playbook_python }}"
       register: _varnish_backends_ec2_instance_info
 
     - name: Set Varnish backend instances if any are running (AWS)
       set_fact:
         varnish_backend_instances_app: "{{ _varnish_backends_ec2_instance_info.instances }}"
@@ -64,16 +66,18 @@
           {{
               varnish_media_cors_allowed_origins +
               https_termination_hosts | default([])|selectattr('server_name', 'defined')|map(attribute='server_name')|list +
               https_termination_hosts | default([])|selectattr('aliases', 'defined')|map(attribute='aliases')|list | flatten
           }}
-      when: mageops_https_termination_enable | default(false)
+      when: mageops_https_termination_enable | default(false) | bool
     - name: Add Cloudfront domnains
       set_fact:
         varnish_media_cors_allowed_origins: |
           {{
             varnish_media_cors_allowed_origins +
             [ aws_cloudfront_distribution_domain ] +
             aws_cloudfront_domain_aliases | default([])
           }}
-      when: aws_cloudfront_distribution_create | default(false) and aws_cloudfront_distribution_domain | default(false, true)
+      when:
+        - aws_cloudfront_distribution_create | default(false) | bool
+        - (aws_cloudfront_distribution_domain | default('', true) | string | length) > 0
   when: varnish_generate_allowed_origins
diff --git a/roles/cs.varnish/vars/main.yml b/roles/cs.varnish/vars/main.yml
index 2a3e6d0..942e340 100644
--- a/roles/cs.varnish/vars/main.yml
+++ b/roles/cs.varnish/vars/main.yml
@@ -9,11 +9,11 @@ varnish_backend_instances_filter_base:
 
 # We support only malloc storage for now
 varnish_storage: "malloc"
 
 # Total system memory in bytes
-varnish_total_sys_mem: "{{ ansible_memtotal_mb * 1024 * 1024 }}"
+varnish_total_sys_mem: "{{ ansible_facts.memtotal_mb * 1024 * 1024 }}"
 
 # Base amount of system memory dedicated to varnish used for calculating derived dynamic param defaults
 varnish_base_mem_quota: >-
   {{
     [
diff --git a/site.maintenance.aws-remove-all.yml b/site.maintenance.aws-remove-all.yml
index ad91a42..05d8b6d 100644
--- a/site.maintenance.aws-remove-all.yml
+++ b/site.maintenance.aws-remove-all.yml
@@ -17,19 +17,19 @@
 
   tasks:
     - name: Remove Auto Scaling Groups and App servers
       block:
         - name: Get Auto Scaling Groups
-          community.aws.ec2_asg_info:
+          amazon.aws.autoscaling_group_info:
             region: "{{ aws_region }}"
             tags: "{{ aws_tags_base }}"
           register: _aws_asgs
         - name: Set list of ASG to drop
           set_fact:
             _aws_asgs_to_remove: "{{ _aws_asgs | json_query('results[].{ name: auto_scaling_group_name } ') }}"
         - name: Remove ASGs
-          ec2_asg:
+          amazon.aws.autoscaling_group:
             name: "{{ item.name }}"
             region: "{{ aws_region }}"
             state: absent
           with_items: "{{ _aws_asgs_to_remove }}"
           when: not dry_run_mode
@@ -82,22 +82,22 @@
           set_fact:
             aws_rds_instance_id: "{{ (_aws_rds_instances | first).db_instance_identifier }}"
           when: _aws_rds_instances | length > 0
         - name: Terminate RDS instance
           when: _aws_rds_instance_id == aws_rds_instance_name and not dry_run_mode
-          rds:
-            command: delete
-            instance_name: "{{ aws_rds_instance_name }}"
-            # snapshot: "{{ aws_rds_instance_name }}-snapshot"
+          amazon.aws.rds_instance:
+            db_instance_identifier: "{{ aws_rds_instance_name }}"
+            state: absent
+            skip_final_snapshot: true
       when: remove_rds
 
     - name: Remove Volumes
       # Currently not working. There seems to be a bug in Ansible and tags are required
       # We do not set tags for volumes
       block:
         - name: Get list of Volumes
-          ec2_vol_facts:
+          amazon.aws.ec2_vol_info:
             region: "{{ aws_region }}"
             filters:
               "status": "available"
             #   "tag:Environment": "{{ mageops_environment }}"
           register: _aws_fact
@@ -106,17 +106,17 @@
       when: remove_vol
 
     - name: Remove EFS
       block:
         - name: Get list of EFS drives
-          efs_facts:
+          community.aws.efs_info:
             region: "{{ aws_region }}"
             tags: "{{ aws_tags_base }}"
           register: _aws_fact
         - name: Set list of EFS instances to drop
           set_fact:
-            _aws_efs_to_remove: "{{ _aws_fact | json_query('ansible_facts.efs[].file_system_id')}}"
+            _aws_efs_to_remove: "{{ _aws_fact | json_query('efs[].file_system_id')}}"
         - name: Remove EFS
           efs:
             id: "{{ item }}"
             region: "{{ aws_region }}"
             state: absent
diff --git a/site.maintenance.aws-start.yml b/site.maintenance.aws-start.yml
index 73387f1..be2e078 100644
--- a/site.maintenance.aws-start.yml
+++ b/site.maintenance.aws-start.yml
@@ -30,17 +30,17 @@
 
     - name: Scale up App Node ASGs
       when: start_asg
       block:
         - name: Get Auto Scaling Groups for App
-          community.aws.ec2_asg_info:
+          amazon.aws.autoscaling_group_info:
             region: "{{ aws_region }}"
             tags: "{{ aws_tags_base | combine(aws_tags_node_app) }}"
           register: start_asg_facts
 
         - name: Scale up ASG
-          ec2_asg:
+          amazon.aws.autoscaling_group:
             name: "{{ item.name }}"
             region: "{{ aws_region }}"
             state: present
             desired_capacity: "{{ aws_app_asg_desired_capacity | default(1) }}"
             min_size: "{{ aws_app_asg_min_size | default(1) }}"
@@ -52,17 +52,17 @@
 
     - name: Scale up Extra App Node ASGs
       when: start_asg and (aws_extra_app_asg_enable or magento_aws_ondemand_import_instance_enable)
       block:
         - name: Get Auto Scaling Groups for Extra App
-          community.aws.ec2_asg_info:
+          amazon.aws.autoscaling_group_info:
             region: "{{ aws_region }}"
             tags: "{{ aws_tags_base | combine(aws_tags_node_extra_app) }}"
           register: start_asg_facts
 
         - name: Scale up ASG
-          ec2_asg:
+          amazon.aws.autoscaling_group:
             name: "{{ item.name }}"
             region: "{{ aws_region }}"
             state: present
             desired_capacity: "{{ aws_extra_app_asg_desired_capacity | default(0) }}"
             min_size: "{{ aws_extra_app_asg_min_size | default(0) }}"
diff --git a/site.maintenance.aws-stop.yml b/site.maintenance.aws-stop.yml
index d025aad..ef2251a 100644
--- a/site.maintenance.aws-stop.yml
+++ b/site.maintenance.aws-stop.yml
@@ -10,17 +10,17 @@
   tasks:
     - name: Scale down all App Node ASGs
       when: stop_asg
       block:
         - name: Get App Node Auto Scaling Groups
-          community.aws.ec2_asg_info:
+          amazon.aws.autoscaling_group_info:
             region: "{{ aws_region }}"
             tags: "{{ aws_tags_base | combine(aws_tags_role_app) }}"
           register: stop_asg_facts
 
         - name: Scale down ASG to zero
-          ec2_asg:
+          amazon.aws.autoscaling_group:
             name: "{{ item.name }}"
             region: "{{ aws_region }}"
             state: present
             desired_capacity: 0
             min_size: 0
@@ -40,11 +40,11 @@
         - "{{ aws_persistent_node_instance }}"
         - "{{ aws_varnish_node_instance }}"
 
     - name: Scale down all App Node ASGs
       when: stop_asg
-      ec2_asg:
+      amazon.aws.autoscaling_group:
         name: "{{ item.auto_scaling_group_name }}"
         region: "{{ aws_region }}"
         state: present
         desired_capacity: 0
         min_size: 0
diff --git a/site.maintenance.purge-db.yml b/site.maintenance.purge-db.yml
index 04cc997..4301f51 100644
--- a/site.maintenance.purge-db.yml
+++ b/site.maintenance.purge-db.yml
@@ -24,20 +24,20 @@
         login_user: "{{ mageops_mysql_root_user }}"
         login_password: "{{ mageops_mysql_root_pass }}"
         state: dump
         name: "{{ mageops_app_mysql_db }}"
         quick: yes
-        target: "{{ pre_purge_db_directory }}/{{ mageops_app_name }}-{{ ansible_date_time.date }}-{{ ansible_date_time.hour }}.{{ ansible_date_time.minute }}.sql"
+        target: "{{ pre_purge_db_directory }}/{{ mageops_app_name }}-{{ ansible_facts.date_time.date }}-{{ ansible_facts.date_time.hour }}.{{ ansible_facts.date_time.minute }}.sql"
 
     - name: Drop the current database
       mysql_db:
         login_host: "{{ mageops_mysql_host }}"
         login_user: "{{ mageops_mysql_root_user }}"
         login_password: "{{ mageops_mysql_root_pass }}"
         state: absent
         name: "{{ mageops_app_mysql_db }}"
   vars:
-    - pre_purge_db_directory: "{{ ansible_env.HOME }}/maintenance-db-purge-dumps/{{ mageops_app_name }}/"
+    pre_purge_db_directory: "{{ ansible_facts.env.HOME }}/maintenance-db-purge-dumps/{{ mageops_app_name }}/"
   vars_files:
     - vars/app/credentials.yml
     - vars/app/env.yml
     - vars/aws/env.yml
diff --git a/site.maintenance.update-certificates.yml b/site.maintenance.update-certificates.yml
index 0b8226f..ca94c39 100644
--- a/site.maintenance.update-certificates.yml
+++ b/site.maintenance.update-certificates.yml
@@ -2,10 +2,10 @@
 
 - hosts: "loadbalancer:&varnish:&current"
   roles:
     - role: cs.nginx-url-blacklist
     - role: cs.nginx-https-termination
+      https_termination_enabled: "{{ mageops_https_termination_enable }}"
       https_termination_upstream_port: "{{ mageops_varnish_port }}"
-      when: mageops_https_termination_enable
   vars:
     nginx_blacklist_urls: "{{ nginx_blacklist_urls_default + nginx_blacklist_urls_project | default([]) }}"
     nginx_config_cleanup: no
diff --git a/site.step-15-varnish.yml b/site.step-15-varnish.yml
index a2d8250..871784c 100644
--- a/site.step-15-varnish.yml
+++ b/site.step-15-varnish.yml
@@ -45,20 +45,20 @@
     - role: geerlingguy.ntp
     - role: cs.nginx
     - role: cs.nginx-url-blacklist
       nginx_blacklist_urls: "{{ nginx_blacklist_urls_default + nginx_blacklist_urls_project | default([]) }}"
     - role: cs.nginx-language-redirect
-      when: mageops_language_redirect_enable and mageops_language_redirect_mode == "normal"
+      nginx_language_redirect_enabled: "{{ mageops_language_redirect_enable and mageops_language_redirect_mode == 'normal' }}"
     - role: cs.nginx-language-redirect-multilevel
-      when: mageops_language_redirect_enable and mageops_language_redirect_mode == "multilevel"
+      nginx_language_redirect_multilevel_enabled: "{{ mageops_language_redirect_enable and mageops_language_redirect_mode == 'multilevel' }}"
     - role: cs.pio
       vars:
         pio_tasks: varnish
       when: mageops_pio_worker_enable
     - role: cs.nginx-https-termination
+      https_termination_enabled: "{{ mageops_https_termination_enable }}"
       https_termination_upstream_port: "{{ mageops_varnish_port }}"
-      when: mageops_https_termination_enable
     - role: cs.cloudflare
     - role: cs.varnish
       varnish_port: "{{ mageops_varnish_port }}"
       varnish_backend_port: "{{ mageops_varnish_backend_port }}"
       varnish_secure_site: "{{ mageops_secure_site }}"
@@ -79,11 +79,11 @@
       varnish_magento_vary_secret: "{{ mageops_magento_vary_sign_secret }}"
     - role: cs.varnish-manager
       when: varnish_standalone and aws_use
     - role: cs.mageops-cli-profile
     - role: cs.goaccess
-      when: goaccess_enable
+      goaccess_enabled: "{{ goaccess_enable }}"
     - role: cs.aws-logs
       aws_logs_log_magento_crash_reports: no
       aws_logs_stream_name: "{{ mageops_node_role }}"
       aws_logs_loggers: "{{ aws_logs_loggers_varnish_default | combine(aws_logs_loggers_varnish_extra | default({}), recursive=True) }}"
       when: aws_use
diff --git a/site.step-20-persistent.yml b/site.step-20-persistent.yml
index fd15df1..b9184d1 100644
--- a/site.step-20-persistent.yml
+++ b/site.step-20-persistent.yml
@@ -14,10 +14,12 @@
     - role: cs.aws-security-group-facts
       delegate_to: localhost
       delegate_facts: no
       become: no
       when: aws_use
+    - role: cs.repo-rabbitmq
+      when: mageops_rabbitmq_create
     - role: cs.versionlock
       node_name: persistent
       versionlock_packages: "{{ versionlock_persistent_packages + versionlock_persistent_packages_base + versionlock_persistent_packages_extra }}"
       versionlock_ban_packages: "{{ versionlock_persistent_ban_packages + versionlock_persistent_ban_packages_base + versionlock_persistent_ban_packages_extra }}"
     - role: cs.selinux-disable
@@ -81,11 +83,11 @@
         - vhost: "{{ magento_rabbitmq_virtual_host }}"
           username: "{{ magento_rabbitmq_username }}"
           password: "{% if magento_rabbitmq_queue %}{{ magento_rabbitmq_password | mandatory }}{% endif %}"
       when: mageops_rabbitmq_create
     - role: cs.ssh-proxy-user
-      when: mageops_ssh_proxy_persistant
+      when: mageops_ssh_proxy_persistant | bool
     - role: cs.tinyproxy
       tinyproxy_enabled: "{{ mageops_tinyproxy_persistant_enabled  }}"
     - role: cs.monitoring
       monitoring_node_exporter_enabled: yes
       monitoring_elasticsearch_exporter_enabled: yes
diff --git a/site.step-40-app-node.yml b/site.step-40-app-node.yml
index efdca46..bd7d753 100644
--- a/site.step-40-app-node.yml
+++ b/site.step-40-app-node.yml
@@ -99,11 +99,11 @@
       nginx_blacklist_urls: "{{ mageops_app_node_https_termination_enable | ternary([], mageops_app_node_nginx_blacklist_urls) }}"
       nginx_fcgi_backend_socket: "{{ php_fpm_pool_fcgi_socket_path }}"
       nginx_fcgi_backend_debug_socket: "{{ php_fpm_debug_pool_fcgi_socket_path }}"
 
     - role: cs.nginx-https-termination
-      when: mageops_app_node_https_termination_enable
+      https_termination_enabled: "{{ mageops_app_node_https_termination_enable }}"
       nginx_blacklist_urls: "{{ mageops_app_node_https_termination_enable | ternary(mageops_app_node_nginx_blacklist_urls, []) }}"
       https_termination_upstream_port: "{{ mageops_varnish_port }}"
 
     - role: cs.php-fpm
       tags: php
@@ -161,11 +161,11 @@
 
     - role: cs.magerun
       when: mageops_install_magerun
 
     - role: cs.ssh-tunel
-      when: mageops_ssh_proxy_persistant
+      when: mageops_ssh_proxy_persistant | bool
 
     - role: cs.new-relic
       when: mageops_new_relic_enabled
 
     - role: cs.monitoring
diff --git a/site.step-45-app-deploy.yml b/site.step-45-app-deploy.yml
index c00d5dd..994b8a7 100644
--- a/site.step-45-app-deploy.yml
+++ b/site.step-45-app-deploy.yml
@@ -34,11 +34,11 @@
           {{ deploy_artifact_composer_json_data.require | to_nice_yaml }}
 
           ---------------------------------------------
 
     - name: Set artifact build number fact if available
-      when: deploy_artifact_build_json_data.nr | default(false, true)
+      when: (deploy_artifact_build_json_data.nr | default('', true) | string | length) > 0
       set_fact:
         mageops_artifact_build_nr: "{{ deploy_artifact_build_json_data.nr }}"
 
     - name: Check if previous release exists
       stat:
@@ -50,11 +50,11 @@
       set_fact:
         deploy_previous_release_exists: "{{ _current_release_check.stat is defined and _current_release_check.stat.islnk is defined and _current_release_check.stat.islnk }}"
 
     - name: Gather deployment run facts
       set_fact:
-        deploy_release_id: "{{ ansible_date_time.iso8601_basic_short }}"
+        deploy_release_id: "{{ ansible_facts.date_time.iso8601_basic_short }}"
         deploy_keep_current_release: "{{ deploy_skip_installation | default(false) and deploy_previous_release_exists }}"
         deploy_previous_release_id: "{{ deploy_previous_release_exists | ternary((_current_release_check.stat.lnk_target | default('')).rstrip('/').split('/') | last, false) }}"
 
     - name: "Skipping installation: reusing previous release"
       set_fact:
@@ -124,14 +124,14 @@
       when: gtm_enabled and varnish_standalone
 
   tasks:
     - name: Execute custom post deploy tasks
       include_tasks: "{{ mageops_extra_tasks_deploy }}"
-      when: mageops_extra_tasks_deploy is defined and mageops_extra_tasks_deploy
+      when: (mageops_extra_tasks_deploy | default('', true) | string | length) > 0
 
     - name: Save deploy release information to file
-      when: deploy_release_save_info_file_path | default(false, true)
+      when: (deploy_release_save_info_file_path | default('', true) | string | length) > 0
       copy:
         dest: "{{ deploy_release_save_info_file_path }}"
         content: "{{ deploy_release_info | to_nice_json }}"
       vars:
         deploy_release_info:
diff --git a/site.step-50-ami.yml b/site.step-50-ami.yml
index 3b45be3..cc173af 100644
--- a/site.step-50-ami.yml
+++ b/site.step-50-ami.yml
@@ -3,13 +3,13 @@
   roles:
     - role: cs.aws-node-facts
 
     - role: cs.aws-create-ami
 
-      ami_description: "{{ mageops_project | capitalize }} {{ mageops_environment | capitalize }} App Node ({{ ansible_date_time.iso8601 }})"
+      ami_description: "{{ mageops_project | capitalize }} {{ mageops_environment | capitalize }} App Node ({{ ansible_facts.date_time.iso8601 }})"
       ami_instance_id: "{{ aws_app_builder_node_instance.instance_id }}"
-      ami_name: "{{ mageops_app_name }}-app-{{ ansible_date_time.epoch }}"
+      ami_name: "{{ mageops_app_name }}-app-{{ ansible_facts.date_time.epoch }}"
       ami_tags: "{{ aws_tags_role_app }}"
 
       aws_ami_build_ebs_volume_type: "{{ aws_app_node_ebs_volume_type | default(aws_ec2_ebs_volume_type, true) }}"
       aws_ami_build_ebs_gp3_iops: "{{ aws_app_node_ebs_gp3_iops | default(aws_ec2_ebs_gp3_iops, true) }}"
       aws_ami_build_ebs_gp3_throughput: "{{ aws_app_node_ebs_gp3_throughput | default(aws_ec2_ebs_gp3_throughput, true) }}"
@@ -20,6 +20,6 @@
         {{
             aws_tags_base | combine(
                 aws_tags_role_app_builder
             )
         }}
-      when: aws_ami_build_terminate_builder
\ No newline at end of file
+      when: aws_ami_build_terminate_builder

```
