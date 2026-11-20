import json
import pytest
from ansibleguard.report import llm_explain as llm

TLS='- name: Fetch\n  ansible.builtin.get_url:\n    url: https://example.invalid/a\n    dest: /tmp/a\n    mode: "0644"\n    validate_certs: false\n'


def selection(monkeypatch, payload=None, mutate=None):
    seen={}
    def model(host,name,system,user,timeout):
        seen.update(system=system,user=json.loads(user),schema=llm._request_generation_schema())
        if mutate:mutate()
        return json.dumps(payload if payload is not None else {'claim_ids':['c0','c1']}),.1,None
    monkeypatch.setattr(llm,'_call_ollama',model)
    return seen


def call(root,style='verified-facts',mode='window',rule='missing-validate-certs',line=1):
    return llm.explain_occurrence({'file':'tasks.yml','line':line,'rule_id':rule},root,evidence_mode=mode,explanation_style=style)


@pytest.mark.parametrize('literal,expected',[('false','supported'),('true','unsupported'),("'{{ verify_tls }}'",'insufficient-evidence')])
@pytest.mark.parametrize('mode',['window','scoped'])
def test_verified_literal_runtime_interpretation_and_provenance(tmp_path,monkeypatch,literal,expected,mode):
    (tmp_path/'tasks.yml').write_text(TLS.replace('validate_certs: false','validate_certs: '+literal))
    seen=selection(monkeypatch);result=call(tmp_path,mode=mode)
    assert result['llm_status']=='ok' and result['llm_assessment']==expected
    assert result['llm_explanation_contract']=='verified-facts-v1'
    assert result['llm_evidence'][0]['line']==6
    assert 'not independent LLM reasoning' in result['llm_prose_origin']
    assert 'claim_ids' in seen['schema']['properties'] and 'assessment' not in seen['schema']['properties']
    assert 'Source-bound assessment' in llm.assessment_text(result)


def test_window_cannot_use_a_hidden_parameter_or_source_value(tmp_path,monkeypatch):
    source=TLS.replace('    validate_certs: false',''.join(f'    # filler {i}\n' for i in range(20))+'    validate_certs: false\n    private_marker: never_send_hidden_value')
    (tmp_path/'tasks.yml').write_text(source)
    seen=selection(monkeypatch);result=call(tmp_path)
    assert result['llm_assessment']=='insufficient-evidence'
    assert not result['llm_evidence_packet']['window_source_closure_verified']
    assert 'never_send_hidden_value' not in json.dumps(seen)
    assert 'validate_certs: false' not in result['llm_explanation']


def test_window_cannot_use_inherited_control_outside_supplied_window(tmp_path,monkeypatch):
    text='- name: Parent\n  no_log: true\n  block:\n'+''.join(f'    # filler {i}\n' for i in range(15))+'    - name: Show\n      ansible.builtin.debug:\n        msg: "{{ api_token }}"\n'
    (tmp_path/'tasks.yml').write_text(text)
    line=text.splitlines().index('    - name: Show')+1
    seen=selection(monkeypatch);result=call(tmp_path,rule='credential-log-exposure',line=line)
    assert result['llm_assessment']=='insufficient-evidence'
    assert 'no_log: true' not in json.dumps(seen['user'])


@pytest.mark.parametrize('payload',[{'claim_ids':['c0','invented']},{'claim_ids':['c1']},{'claim_ids':['c0','c0']},{'claim_ids':['c0'],'reasoning':'invented prose'}])
def test_fabricated_missing_primary_duplicate_or_extra_prose_is_rejected(tmp_path,monkeypatch,payload):
    (tmp_path/'tasks.yml').write_text(TLS);selection(monkeypatch,payload)
    result=call(tmp_path)
    assert result['llm_status']=='error' and 'llm_explanation' not in result


def test_changed_source_is_not_published_as_verified(tmp_path,monkeypatch):
    p=tmp_path/'tasks.yml';p.write_text(TLS)
    selection(monkeypatch,mutate=lambda:p.write_text(TLS.replace('false','true')))
    result=call(tmp_path)
    assert result['llm_status']=='source-changed' and 'llm_explanation' not in result


def test_task_binding_and_citations_do_not_switch_to_neighbouring_mode(tmp_path,monkeypatch):
    text='- name: Directory\n  ansible.builtin.file:\n    path: /srv/x\n    state: directory\n    mode: "0777"\n- name: Copy\n  ansible.builtin.copy:\n    src: input\n    dest: /srv/x/file\n    mode: "0644"\n'
    (tmp_path/'tasks.yml').write_text(text);selection(monkeypatch)
    result=call(tmp_path,mode='scoped',rule='insecure-permissions',line=6)
    assert result['llm_assessment']=='unsupported'
    assert any(c['line']==10 for c in result['llm_evidence'])
    assert all(c['line']!=5 for c in result['llm_evidence'])
    assert '0644' in result['llm_explanation'] and '0777' not in result['llm_explanation']


def test_unseen_private_content_cannot_influence_window_permission_assessment(tmp_path,monkeypatch):
    text='- name: Manage\n  ansible.builtin.copy:\n    dest: /srv/public\n    mode: "0644"\n'+''.join(f'    # filler {i}\n' for i in range(20))+'    content: private_key_never_send\n'
    (tmp_path/'tasks.yml').write_text(text);seen=selection(monkeypatch)
    result=call(tmp_path,rule='insecure-permissions',line=1)
    assert result['llm_assessment']=='insufficient-evidence'
    assert 'private_key_never_send' not in json.dumps(seen['user'])


def test_partial_task_can_establish_explicit_tls_without_unseen_irrelevant_fields(tmp_path,monkeypatch):
    text=TLS+''.join(f'    # filler {i}\n' for i in range(20))+'    headers: {irrelevant_marker: hidden_header_value}\n'
    (tmp_path/'tasks.yml').write_text(text);seen=selection(monkeypatch)
    result=call(tmp_path)
    assert result['llm_assessment']=='supported'
    assert result['llm_evidence_packet']['local_fact_support_verified']
    assert 'hidden_header_value' not in json.dumps(seen['user'])


def test_verified_origin_survives_json_csv_sarif_and_pr_annotation(tmp_path,monkeypatch):
    import csv
    from ansibleguard.report.occurrences import build_occurrences,occurrence_findings
    from ansibleguard.report.output_contract import write_occurrences_csv
    from ansibleguard.report.sarif_writer import build_sarif
    from ansibleguard.report.pr_annotations import annotation_command
    (tmp_path/'tasks.yml').write_text(TLS);selection(monkeypatch)
    result=call(tmp_path)
    occurrence=build_occurrences([{'provider':'ansibleguard','rule_id':'missing-validate-certs','file':'tasks.yml','line':1,'severity':'warning','message':'Explicit setting','native_rule_id':'missing-validate-certs'}])[0]
    occurrence.update(result)
    finding=occurrence_findings([occurrence])[0]
    assert finding['llm_explanation_contract']=='verified-facts-v1'
    write_occurrences_csv([occurrence],tmp_path/'occurrences.csv')
    row=next(csv.DictReader(open(tmp_path/'occurrences.csv')))
    assert row['llm_prose_origin']==result['llm_prose_origin']
    properties=build_sarif([finding],tmp_path)['runs'][0]['results'][0]['properties']
    assert properties['llm_explanation_contract']=='verified-facts-v1'
    assert 'Verified source claims' in annotation_command(occurrence)


def test_checkpoint_does_not_reuse_free_prose_for_verified_contract(tmp_path,monkeypatch):
    from ansibleguard.report import llm_runtime
    (tmp_path/'tasks.yml').write_text(TLS)
    monkeypatch.setattr(llm_runtime,'source_identity',lambda *a,**k:'same-source')
    monkeypatch.setattr(llm_runtime,'model_identity',lambda *a,**k:'same-model')
    calls=[]
    def explain(occurrence,root,**kwargs):
        calls.append(kwargs['explanation_style'])
        return {'llm_status':'ok','llm_explanation_contract':kwargs['explanation_style']}
    monkeypatch.setattr(llm,'explain_occurrence',explain)
    occurrence={'file':'tasks.yml','line':1,'rule_id':'missing-validate-certs'}
    for style in ['free','free','verified-facts']:
        llm.enrich_occurrences_with_explanations([dict(occurrence)],tmp_path,checkpoint_dir=tmp_path/'records',explanation_style=style,actionable_only=False)
    assert calls==['free','verified-facts']


def test_unknown_window_exposes_exact_supplied_extent_without_sending_hidden_values(tmp_path,monkeypatch):
    text=TLS.replace('    validate_certs: false',''.join(f'    # filler {i}\n' for i in range(20))+'    validate_certs: false\n    marker: hidden_marker_value')
    (tmp_path/'tasks.yml').write_text(text);seen=selection(monkeypatch)
    result=call(tmp_path)
    span=result['llm_evidence'][0]['source_span']
    assert span['start']==1 and span['end']==7
    assert span['quote']=='\n'.join(text.splitlines()[:7])
    assert 'hidden_marker_value' not in span['quote']
    assert 'source_span' not in seen['user']['source_evidence'][0]


def test_window_extent_attaches_when_task_anchor_is_inside_not_at_start(tmp_path,monkeypatch):
    text='---\n'+TLS.replace('    validate_certs: false',''.join(f'    # filler {i}\n' for i in range(20))+'    validate_certs: false')
    (tmp_path/'tasks.yml').write_text(text);selection(monkeypatch)
    result=call(tmp_path,line=2)
    assert result['llm_evidence'][0]['line']==2
    assert result['llm_evidence'][0]['source_span']['start']==1
    assert result['llm_evidence'][0]['source_span']['end']==8
