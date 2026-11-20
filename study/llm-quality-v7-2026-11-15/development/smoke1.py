import sys,json,time,hashlib
from pathlib import Path
ROOT=Path('/home/aymmzn/Documents/AnsibleChecklist');sys.path.insert(0,str(ROOT))
from scripts.llm_quality_study import load,save,case_root,llm,implementation
m=load(ROOT/'study/llm-quality-v6-2026-11-14/manifest.json')
out=ROOT/'study/runs/llm-v7-smoke1-2026-11-15';out.mkdir(exist_ok=False)
cases=[c for c in m['panels']['explanation'] if c['kind']=='controlled' and int(c['case_id'].rsplit('-',1)[1])<3]
save(out/'design.json',{'development_only':True,'cases':[c['case_id'] for c in cases],'max_development_rounds':2,'implementation':implementation()})
for c in cases:
 for mode in ('window','scoped'):
  r={};tok=llm._CALL_RECORD.set(r)
  with case_root(c,ROOT/'study/repositories') as root:
   try: result=llm.explain_occurrence(c['occurrence'],root,evidence_mode=mode,timeout=120)
   finally:llm._CALL_RECORD.reset(tok)
  save(out/(c['case_id']+'-'+mode+'.json'),{'case_id':c['case_id'],'mode':mode,'result':result,'telemetry':r})
  print(json.dumps({'case':c['case_id'],'mode':mode,'status':result['llm_status'],'assessment':result.get('llm_assessment'),'error':result.get('llm_error')}),flush=True)
