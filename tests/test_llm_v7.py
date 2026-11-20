import json
import pytest
from ansibleguard.report import llm_explain as llm


@pytest.mark.parametrize('state,expected', list(llm.CONDITION_STATES.items()))
def test_neutral_state_mapping_preserves_raw_meaning(state, expected):
    raw = json.dumps({'condition_state': state, 'reasoning': 'Opposite-sounding prose is not used to change the explicit decision.'})
    record = {}; token = llm._CALL_RECORD.set(record)
    try:
        normalized = json.loads(llm._normalize_generation_response(raw))
    finally:
        llm._CALL_RECORD.reset(token)
    assert normalized['assessment'] == expected and 'condition_state' not in normalized
    assert json.loads(raw)['condition_state'] == state
    assert record['generation_state_mapping']['condition_state'] == state


@pytest.mark.parametrize('value', [{'condition_state':'safe'}, {'condition_state':None}, {'condition_state':'present','assessment':'unsupported'}])
def test_invalid_or_conflicting_state_is_rejected(value):
    assert llm._validate(llm._normalize_generation_response(json.dumps(value)))[0] is None


def test_window_generation_has_neutral_decisions_but_no_forced_source_answers():
    token = llm._CALL_RECORD.set({})
    try:
        schema = llm._request_generation_schema()
    finally:
        llm._CALL_RECORD.reset(token)
    branches = schema['anyOf']
    assert [b['properties']['condition_state']['enum'][0] for b in branches] == ['present', 'absent', 'unknown']
    for branch in branches:
        fields = branch['properties']
        assert 'enum' not in fields['summary'] and 'enum' not in fields['evidence']
        assert fields['limitations'] == {'type':'string','minLength':1}
    unknown = branches[2]['properties']
    assert unknown['missing_evidence']['minItems'] == 1 and unknown['confidence']['enum'] == ['low']
    assert llm.RESPONSE_SCHEMA['properties']['assessment']['enum'] == list(llm.ASSESSMENTS)


@pytest.mark.parametrize('literal,state,assessment', [('false','present','supported'), ('true','absent','unsupported'), ("'{{ verify_tls }}'",'unknown','insufficient-evidence')])
def test_window_neutral_question_and_literal_unknown_behavior(tmp_path, monkeypatch, literal, state, assessment):
    (tmp_path/'tasks.yml').write_text('- name: Fetch\n  ansible.builtin.get_url:\n    validate_certs: '+literal+'\n')
    seen={}
    def call(host, name, system, user, timeout):
        seen.update(system=system,user=user)
        return json.dumps({'condition_state':state,'actionability':'context-dependent',
            'evidence':[{'file':'tasks.yml','line':3}], 'missing_evidence':['runtime setting'] if state=='unknown' else [],
            'summary':'The shown setting is '+literal, 'reasoning':'The setting is read directly from line 3.',
            'recommended_fix':None,'fixed_code_snippet':None,'confidence':'low' if state=='unknown' else 'high',
            'limitations':'Runtime value unknown.' if state=='unknown' else 'Deployment intent and execution are not established.'}), .1, None
    monkeypatch.setattr(llm,'_call_ollama',call)
    result=llm.explain_occurrence({'file':'tasks.yml','line':3,'rule_id':'missing-validate-certs','message':'Accusation is not proof'},tmp_path,evidence_mode='window')
    assert result['llm_status']=='ok' and result['llm_assessment']==assessment
    assert 'explicitly configured off, on, or unknown' in seen['user']
    assert 'Bounded backend facts' not in seen['user'] and 'summary_text' not in seen['user']
    assert 'flagged' in seen['system']
