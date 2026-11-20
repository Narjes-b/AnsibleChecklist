# Frozen source context: V007PILOT-SECURITY-027

- Repository: `ethpandaops/ansible-collection-general`
- Commit: `15a1f3490258357c4652b96b80f0a92636fa4135`
- Family: Security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/xatu_stack/defaults/main.yaml` (reported anchor line 29)
- Object: `variable` `47e63137e1a4131702ff20e7a4c0f2dc23c6d6b0a517c4c1fd056eee646327ea`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–60 of 60:

```text
    1 | xatu_stack_cleanup: false
    2 | 
    3 | xatu_stack_user: "xatu-stack"
    4 | 
    5 | xatu_stack_repo_url: "https://github.com/ethpandaops/xatu"
    6 | xatu_stack_repo_version: "master"
    7 | xatu_stack_repo_path: "/data/xatu-stack"
    8 | 
    9 | xatu_stack_env_vars:
   10 |   # NGINX
   11 |   NGINX_PORT: 80
   12 |   BASE_HOSTNAME: "http://xatu.example.com"
   13 | 
   14 |   # Clickhouse
   15 |   ## Clickhouse 01
   16 |   CLICKHOUSE_01_HTTP_ADDRESS: 127.0.0.1
   17 |   CLICKHOUSE_01_HTTP_PORT: 8123
   18 |   CLICKHOUSE_01_NATIVE_PORT: 9000
   19 |   CLICKHOUSE_01_NATIVE_ADDRESS: 127.0.0.1
   20 |   ## Clickhouse 02
   21 |   CLICKHOUSE_02_HTTP_ADDRESS: 127.0.0.1
   22 |   CLICKHOUSE_02_HTTP_PORT: 8124
   23 |   CLICKHOUSE_02_NATIVE_PORT: 9001
   24 |   CLICKHOUSE_02_NATIVE_ADDRESS: 127.0.0.1
   25 | 
   26 |   # Xatu Server
   27 |   XATU_SERVER_ADDRESS: 127.0.0.1
   28 |   XATU_SERVER_PORT: 8080
   29 |   EVENT_INGESTER_AUTHORIZATION_SECRET: [REDACTED_LITERAL]
   30 | 
   31 |   # Postgres
   32 |   POSTGRES_DB: xatu
   33 |   POSTGRES_USER: user
   34 |   POSTGRES_PASSWORD: password
   35 | 
   36 |   # Grafana
   37 |   GRAFANA_ADDRESS: 127.0.0.1
   38 |   GRAFANA_PORT: 3000
   39 |   # Prometheus
   40 |   PROMETHEUS_ADDRESS: 127.0.0.1
   41 |   PROMETHEUS_PORT: 9090
   42 |   # Tempo
   43 |   ## Jaeger
   44 |   TEMPO_JAEGER_ADDRESS: 127.0.0.1
   45 |   TEMPO_JAEGER_PORT: 6831
   46 |   ## HTTP
   47 |   TEMPO_HTTP_ADDRESS: 127.0.0.1
   48 |   TEMPO_HTTP_PORT: 3200
   49 |   ## GRPC
   50 |   TEMPO_GRPC_ADDRESS: 127.0.0.1
   51 |   TEMPO_GRPC_PORT: 9095
   52 |   ## OTLP GRPC
   53 |   TEMPO_OTLP_GRPC_ADDRESS: 127.0.0.1
   54 |   TEMPO_OTLP_GRPC_PORT: 4317
   55 |   ## OTLP HTTP
   56 |   TEMPO_OTLP_HTTP_ADDRESS: 127.0.0.1
   57 |   TEMPO_OTLP_HTTP_PORT: 4318
   58 |   ## Zipkin
   59 |   TEMPO_ZIPKIN_ADDRESS: 127.0.0.1
   60 |   TEMPO_ZIPKIN_PORT: 9411
```
