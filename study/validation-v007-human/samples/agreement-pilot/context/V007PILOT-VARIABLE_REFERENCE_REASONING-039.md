# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-039

- Repository: `openfun/arnold`
- Commit: `f19ea6d060de69f01e750fab289b9fb7a991e27d`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `tasks/deploy_get_stamp_from_static_service.yml` (reported anchor line 36)
- Object: `variable` `ec423e56b27124f41efecf3d6d57d1c055b58562f7c1c516bde2cc452c0806df`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–37 of 37:

```text
    1 | ---
    2 | # Get deployment_stamp from a static service
    3 | 
    4 | # An application can define several static services. (e.g. two static services with
    5 | # two different ingresses). Our goal here is to get the deployment_stamp of a
    6 | # deployed stack by getting a service object. We retrieve the service and it will
    7 | # be labelled with the deploy_stamp we are looking for.
    8 | - name: Get static service for application {{ app.name }} with prefix {{ prefix }}
    9 |   kubernetes.core.k8s_info:
   10 |     api_version: "v1"
   11 |     namespace: "{{ namespace_name }}"
   12 |     kind: "Service"
   13 |     label_selectors:
   14 |       - type=static-service
   15 |       - app={{ app.name }}
   16 |       - service_prefix={{ prefix }}
   17 |   register: app_service
   18 |   when: static_services | length > 0 and app.settings.is_blue_green_compatible | default(True)
   19 | 
   20 | # app_deployment_stamp must be defined otherwise all script dependending on this one will fail
   21 | - name: Initialize app_deployment_stamp
   22 |   ansible.builtin.set_fact:
   23 |     app_deployment_stamp: ""
   24 | 
   25 | - name: Set app_deployment_stamp
   26 |   ansible.builtin.set_fact:
   27 |     app_deployment_stamp: "{{ (app_service.resources | first ).metadata.labels.deployment_stamp | default(none) }}"
   28 |   when: app_service.resources is defined and app_service.resources | length >= 1
   29 | 
   30 | - name: "Set {{ prefix }}_app_deployment_stamp"
   31 |   ansible.builtin.set_fact:
   32 |     "{{ prefix }}_app_deployment_stamp": "{{ app_deployment_stamp }}"
   33 | 
   34 | - name: Print app_deployment_stamp
   35 |   ansible.builtin.debug:
   36 |     msg: "[{{ app.name }}] app_deployment_stamp[{{ app_deployment_stamp }}]"
   37 |   when: app_deployment_stamp is defined
```

## Visible variable references

```text
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:239:  # Test community apps fetching and deployments
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:253:          name: Test community applications installation
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:258:          name: Test community applications deployment
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:262:  # Test the bootstrap playbook on the "hello" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:277:          name: Test the "hello" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:279:            # Bootstrap app
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:285:          name: Test the "hello" application switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:293:          name: Test the "hello" application rollback
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:308:  # Test the redirect application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:322:          name: Bootstrap the hello app and switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:324:            # Bootstrap app
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:335:  # Test the bootstrap playbook on the "mailcatcher" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:350:          name: Test the "mailcatcher" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:355:  # Test the bootstrap playbook on the "richie" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:370:          name: Test the "richie" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:372:            # Bootstrap app
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:378:          name: Test the "richie" application switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:385:  # Test the bootstrap playbook on the "forum" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:400:          name: Test the "forum" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:402:            # Bootstrap app
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:405:            cmd="kubectl get pods -n ci-eugene -l app=forum,service=forum"
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:411:  # Test the bootstrap playbook on the "edxapp" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:413:  test-bootstrap-edxapp:
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:426:          name: Test the "edxapp" application bootstrapping (with redis enabled)
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:428:            # Bootstrap app
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:429:            bin/arnold -c eugene -e ci -a edxapp,redis bootstrap
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:435:          name: Test the "edxapp" application switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:438:            bin/arnold -c eugene -e ci -a edxapp switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:443:  # Test the bootstrap playbook on the "edxec" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:458:          name: Test the "edxec" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:466:          name: Test the "edxec" application switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:472:  # Test the bootstrap playbook on the "ashley" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:487:          name: Test the "ashley" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:489:            # Bootstrap app
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:495:          name: Test the "ashley" application switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:503:  # Test the bootstrap playbook on the "nextcloud" application.
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:504:  # We also need redis and mailcatcher for this application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:521:          name: Test the "nextcloud" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:525:            oc exec -it $(oc get pod -l 'app in (nextcloud),service in (nextcloud),!job_stamp' -o json | jq -r '.items[0].metadata.name') \
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:526:              -- php /app/occ maintenance:mode --off
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:530:          name: Test the "nextcloud" application switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:538:  # Test the bootstrap playbook on the "kibana" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:553:          name: Test the "kibana" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:564:          name: Test the "kibana" application switch
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:571:  # Test the bootstrap playbook on the "prosody" application
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:586:          name: Test the "prosody" application bootstrapping
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:588:            # Bootstrap app
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:593:  # Test the delete_app tasks for blue-green applications
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:595:  test-delete-app:
f19ea6d060de69f01e750fab289b9fb7a991e27d:.circleci/config.yml:608:          name: Prepare "richie" application bootstrapping
[reference search truncated after 50 matches]
```
