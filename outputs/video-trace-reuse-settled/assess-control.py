"""Compare shutdown-only emulator popups with an unchanged-driver control.
Preserves the strict failed audits. Eligibility here is only for one bounded
physical trial, not a clean-event qualification or a production release.
"""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
paths={'candidate':k/'audit.json','control':k.parent/'video-trace-reuse-control/audit.json'}
a={name:json.loads(path.read_text()) for name,path in paths.items()}

def other_checks(r,cycles,return_key):
    return all([all(v['matched'] for v in r['payloads']),
        all(r['baseline_checks'].values()),r['trace_valid'],r[return_key],
        r['normal_shutdown_count']==cycles,not r['unexpected_errors'],
        not r['new_events']['application'],len(r['cycles'])==cycles,
        all(v['pixel_and_timing_workload_passed'] and v['normal_restart_requested'] for v in r['cycles'])])

def signature(v):
    return {key:v[key] for key in ['source','event_id','event_id_hex','type','strings','data_hex']}

expected={'source':'Application Popup','event_id':26,'event_id_hex':'4000001a','type':4,
 'strings':['rundll32.exe - DLL Initialization Failed',
            'The application failed to initialize because the window station is shutting down. '],
 'data_hex':''}

def shutdown_only(r):
    stops=[v for v in r['new_events']['system'] if v['source']=='EventLog' and v['event_id']==6006]
    popups=r['new_popup_records'];assigned=[]
    for v in popups:
        if signature(v)!=expected:return False
        matched=[s['record'] for s in stops if s['record']>v['record'] and 0<=s['generated_unix']-v['generated_unix']<=5]
        if len(matched)!=1:return False
        assigned.extend(matched)
    return bool(popups) and len(assigned)==len(set(assigned))

fixture=json.loads((k.parent/'video-trace-reuse-control/fixture.json').read_text())
candidate_fixture=json.loads((k/'fixture.json').read_text())
files=lambda f:{v['path']:v['sha256'] for v in f['payloads']}
bf,cf=files(fixture),files(candidate_fixture)
original='f8af1d8477d61ad8933962fd6347f43620f5ef1d21efe54110b94fec106986eb'
checks={
 'control_original_miniport':bf['winnt/system32/drivers/xboxvnt5.sys']==original,
 'identical_runner_and_probe':all(bf[p]==cf[p] for p in ['xwnrps01/runner.exe','xwnrps01/replay.exe','xwnrps02/replay.exe']),
 'same_base_fixture':fixture['source_sha256']==candidate_fixture['source_sha256'],
 'control_other_checks':other_checks(a['control'],1,'one_dashboard_return'),
 'candidate_other_checks':other_checks(a['candidate'],2,'two_dashboard_returns'),
 'control_shutdown_popup_reproduced':shutdown_only(a['control']),
 'candidate_popups_match_bounded_control':shutdown_only(a['candidate'])}
r={'scope':__doc__,'checks':checks,'eligible_for_bounded_physical_trial':all(checks.values()),
 'strict_audits_passed':{name:r['passed'] for name,r in a.items()},
 'inputs':{name:{'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for name,path in paths.items()},
 'matched_popup_signature':expected,
 'limits':('Matching baseline shutdown popups reproduced.' if all(checks.values()) else 'Control did not establish matching baseline behavior; hardware remains blocked.')+' Strict audits remain unchanged; this assessment does not identify a root cause.'}
(k/'control-assessment.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
