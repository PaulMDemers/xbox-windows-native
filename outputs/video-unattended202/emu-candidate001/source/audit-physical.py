"""Preserved265-pixel/phase/real-window physical observation; strict event errors remain failures."""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
base=Path(__file__).resolve().parent;ws=base.parents[1]
case=sys.argv[1];assert case in ['control001','candidate001'];k=base/case;art=k/'artifacts/physical'
dest=k/'physical-audit.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
r=read(k/'physical.json');assert r.get('collected_utc') and r['baseline_restored'] and not r['startup_enabled']
result=dict(scope=__doc__,physical_result=True,strict_qualification_passed=False,release_qualified=False,
    full_storage_qualified=False,new_events={},event_history_preserved=True)
result['preserved_files_exact']=all(row is None or sha((ws/row['path']).read_bytes())==row['sha256']
    for group in [r['before'],r['after'],r['before_payloads']] for row in group.values())
for label,filename in [('system','sysevent.evt'),('application','appevent.evt')]:
    pair=[]
    for phase in ['before','after']:
        output=k/(phase+'-physical-'+label+'-events.json');assert not output.exists()
        subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),
            str(art/(phase+'-'+filename)),'--output',str(output)],check=True,stdout=subprocess.DEVNULL)
        pair.append(read(output)['records'])
    before,after=pair;by={v['record']:v for v in after}
    result['event_history_preserved'] &= all(by.get(v['record'])==v for v in before)
    boundary=max((v['record'] for v in before),default=0)
    result['new_events'][label]=[v for v in after if v['record']>boundary]
result['warnings_errors']=[v for group in result['new_events'].values() for v in group if v['type'] in [1,2]]
sys.path.insert(0,str(base));from runner_analysis import analyze as boundary_analyze
from interval_policy import documented_only, measurement_events
from sample_analysis import analyze;from dib_analysis import analyze as rows_analyze
from timing_analysis import timing
from window_analysis import window
logs=[None if r['after']['sample%d'%i] is None else (art/('after-sample%d'%i)).read_bytes().decode('ascii') for i in range(5)]
samples=[analyze(v) for v in logs];dib=[rows_analyze(v,0) for v in logs]
phases=[timing(v,int(case=='candidate001')) for v in logs]
windows=[window(v,int(case=='candidate001')) for v in logs]
attempt='' if r['after']['attempt.log'] is None else (art/'after-attempt.log').read_bytes().decode('ascii')
checkpoint_rows=[r['after'].get(name) for name in ['setup-before.log','setup-after.log']]
snapshots=[None if row is None else (ws/row['path']).read_bytes() for row in checkpoint_rows]
wizard_row=r['after'].get('wizard201.log');wizard=None if wizard_row is None else (ws/wizard_row['path']).read_bytes()
boundary=boundary_analyze(attempt,snapshots,wizard,0)
setup_gate_passed=boundary['idle_branch_passed']
result['boundary_analysis']=boundary
result['setup_gate_passed']=setup_gate_passed
boot_before=(art/'before-setupapi.log').read_bytes();boot_after=(art/'after-setupapi.log').read_bytes()
result['setupapi_history_preserved']=boot_after.startswith(boot_before)
result['checkpoint_history_preserved']=all(v is not None and v.startswith(boot_before) and boot_after.startswith(v) for v in snapshots)
result['measurement_events']=[]
if setup_gate_passed:
    interval,inside=measurement_events(attempt,[v for group in result['new_events'].values() for v in group])
    result['measurement_interval_unix']=interval
    result['measurement_event_margin_seconds']=1
    result['measurement_events']=inside
result['measurement_events_passed']=setup_gate_passed and not result['measurement_events']
result.update(samples=samples,row_samples=dib,phase_samples=phases,window_samples=windows,
    phase_coverage_passed=all(v['passed'] for v in phases),window_coverage_passed=all(v['passed'] for v in windows),runner_log=attempt,
    probe_passed=all(v['probe_passed'] for v in samples),
    pixel_checks_passed=all(v['copy_checks_passed'] for v in samples) and all(v['passed'] for v in dib),
    counters_passed=all(v['counters_passed'] for v in samples) and all(v['passed'] for v in dib),
    loop_coverage=all(v['loop_coverage'] for v in samples),
    actual_caps=samples[0]['actual_caps'],actual_modes=samples[0]['actual_modes'],
    normal_restart_requested=setup_gate_passed,
    normal_shutdown_count=sum(v['source']=='EventLog' and v['event_id']==6006 for v in result['new_events']['system']),
    dashboard_return=read(k/'physical-return.json')['dashboard_return'])
emu=read(base/('emu-'+case)/'audit.json')
result['caps_consistent']=all(v['actual_caps']==result['actual_caps'] and v['actual_modes']==result['actual_modes'] for v in samples)
result['matched_emulator_geometry']=result['actual_caps']==emu['actual_caps'] and result['actual_modes']==emu['actual_modes']
package=read(base/'package-review.json')
result['deployed_payloads_exact']=all(r['after'][v['target'].rsplit('/',1)[1]]['sha256']==v['sha256'] for v in package['cases'][case])
expected={('/'+v['target']):v['sha256'] for v in package['cases'][case]}
result['protected_files_exact']=all(r['after'][name]['sha256']==expected.get(name.removeprefix('protected:'),row['sha256'])
    for name,row in r['before'].items() if name.startswith('protected:'))
result['setupapi_unchanged']=r['before']['setupapi.log']['sha256']==r['after']['setupapi.log']['sha256']
trace=(art/'after-trace.bin').read_bytes();assert len(trace)==4096 and trace[:16]==b'XWN-VID-TRACE01\n'
count,dropped=struct.unpack_from('<II',trace,16);assert count<=254
result['trace_records']=count;result['trace_dropped']=dropped
result['shared_events']=[list(struct.unpack_from('<4I',trace,32+i*16)) for i in range(count)
    if struct.unpack_from('<I',trace,32+i*16)[0] in [0x30,0x31,0x32]]
acquires=[v for v in result['shared_events'] if v[0]==0x30]
result['shared_acquire_success']=bool(acquires) and dropped==0 and all(v[1]==0 and v[2]>=0x80000000 and v[2]%4096==0 and v[3]>0 for v in acquires) and all(v[1]==0 for v in result['shared_events'])
fields=['source','event_id','type','strings','data_hex'];signature=lambda v:{f:v[f] for f in fields}
expected_errors=read(base/'physical-ready.json')['documented_physical_warning_signatures']
actual_signatures=[signature(v) for v in result['warnings_errors']]
result['warnings_are_documented_baseline_only']=documented_only(result['warnings_errors'],expected_errors)
result['documented_physical_warning_signatures']=expected_errors
result['strict_error_waiver']=False
result['strict_events_passed']=result['event_history_preserved'] and not result['warnings_errors'] and not result['new_events']['application'] and not any(v['source']=='Application Popup' for v in result['new_events']['system'])
result['workload_passed']=all(result[n] for n in ['caps_consistent','matched_emulator_geometry','probe_passed','pixel_checks_passed','counters_passed','loop_coverage','phase_coverage_passed','window_coverage_passed','normal_restart_requested','dashboard_return']) and result['normal_shutdown_count']==1
result['wizard_helper_exact']=all(r['after'][name]['sha256']==package['helpers'][source] for name,source in [('wizard.exe','wizard.exe'),('runner.exe','runner.exe'),('replay.exe','gdi-probe.exe')])
result['scoped_display_passed']=result['wizard_helper_exact'] and all(result[n] for n in ['workload_passed','preserved_files_exact','event_history_preserved','deployed_payloads_exact','protected_files_exact','setupapi_history_preserved','checkpoint_history_preserved','measurement_events_passed','shared_acquire_success']) and not result['new_events']['application'] and not any(v['source']=='Application Popup' for v in result['new_events']['system'])
result['pixel_copy_checks']=265 if result['pixel_checks_passed'] and result['window_coverage_passed'] else None
result['limits']='Profile OFF/ON synchronous GDI plus actual window observation, scalar OFF both, not desktop FPS, new modes, release, crash-dump or full physical storage qualification. Strict Ft49 failure is preserved. Both temporary display chains restored. All boot warnings stay strict failures; explicit interval gates do not override193 or establish release qualification.'
dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:result[n] for n in ['scoped_display_passed','workload_passed','pixel_copy_checks','strict_events_passed','warnings_errors']},indent=2))
