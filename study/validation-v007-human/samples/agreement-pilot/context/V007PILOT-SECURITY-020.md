# Frozen source context: V007PILOT-SECURITY-020

- Repository: `openfoodfoundation/ofn-install`
- Commit: `5e26b29ee7c0eb6ffff54e502b570b4b92e0b7d9`
- Family: Security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `inventory/group_vars/local.yml` (reported anchor line 33)
- Object: `variable` `9e6cf8d8cdced0a71e44456c4d5626f686775631233559946e65d1045f96ba11`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–40 of 40:

```text
    1 | rails_env: "staging"
    2 | 
    3 | ssl_certificate: "/etc/ssl/certs/ssl-cert-snakeoil.pem"
    4 | ssl_certificate_key:  "/etc/ssl/private/ssl-cert-snakeoil.key"
    5 | 
    6 | # See https://github.com/openfoodfoundation/ofn-install/wiki/Setup for more info
    7 | checkout_zone: Australia
    8 | country_code: AU
    9 | currency: AUD
   10 | locale: en
   11 | language: en_AU.UTF-8
   12 | language_packages:
   13 |   - language-pack-en-base
   14 | l10n_repo: https://github.com/openfoodfoundation/l10n_au.git
   15 | timezone: Melbourne
   16 | 
   17 | developer_email: admin@example.com
   18 | 
   19 | users_sysadmin:
   20 |   - "{{ core_devs }}"
   21 | 
   22 | # *** Test host configuration ***
   23 | #
   24 | # This is usually set in the host config but it's the same for all local
   25 | # containers.
   26 | domain: localhost
   27 | 
   28 | admin_email: ofn@example.com
   29 | mail_domain: example.com
   30 | 
   31 | # Add missing vars to emulate secrets.yml
   32 | db_password: [REDACTED_LITERAL]
   33 | admin_password: [REDACTED_LITERAL]
   34 | secret_token: [REDACTED_LITERAL]
   35 | google_maps_api_key: [REDACTED_LITERAL]
   36 | 
   37 | mail_host: 'example.com'
   38 | mail_port: 25
   39 | smtp_username: 'admin'
   40 | smtp_password: 'password'
```
