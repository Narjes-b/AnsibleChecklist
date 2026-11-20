# Frozen source context: V007PILOT2-VARIABLE_REFERENCE_REASONING-020

- Repository: `CMSgov/bluebutton-web-deployment`
- Commit: `ef2da5200c4d70c9db49e682ae28cd52ca92c995`
- Family: variable_reference_reasoning
- Rule: `ansibleguard/unguarded-variable`
- Codebook: `codebooks-v2/FAMILY_VARIABLES_V2.md`
- Source: `vars/all_var.yml` (reported anchor line 135)
- Flagged construct: variable `env_slsx_verify_ssl_internal`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–141 of 141:

```text
    1 | ---
    2 | 
    3 |   ### Environment:
    4 |   env: "{{ env_env }}"
    5 | 
    6 |   ### DJANGO_SECRET_KEY:[REDACTED VALUE BLOCK]
    7 |   # 50 character Random Key
    8 |   # http://www.miniwebtool.com/django-secret-key-generator/
    9 |   django_secret_key: "{{ env_django_secret_key }}"
   10 | 
   11 |   # a unix path-friendly name (IE, no spaces or special characters)
   12 |   project_name: "{{ common_project_name }}"
   13 | 
   14 |   # Virtual Environment location
   15 |   venv_full: "{{ venv }}{{ common_project_dir }}"
   16 | 
   17 |   # git branch to deploy
   18 |   git_branch: "master"
   19 | 
   20 |   # the base path to install to. You should not need to change this.
   21 |   # git installs the repo in a folder beneath this path
   22 |   # files and folders excluded from the repository can be installed here
   23 |   # in files and folders alongside the repo.
   24 |   install_root: "{{ project_parent }}{{ common_project_dir }}"
   25 | 
   26 |   # the git repository URL for the project
   27 |   project_repo: "https://github.com/CMSgov/bluebutton-web-server.git"
   28 | 
   29 |   # the git repository URL for the deployment
   30 |   deployment_repo: "https://github.com/CMSgov/bluebutton-web-deployment.git"
   31 | 
   32 |   # DEBUG Mode
   33 |   # False in IMPL / PROD
   34 |   django_debug: "{{ env_django_debug }}"
   35 | 
   36 |   # application owner: pyapps
   37 |   app_owner: "pyapps"
   38 |   # application group: nginx
   39 |   app_group: "www-data"
   40 | 
   41 |   ### HOSTNAME_URL:
   42 |   host_url: "{{ env_external_dns_name }}"
   43 | 
   44 |   # django environment specific apps list
   45 |   django_environment_apps: "{{ env_django_environment_apps }}"
   46 |   django_optional_installed_apps: "{{ env_django_optional_installed_apps }}"
   47 |   django_cors_origin_allow_all: "{{ env_django_cors_origin_allow_all }}"
   48 | 
   49 |   ### Email configuration - AWS SES
   50 |   django_email_backend: "{{ env_django_email_backend }}"
   51 |   django_from_email: "{{ env_django_from_email }}"
   52 |   django_admin_email: "{{ env_django_admin_email }}"
   53 | 
   54 |   # SALT and ITERATIONS
   55 |   django_user_id_salt: "{{ env_django_user_id_salt }}"
   56 |   django_user_id_iterations: "{{ env_django_user_id_iterations }}"
   57 | 
   58 |   # django password hash iterations
   59 |   django_password_hash_iterations: "{{ env_django_password_hash_iterations }}"
   60 |   
   61 |   fhir_url: "{{ env_fhir_url }}"
   62 |   fhir_url_v3: "{{ env_fhir_url_v3 }}"
   63 |   
   64 |   # Default Sample FHIR ID
   65 |   django_default_sample_fhir_id: "{{ env_django_default_sample_fhir_id }}"
   66 | 
   67 |   django_fhir_certstore_relative: "{{ env_django_fhir_certstore_relative }}"
   68 | 
   69 |   django_signup_timeout_days: "{{ env_django_signup_timeout_days }}"
   70 | 
   71 |   ### S3 Bucket Settings:
   72 |   s3_storage_bucket_name: "{{ env_s3_storage_bucket_name }}"
   73 | 
   74 |   ### Django Settings:
   75 |   django_app_title: "{{ env_django_app_title }}"
   76 | 
   77 |   ### Application LOGO image settings:
   78 |   django_app_logo_size_max: "{{ env_django_app_logo_size_max }}"
   79 |   django_app_logo_width_max: "{{ env_django_app_logo_width_max }}"
   80 |   django_app_logo_height_max: "{{ env_django_app_logo_height_max }}"
   81 | 
   82 |   # Application label slugs to exclude from externally
   83 |   # published lists, like those used for internal use testing.
   84 |   django_app_list_exclude: "{{ env_django_app_list_exclude }}"
   85 | 
   86 |   # Add a variable endpoint for admin/
   87 |   # eg. To move from /admin/ to /secret/admin/
   88 |   #     set redirector to 'secret/'
   89 |   django_admin_redirector: "{{ env_django_admin_redirector }}"
   90 | 
   91 |   ### Database Settings:
   92 |   db_name: "{{ env_db_name }}"
   93 |   db_user_name: "{{ env_db_user_name }}"
   94 |   db_user_pw: "{{ env_db_user_pw }}"
   95 |   db_platform_type: "postgres"
   96 |   db_host_address: "db.bluebutton-{{ env }}.local"
   97 |   db_host_port: "15432"
   98 |   db_host_options: "?sslmode=require&options=-c role={{ env_db_role }}"
   99 | 
  100 |   # legacy value still used in roles, should be renamed for clarity
  101 |   cf_region: "{{ aws_region }}"
  102 | 
  103 |   # Nginx cert, key and fullchain files
  104 |   # Assigned Certificates and Keys to be copied to /etc/ssl/certs
  105 |   www_cert_file: "{{ env_www_cert_file }}"
  106 |   www_key_file: "{{ env_www_key_file }}"
  107 |   www_fullchain_file: "{{ env_www_fullchain_file }}"
  108 | 
  109 |   # AppServer cert and key for communication with FHIR Server
  110 |   app_fhir_cert: "{{ env_app_fhir_cert }}"
  111 |   app_fhir_key: "{{ env_app_fhir_key }}"
  112 |   app_fhir_cert_name: "{{ env_app_fhir_cert_name }}"
  113 |   app_fhir_key_name: "{{ env_app_fhir_key_name }}"
  114 | 
  115 |   # legacy values still used in roles, should be renamed for clarity
  116 |   cf_app_tag_key_layer: "{{ env_cf_app_tag_key_layer }}"
  117 |   cf_app_pyapps_pwd: "{{ env_cf_app_pyapps_pwd }}"
  118 | 
  119 |   mon_nessus_user: "{{ env_mon_nessus_user }}"
  120 |   mon_nessus_pwd: "{{ env_mon_nessus_pwd }}"
  121 |   mon_nessus_pub_key: "{{ env_mon_nessus_pub_key }}"
  122 | 
  123 |   #
  124 |   # SLSx / Medicare.gov Authentication Integration
  125 |   #
  126 |   slsx_client_id: "{{ env_slsx_client_id }}"
  127 |   slsx_client_secret: "{{ env_slsx_client_secret }}"
  128 |   medicare_slsx_akamai_aca_token: "{{ env_medicare_slsx_akamai_aca_token }}"
  129 |   medicare_slsx_login_uri: "{{ env_medicare_slsx_login_uri }}"
  130 |   medicare_slsx_redirect_uri: "{{ env_medicare_slsx_redirect_uri }}"
  131 |   slsx_health_check_endpoint: "{{ env_slsx_health_check_endpoint }}"
  132 |   slsx_token_endpoint: "{{ env_slsx_token_endpoint }}"
  133 |   slsx_signout_endpoint: "{{ env_slsx_signout_endpoint }}"
  134 |   slsx_userinfo_endpoint: "{{ env_slsx_userinfo_endpoint }}"
  135 |   slsx_verify_ssl_internal: "{{ env_slsx_verify_ssl_internal }}"
  136 |   slsx_verify_ssl_external: "{{ env_slsx_verify_ssl_external }}"
  137 | 
  138 |   django_logging: "{{ env_django_logging }}"
  139 | 
  140 |   # new relic
  141 |   new_relic_license_key: "{{ env_new_relic_license_key }}"
```

## Visible variable references

```text
Whole-word search for `env_slsx_verify_ssl_internal`: 4 matches in 4 files; 3 look like definitions (key assignment, register, set_fact) and are listed first.
Likely definitions:
vars/env/impl/env.yml:104:env_slsx_verify_ssl_internal: "{{ lookup('aws_secret', '/bb2/impl/app/slsx_verify_ssl_internal', region='us-east-1')  }}"
vars/env/prod/env.yml:105:env_slsx_verify_ssl_internal: "{{ lookup('aws_secret', '/bb2/prod/app/slsx_verify_ssl_internal', region='us-east-1')  }}"
vars/env/test/env.yml:106:env_slsx_verify_ssl_internal: "{{ lookup('aws_secret', '/bb2/test/app/slsx_verify_ssl_internal', region='us-east-1')  }}"

Other references:
vars/all_var.yml:135:  slsx_verify_ssl_internal: "{{ env_slsx_verify_ssl_internal }}"
```
