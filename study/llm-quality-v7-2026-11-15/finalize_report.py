"""Finalize explicitly reviewed V7 outcomes; never manufacture human labels."""
from pathlib import Path
import sys,json,hashlib,csv
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from scripts.llm_quality_study import load,save,table,records_for,implementation
from scripts.llm_v5_experiment import summarize
P=Path(__file__).resolve().parent

def main():
    notes=load(P/'manual-notes.json');_,records=records_for(P,ROOT/'study/runs/llm-v7-explanation-2026-11-15')
    assert len(records)==96 and len(notes)==96, (len(records),len(notes))
    assert {r['case_id']+'/'+r['mode'] for r in records}==set(notes)
    assert load(P/'freeze.json')['implementation']==implementation()
    fields=['case_id','mode','content_adequate','decisive_citation_support','notes']
    rows=[]
    for r in records:
        cid,mode=r['case_id'],r['mode'];content,citation,note=notes[cid+'/'+mode]
        rows.append(dict(zip(fields,[cid,mode,content,citation,note])))
    table(P/'manual-ai-ratings.csv',fields,rows)
    review=P/'reviewed-results'
    if not review.exists():summarize(P,ROOT/'study/runs/llm-v7-explanation-2026-11-15',ROOT/'study/llm-quality-2026-11-14/ai-exploratory',P/'manual-ai-ratings.csv',review)
    result=load(review/'summary.json');old=load(ROOT/'study/llm-quality-v6-2026-11-14/reviewed-results/summary.json')
    groups={(r['kind'],r['mode']):r for r in result['groups']};oldgroups={(r['kind'],r['mode']):r for r in old['groups']}
    comparisons=[]
    for mode in ['window','scoped']:
        for key in ['available','decision','content','strict']:
            a,b=oldgroups['all',mode][key],groups['all',mode][key]
            comparisons.append({'condition':mode,'measure':key,'V6':a,'V7':b,'denominator':48,'percentage_point_change':round(100*(b-a)/48,2)})
    table(P/'before-after.csv',list(comparisons[0]),comparisons)
    repair=load(P/'model-requested-edits-summary.json')
    _,triage=records_for(P,ROOT/'study/runs/llm-v7-ai-triage-repair-2026-11-15')
    spontaneous=sum(bool(r['result'].get('llm_fixed_code_snippet')) for r in triage)
    save(P/'spontaneous-repair-summary.json',{'cases':12,'accepted':sum(r['result']['llm_status']=='ok' for r in triage),'proposals':spontaneous,'eligible_sources':8,'task':'Autonomous triage, separate from caller-selected edits'})
    data={'window':groups['all','window']['strict'],'scoped':groups['all','scoped']['strict'],
          'window_available':groups['all','window']['available'],'scoped_available':groups['all','scoped']['available'],
          'window_decision':groups['all','window']['decision'],'scoped_decision':groups['all','scoped']['decision'],
          'controlled_window':groups['controlled','window']['strict'],'controlled_scoped':groups['controlled','scoped']['strict'],
          'real_window':groups['real','window']['strict'],'real_scoped':groups['real','scoped']['strict'],
          'requested':repair['eligible_drafts'],'behavior':repair['eligible_behavior_passed'],
          'blocked':sum(not r['eligible'] and not r['model_called'] and not r['proposal_ready'] for r in repair['rows']),
          'spontaneous':spontaneous,'tests':1676,'skips':2}
    save(P/'paper-results.json',data)
    errors=[{'case_id':r['case_id'],'mode':r['mode'],'error':r['result'].get('llm_error'),'status':r['result']['llm_status']} for r in records if r['result']['llm_status']!='ok']
    save(P/'execution-failures.json',errors)
    save(P/'FINAL_STATUS.json',{'finished_outputs':96,'manual_AI_review_rows':96,'independent_human_reviews':0,
        'development_exposure':True,'source_candidate_matches_freeze':True,'comparisons':comparisons,
        'paper_results':data,'source_reference_labels_changed':False,'human_forms_changed':False,
        'measured_human_agreement':None,'hypothetical_copy_policy':'Clearly labelled placeholders, no kappa/AC1 calculated.',
        'deployment_selection':'V7 evaluated development candidate; use reported comparison, not guaranteed improvement.'})
    lines=['# V7 frozen development experiment','',
      'All 96 outputs were explicitly reviewed by the same unblinded AI implementer using unchanged AI source references. Cases are development-exposed. These are complete-pipeline results, not independent human accuracy or reviewer agreement.','',
      '| Condition | Measure | V6 /48 | V7 /48 | Change (percentage points) |','|---|---|---:|---:|---:|']
    for r in comparisons:lines.append(f"| {r['condition']} | {r['measure']} | {r['V6']} | {r['V7']} | {r['percentage_point_change']:+.2f} |")
    lines+=['','| Panel / condition | N | Accepted | Decision matches | Adequate | Adequate + citations |','|---|---:|---:|---:|---:|---:|']
    for r in result['groups']:lines.append(f"| {r['kind']} / {r['mode']} | {r['scheduled']} | {r['available']} | {r['decision']} | {r['content']} | {r['strict']} |")
    lines+=['','## Implementation and outcome interpretation','',
      'Generation now uses neutral present/absent/unknown states mapped to the unchanged public assessment vocabulary. No decision is inferred or corrected from prose. State-specific grammars require low confidence and nonempty missing dependencies for unknown; nonempty evidence-boundary text is required. Rule definitions and neutral questions are shared by both conditions. The window arm retains its prior context boundary and receives no scoped facts, selected answers or selected citations.',
      'The scoped condition still uses backend-constrained decisions, authored fact summaries and selected citations. Every free-reasoning claim is also reviewed. Rejected responses, wrong citations, incorrect bit interpretation and ambiguous reference disagreements are retained as unsuccessful outcomes. A right structured decision does not rescue false prose.',
      f"There are {len(errors)} unavailable/rejected outputs, including {sum('budget' in (r['error'] or '') for r in errors)} conservative byte/token-budget rejections. The larger state-specific grammar and shared rule guidance consume conservative context allowance; this can reduce availability without source truncation. The generation grammar does not certify substantive truth, and the model can still choose an incorrect known state rather than admit unknown facts.",
      'Two smoke rounds (24 calls each) were used, with raw attempts retained. Exact round1/round2 explanation sources were recovered and hash-verified against their recorded identities. Compact JSON serialization followed the second-round code changes; candidate freezing preceded completion of smoke2 collection, with no further model-driven code edits. Final tests and the scored run use the frozen compact candidate. Shared local-model queue affects timing, which is not used as a comparative outcome.','',
      '## Repair experiments','',
      f"Caller-selected local-model drafts: {data['requested']}/8 delivered; {data['behavior']}/8 passed mechanical and isolated behavioral checks. {data['blocked']}/4 ineligible sources were blocked before any generation request. All eight raw snippets and BEFORE-only prompts were explicitly inspected. No reference AFTER task was supplied and no source was applied. See model-requested-edits-ai-review.csv.",
      f"Autonomous triage still produced {spontaneous}/8 eligible code proposals across 12 source calls. This is a separate task; do not substitute the requested-edit success rate. The prior deterministic generator also passed 8/8, so these tests do not establish LLM superiority.",'',
      '## Scientific and manuscript provenance','',
      'The original detection precision, corpus prevalence, PR replay and 60-case pilot are historical results, not recomputed by this experiment. Corrected detection-family agreement percentages (67%, 27%, 77%) are author-supplied with unresolved denominators/paired labels; no aggregate agreement or kappa/AC1 is inferred. The new 48-case quality counts are not human agreement.',
      'Human explanation/repair forms remain blank and recruitment deferred. An optional internal paper copy may show explicitly hypothetical agreement placeholders; measured paper versions retain the actual method. No independent explanation correctness, general repair semantic correctness or comprehension benefit is established.',
      'Full test suite: 1,676 passed, two skipped. Production hashes match freeze.json. See full-validation.log, validation-sources.tar.gz, raw run records, manual-ai-ratings.csv, environment.json and the archived implementation for reproduction.','']
    (P/'RESULTS.md').write_text('\n'.join(lines))
    print(json.dumps(data,indent=2))
if __name__=='__main__':main()
