"""One cold audit after the single ordinary run; strict baseline errors are not waived."""
import contextlib,subprocess
from common import *
case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;dest=out/'audit.json';assert not dest.exists()
f=read(k/('fixture-'+case+'.json'));pre=read(out/'preflight.json');art=out/'artifacts'
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];disk=ws/('work/runs/nt5-vphys164-'+case+'/hdd.qcow2')
assert (disk.parent/'cleanup.json').exists() and sha(base)==f['fixture_sha256']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
r=dict(case=case,physical_access=False,debugger=False,files=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
    for name in ['attempt.log','gdi-baseline.txt']:
        try:data=after['F'].read('xwnv164/'+name)
        except KeyError:data=None
        if data is not None:(art/name).write_bytes(data)
        r[name]=None if data is None else data.decode('ascii',errors='backslashreplace')
    for row in pre['files']:
        try:actual=m.sha(after[row['volume']].read(row['path']))
        except KeyError:actual=None
        r['files'].append(dict(**row,after_sha256=actual,matched=actual==row['sha256']))
    trace=after['F'].read('winnt/system32/xwn-video-trace.bin');(art/'video-trace.bin').write_bytes(trace)
    initial=before['F'].read('winnt/system32/xwn-video-trace.bin');(art/'before-video-trace.bin').write_bytes(initial)
    r['trace_sha256']=m.sha(trace)
    r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==f['files']['F/'+STARTUP]
    for name in HIVES:
        p=art/('after-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name))
        try:result=hive(p)
        except Exception as exc:result=dict(parsed=False,error=repr(exc))
        r['hives'].append(dict(name=name,**result))
    r['event_history_preserved']=True
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        decoded=[]
        for phase,rr in [('before',before),('after',after)]:
            p=art/(phase+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));d=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(k.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(d)],check=True,stdout=subprocess.DEVNULL)
            decoded.append(read(d)['records'])
        a,b=decoded;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
log=(r['gdi-baseline.txt'] or '').splitlines();rows=[v.split() for v in log]
r['probe_passed']=bool(rows) and rows[0]==['XWN_GDI_PROBE_VERSION','3','256','128'] and rows[-1]==['PASS','0','0','0'] and not any(v[0].startswith(('FAIL','MISMATCH','CANCELLED')) for v in rows)
r['copy_checks_passed']=all(['COPY_stage_pass',str(i),'1','0'] in rows for i in range(4))
r['timed_loops']=[v for v in rows if v[0]=='TIMING_kind_count_ms']
r['loop_coverage']=len(r['timed_loops'])==5 and {int(v[1]) for v in r['timed_loops']}==set(range(5)) and all(1<=int(v[2])<=2000 for v in r['timed_loops'])
r['actual_caps']=[v for v in rows if v[0]=='CAP_index_value'];r['actual_modes']=[v for v in rows if v[0].startswith('MODE_')]
r['runner_normal_restart']=(r['attempt.log'] or '').splitlines()==['ATTEMPT_ONCE','REPLAY_EXIT_ZERO','NORMAL_RESTART_REQUEST']
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application'] and not any(v['source']=='Application Popup' for v in r['new_events']['system']) and r['event_history_preserved']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
launch=read(out/'launch.json');r['dashboard_return']=len(launch['cycles'])==1 and launch['cycles'][0].get('dashboard_return') is True
if not (out/'allocation.json').exists():scan(disk,art)
a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['workload_passed']=r['probe_passed'] and r['copy_checks_passed'] and r['loop_coverage'] and r['runner_normal_restart'] and r['normal_shutdown_count']==1 and r['dashboard_return']
r['integrity_passed']=r['allocation_passed'] and all(v['parsed'] for v in r['hives']) and all(v['matched'] for v in r['files']) and r['startup_unchanged']
r['strict_qualification_passed']=r['workload_passed'] and r['integrity_passed'] and r['strict_events_passed']
r['physical_qualified']=False;r['performance_qualified']=False
r['limits']='Ordinary emulator reconstruction only. Generic v3 guest live checks and cold logs, not independent cold RGB files. Timings descriptive. Captured core/hives preserve physical settings; remaining inherited files/partitions are not a whole-console clone. No baseline warning waiver or physical promotion.'
save(dest,r);print(json.dumps({key:r[key] for key in ['case','workload_passed','integrity_passed','strict_events_passed','strict_qualification_passed','actual_caps','warnings_errors']},indent=2))
