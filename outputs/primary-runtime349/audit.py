"""Cold audit of one closed202 joined-helper benchmark; never treat host closure as normal restart."""
import contextlib,subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'video-text-oracle206'))
from common import *
from stock_io002 import readers,scan
k=Path(__file__).resolve().parent;ws=k.parents[1]
from runner_analysis import analyze as runner
from sample_analysis import analyze
from dib_analysis import analyze as dib
from timing_analysis import timing
from window_analysis import window
from text_analysis import analyze as text_analysis
from interval_policy import measurement_events

case=sys.argv[1];mode=1;assert case in ['control001','candidate001'];out=k/case;art=out/'artifacts'
dest=out/'audit.json';assert not dest.exists()
run=Path('/mnt/e/xwn349/runs/nt5-primary349-'+case);assert (run/'cleanup.json').exists()
f=read(out/'fixture.json');base=Path(f['fixture_path_linux']);disk=run/'hdd.qcow2'
assert sha(base)==f['fixture_sha256'] and sha(Path(f['parent']))==f['parent_sha256']
for name,digest in read(out/'emulator-frozen.json').items():assert sha(ws/name.replace(chr(92), chr(47)))==digest,name
r=dict(case=case,physical_access=False,debugger=False,files=[],hives=[],new_events={})
logs={}
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
    names=['attempt.log','wizard201.log','setup-before.log','setup-after.log','audio207.log','state207.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]
    for name in names:
        try:blob=after['E'].read(f['namespace']+'/'+name)
        except KeyError:blob=None
        logs[name]=blob
        if blob is not None:
            p=art/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(blob)
    for name,digest in f['protected'].items():
        v,path=name.split('/',1)
        if path.startswith('winnt/system32/config/') or path in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:continue
        actual=m.sha(after[v].read(path));r['files'].append(dict(path=name,before_sha256=digest,after_sha256=actual,matched=digest==actual))
    r['startup_unchanged']=m.sha(after['E'].read(STARTUP))==f['files']['E/'+STARTUP]
    for name in HIVES:
        p=art/('after-'+name);p.write_bytes(after['E'].read('winnt/system32/config/'+name))
        try:row=hive(p)
        except Exception as exc:row=dict(parsed=False,error=type(exc).__name__)
        r['hives'].append(dict(name=name,**row))
    for phase,rr in [('before',before),('after',after)]:
        (art/(phase+'-setupapi.log')).write_bytes(rr['E'].read('winnt/setupapi.log'))
    r['setupapi_history_preserved']=(art/'after-setupapi.log').read_bytes().startswith((art/'before-setupapi.log').read_bytes())
    r['event_history_preserved']=True
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        pair=[]
        for phase,rr in [('before',before),('after',after)]:
            p=art/(phase+'-'+name);p.write_bytes(rr['E'].read('winnt/system32/config/'+name));d=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(k.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(d)],check=True,stdout=subprocess.DEVNULL)
            pair.append(read(d)['records'])
        a,b=pair;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
attempt='' if logs['attempt.log'] is None else logs['attempt.log'].decode('ascii',errors='backslashreplace')
audio_tags=['AUDIO_STATE_JOIN 0','AUDIO_STATE_EXIT 0','AUDIO_PROBE_JOIN 0','AUDIO_PROBE_EXIT 0']
audio_lines=[v for v in attempt.splitlines() if v.startswith('AUDIO_')]
r['audio_children_joined']=audio_lines==audio_tags
projected='\n'.join(v for v in attempt.splitlines() if not v.startswith('AUDIO_'))
r['boundary_analysis']=runner(projected,[logs['setup-before.log'],logs['setup-after.log']],logs['wizard201.log'],1)
r['setup_gate_passed']=r['boundary_analysis']['idle_branch_passed']
texts=[None if logs['sample%d/gdi-baseline.txt'%i] is None else logs['sample%d/gdi-baseline.txt'%i].decode('ascii',errors='backslashreplace') for i in range(5)]
r['samples']=[analyze(v) for v in texts];r['dib_samples']=[dib(v,0) for v in texts]
r['phase_samples']=[timing(v,mode) for v in texts]
r['window_samples']=[window(v,mode) for v in texts]
r['text_samples']=[text_analysis(v,1) for v in texts]
r['actual_caps']=r['samples'][0]['actual_caps'];r['actual_modes']=r['samples'][0]['actual_modes']
r['caps_consistent']=all(v['actual_caps']==r['actual_caps'] and v['actual_modes']==r['actual_modes'] for v in r['samples'])
r['display_workload_passed']=r['caps_consistent'] and all(v['probe_passed'] and v['copy_checks_passed'] and v['loop_coverage'] and v['counters_passed'] for v in r['samples']) and all(v['passed'] for group in ['dib_samples','phase_samples','window_samples','text_samples'] for v in r[group])
sys.path.insert(0,str(k.parent/'hd-phase344'))
from phase_analysis import analyze as large_phase
r['large_phase_samples']=[large_phase(v,mode) for v in texts]
r['display_workload_passed'] &= all(v['passed'] for v in r['large_phase_samples'])
from primary_analysis import analyze as primary_analysis
r['primary_samples']=[primary_analysis(v,int(case=='candidate001')) for v in texts]
r['display_workload_passed'] &= all(v['passed'] for v in r['primary_samples'])
subprocess.run([sys.executable,str(k/'typed-state.py'),case],check=True);r['typed_state']=read(out/'device-state.json')
scan(disk,art);a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and all(v['parsed'] for v in r['hives']) and all(v['matched'] for v in r['files']) and r['startup_unchanged'] and r['event_history_preserved'] and r['setupapi_history_preserved'] and all(r['typed_state'][n] for n in ['hive_headers_valid','selected_policy_unchanged','no_new_device_disabling'])
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application'] and r['event_history_preserved']
r['measurement_events_passed']=False
if r['setup_gate_passed']:
    interval,inside=measurement_events(attempt,[v for group in r['new_events'].values() for v in group]);r['measurement_events']=inside;r['measurement_interval_unix']=interval;r['measurement_events_passed']=not inside
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['dashboard_return']=read(out/'launch.json')['cycles'][0].get('dashboard_return') is True
r['scoped_display_passed']=r['setup_gate_passed'] and r['display_workload_passed'] and r['integrity_passed'] and r['measurement_events_passed'] and r['normal_shutdown_count']==1 and r['dashboard_return'] and not r['new_events']['application'] and not any(v['source']=='Application Popup' for v in r['new_events']['system'])
r['strict_qualification_passed']=r['scoped_display_passed'] and r['strict_events_passed']
r.update(ordinary_qualified=r['strict_qualification_passed'],physical_qualified=False,performance_qualified=False,
         limits='Ordinary fresh202 joined helper + new204 text bytes/pixels plus retained199 copy/window/clock scope. Whole-boot warnings remain strict failures. No emulator timing implies hardware speed; no physical or release promotion.')
# The audio and video scopes must BOTH pass; neither child can supply restart success.
rows=[] if logs['audio207.log'] is None else [v.split() for v in logs['audio207.log'].decode('ascii').splitlines()]
r['audio_probe_passed']=bool(rows) and rows[-1]==['CHANNEL001_END','6','0'] and rows.count(['CHANNEL001_BEGIN','1','1'])==1
for i in range(6):
    for tag in ['OPEN','PREPARE','WRITE','RESET','UNPREPARE','CLOSE']:
        r['audio_probe_passed'] &= rows.count([tag,str(i),'0'])==1
    for tag,value in [('DONE_AFTER_RESET','1'),('DONE_BEFORE_RESET','1'),('POSITION_RESULT','0'),('POSITION_TYPE','2'),('POSITION_SAMPLES','144000'),('PHASE_MASK',str(i%3+1)),('CYCLE','0')]:
        r['audio_probe_passed'] &= rows.count([tag,str(i),value])==1
state=[] if logs['state207.log'] is None else logs['state207.log'].decode('ascii').splitlines()
r['audio_state_passed']=all(state.count(s)==1 for s in ['ACTUAL_SERVICE xwnaci207','DEVNODE_STATUS_RESULT 0','DEVNODE_PROBLEM 0','TARGET_MODULE_COUNT 1','LEGACY_MODULE_COUNT 0','STATE207_END 0']) and not any('FAIL' in s for s in state)
subprocess.run([sys.executable,str(k/'installed-binding.py'),case],check=True)
r['installed_audio_binding']=read(out/'installed-binding.json')
try:
    subprocess.run([sys.executable,str(k/'analyze-capture.py'),str(run/'ac97-output.wav'),str(out/'capture.json')],check=True)
    r['audio_capture']=read(out/'capture.json')
except Exception as exc:r['audio_capture']=dict(passed=False,error=repr(exc))
r['orderly_host_exit']=read(run/'host-exit.json')['passed']
r['scoped_combined_passed']=r['scoped_display_passed'] and r['audio_children_joined'] and r['audio_probe_passed'] and r['audio_state_passed'] and r['installed_audio_binding']['passed'] and r['audio_capture']['passed'] and r['orderly_host_exit']
r['strict_qualification_passed']=r['scoped_combined_passed'] and r['strict_events_passed']
r['ordinary_qualified']=r['strict_qualification_passed']
r['limits']='New348 primary-copy body: clock category1 measures selected fast/Eng body. New coverage required; original strict warnings retained, no physical speed or release qualification.'
save(dest,r);save(out/'closure.json' ,dict(closed=True,never_relaunch_or_recollect=True,audit_sha256=sha(dest),cleanup_sha256=sha(run/'cleanup.json'),scoped_display_passed=r['scoped_display_passed'],scoped_combined_passed=r['scoped_combined_passed'],strict_qualification_passed=r['strict_qualification_passed'],physical_access=False))
print(json.dumps({n:r[n] for n in ['scoped_display_passed','display_workload_passed','integrity_passed','normal_shutdown_count','warnings_errors']},indent=2))
