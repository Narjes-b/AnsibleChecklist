# Frozen source context: V007PILOT-SECURITY-006

- Repository: `confluentinc/cp-ansible`
- Commit: `11aa6b84f2ac19da7dc259c23fe854e01a1c5be3`
- Family: Security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `roles/variables/defaults/main.yml` (reported anchor line 1884)
- Object: `variable` `3f835e812e01c06fca3a10db9756b73b9e64b3de17a2feb1b36aab3f12f55d96`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1849–1919 of 3513:

```text
 1849 | 
 1850 | ### Not before time for the client assertion
 1851 | ksql_oauth_client_assertion_nbf_include: none
 1852 | 
 1853 | ### Audience for the client assertion
 1854 | ksql_oauth_client_assertion_audience: none
 1855 | 
 1856 | ### Issuer for the client assertion
 1857 | ksql_oauth_client_assertion_issuer: none
 1858 | 
 1859 | ### Subject for the client assertion
 1860 | ksql_oauth_client_assertion_sub: none
 1861 | 
 1862 | ### Scope for the client assertion
 1863 | ksql_oauth_client_assertion_scope: none
 1864 | 
 1865 | ### Path to the file containing the private key for the client assertion
 1866 | ksql_oauth_client_assertion_private_key_file: [REDACTED_LITERAL]
 1867 | 
 1868 | ### Passphrase for the private key for the client assertion
 1869 | ksql_oauth_client_assertion_private_key_passphrase: [REDACTED_LITERAL]
 1870 | 
 1871 | ### JTI for the client assertion
 1872 | ksql_oauth_client_assertion_jti_include: none
 1873 | 
 1874 | ### Path to the file containing the template for the client assertion
 1875 | ksql_oauth_client_assertion_template_file: none
 1876 | 
 1877 | ### Service principal for Ksql client in IdPserver. Defaults to Ksql Client Id
 1878 | ksql_oauth_principal: "{{ ksql_oauth_user }}"
 1879 | 
 1880 | ### LDAP User for Rest Proxy to authenticate as
 1881 | kafka_rest_ldap_user: kafka-rest
 1882 | 
 1883 | ### Password to kafka_rest_ldap_user LDAP User
 1884 | kafka_rest_ldap_password: password
 1885 | 
 1886 | ### OAuth Client Id for Rest Proxy to authenticate as
 1887 | kafka_rest_oauth_user: kafka-rest
 1888 | 
 1889 | ### Client Secret for kafka_rest_oauth_user
 1890 | kafka_rest_oauth_password: password
 1891 | 
 1892 | ### Boolean to enable OAuth client assertion
 1893 | kafka_rest_oauth_client_assertion_enabled: false
 1894 | 
 1895 | ### Path to the Directory containing the client assertion
 1896 | kafka_rest_oauth_client_assertion_file_base_path: none
 1897 | 
 1898 | ### Not before time for the client assertion
 1899 | kafka_rest_oauth_client_assertion_nbf_include: none
 1900 | 
 1901 | ### Audience for the client assertion
 1902 | kafka_rest_oauth_client_assertion_audience: none
 1903 | 
 1904 | ### Issuer for the client assertion
 1905 | kafka_rest_oauth_client_assertion_issuer: none
 1906 | 
 1907 | ### Subject for the client assertion
 1908 | kafka_rest_oauth_client_assertion_sub: none
 1909 | 
 1910 | ### Scope for the client assertion
 1911 | kafka_rest_oauth_client_assertion_scope: none
 1912 | 
 1913 | ### Path to the file containing the private key for the client assertion
 1914 | kafka_rest_oauth_client_assertion_private_key_file: [REDACTED_LITERAL]
 1915 | 
 1916 | ### Passphrase for the private key for the client assertion
 1917 | kafka_rest_oauth_client_assertion_private_key_passphrase: [REDACTED_LITERAL]
 1918 | 
 1919 | ### JTI for the client assertion
```

The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.
