# Frozen source context: V007PILOT2-STYLE_POLICY-021

- Repository: `ansible-collections/community.general`
- Commit: `60972bc7422ba42060695353ecb54a7c5a99eef0`
- Family: style_policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `meta/runtime.yml` (reported anchor line 1133)
- Flagged construct: not named by the finding; the anchor line 1133 lies in the task at line 55, unnamed.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1033–1233 of 1786:

```text
 1033 |       tombstone:
 1034 |         removal_version: 3.0.0
 1035 |         warning_text: Use ovirt.ovirt.ovirt_nic_info instead.
 1036 |     ovirt_permission_facts:
 1037 |       tombstone:
 1038 |         removal_version: 3.0.0
 1039 |         warning_text: Use ovirt.ovirt.ovirt_permission_info instead.
 1040 |     ovirt_quota_facts:
 1041 |       tombstone:
 1042 |         removal_version: 3.0.0
 1043 |         warning_text: Use ovirt.ovirt.ovirt_quota_info instead.
 1044 |     ovirt_scheduling_policy_facts:
 1045 |       tombstone:
 1046 |         removal_version: 3.0.0
 1047 |         warning_text: Use ovirt.ovirt.ovirt_scheduling_policy_info instead.
 1048 |     ovirt_snapshot_facts:
 1049 |       tombstone:
 1050 |         removal_version: 3.0.0
 1051 |         warning_text: Use ovirt.ovirt.ovirt_snapshot_info instead.
 1052 |     ovirt_storage_domain_facts:
 1053 |       tombstone:
 1054 |         removal_version: 3.0.0
 1055 |         warning_text: Use ovirt.ovirt.ovirt_storage_domain_info instead.
 1056 |     ovirt_storage_template_facts:
 1057 |       tombstone:
 1058 |         removal_version: 3.0.0
 1059 |         warning_text: Use ovirt.ovirt.ovirt_storage_template_info instead.
 1060 |     ovirt_storage_vm_facts:
 1061 |       tombstone:
 1062 |         removal_version: 3.0.0
 1063 |         warning_text: Use ovirt.ovirt.ovirt_storage_vm_info instead.
 1064 |     ovirt_tag_facts:
 1065 |       tombstone:
 1066 |         removal_version: 3.0.0
 1067 |         warning_text: Use ovirt.ovirt.ovirt_tag_info instead.
 1068 |     ovirt_template_facts:
 1069 |       tombstone:
 1070 |         removal_version: 3.0.0
 1071 |         warning_text: Use ovirt.ovirt.ovirt_template_info instead.
 1072 |     ovirt_user_facts:
 1073 |       tombstone:
 1074 |         removal_version: 3.0.0
 1075 |         warning_text: Use ovirt.ovirt.ovirt_user_info instead.
 1076 |     ovirt_vm_facts:
 1077 |       tombstone:
 1078 |         removal_version: 3.0.0
 1079 |         warning_text: Use ovirt.ovirt.ovirt_vm_info instead.
 1080 |     ovirt_vmpool_facts:
 1081 |       tombstone:
 1082 |         removal_version: 3.0.0
 1083 |         warning_text: Use ovirt.ovirt.ovirt_vmpool_info instead.
 1084 |     postgresql_copy:
 1085 |       redirect: community.postgresql.postgresql_copy
 1086 |       deprecation:
 1087 |         removal_version: 18.0.0
 1088 |         warning_text: The redirection of community.general.postgresql_copy to community.postgresql.postgresql_copy will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1089 |     postgresql_db:
 1090 |       redirect: community.postgresql.postgresql_db
 1091 |       deprecation:
 1092 |         removal_version: 18.0.0
 1093 |         warning_text: The redirection of community.general.postgresql_db to community.postgresql.postgresql_db will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1094 |     postgresql_ext:
 1095 |       redirect: community.postgresql.postgresql_ext
 1096 |       deprecation:
 1097 |         removal_version: 18.0.0
 1098 |         warning_text: The redirection of community.general.postgresql_ext to community.postgresql.postgresql_ext will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1099 |     postgresql_idx:
 1100 |       redirect: community.postgresql.postgresql_idx
 1101 |       deprecation:
 1102 |         removal_version: 18.0.0
 1103 |         warning_text: The redirection of community.general.postgresql_idx to community.postgresql.postgresql_idx will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1104 |     postgresql_info:
 1105 |       redirect: community.postgresql.postgresql_info
 1106 |       deprecation:
 1107 |         removal_version: 18.0.0
 1108 |         warning_text: The redirection of community.general.postgresql_info to community.postgresql.postgresql_info will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1109 |     postgresql_lang:
 1110 |       redirect: community.postgresql.postgresql_lang
 1111 |       deprecation:
 1112 |         removal_version: 18.0.0
 1113 |         warning_text: The redirection of community.general.postgresql_lang to community.postgresql.postgresql_lang will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1114 |     postgresql_membership:
 1115 |       redirect: community.postgresql.postgresql_membership
 1116 |       deprecation:
 1117 |         removal_version: 18.0.0
 1118 |         warning_text: The redirection of community.general.postgresql_membership to community.postgresql.postgresql_membership will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1119 |     postgresql_owner:
 1120 |       redirect: community.postgresql.postgresql_owner
 1121 |       deprecation:
 1122 |         removal_version: 18.0.0
 1123 |         warning_text: The redirection of community.general.postgresql_owner to community.postgresql.postgresql_owner will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1124 |     postgresql_pg_hba:
 1125 |       redirect: community.postgresql.postgresql_pg_hba
 1126 |       deprecation:
 1127 |         removal_version: 18.0.0
 1128 |         warning_text: The redirection of community.general.postgresql_pg_hba to community.postgresql.postgresql_pg_hba will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1129 |     postgresql_ping:
 1130 |       redirect: community.postgresql.postgresql_ping
 1131 |       deprecation:
 1132 |         removal_version: 18.0.0
 1133 |         warning_text: The redirection of community.general.postgresql_ping to community.postgresql.postgresql_ping will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1134 |     postgresql_privs:
 1135 |       redirect: community.postgresql.postgresql_privs
 1136 |       deprecation:
 1137 |         removal_version: 18.0.0
 1138 |         warning_text: The redirection of community.general.postgresql_privs to community.postgresql.postgresql_privs will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1139 |     postgresql_publication:
 1140 |       redirect: community.postgresql.postgresql_publication
 1141 |       deprecation:
 1142 |         removal_version: 18.0.0
 1143 |         warning_text: The redirection of community.general.postgresql_publication to community.postgresql.postgresql_publication will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1144 |     postgresql_query:
 1145 |       redirect: community.postgresql.postgresql_query
 1146 |       deprecation:
 1147 |         removal_version: 18.0.0
 1148 |         warning_text: The redirection of community.general.postgresql_query to community.postgresql.postgresql_query will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1149 |     postgresql_schema:
 1150 |       redirect: community.postgresql.postgresql_schema
 1151 |       deprecation:
 1152 |         removal_version: 18.0.0
 1153 |         warning_text: The redirection of community.general.postgresql_schema to community.postgresql.postgresql_schema will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1154 |     postgresql_sequence:
 1155 |       redirect: community.postgresql.postgresql_sequence
 1156 |       deprecation:
 1157 |         removal_version: 18.0.0
 1158 |         warning_text: The redirection of community.general.postgresql_sequence to community.postgresql.postgresql_sequence will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1159 |     postgresql_set:
 1160 |       redirect: community.postgresql.postgresql_set
 1161 |       deprecation:
 1162 |         removal_version: 18.0.0
 1163 |         warning_text: The redirection of community.general.postgresql_set to community.postgresql.postgresql_set will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1164 |     postgresql_slot:
 1165 |       redirect: community.postgresql.postgresql_slot
 1166 |       deprecation:
 1167 |         removal_version: 18.0.0
 1168 |         warning_text: The redirection of community.general.postgresql_slot to community.postgresql.postgresql_slot will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1169 |     postgresql_subscription:
 1170 |       redirect: community.postgresql.postgresql_subscription
 1171 |       deprecation:
 1172 |         removal_version: 18.0.0
 1173 |         warning_text: The redirection of community.general.postgresql_subscription to community.postgresql.postgresql_subscription will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1174 |     postgresql_table:
 1175 |       redirect: community.postgresql.postgresql_table
 1176 |       deprecation:
 1177 |         removal_version: 18.0.0
 1178 |         warning_text: The redirection of community.general.postgresql_table to community.postgresql.postgresql_table will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1179 |     postgresql_tablespace:
 1180 |       redirect: community.postgresql.postgresql_tablespace
 1181 |       deprecation:
 1182 |         removal_version: 18.0.0
 1183 |         warning_text: The redirection of community.general.postgresql_tablespace to community.postgresql.postgresql_tablespace will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1184 |     postgresql_user:
 1185 |       redirect: community.postgresql.postgresql_user
 1186 |       deprecation:
 1187 |         removal_version: 18.0.0
 1188 |         warning_text: The redirection of community.general.postgresql_user to community.postgresql.postgresql_user will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1189 |     postgresql_user_obj_stat_info:
 1190 |       redirect: community.postgresql.postgresql_user_obj_stat_info
 1191 |       deprecation:
 1192 |         removal_version: 18.0.0
 1193 |         warning_text: The redirection of community.general.postgresql_user_obj_stat_info to community.postgresql.postgresql_user_obj_stat_info will be removed in community.general 18.0.0. Please update your roles/playbooks.
 1194 |     profitbricks:
 1195 |       tombstone:
 1196 |         removal_version: 11.0.0
 1197 |         warning_text: Supporting library is unsupported since 2021.
 1198 |     profitbricks_datacenter:
 1199 |       tombstone:
 1200 |         removal_version: 11.0.0
 1201 |         warning_text: Supporting library is unsupported since 2021.
 1202 |     profitbricks_nic:
 1203 |       tombstone:
 1204 |         removal_version: 11.0.0
 1205 |         warning_text: Supporting library is unsupported since 2021.
 1206 |     profitbricks_volume:
 1207 |       tombstone:
 1208 |         removal_version: 11.0.0
 1209 |         warning_text: Supporting library is unsupported since 2021.
 1210 |     profitbricks_volume_attachments:
 1211 |       tombstone:
 1212 |         removal_version: 11.0.0
 1213 |         warning_text: Supporting library is unsupported since 2021.
 1214 |     proxmox:
 1215 |       redirect: community.proxmox.proxmox
 1216 |       deprecation:
 1217 |         removal_version: 15.0.0
 1218 |         warning_text: The proxmox content has been moved to community.proxmox.
 1219 |     proxmox_backup:
 1220 |       redirect: community.proxmox.proxmox_backup
 1221 |       deprecation:
 1222 |         removal_version: 15.0.0
 1223 |         warning_text: The proxmox content has been moved to community.proxmox.
 1224 |     proxmox_backup_info:
 1225 |       redirect: community.proxmox.proxmox_backup_info
 1226 |       deprecation:
 1227 |         removal_version: 15.0.0
 1228 |         warning_text: The proxmox content has been moved to community.proxmox.
 1229 |     proxmox_disk:
 1230 |       redirect: community.proxmox.proxmox_disk
 1231 |       deprecation:
 1232 |         removal_version: 15.0.0
 1233 |         warning_text: The proxmox content has been moved to community.proxmox.
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).
