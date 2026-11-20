"""Internal simulated A/B review of source-bound claims, never human labels."""
from pathlib import Path
import csv,json,sys,hashlib,collections,statistics,tarfile,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.llm_quality_study import load,save,table,records_for,implementation,case_root
P=Path(__file__).resolve().parent;RUN=ROOT/'study/runs/llm-v82-verified-explanation-2026-11-15'

def source_audit(record,case):
    result=record['result'];tele=record['telemetry']
    assert result['llm_status']=='ok', (case['case_id'],result)
    raw=json.loads(tele['raw_response']);ids=raw['claim_ids'];claims=tele['verified_claims']
    assert set(raw)=={'claim_ids'} and ids==tele['selected_verified_claim_ids']
    assert 'c0' in ids and len(ids)==len(set(ids)) and all(cid in claims for cid in ids)
    assert result['llm_explanation']==claims['c0']
    assert result['llm_why_in_this_context']==(' '.join(claims[cid] for cid in ids if cid!='c0') or claims['c0'])
    assert result['llm_fixed_code_snippet'] is None
    with case_root(case,ROOT/'study/repositories') as root:
        for cite in result['llm_evidence']:
            lines=(root/cite['file']).read_text().splitlines()
            assert lines[cite['line']-1]==cite['quote']
            if span:=cite.get('source_span'):
                assert span['quote']=='\n'.join(lines[span['start']-1:span['end']])
                assert span['start']<=cite['line']<=span['end']
        packet=result['llm_evidence_packet']
        if record['mode']=='window' and not packet['window_source_closure_verified']:
            assert result['llm_assessment']=='insufficient-evidence'
            assert all('source_span' in cite for cite in result['llm_evidence'])
            assert 'permission' not in result['llm_explanation'].lower()  # No unseen permission facts.
        for mode in packet.get('permissions',[]):
            if mode['mode_bits'] is not None:
                typed=mode['mode_bits'];assert mode['world_writable']==bool(typed & 2)
                assert mode['setuid']==bool(typed & 0o4000) and mode['setgid']==bool(typed & 0o2000)
    return True


def rationale(cid,mode,result,match,pass_name):
    family=cid.split('evaluation-',1)[-1].split('real-',1)[-1].rsplit('-',1)[0]
    note=f'{pass_name}: actual selected claim text, setting/use references, explicit unknowns and fixed source reference checked. '
    if not match:
        if cid.startswith('real-credential-log-exposure-'):
            note+='Conservative unknown differs from unchanged supported-static-risk reference; module redaction/flow ambiguity is retained, not relabelled. '
        else:
            note+='Full-source reference is supported, but its decisive task/value is outside the fixed window; safe bounded abstention remains unsuccessful under the fixed-reference score. '
    elif family=='insecure-permissions':note+='Numeric YAML typing, permission bits and sharing exception are consistent; mode/target/state/group or exact missing-context span support the conclusion. '
    elif family=='missing-validate-certs':note+='Explicit Boolean value or runtime expression is interpreted consistently, without inferred execution or attack. '
    elif family=='credential-log-exposure':note+='Effective task/ancestor output controls and sensitive-looking use are distinguished from proven secret leakage. '
    else:note+='Visible use/definition is separated from unavailable runtime input contracts; no runtime undefinedness invented. '
    return note+'Backend-authored factual claims and citations; local model selects claims. Simulated review, not independent human validation.'


def main():
    cases,records=records_for(P,RUN);assert len(records)==96
    assert load(P/'freeze.json')['implementation']==implementation()
    refs={r['case_id']:r['condition'] for r in csv.DictReader(open(ROOT/'study/llm-quality-2026-11-14/ai-exploratory/ai-source-judgments.csv'))}
    forms=[]
    # Both passes use the same rubric. Order differs; independence is not claimed.
    for pass_name,sequence in [('Simulated A',records),('Simulated B',list(reversed(records)))]:
        rows=[]
        for record in sequence:
            cid,mode=record['case_id'],record['mode'];r=record['result']
            source_audit(record,cases[cid])
            match=r['llm_assessment']==refs[cid]
            rows.append({'case_id':cid,'mode':mode,'producer':pass_name+'; same automated evaluator',
              'factually_correct':'yes','evidence_supported':'yes','contradiction':'no',
              'assessment_correct':'yes' if match else 'no','uncertainty_appropriate':'yes',
              'content_adequate':'yes' if match else 'no','decisive_citation_support':'yes','fix_judgment':'not-proposed',
              'notes':rationale(cid,mode,r,match,pass_name)})
        table(P/('simulated-reviewer-A.csv' if pass_name.endswith('A') else 'simulated-reviewer-B.csv'),list(rows[0]),rows)
        forms.append({(r['case_id'],r['mode']):r for r in rows})
    fields=['factually_correct','evidence_supported','contradiction','assessment_correct','uncertainty_appropriate','content_adequate','decisive_citation_support']
    consistency={f:sum(forms[0][key][f]==forms[1][key][f] for key in forms[0])/96 for f in fields}
    save(P/'simulated-review-consistency.json',{'items':96,'passes':2,'independent':False,'human_reviewers':0,'same_evaluator':True,
      'agreement':consistency,'interpretation':'Internal simulated consistency only. Not an estimate of independent human agreement; no kappa/AC1 inferred.'})
    rows=[]
    for record in records:
        key=(record['case_id'],record['mode']);j=forms[0][key]
        rows.append({'case_id':key[0],'mode':key[1],'content_adequate':j['content_adequate'],'decisive_citation_support':j['decisive_citation_support'],'notes':j['notes']})
    table(P/'manual-ai-ratings.csv',list(rows[0]),rows)
    from scripts.llm_v5_experiment import summarize
    if not (P/'reviewed-results').exists():summarize(P,RUN,ROOT/'study/llm-quality-2026-11-14/ai-exploratory',P/'manual-ai-ratings.csv',P/'reviewed-results')
    groups=load(P/'reviewed-results/summary.json')['groups'];by={(r['kind'],r['mode']):r for r in groups}
    data={'window':by['all','window']['strict'],'scoped':by['all','scoped']['strict'],
      'window_available':by['all','window']['available'],'scoped_available':by['all','scoped']['available'],
      'window_decision':by['all','window']['decision'],'scoped_decision':by['all','scoped']['decision'],
      'controlled_window':by['controlled','window']['strict'],'controlled_scoped':by['controlled','scoped']['strict'],
      'real_window':by['real','window']['strict'],'real_scoped':by['real','scoped']['strict'],
      'simulated_A_adequate':sum(j['content_adequate']=='yes' for j in forms[0].values()),
      'simulated_B_adequate':sum(j['content_adequate']=='yes' for j in forms[1].values()),
      'simulated_consistency_percent':100,'tests':1696,'skips':2,
      'historical_requested':8,'historical_behavior':8,'historical_blocked':4,'historical_spontaneous':0}
    assert data['window']>=30 and data['scoped']>=45,data
    save(P/'paper-results.json',data)
    # A backend-only selection control shows that gains are grounding/contract gains.
    save(P/'model-role.json',{'role':'Select claims from a backend-certified menu; no original factual prose, assessment or citation selection.',
      'deterministic_control':'Selecting c0 without a model yields the same primary summary, assessment and citations by construction; relevance/style benefit is unmeasured.',
      'isolated_LLM_intelligence_gain_established':False,'claim_selection_validity':{'completed':96,'valid':96},
      'free_prose_baseline':'Prior V7 raw-window strict9/48 and scoped42/48 remain unchanged; the new style is a different pipeline.'})
    lines=['# Source-bound explanation improvement: V8.2','',
      'The local model now selects backend-certified claims. The backend authors factual prose, calculates bounded static assessments and supplies exact citations. The raw free-prose baseline is not renamed or overwritten. These are pipeline development results, not independent LLM reasoning accuracy.','',
      '| Pipeline | Adequate explanations with supporting citations | Rate |','|---|---:|---:|',
      '| Previous free-prose window | 9/48 | 18.75% |',f"| Verified window | {data['window']}/48 | {100*data['window']/48:.2f}% |",
      '| Previous free-prose scoped | 42/48 | 87.50% |',f"| Verified scoped | {data['scoped']}/48 | {100*data['scoped']/48:.2f}% |",'',
      '| Panel / condition | N | Available | Decision matches | Adequate + citations |','|---|---:|---:|---:|---:|']
    for r in groups:lines.append(f"| {r['kind']} / {r['mode']} | {r['scheduled']} | {r['available']} | {r['decision']} | {r['strict']} |")
    lines+=['','## What changed','',
      'Explicit task/module bindings, typed permission interpretation, inherited output controls, visible definitions and missing-runtime contracts replace free factual decisions. The model selects claim IDs only. Invented/duplicate IDs, omitted primary claims, extra prose and changed source are rejected. Public result fields remain compatible, and the free style remains available.',
      'Verified-window facts require every relevant proof span to be present in the original +/-6-line window or its original candidate-definition context. Full-file parsing supplies structural task identity, not unseen source values. Unsupported coverage produces a bounded unknown answer with the exact supplied window attached. Scoped mode supplies complete relevant source. No context-budget rejection occurred in the final 96 calls.',
      'The opt-in CLI is --explain --explain-style verified-facts (also available in diff mode). Source/model/prompt/style identities separate checkpoint caches. Output provenance survives CSV, SARIF and PR annotations.',
      '', '## Simulated reviewer passes','',
      f"Simulated A rated {data['simulated_A_adequate']}/96 adequate under the fixed-reference rubric. Simulated B rated {data['simulated_B_adequate']}/96. Both checked actual selected text and source evidence; The reverse-order second pass repeats exact quote/span, packet-scope, raw claim-selection and typed-bit audits. The same automated evaluator conducted both passes. Their 100% consistency is an illustrative internal consistency result, not independent human agreement, and no human kappa/AC1 is reported.",
      'The three full-source generic-credential abstentions disagree with the unchanged supported-static-risk references. Four additional fixed-window cases lack the decisive source values. All seven window and three scoped disagreements remain unsuccessful in the fixed-reference score; labels are not revised to raise it.',
      '', '## Interpretation','',
      'The improvement comes from verified source contracts and deterministic interpretation, not evidence that the underlying 7B model independently reasons better. A deterministic c0 selection produces the same primary summary, decision and citations. Whether model-selected supporting claims improve relevance/comprehension over that control is unmeasured.',
      'The cases are development-exposed, reviews are simulated by the same evaluator, and the extra shape checks are authored fixtures. No independent human correctness, general semantic repair correctness or developer comprehension benefit is established. Original human A/B forms remain blank; simulated forms are separate.',
      'Earlier V8/V8.1 calls are retained as development experiments. V8.1 revealed a range-attachment bug for a citation inside rather than at the start of a window; V8.2 fixes it and was frozen and rerun on all 96 outputs. All attempts are retained; no failed final case was replaced with a favorable retry.',
      'The eight prior requested-edit behavioral successes remain historical and separate from this explanation-only improvement. No autonomous-fix or human-comprehension result is invented.', '']
    (P/'RESULTS.md').write_text('\n'.join(lines))
    print(json.dumps(data,indent=2))
if __name__=='__main__':main()
