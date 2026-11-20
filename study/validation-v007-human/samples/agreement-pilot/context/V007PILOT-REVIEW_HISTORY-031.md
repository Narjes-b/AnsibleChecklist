# Frozen Git review context: V007PILOT-REVIEW_HISTORY-031

- Repository: `osism/ansible-collection-services`
- Target commit: `131734f2c007d0009a7fc218849f4ede66c7c899`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
manager: reload the services when an environment file changes

A change to netbox_role_mapping never reached the inventory reconciler on a
production manager. The new value was in
/opt/manager/configuration/inventory-reconciler.env, `osism apply manager`
reported changed=0, and the running container still had the mapping it had been
created with, so the generated inventory kept the old host groups and the
symptom was silent: the reconciler completed and wrote every file.

Only the docker-compose.yml template in service.yml notifies a handler. The
eleven tasks that render an environment file notify nothing, so a change to any
manager environment value is written to disk and never delivered to the
container that reads it. The environment of a container is fixed when it is
created, so a restart cannot pick it up either, the container has to be
recreated.

They now notify "Ensure that all containers are up" rather than "Restart
manager service". That handler runs

    docker compose --project-directory /opt/manager up -d

which is exactly what delivers a new environment, and no more. Measured with
docker 29.7.2 and compose v5.5.0 on a two service project:

  * env file changed, then docker restart: same container id, old value
  * env file changed, then compose up -d: new container id, new value
  * compose up -d with nothing changed: same container id, nothing recreated
  * two services, only one env file changed: only that service is recreated

The last two lines are why this handler is the right one. Notifying "Restart
manager service" instead would restart the whole manager stack through systemd
and then wait the hardcoded minute of "Wait for manager service to start" for
every environment change, even though compose narrows the work to the services
whose environment actually differs.

yamllint with the repository configuration and ansible-lint at the production
profile are clean on roles/manager.

Signed-off-by: Timon Schnell <timon.schnell@btc-it-services.com>
Assisted-by: Claude:claude-opus-5
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.
