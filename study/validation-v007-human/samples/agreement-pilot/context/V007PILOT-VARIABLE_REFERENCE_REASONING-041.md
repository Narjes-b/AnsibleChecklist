# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-041

- Repository: `silogen/cluster-bloom`
- Commit: `6122fdec7e1e0feed6081e46be0e44cd45d08809`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unscoped-shell-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `pkg/ansible/runtime/playbooks/tasks/update/update_keycloak.yaml` (reported anchor line 36)
- Object: `source_location` `e5bce22a29521038cd045a53f364a2cfed25684fce377b5521c392a2d5c5281a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–336 of 336:

```text
    1 | ---
    2 | # Purpose: Update Keycloak client redirect URIs for new domain
    3 | # Dependencies: NEW_DOMAIN, DRY_RUN variables
    4 | # Usage: Imported by update_config.yaml
    5 | 
    6 | - name: Update Keycloak client redirect URIs
    7 |   block:
    8 |     - name: Display dry-run message for Keycloak
    9 |       debug:
   10 |         msg: "🔐 [DRY RUN] Would update Keycloak client redirect URIs"
   11 |       when: DRY_RUN
   12 | 
   13 |     - name: Update Keycloak clients in cluster
   14 |       when: not DRY_RUN
   15 |       block:
   16 |         - name: Display Keycloak update header
   17 |           debug:
   18 |             msg: "🔐 Updating Keycloak client redirect URIs..."
   19 | 
   20 |         - name: Get AIRM admin client credentials from secrets
   21 |           shell: |
   22 |             ADMIN_CLIENT_ID=$(/var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml get secret airm-realm-credentials -n keycloak -o jsonpath='{.data.ADMIN_CLIENT_ID}' 2>/dev/null | base64 -d || echo "")
   23 |             ADMIN_CLIENT_SECRET=[REDACTED_LITERAL]
   24 | 
   25 |             echo "${ADMIN_CLIENT_ID}|${ADMIN_CLIENT_SECRET}"
   26 |           register: airm_admin_client_creds_result
   27 |           changed_when: false
   28 |           no_log: true
   29 | 
   30 |         - name: Parse AIRM admin client credentials
   31 |           set_fact:
   32 |             airm_admin_client_id: "{{ airm_admin_client_creds_result.stdout.split('|')[0] }}"
   33 |             airm_admin_client_secret: "{{ airm_admin_client_creds_result.stdout.split('|')[1] }}"
   34 |           no_log: true
   35 | 
   36 |         - name: Create ConfigMap with Keycloak update script
   37 |           shell: |
   38 |             cat <<'EOF' | /var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml apply -f -
   39 |             apiVersion: v1
   40 |             kind: ConfigMap
   41 |             metadata:
   42 |               name: keycloak-domain-update
   43 |               namespace: default
   44 |             data:
   45 |               update-clients.sh: |
   46 |                 #!/bin/bash
   47 |                 set -e
   48 | 
   49 |                 KC_URL="http://keycloak.keycloak.svc:8080"
   50 |                 NEW_DOMAIN="{{ NEW_DOMAIN }}"
   51 |                 ADMIN_CLIENT_ID="{{ airm_admin_client_id }}"
   52 |                 ADMIN_CLIENT_SECRET="{{ airm_admin_client_secret }}"
   53 | 
   54 |                 # Get admin token using client_credentials
   55 |                 echo "Getting Keycloak admin token..."
   56 |                 KC_TOKEN=[REDACTED_LITERAL]
   57 |                   -H "Content-Type: application/x-www-form-urlencoded" \
   58 |                   -d "grant_type=client_credentials" \
   59 |                   -d "client_id=${ADMIN_CLIENT_ID}" \
   60 |                   -d "client_secret=${ADMIN_CLIENT_SECRET}" | jq -r '.access_token')
   61 | 
   62 |                 if [ "$KC_TOKEN" = [REDACTED_LITERAL]
   63 |                   echo "Failed to get Keycloak admin token"
   64 |                   exit 1
   65 |                 fi
   66 | 
   67 |                 echo "Token obtained successfully"
   68 | 
   69 |                 # Function to update a client by clientId
   70 |                 update_client() {
   71 |                   local CLIENT_ID="$1"
   72 |                   shift
   73 |                   local REDIRECT_URIS=("$@")
   74 | 
   75 |                   echo "Looking up client: ${CLIENT_ID}..."
   76 | 
   77 |                   # Get all clients and find the one with matching clientId
   78 |                   CLIENT_UUID=$(curl -s -X GET \
   79 |                     "${KC_URL}/admin/realms/airm/clients" \
   80 |                     -H "Authorization: [REDACTED_LITERAL]
   81 |                     jq -r --arg cid "$CLIENT_ID" '.[] | select(.clientId == $cid) | .id')
   82 | 
   83 |                   if [ -z "$CLIENT_UUID" ] || [ "$CLIENT_UUID" = "null" ]; then
   84 |                     echo "  ⚠️  Client ${CLIENT_ID} not found, skipping"
   85 |                     return 0
   86 |                   fi
   87 | 
   88 |                   echo "  Found client UUID: ${CLIENT_UUID}"
   89 |                   echo "  Updating redirect URIs..."
   90 | 
   91 |                   # Get current client configuration
   92 |                   CURRENT_CLIENT=$(curl -s -X GET \
   93 |                     "${KC_URL}/admin/realms/airm/clients/${CLIENT_UUID}" \
   94 |                     -H "Authorization: [REDACTED_LITERAL]
   95 | 
   96 |                   # Build redirect URIs JSON array
   97 |                   REDIRECT_JSON=$(printf '%s\n' "${REDIRECT_URIS[@]}" | jq -R . | jq -s .)
   98 | 
   99 |                   # Update client with new redirect URIs
  100 |                   UPDATED_CLIENT=$(echo "$CURRENT_CLIENT" | jq \
  101 |                     --argjson uris "$REDIRECT_JSON" \
  102 |                     '.redirectUris = $uris')
  103 | 
  104 |                   curl -s -X PUT \
  105 |                     "${KC_URL}/admin/realms/airm/clients/${CLIENT_UUID}" \
  106 |                     -H "Authorization: [REDACTED_LITERAL]
  107 |                     -H "Content-Type: application/json" \
  108 |                     -d "$UPDATED_CLIENT"
  109 | 
  110 |                   echo "  ✓ Updated ${CLIENT_ID}"
  111 |                 }
  112 | 
  113 |                 # Function to update post logout redirect URIs for a client
  114 |                 update_client_post_logout_uris() {
  115 |                   local CLIENT_ID="$1"
  116 |                   shift
  117 |                   local POST_LOGOUT_URIS=("$@")
  118 | 
  119 |                   echo "Updating post logout redirect URIs for: ${CLIENT_ID}..."
  120 | 
  121 |                   # Get all clients and find the one with matching clientId
  122 |                   CLIENT_UUID=$(curl -s -X GET \
  123 |                     "${KC_URL}/admin/realms/airm/clients" \
  124 |                     -H "Authorization: [REDACTED_LITERAL]
  125 |                     jq -r --arg cid "$CLIENT_ID" '.[] | select(.clientId == $cid) | .id')
  126 | 
  127 |                   if [ -z "$CLIENT_UUID" ] || [ "$CLIENT_UUID" = "null" ]; then
  128 |                     echo "  ⚠️  Client ${CLIENT_ID} not found, skipping"
  129 |                     return 0
  130 |                   fi
  131 | 
  132 |                   echo "  Found client UUID: ${CLIENT_UUID}"
  133 | 
  134 |                   # Get current client configuration
  135 |                   CURRENT_CLIENT=$(curl -s -X GET \
  136 |                     "${KC_URL}/admin/realms/airm/clients/${CLIENT_UUID}" \
  137 |                     -H "Authorization: [REDACTED_LITERAL]
  138 | 
  139 |                   # Build post logout URIs as newline-delimited string
  140 |                   POST_LOGOUT_STRING=$(printf '%s\n' "${POST_LOGOUT_URIS[@]}" | sed ':a;N;$!ba;s/\n/\\n/g')
  141 | 
  142 |                   # Update client with new post logout redirect URIs
  143 |                   UPDATED_CLIENT=$(echo "$CURRENT_CLIENT" | jq \
  144 |                     --arg uris "$POST_LOGOUT_STRING" \
  145 |                     '.attributes["post.logout.redirect.uris"] = $uris')
  146 | 
  147 |                   curl -s -X PUT \
  148 |                     "${KC_URL}/admin/realms/airm/clients/${CLIENT_UUID}" \
  149 |                     -H "Authorization: [REDACTED_LITERAL]
  150 |                     -H "Content-Type: application/json" \
  151 |                     -d "$UPDATED_CLIENT"
  152 | 
  153 |                   echo "  ✓ Updated post logout redirect URIs for ${CLIENT_ID}"
  154 |                 }
  155 | 
  156 |                 # Function to update rootUrl for a client
  157 |                 update_client_root_url() {
  158 |                   local CLIENT_ID="$1"
  159 |                   local ROOT_URL="$2"
  160 | 
  161 |                   echo "Updating rootUrl for: ${CLIENT_ID}..."
  162 | 
  163 |                   # Get all clients and find the one with matching clientId
  164 |                   CLIENT_UUID=$(curl -s -X GET \
  165 |                     "${KC_URL}/admin/realms/airm/clients" \
  166 |                     -H "Authorization: [REDACTED_LITERAL]
  167 |                     jq -r --arg cid "$CLIENT_ID" '.[] | select(.clientId == $cid) | .id')
  168 | 
  169 |                   if [ -z "$CLIENT_UUID" ] || [ "$CLIENT_UUID" = "null" ]; then
  170 |                     echo "  ⚠️  Client ${CLIENT_ID} not found, skipping"
  171 |                     return 0
  172 |                   fi
  173 | 
  174 |                   echo "  Found client UUID: ${CLIENT_UUID}"
  175 | 
  176 |                   # Get current client configuration
  177 |                   CURRENT_CLIENT=$(curl -s -X GET \
  178 |                     "${KC_URL}/admin/realms/airm/clients/${CLIENT_UUID}" \
  179 |                     -H "Authorization: [REDACTED_LITERAL]
  180 | 
  181 |                   # Update client with new rootUrl
  182 |                   UPDATED_CLIENT=$(echo "$CURRENT_CLIENT" | jq \
  183 |                     --arg url "$ROOT_URL" \
  184 |                     '.rootUrl = $url')
  185 | 
  186 |                   curl -s -X PUT \
  187 |                     "${KC_URL}/admin/realms/airm/clients/${CLIENT_UUID}" \
  188 |                     -H "Authorization: [REDACTED_LITERAL]
  189 |                     -H "Content-Type: application/json" \
  190 |                     -d "$UPDATED_CLIENT"
  191 | 
  192 |                   echo "  ✓ Updated rootUrl for ${CLIENT_ID}"
  193 |                 }
  194 | 
  195 |                 # Function to update adminUrl for a client
  196 |                 update_client_admin_url() {
  197 |                   local CLIENT_ID="$1"
  198 |                   local ADMIN_URL="$2"
  199 | 
  200 |                   echo "Updating adminUrl for: ${CLIENT_ID}..."
  201 | 
  202 |                   # Get all clients and find the one with matching clientId
  203 |                   CLIENT_UUID=$(curl -s -X GET \
  204 |                     "${KC_URL}/admin/realms/airm/clients" \
  205 |                     -H "Authorization: [REDACTED_LITERAL]
  206 |                     jq -r --arg cid "$CLIENT_ID" '.[] | select(.clientId == $cid) | .id')
  207 | 
  208 |                   if [ -z "$CLIENT_UUID" ] || [ "$CLIENT_UUID" = "null" ]; then
  209 |                     echo "  ⚠️  Client ${CLIENT_ID} not found, skipping"
  210 |                     return 0
  211 |                   fi
  212 | 
  213 |                   echo "  Found client UUID: ${CLIENT_UUID}"
  214 | 
  215 |                   # Get current client configuration
  216 |                   CURRENT_CLIENT=$(curl -s -X GET \
  217 |                     "${KC_URL}/admin/realms/airm/clients/${CLIENT_UUID}" \
  218 |                     -H "Authorization: [REDACTED_LITERAL]
  219 | 
  220 |                   # Update client with new adminUrl
  221 |                   UPDATED_CLIENT=$(echo "$CURRENT_CLIENT" | jq \
  222 |                     --arg url "$ADMIN_URL" \
  223 |                     '.adminUrl = $url')
  224 | 
  225 |                   curl -s -X PUT \
  226 |                     "${KC_URL}/admin/realms/airm/clients/${CLIENT_UUID}" \
  227 |                     -H "Authorization: [REDACTED_LITERAL]
  228 |                     -H "Content-Type: application/json" \
  229 |                     -d "$UPDATED_CLIENT"
  230 | 
  231 |                   echo "  ✓ Updated adminUrl for ${CLIENT_ID}"
  232 |                 }
  233 | 
  234 |                 # Check client IDs, add minio, gitea and argocd..
  235 | 
  236 |                 # Update AIRM UI Client (fixed UUID-based clientId)
  237 |                 echo "Updating AIRM UI Client..."
  238 |                 update_client "354a0fa1-35ac-4a6d-9c4d-d661129c2cd0" \
  239 |                   "https://${NEW_DOMAIN}/*" \
  240 |                   "https://airmui.${NEW_DOMAIN}/*" \
  241 |                   "https://airmapi.${NEW_DOMAIN}/*" \
  242 |                   "https://aiwbui.${NEW_DOMAIN}/*" \
  243 |                   "https://aiwbapi.${NEW_DOMAIN}/*"
  244 | 
  245 |                 # Update Argocd Client 
  246 |                 echo "Updating Argocd Client..."
  247 |                 update_client "argocd" \
  248 |                   "https://argocd.${NEW_DOMAIN}/*"
  249 | 
  250 |                 update_client_post_logout_uris "argocd" \
  251 |                   "https://argocd.${NEW_DOMAIN}/auth/callback"
  252 | 
  253 |                 update_client_root_url "argocd" \
  254 |                   "https://argocd.${NEW_DOMAIN}"                  
  255 | 
  256 |                 update_client_admin_url "argocd" \
  257 |                 "https://argocd.${NEW_DOMAIN}"
  258 | 
  259 |                 # Update Gitea Client 
  260 |                 echo "Updating Gitea Client..."
  261 |                 update_client "gitea" \
  262 |                   "https://gitea.${NEW_DOMAIN}/*"
  263 | 
  264 |                 # Update minio Client
  265 |                 echo "Updating Minio Client..."
  266 |                 update_client "minio" \
  267 |                   "https://minio.${NEW_DOMAIN}/*"
  268 | 
  269 |                 echo "All Keycloak clients updated successfully"
  270 |             EOF
  271 |           changed_when: true
  272 |           no_log: true
  273 | 
  274 |         - name: Create Job to update Keycloak clients
  275 |           shell: |
  276 |             cat <<'EOF' | /var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml apply -f -
  277 |             apiVersion: batch/v1
  278 |             kind: Job
  279 |             metadata:
  280 |               name: keycloak-domain-update
  281 |               namespace: default
  282 |             spec:
  283 |               ttlSecondsAfterFinished: 300
  284 |               template:
  285 |                 spec:
  286 |                   restartPolicy: Never
  287 |                   containers:
  288 |                   - name: update-keycloak
  289 |                     image: amdenterpriseai/cluster-tool:latest
  290 |                     command: ["/bin/bash", "/scripts/update-clients.sh"]
  291 |                     volumeMounts:
  292 |                     - name: script
  293 |                       mountPath: /scripts
  294 |                   volumes:
  295 |                   - name: script
  296 |                     configMap:
  297 |                       name: keycloak-domain-update
  298 |                       defaultMode: 0755
  299 |             EOF
  300 |           changed_when: true
  301 | 
  302 |         - name: Wait for Keycloak update job to complete
  303 |           command: /var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml wait --for=condition=complete --timeout=60s job/keycloak-domain-update -n default
  304 |           register: job_wait
  305 |           changed_when: false
  306 |           failed_when: false
  307 | 
  308 |         - name: Get job logs
  309 |           command: /var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml logs job/keycloak-domain-update -n default
  310 |           register: job_logs
  311 |           changed_when: false
  312 |           failed_when: false
  313 | 
  314 |         - name: Display job logs
  315 |           debug:
  316 |             msg: "{{ job_logs.stdout_lines }}"
  317 |           when: job_logs.stdout_lines is defined
  318 | 
  319 |         - name: Check job status
  320 |           fail:
  321 |             msg: "Keycloak update job failed. Check logs above."
  322 |           when: job_wait.rc != 0
  323 | 
  324 |         - name: Cleanup Keycloak update job
  325 |           command: /var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml delete job keycloak-domain-update -n default --ignore-not-found=true
  326 |           changed_when: false
  327 |           failed_when: false
  328 | 
  329 |         - name: Cleanup Keycloak update ConfigMap
  330 |           command: /var/lib/rancher/rke2/bin/kubectl --kubeconfig /etc/rancher/rke2/rke2.yaml delete configmap keycloak-domain-update -n default --ignore-not-found=true
  331 |           changed_when: false
  332 |           failed_when: false
  333 | 
  334 |         - name: Display Keycloak update result
  335 |           debug:
  336 |             msg: "  ✅ Keycloak client redirect URIs updated"
```
