"""Qualify the single baseline hardware measurement from persisted logs."""
import json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[2];art=k/'artifacts/physical'
r=json.loads((k/'trial.json').read_text());assert r.get('collected_utc') and not r['startup_enabled']
result=dict(scope=__doc__,physical_result=True,new_events={});known_before=[]
for label in ['system','application']:
    for prefix in ['before','after']:
        subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(art/(prefix+'-'+label+'.evt')),'--output',str(k/(prefix+'-'+label+'-events.json'))],check=True,stdout=subprocess.DEVNULL)
    a=json.loads((k/('before-'+label+'-events.json')).read_text())['records'];b=json.loads((k/('after-'+label+'-events.json')).read_text())['records']
    by={v['record']:v for v in b};assert all(by.get(v['record'])==v for v in a), 'Before/after boundary needs manual review'
    boundary=max((v['record'] for v in a),default=0)
    known_before.extend(a)
    result['new_events'][label]=[v for v in b if v['record']>boundary]
log=(art/'after-gdi-baseline.txt').read_bytes().decode('ascii') if r['collected'].get('gdi-baseline.txt') else ''
runner=(art/'after-attempt.log').read_bytes().decode('ascii') if r['collected'].get('attempt.log') else ''
result['probe_log']=log;result['runner_log']=runner
result['pixel_checks_passed']=all(f'COPY_stage_pass {i} 1 0\r\n' in log for i in range(4))
result['probe_passed']=log.endswith('PASS 0 0 0\r\n') and 'FAIL' not in log
result['normal_restart_requested']=runner=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
result['normal_shutdown_recorded']=any(v['source']=='EventLog' and v['event_id']==6006 for v in result['new_events']['system'])
known={('Service Control Manager',7000),('Ftdisk',49)}
def known_recurring(v):
    return (v['source'],v['event_id']) in known and any(all(old[key]==v[key] for key in ['source','event_id','type','strings','data_hex']) for old in known_before)
result['unexpected_error_or_warning_records']=[v for records in result['new_events'].values() for v in records if v['type'] in (1,2) and not known_recurring(v)]
result['new_popup_records']=[v for v in result['new_events']['system'] if v['source']=='Application Popup']
result['timings']=[]
names=['opaque fill','DIB to screen','screen to DIB','overlap right/down','overlap left/up']
for line in log.splitlines():
    if line.startswith('TIMING_kind_count_ms '):
        kind,count,ms=map(int,line.split()[1:]);assert 0<=kind<5 and count>0 and ms>0
        result['timings'].append(dict(kind=kind,operation=names[kind],count=count,milliseconds=ms,ms_per_operation=ms/count,megapixels_per_second=(256*128*count)/(ms*1000)))
result['baseline_unchanged']=all(r['baseline_checks_after'].values()) and all(r['payload_checks_after'].values())
result['passed']=all([result['probe_passed'],result['pixel_checks_passed'],result['normal_restart_requested'],result['normal_shutdown_recorded'],result['baseline_unchanged'],not result['unexpected_error_or_warning_records'],not result['new_popup_records'],len(result['timings'])==5])
result['limits']='One 256x128 synchronous GDI sample per operation; includes flush/message/visibility checks. Not window-drag FPS, bus bandwidth, repeated-run variance or full storage qualification.'
(k/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
r['qualification']='qualification.json';r['bounded_gdi_passed']=result['passed'];(k/'trial.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(passed=result['passed'],timings=result['timings'],unexpected=result['unexpected_error_or_warning_records']),indent=2))
