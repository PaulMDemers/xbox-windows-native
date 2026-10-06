"""Review sparse installer ordering without substituting clean runs for failures."""
import hashlib
import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parent
case=sys.argv[1] if len(sys.argv)>1 else '003'
assert case in ['003','004']
out=root/case
def read(path):return json.loads(path.read_text())
trace=read(out/'trace.json')
audit=read(out/'audit.json')
launch=read(out/'launch.json')
assert trace['status']=='reached_kernel_shutdown' and trace['guest_resumed']
sha=hashlib.sha256((out/'trace-source.py').read_bytes()).hexdigest()
assert sha==trace['trace_source_sha256']
assert len(launch['cycles'])==1 and launch['cycles'][0]['dashboard_return']
assert audit['mapping_checks']==527 and audit['probe_completed'] and audit['persistence_passed']
assert len(audit['files'])==50 and all(f['exact'] for f in audit['files'])
assert len(audit['workload']['deleted_files_absent'])==34
assert all(audit['workload']['deleted_files_absent'].values())
assert audit['workload']['paint_api_replay_passed']
assert len(audit['workload']['timed_rounds'])==15 and audit['workload']['timed_rounds'][-1][1]>=60000
assert all(b['matched'] for b in audit['runtime_binary_checks'])
assert len(audit['hives'])==5 and all(h['parsed'] for h in audit['hives'])
assert audit['normal_shutdown_count']==1 and not audit['ordinary_run_valid']
events=trace['events']; pairs=[]
for event in events:
    if event['function']!='PnP_Create_return':continue
    entry=events[event['entry_index']] if event['entry_index'] is not None else None
    if case=='003':
        assert entry and entry['function']=='PnP_Create_call'
        assert entry['thread']==event['thread'] and entry['command_line']==event['command_line']
        assert not entry.get('pnp_decode_error')
    else:assert entry is None
    assert not event.get('pnp_decode_error')
    pairs.append(dict(entry_index=entry['index'] if entry else None,return_index=event['index'],
        command_line=event['command_line'],token=entry['call_arguments'][0] if entry else None,
        creation_flags=entry['call_arguments'][6] if entry else None,return_eax=event['return_eax'],
        last_error=event['last_error'],process_information=event['process_information']))
hard=[e for e in events if 'HardError' in e['function']]
assert len(pairs)==2 and not hard and not audit['popup_records']
assert audit['diagnostic_checks_passed']
assert 'VEN_10DE&DEV_02A0' in pairs[0]['command_line'] and pairs[0]['return_eax']=='0x1'
assert 'VEN_1B36&DEV_0005' in pairs[1]['command_line']
assert pairs[1]['return_eax']=='0x0' and pairs[1]['last_error']==6
assert pairs[1]['process_information']==['0x0']*4
if case=='003':
    assert len(events)==9
    assert events[2]['function']=='PnP_Wait_return' and events[2]['wait_result']=='0x0'
    assert events[3]['function']=='PnP_Create_call' and events[3]['saved_token']=='0x8ac'
    assert events[4]['function']=='PnP_Control_entry' and events[4]['control']==5
    assert events[3]['thread']!=events[4]['thread']
    assert events[5]['function']=='PnP_Create_return' and events[5]['saved_token']=='0x0'
    assert events[3]['tick_count']<events[4]['tick_count']<events[5]['tick_count']
else:
    assert len(events)==3 and events[1]['saved_token']=='0x0'
assert events[-1]['function']=='_NtShutdownSystem@4'
links=[]
for event in hard:
    owner=event['owner']
    matches=[p for p in pairs if p['return_eax']!='0x0' and
             int(p['process_information'][2],16)==owner['pid'] and
             p['command_line']==owner['command_line']]
    assert len(matches)<=1
    links.append(dict(hard_error_index=event['index'],owner=owner,
        creation_return_index=matches[0]['return_index'] if matches else None,
        basis='Matching command and returned PID within this bounded trace; EPROCESS available only at hard-error observation.'))
result=dict(case=case,trace_source_sha256=sha,source_hash_matches=True,
    physical_access=False,ordinary_boot_qualified=False,
    trace_events=len(events),trace_status=trace['status'],guest_resumed=True,
    creation_pairs=pairs,hard_errors=hard,hard_error_creation_links=links,
    control_events=[e for e in events if e['function']=='PnP_Control_entry'],
    wait_returns=[e for e in events if e['function']=='PnP_Wait_return'],
    popup_records=audit['popup_records'],diagnostic_checks_passed=audit['diagnostic_checks_passed'],
    cleanup=read(root.parents[1]/'work/runs'/launch['run']/'cleanup.json'),
    limits=[
        'Matching creation return PID to hard-error owner links an observed child; handles alone are not process identity.',
        'A successful create return does not by itself prove user initialization completed.',
        'Control entry is one PnP shutdown notification, not the global start of window-station shutdown.',
        'LastError is not meaningful on a successful Win32 call.',
        'Debugger pauses still affect timing; no ordinary boot or physical qualification.',
        'No full allocation audit; synthetic BMP API cases remain distinct from user application tests.'])
(out/'sparse-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(events=len(events),creation_pairs=len(pairs),hard_errors=len(hard),popups=len(audit['popup_records']),diagnostic_checks_passed=audit['diagnostic_checks_passed'])))
