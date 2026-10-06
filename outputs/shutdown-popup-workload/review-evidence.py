"""Review the reproduced popup against its trace, event delta and cold artifacts."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
workspace=root.parents[1]
def read(path):return json.loads(path.read_text())
trace=read(root/'001/trace.json')
audit=read(root/'001/audit.json')
launch=read(root/'001/launch.json')
runtime=read(root/'001/runtime.json')
previous=read(root.parent/'fatx0098-soak/rehearsal/audit.json')
source_sha=hashlib.sha256((root/'001/trace-source.py').read_bytes()).hexdigest()
assert source_sha==trace['trace_source_sha256']
assert trace['status']=='reached_kernel_shutdown' and trace['guest_resumed']
assert [e['function'] for e in trace['events']]==['_ExRaiseHardError@24','_ExpRaiseHardError@24','_NtShutdownSystem@4']
first,second,shutdown=trace['events']
assert first['arguments'][0]==second['arguments'][0]=='0xc000026b'
assert first['caller']=='0xa007e406'
assert first['owner']==second['owner'] and first['thread']==second['thread']
assert first['owner']['image']=='rundll32.exe' and 'VEN_1B36&DEV_0005' in first['owner']['command_line']
assert shutdown['owner']['image']=='winlogon.exe' and shutdown['arguments']==['0x1']
assert len(audit['popup_records'])==1
popup=audit['popup_records'][0]
assert popup['strings']==previous['popup_records'][0]['strings']
assert not audit['diagnostic_checks_passed'] and not audit['ordinary_run_valid']
assert audit['mapping_checks']==527 and audit['probe_completed'] and audit['persistence_passed']
work=audit['workload']
assert len(work['files'])==50 and all(f['matched'] for f in work['files'])
assert len(work['deleted_files_absent'])==34 and all(work['deleted_files_absent'].values())
assert work['paint_api_replay_passed'] and len(work['timed_rounds'])==15 and work['timed_rounds'][-1][1]>=60000
assert len(audit['hives'])==5 and all(h['parsed'] for h in audit['hives'])
assert all(b['matched'] for b in audit['runtime_binary_checks'])
assert any(b['path']=='winnt/system32/win32k.sys' for b in audit['runtime_binary_checks'])
assert len(launch['cycles'])==1 and audit['dashboard_return'] and audit['normal_shutdown_count']==1
fixture=read(root/'fixture-001.json')
summary=dict(
    scope=__doc__, physical_access=False, popup_reproduced=True,
    diagnostic_checks_passed=False, ordinary_boot_qualified=False,
    fixture=fixture, launch=launch['cycles'][0], trace_source_sha256=source_sha,
    source_hash_matches=True, trace_events=3, trace_status=trace['status'],
    guest_resumed=True, originating_process=first['owner'], originating_thread=first['thread'],
    hard_error_status=first['arguments'][0], caller=first['caller'], caller_module='win32k.sys',
    caller_review='caller-review.json', popup_record=popup, popup_matches_original=True,
    pending_device=[n for n in runtime['pnp_tree'] if 'VEN_1B36&DEV_0005' in n['InstancePath']],
    workload=dict(mappings=527,exact_final_files=50,absent_intermediates=34,bmp_api_cases=16,
                  timed_rounds=15,required_duration_ms=60000,last_round=work['timed_rounds'][-1]),
    normal_shutdown_count=1, structurally_parsed_hives=5,
    runtime_binary_checks=audit['runtime_binary_checks'],
    cleanup=read(workspace/'work/runs'/launch['run']/'cleanup.json'),
    limits=[
        'Two hard-error entry observations belong to one process/thread and one logged popup.',
        'The exact failing installer is identified for this emulator run only; physical installer identity is unproven.',
        'No creation/resume timing or token-lifetime observation belongs to this minimal trace; do not import the01B4 control ordering.',
        'Matched win32k static code describes a following termination request; that request was not separately traced.',
        'Debugger pauses remain a timing influence; this is not ordinary boot qualification.',
        'Rehearsal is a60-second minimum workload, not a15-minute soak or full allocation audit.',
        'No driver, registry/device policy or installed physical baseline changed; strict failure remains.'])
control_trace=read(root/'002/trace.json')
control_audit=read(root/'002/audit.json')
control_launch=read(root/'002/launch.json')
control_sha=hashlib.sha256((root/'002/trace-source.py').read_bytes()).hexdigest()
assert control_sha==control_trace['trace_source_sha256']
assert control_trace['status']=='reached_kernel_shutdown' and control_trace['guest_resumed']
assert len(control_trace['events'])==312
assert not any('HardError' in e['function'] for e in control_trace['events'])
assert control_audit['diagnostic_checks_passed'] and not control_audit['ordinary_run_valid']
assert not control_audit['popup_records'] and control_audit['normal_shutdown_count']==1
assert control_audit['mapping_checks']==527 and control_audit['probe_completed']
assert control_audit['persistence_passed'] and control_audit['dashboard_return']
assert len(control_launch['cycles'])==1
control_work=control_audit['workload']
assert len(control_work['files'])==50 and all(f['matched'] for f in control_work['files'])
assert len(control_work['deleted_files_absent'])==34 and all(control_work['deleted_files_absent'].values())
assert control_work['paint_api_replay_passed'] and len(control_work['timed_rounds'])==15
assert control_work['timed_rounds'][-1][1]>=60000
assert len(control_audit['hives'])==5 and all(h['parsed'] for h in control_audit['hives'])
assert all(b['matched'] for b in control_audit['runtime_binary_checks'])
events={e['index']:e for e in control_trace['events']}
gpu=events[66]['target']
assert events[66]['function']=='NtResumeThread_BeforeResume'
assert events[66]['owner']['image']=='services.exe'
assert gpu['pid']==828 and gpu['eprocess']=='0xff9df020'
assert 'VEN_10DE&DEV_02A0' in gpu['command_line']
terminate=events[217]
assert terminate['function']=='NtTerminateProcess_AfterReference'
assert terminate['owner']['image']=='csrss.exe'
identity_fields=['pid','eprocess','image','command_line']
# The loader normalizes relative process-parameter pointers after first resume.
assert all(terminate['target'][n]==gpu[n] for n in identity_fields)
assert terminate['arguments'][1]=='0x40010004'
assert events[218]['function']=='_PspExitProcess@8'
assert all(events[218]['target'][n]==gpu[n] for n in identity_fields)
assert events[223]['function']=='_NtCreateProcess@32' and events[223]['owner']['image']=='services.exe'
cleanup=events[227]
late=cleanup['target']
assert cleanup['function']=='NtTerminateProcess_AfterReference'
assert cleanup['owner']['image']=='services.exe' and cleanup['arguments'][1]=='0x5'
assert late['pid']==884 and late['eprocess']=='0xffb3f020'
assert 'VEN_1B36&DEV_0005' in late['command_line']
assert events[228]['function']=='_PspExitProcess@8' and events[228]['target']==late
assert not any(e['function']=='NtResumeThread_BeforeResume' and
               e.get('target',{}).get('eprocess')==late['eprocess'] and
               e.get('target',{}).get('pid')==late['pid'] for e in control_trace['events'])
summary['lifecycle_control']=dict(
    case='002', trace_source_sha256=control_sha, source_hash_matches=True,
    trace_events=len(control_trace['events']), trace_status=control_trace['status'],
    guest_resumed=True, popup_reproduced=False, diagnostic_checks_passed=True,
    ordinary_boot_qualified=False, initial_installer=gpu, late_installer=late,
    selected_events=[events[i] for i in [66,217,218,220,223,227,228,229,311]],
    workload=dict(mappings=527,exact_final_files=50,absent_intermediates=34,
                  bmp_api_cases=16,timed_rounds=15,required_duration_ms=60000,
                  last_round=control_work['timed_rounds'][-1]),
    runtime_binary_checks=control_audit['runtime_binary_checks'],
    structurally_parsed_hives=5, normal_shutdown_count=1,
    cleanup=read(workspace/'work/runs'/control_launch['run']/'cleanup.json'),
    limits=[
        'No hard error occurred in this trace; its clean path does not describe the preceding failing run.',
        'No resume-site hit for the late PID/EPROCESS was observed; this is not proof about every possible thread execution path.',
        'NtCreateProcess entry does not independently identify a resulting child; the subsequent termination target supplies the late installer identity.',
        'Termination argument5 is retained as an argument, not inferred to be the original creation error.',
        'No token-lifetime sites were armed here; do not infer the earlier token race occurred in this run.',
        'A changed debugger schedule is an influence, not a demonstrated explanation for the different outcome.'])
(root/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('Verified reproduced popup and separate clean lifecycle control; original diagnostic remains FAIL.')
