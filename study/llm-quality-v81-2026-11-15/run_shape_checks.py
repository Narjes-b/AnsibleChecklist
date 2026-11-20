"""Additional authored shape fixtures, separate from the 48-case development panel."""
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.llm_quality_study import llm,save,load,implementation,case_root,digest,write_checkpoint
P=Path(__file__).resolve().parent
cases=[
 ('tls-args','missing-validate-certs','supported', '- name: Fetch\n  ansible.builtin.uri:\n    url: https://example.invalid/a\n  args:\n    validate_certs: false\n',None),
 ('tls-local-action','missing-validate-certs','unsupported', '- name: Fetch\n  local_action:\n    module: ansible.builtin.get_url\n    url: https://example.invalid/a\n    dest: /tmp/a\n    validate_certs: true\n',None),
 ('tls-runtime','missing-validate-certs','insufficient-evidence', '- name: Fetch\n  ansible.builtin.uri:\n    url: https://example.invalid/a\n    validate_certs: "{{ check_endpoint_certificate }}"\n',None),
 ('permission-decimal','insecure-permissions','supported','- name: Manage\n  ansible.builtin.file:\n    path: /srv/pipeline-data\n    mode: 2750\n',None),
 ('permission-grouped','insecure-permissions','unsupported','- name: Manage\n  ansible.builtin.file:\n    path: /srv/release\n    state: directory\n    group: release\n    mode: "2770"\n',None),
 ('permission-runtime','insecure-permissions','insufficient-evidence','- name: Render\n  ansible.builtin.template:\n    src: deployment.j2\n    dest: /srv/deployment\n    mode: "{{ access_bits }}"\n',None),
 ('logging-inherited','credential-log-exposure','unsupported','- name: Parent\n  no_log: true\n  block:\n    - name: Inspect\n      ansible.builtin.debug:\n        msg: "{{ service_api_key }}"\n',4),
 ('logging-override','credential-log-exposure','supported','- name: Parent\n  no_log: true\n  block:\n    - name: Inspect\n      no_log: false\n      ansible.builtin.debug:\n        msg: "{{ service_token }}"\n',4),
 ('logging-opaque','credential-log-exposure','insufficient-evidence','- name: Custom\n  company.service:\n    password: "{{ deployment_password }}"\n',None),
 ('variable-prior','unguarded-variable','unsupported','- name: Define\n  ansible.builtin.set_fact:\n    ApplicationPort: 8080\n- name: Show\n  ansible.builtin.debug:\n    msg: "{{ ApplicationPort }}"\n',6),
 ('variable-conditional','unguarded-variable','insufficient-evidence','- name: Define\n  ansible.builtin.set_fact:\n    ApplicationPort: 8080\n  when: set_port\n- name: Show\n  ansible.builtin.debug:\n    msg: "{{ ApplicationPort }}"\n',7),
 ('variable-external','unguarded-variable','insufficient-evidence','- name: Show\n  ansible.builtin.debug:\n    msg: "{{ PossiblyProvided }}"\n',3),
]

def main():
    assert load(P/'freeze.json')['implementation']==implementation()
    out=ROOT/'study/runs/llm-v81-shape-checks-2026-11-15';out.mkdir(exist_ok=False,mode=0o700)
    save(P/'shape-cases.json',{'cases':cases,'sha256':digest(cases),'status':'Authored fixtures, not independent human labels or held-out natural data'})
    rows=[]
    for name,rule,expected,source,line in cases:
        occ={'file':'task.yml','line':line or 1,'rule_id':rule}
        if rule=='unguarded-variable':occ['semantic_subject']='variable:PossiblyProvided' if name=='variable-external' else 'variable:ApplicationPort'
        case={'kind':'controlled','files':{'task.yml':source}}
        for mode in ['window','scoped']:
            telemetry={};token=llm._CALL_RECORD.set(telemetry)
            try:
                with case_root(case,ROOT/'study/repositories') as root:
                    result=llm.explain_occurrence(occ,root,evidence_mode=mode,explanation_style='verified-facts')
            finally:llm._CALL_RECORD.reset(token)
            row={'case':name,'mode':mode,'expected':expected,'assessment':result.get('llm_assessment'),
                 'status':result['llm_status'],'matches':result.get('llm_assessment')==expected and result['llm_status']=='ok'}
            rows.append(row);write_checkpoint(out,name+'-'+mode,{'result':result,'telemetry':telemetry,'fixture':case,'occurrence':occ,'check':row})
            print(json.dumps(row),flush=True)
    save(P/'shape-results.json',{'rows':rows,'matches':sum(r['matches'] for r in rows),'total':24,'authority':'Developer-authored static fixtures; no independent human evaluation'})
if __name__=='__main__':main()
