"""Bind recorder evidence to executed source, fixed sites and cold audit results."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build.json');r=read(k/'002/events.json');pair=read(k/'comparison.json')
assert b['built'] and b['borrowed_sources_restored']
for path,key in [('recorder.c.inc','recorder_source_sha256'),('xwn-sites.h','sites_header_sha256'),('recorder.patch','patch_sha256')]:
    assert sha(k/path)==b[key]
assert sha(k/'artifacts/xemu-events.exe')==b['binary_sha256']
assert r['kernel_shutdown_observed'] and r['invalid_site_records']==0 and r['record_count']<r['capacity']
assert not (k/'001/events.bin').exists()
for row in pair['cases']:
    assert row['emulator_sha256']==b['binary_sha256']
    assert row['idle_ms']==120000 and row['normal_shutdown_count']==1 and row['dashboard_return']
    assert row['installation_checks_passed'] and row['allocation_consistent'] and row['orphan_clusters']==0
    assert row['payload_hashes_match'] and row['runtime_hashes_match'] and row['structural_hives']==5
    assert not row['popup_records'] and not row['unexpected_errors']
    assert len(row['launch'])==1
    assert (ws/('work/runs/nt5-native-event-recorder-'+row['case']+'/cleanup.json')).exists()
es=r['events']
gpu_term=es[326];gpu_exit=es[328];wait=es[330]
call=es[331];control=es[333];term=es[337];returned=es[338];exit_entry=es[339]
assert gpu_term['target']==gpu_exit['target']==gpu_exit['owner']
assert '10DE&DEV_02A0' in gpu_term['target_command']
assert wait['site']=='PnP_Wait_return' and wait['registers']['eax']=='0x0'
assert call['site']=='PnP_Create_call' and '1B36&DEV_0005' in call['installer_command']
assert control['site']=='PnP_Control_entry' and control['stack'][1]=='0x5'
assert call['thread']!=control['thread'] and call['owner']==control['owner']
assert term['site']=='NtTerminateProcess_AfterReference' and '1B36&DEV_0005' in term['target_command']
assert returned['site']=='PnP_Create_return' and returned['registers']['eax']=='0x0' and returned['last_error']==6
assert call['saved_token']=='0x8dc' and returned['saved_token']=='0x0'
assert exit_entry['site']=='_PspExitProcess@8' and exit_entry['stack'][1]=='0x1'
assert term['target']==exit_entry['target']==exit_entry['owner']
assert not any(e['site']=='NtResumeThread_BeforeResume' and e.get('target')==term['target'] for e in es)
# An earlier, different process uses the same PID. Never correlate by PID alone.
assert es[334]['target_pid']==term['target_pid'] and es[334]['target']!=term['target']
selected=[gpu_term,gpu_exit,wait,call,control,term,returned,exit_entry,es[-1]]
report=dict(scope=__doc__,evidence_consistent=True,physical_access=False,popup_fixed=False,
    raw_trace_sha256=sha(k/'002/events.bin'),record_count=r['record_count'],all_retained_sites_verified=True,
    unknown_owner_commands=sum('command' not in e for e in es),kernel_shutdown_observed=True,
    events=selected,process_identity=term['target'],pid=term['target_pid'],
    prior_same_pid_other_process=dict(index=334,pid=es[334]['target_pid'],process=es[334]['target']),
    conclusions=[
        'The enabled recorder observed a clean comparison path, not the earlier popup path.',
        'CSRSS requested termination of the GPU installer; exit handling and a successful process wait precede the next installation attempt.',
        'The placeholder-device create attempt overlaps PnP service control 5 on another thread.',
        'Termination is requested before create returns false/error6; matching-process exit handling is observed afterward.',
        'No resume-site record names the matching placeholder EPROCESS. This is a bounded observation, not a general proof that the process never ran.',
        'The saved token changes from 0x8dc to zero; CloseHandle was not captured, so token closure is not directly proved here.',
        'No hard-error record and no new cold popup were observed.',
    ],
    limits='One disabled/enabled pair on a new emulator build. No zero-overhead claim, universal causality, full GUI-shutdown ordering or physical qualification.')
(k/'evidence-review.json').write_text(json.dumps(report,indent=2)+'\n')
print({n:report[n] for n in ['evidence_consistent','record_count','unknown_owner_commands','popup_fixed']})
