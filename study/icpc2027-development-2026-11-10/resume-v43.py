"""Auditable recovery of the daemon-interrupted v4.3 development run only."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ansibleguard.report import llm_explain as llm
from ansibleguard.report.llm_evidence import digest
from ansibleguard.report.llm_runtime import write_checkpoint

run = ROOT / 'study/runs/icpc2027-development-v43-pass3-20261110'
manifest = json.loads((ROOT / 'study/icpc2027-readiness-2026-11-10/evaluation/cases.json').read_text())
progress = json.loads((run / 'run-manifest.json').read_text())
assert progress['panel'] == 'development'
assert manifest['cases_sha256'] == digest([manifest['development'], manifest['evaluation']]) == progress['cases_sha256']
paths = {'icpc_llm_evaluation.py': ROOT / 'scripts/icpc_llm_evaluation.py',
         **{name: ROOT / 'src/ansibleguard/report' / name for name in ('llm_explain.py','llm_evidence.py','llm_suggestions.py')}}
for name, expected in progress['implementation_sha256'].items():
    assert hashlib.sha256(paths[name].read_bytes()).hexdigest() == expected, name
identity = llm.llm_runtime.model_identity(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, llm._open_local, llm._local_chat_url)
assert identity == progress['model_digest']
if progress['status'] == 'completed':
    print('Run already completed; no requests repeated.')
    raise SystemExit(0)
progress.setdefault('recovery_events', []).append({
    'reason': 'daemon restart ended coordinator; completed checkpoints reused irrespective of outcome',
    'completed_at_resume': progress['completed'], 'pending_at_resume': progress['pending'].copy(),
    'inflight_request_before_restart': 'unknown; no unrecorded answer is treated as a result',
    'recovery_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'resume_budget_seconds': 3600,
})
write_checkpoint(run, 'run-manifest', progress)
started, records, reused = time.monotonic(), [], 0
for case in manifest['development']:
    assert case['kind'] == 'controlled'
    with tempfile.TemporaryDirectory(prefix='ansibleguard-evaluation-resume-') as directory:
        root = Path(directory)
        for name, content in case['files'].items():
            path = root / name
            assert path.resolve().is_relative_to(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        for mode in ('window','scoped'):
            key = case['case_id'] + '-' + mode
            path = run / (key + '.json')
            retained = path if path.exists() else next(iter(sorted((run/'history').glob(key+'-*.json'), key=lambda p:p.stat().st_mtime_ns, reverse=True)), None)
            if retained is not None:
                payload = json.loads(retained.read_text())
                assert payload['case_id'] == case['case_id'] and payload['mode'] == mode
                assert payload['model_digest'] == identity and payload['cases_sha256'] == manifest['cases_sha256']
                assert payload['prompt_version'] == llm.PROMPT_VERSION and isinstance(payload['result'], dict)
                if retained != path:
                    write_checkpoint(run, key, payload)
                reused += 1
            else:
                record = {}
                token = llm._CALL_RECORD.set(record)
                try:
                    remaining = 3600 - (time.monotonic() - started)
                    result = ({'llm_status':'budget-exhausted'} if remaining <= 0 else
                              llm.explain_occurrence(case['occurrence'], root, timeout=min(progress['timeout_seconds'], remaining), evidence_mode=mode))
                finally:
                    llm._CALL_RECORD.reset(token)
                payload = {'case_id':case['case_id'], 'family':case['family'], 'mode':mode,
                           'model_digest':identity, 'prompt_version':llm.PROMPT_VERSION,
                           'cases_sha256':manifest['cases_sha256'], 'result':result, **record}
                write_checkpoint(run, key, payload)
                print(json.dumps({'case_id':case['case_id'],'mode':mode,'status':result['llm_status']}), flush=True)
            records.append(payload)
            if key in progress['pending']:
                progress['pending'].remove(key)
            progress['completed'] = len(records)
            write_checkpoint(run, 'run-manifest', progress)
assert not progress['pending'] and len(records) == 48
assert llm.llm_runtime.model_identity(llm.DEFAULT_HOST,llm.DEFAULT_MODEL,llm._open_local,llm._local_chat_url) == identity
summary = {'model_digest':identity,'cases_sha256':manifest['cases_sha256'],'panel':'development',
           'counts':{mode:dict(Counter(r['result']['llm_status'] for r in records if r['mode']==mode)) for mode in ('window','scoped')},
           'recovery_duration_seconds':round(time.monotonic()-started,2), 'reused_completed_records':reused,
           'timing_note':'Interrupted duration is not available; recovery timing excludes interruption and prior requests.',
           'human_quality_results':'pending independent review'}
(run/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
progress['status']='completed'
progress['model_digest_stable_after_recovery']=True
write_checkpoint(run,'run-manifest',progress)
print(json.dumps(summary),flush=True)
