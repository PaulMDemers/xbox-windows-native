"""Qualify one physical candidate cycle against its preceding event-log boundary."""
import argparse,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];art=k/'artifacts/physical'
parser=argparse.ArgumentParser();parser.add_argument('--cycle',type=int,choices=[1],required=True);cycle=parser.parse_args().cycle
r=json.loads((k/'physical.json').read_text());row=r['cycles'][cycle-1];assert row.get('collected_utc') and not r['startup_enabled']
tag=f'physical-cycle{cycle}-'
result=dict(scope=__doc__,physical_result=True,new_events={});known_before=[]
for label in ['system','application']:
    for prefix in ['before','after']:
        subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(art/((('before' if cycle==1 else f'cycle{cycle-1}') if prefix=='before' else f'cycle{cycle}')+'-'+label+'.evt')),'--output',str(k/(tag+prefix+'-'+label+'-events.json'))],check=True,stdout=subprocess.DEVNULL)
    a=json.loads((k/(tag+'before-'+label+'-events.json')).read_text())['records'];b=json.loads((k/(tag+'after-'+label+'-events.json')).read_text())['records']
    by={v['record']:v for v in b};assert all(by.get(v['record'])==v for v in a), 'Before/after boundary needs manual review'
    boundary=max((v['record'] for v in a),default=0)
    known_before.extend(a)
    result['new_events'][label]=[v for v in b if v['record']>boundary]
log=(art/f'cycle{cycle}-gdi-baseline.txt').read_bytes().decode('ascii') if row['collected'].get('gdi-baseline.txt') else ''
runner=(art/f'cycle{cycle}-attempt.log').read_bytes().decode('ascii') if row['collected'].get('attempt.log') else ''
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
result['expected_binaries_match']=all(row['candidate_checks'].values()) and all(row['payload_checks'].values())
subprocess.run([sys.executable,str(k/'decode-mapping.py'),str(art/f'cycle{cycle}-trace.bin'),'--output',str(k/'physical-mapping.json')],check=True,stdout=subprocess.DEVNULL)
mapping=json.loads((k/'physical-mapping.json').read_text())['mapping_observations']
result['direct_ram_uc_verified']=bool(mapping) and all(g['physical']==g['ram_offset'] and g['length']==0x400000 and all(g['pages'][str(i)].get('physical')==g['ram_offset']+(0 if i==0 else 0x3ff000) and g['pages'][str(i)].get('effective_type')=='UC' for i in [0,1]) for g in mapping)
result['passed']=all([result['direct_ram_uc_verified'],result['probe_passed'],result['pixel_checks_passed'],result['normal_restart_requested'],result['normal_shutdown_recorded'],result['expected_binaries_match'],not result['unexpected_error_or_warning_records'],not result['new_popup_records'],len(result['timings'])==5,row['trace_valid']])
result['limits']='One 256x128 synchronous GDI sample per operation; includes flush/message/visibility checks. Not window-drag FPS, bus bandwidth, repeated-run variance or full storage qualification.'
(k/(tag+'qualification.json')).write_text(json.dumps(result,indent=2)+'\n')
row['qualification']=tag+'qualification.json';row['passed']=result['passed'];(k/'physical.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(dict(passed=result['passed'],timings=result['timings'],unexpected=result['unexpected_error_or_warning_records']),indent=2))
