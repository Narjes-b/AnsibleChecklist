# Frozen source context: V007PILOT-STRUCTURE_REUSE-049

- Repository: `ansible/instruqt`
- Commit: `e23435acd50f1f645c88958c8dee4fe2929014b6`
- Family: Structure/reuse
- Rule: `ansibleguard/insufficient-modularization`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `images/ansible/mesh-lab-install.yml` (reported anchor line 1)
- Object: `source_location` `43b04010b47e1d2d1e5b5174c24ad69cff53b33ac9a29ec5371c92b59131873b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–36 of 654:

```text
    1 | # Configures mesh environment by reinstalling controller and using "{{ mesh_inventory_template }} file for configuration"
    2 | ##
    3 | # Tags:
    4 | # create-instances - Create temporary GCP instances
    5 | # delete-instances - Delete temporary GCP instances
    6 | # install-controller - Controller installation
    7 | # controller-config - Setup controller objects for lab
    8 | # create-images - Create new GCP images
    9 | # delete-images - Deletes the current mesh GCP images
   10 | # install-code-server - Install code server
   11 | ##
   12 | - name: Setup localhost for mesh instruqt lab
   13 |   hosts: localhost
   14 |   gather_facts: false
   15 | 
   16 |   vars:
   17 |     gcp_login: &gcp_login
   18 |       project: "{{ gcp_project }}"
   19 |       auth_kind: serviceaccount
   20 |       service_account_file: "{{ gcp_service_account_file }}"
   21 | 
   22 |   pre_tasks:
   23 |     - name: Include variable tasks
   24 |       vars:
   25 |         extra_vars:
   26 |           - name: track_slug
   27 |             env: TRACK_SLUG
   28 |           - name: redhat_username
   29 |             env: REDHAT_USERNAME
   30 |           - name: redhat_password
   31 |             env: REDHAT_PASSWORD
   32 |           - name: offline_token
   33 |             env: REDHAT_OFFLINE_TOKEN
   34 |           - name: gcp_service_account_file
   35 |             env: GCP_SERVICE_ACCOUNT_FILE
   36 |           - name: gcp_service_account
```

## Frozen tracked paths in the relevant role/scope

```text
.ansible-lint
.devcontainer/Dockerfile
.devcontainer/devcontainer.json
.github/workflows/ansible/instruqt-track-test.yml
.github/workflows/ansible/prod-track-test.yml
.github/workflows/ansible/query-tracks.json
.github/workflows/ansible/roles/instruqt-track-test/tasks/main.yml
.github/workflows/build-aap-cache.yml
.github/workflows/build-images.yml
.github/workflows/community-ansible-build.yml
.github/workflows/controller-build.yml
.github/workflows/jekyll-gh-pages.yml
.github/workflows/lint.yml
.github/workflows/mesh-node-build.yml
.github/workflows/pages.yml
.github/workflows/rhel8-build.yml
.github/workflows/rhel9-build.yml
.github/workflows/validate-packer.yml
.github/workflows/windows-build.yml
.gitignore
.pre-commit-config.yaml
README.md
_config.yml
_layouts/default.html
assets/ansible-demo.png
assets/builder/ansible_builder.png
assets/builder/builder_create.png
assets/content_signing/ansible-test_collection-1.0.0.tar.gz
assets/content_signing/community-lab_collection-1.0.0.tar.gz
assets/controller/controller-credentials.png
assets/controller/controller-hosts.png
assets/controller/controller-inst-add-group.png
assets/controller/controller-inst-add-hosts-group.png
assets/controller/controller-inst-add-jt.png
assets/controller/controller-inst-credntials.png
assets/controller/controller-inst-inv-source-complete.png
assets/controller/controller-inst-inv-source.png
assets/controller/controller-inst-inventory.png
assets/controller/controller-inst-jt-click.png
assets/controller/controller-inst-jt-edit.png
assets/controller/controller-inst-jt-explore.png
assets/controller/controller-inst-jt-launch.png
assets/controller/controller-inst-jt-output.png
assets/controller/controller-inst-templates-menu.png
assets/controller/controller-inventory-source.png
assets/controller/controller-inventory.png
assets/controller/controller_dashboard.png
assets/controller/controller_filters.png
assets/controller/controller_jt.png
assets/css/prism-vsc-dark-plus.css
assets/css/style.scss
assets/icons/Product_Icon-Red_Hat-Ansible-Execution_environments-RGB.png
assets/icons/Product_Icon-Red_Hat-Ansible-RGB.png
assets/icons/automation_controller.png
assets/icons/builder/Product_icon-Red_Hat-Ansible-Execution_environment_builder-RGB.png
assets/icons/navigator/Product_icon-Red_Hat-Ansible-Automation_content_navigator-RGB.png
assets/images/cisco_workshops.png
assets/images/cisco_workshops_tony.png
assets/images/favicon.png
assets/images/redhat-ansible-logo.svg
assets/images/redhat-logo.svg
assets/logos/Logo-Red_Hat-Ansible_Automation_Platform-A-Black-RGB.png
assets/logos/Logo-Red_Hat-Ansible_Automation_Platform-A-Red-RGB.png
assets/logos/Logo-Red_Hat-Ansible_Automation_Platform-A-Reverse-RGB.png
assets/logos/Logo-Red_Hat-Ansible_Automation_Platform-A-Standard-RGB.png
assets/logos/Logo-Red_Hat-Ansible_Automation_Platform-A-White-RGB.png
assets/navigator.png
assets/prism.js
assets/private_automation_hub/cloud-lab_collection_with_tags-1.0.0.tar.gz
assets/private_automation_hub/cloud-lab_collection_without_tags-1.0.0.tar.gz
assets/private_automation_hub/cloud-test_collection-1.0.0.tar.gz
assets/private_automation_hub/network-lab_collection_with_tags-1.0.0.tar.gz
assets/private_automation_hub/network-lab_collection_without_tags-1.0.0.tar.gz
assets/private_automation_hub/network-test_collection-1.0.0.tar.gz
assets/readme_mesh_images.png
assets/tablelink.js
containers/README.md
containers/devops-controller-jenkins-ssl/Dockerfile
containers/devops-controller-jenkins-ssl/src/usr/share/jenkins/ref/jenkins_casc.yml
containers/devops-controller-jenkins-ssl/src/usr/share/jenkins/ref/plugins.txt
containers/devops-controller-jenkins-ssl/src/var/jenkins_home/.gitconfig
containers/devops-controller-jenkins-ssl/src/var/lib/jenkins/jenkins_keystore.jks
containers/devops-controller-jenkins/Dockerfile
containers/devops-controller-jenkins/src/usr/share/jenkins/ref/jenkins_casc.yml
containers/devops-controller-jenkins/src/usr/share/jenkins/ref/plugins.txt
containers/instruqt_gitea/Dockerfile
containers/instruqt_gitea/src/data/gitea/conf/app.ini
containers/instruqt_gitea/src/usr/bin/startup.sh
docs/contribute.md
docs/snippets.md
images/README.md
images/ansible/ansible-setup.yml
images/ansible/automationhub-setup.yml
images/ansible/automationhub-signing-setup.yml
images/ansible/build-aap-cache.yml
images/ansible/common/10_image_cleanup.yml
images/ansible/common/30_mesh_node.yml
images/ansible/common/50_install_controller.yml
images/ansible/common/5_configure_users.yml
images/ansible/common/60_check_vars.yml
images/ansible/common/70_controller_post_install.yml
images/ansible/controller-setup.yml
images/ansible/devops-controller-setup.yml
images/ansible/extra-vars.yml
images/ansible/getting-started-edge-lab_node-setup.yml
images/ansible/getting-started-mesh_node-setup.yml
images/ansible/inventory
images/ansible/lightspeed-101-setup.yml
images/ansible/manifest.zip.gpg
images/ansible/mesh-lab-install.yml
images/ansible/requirements.yml
images/ansible/rhel-setup.yml
images/ansible/roles/code_server/README.md
images/ansible/roles/code_server/defaults/main.yml
images/ansible/roles/code_server/meta/argument_spec.yml
images/ansible/roles/code_server/tasks/codeserver.yml
images/ansible/roles/code_server/tasks/codeserver_always.yml
images/ansible/roles/code_server/tasks/main.yml
images/ansible/roles/code_server/tasks/teardown.yml
images/ansible/roles/code_server/templates/code-server.service.j2
[listing truncated after 120 paths]
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.
