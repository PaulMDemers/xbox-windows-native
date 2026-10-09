"""One complete cold197 ordinary pending audit after owned closure; no event waiver."""
import contextlib,subprocess
from common import *
from sample_analysis import analyze
from dib_analysis import analyze as analyze_dib
from boundary_analysis import analyze as analyze_boundary
case=sys.argv[1];assert case in ['pending001'];out=k/case;dest=out/'audit.json';assert not dest.exists()
f=read(k/('fixture-'+case+'.json'));run=ws/('work/runs/nt5-pending197-'+case);assert (run/'cleanup.json').exists()
base=Path(f['fixture_path_linux']);disk=run/'hdd.qcow2';assert sha(base)==f['fixture_sha256']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
for name,digest in read(k/'frozen-inputs.json').items():assert sha(ws/name)==digest,name
art=out/'artifacts';art.mkdir(exist_ok=True);r=dict(case=case,physical_access=False,debugger=False,files=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
    for name,digest in f['protected'].items():
        volume,path=name.split('/',1);actual=m.sha(after[volume].read(path));r['files'].append(dict(path=name,before_sha256=digest,after_sha256=actual,matched=actual==digest))
    r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==f['files']['F/'+STARTUP]
    logs={};snapshots=[]
    for name in ['attempt.log']+['sample%d/gdi-baseline.txt'%i for i in range(5)]+['setup-before.log','setup-after.log']:
        try:data=after['F'].read('xwnpre194/'+name)
        except KeyError:data=None
        if data is not None:
            assert len(data)<=4*1024*1024
            path=art/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        if name.startswith('setup-'):snapshots.append(data)
        logs[name]=None if data is None else data.decode('ascii',errors='backslashreplace')
    r['logs']=logs
    for name in HIVES:
        path=art/('after-'+name);path.write_bytes(after['F'].read('winnt/system32/config/'+name))
        try:result=hive(path)
        except Exception as exc:result=dict(parsed=False,error=repr(exc))
        r['hives'].append(dict(name=name,**result))
    setup=[rr['F'].read('winnt/setupapi.log') for rr in [before,after]]
    for phase,data in zip(['before','after'],setup):(art/(phase+'-setupapi.log')).write_bytes(data)
    r['setupapi_history_preserved']=setup[1].startswith(setup[0]);r['setupapi_unchanged']=setup[1]==setup[0]
    r['event_history_preserved']=True
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        decoded=[]
        for phase,rr in [('before',before),('after',after)]:
            path=art/(phase+'-'+name);path.write_bytes(rr['F'].read('winnt/system32/config/'+name));d=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(k.parent/'native-windows-physical-f/decode-legacy-events.py'),str(path),'--output',str(d)],check=True,stdout=subprocess.DEVNULL);decoded.append(read(d)['records'])
        a,b=decoded;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
    (art/'after-video-trace.bin').write_bytes(after['F'].read('winnt/system32/xwn-video-trace.bin'))
lines=(logs['attempt.log'] or '').splitlines();r['attempt_lines']=lines
r['boundary_analysis']=analyze_boundary(logs['attempt.log'],snapshots)
r['samples']=[analyze(logs.get('sample%d/gdi-baseline.txt'%i)) for i in range(5)]
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
launch=read(out/'launch.json');r['dashboard_return']=len(launch['cycles'])==1 and launch['cycles'][0].get('dashboard_return') is True
if case=='pending001':
    r['pending_branch_passed']=r['boundary_analysis']['pending_branch_passed'] and all(logs['sample%d/gdi-baseline.txt'%i] is None for i in range(5)) and r['normal_shutdown_count']==0 and not r['dashboard_return']
    r['workload_passed']=r['pending_branch_passed'];r['idle_branch_passed']=False
else:
    r['dib_samples']=[analyze_dib(logs.get('sample%d/gdi-baseline.txt'%i),1) for i in range(5)]
    r['checkpoint_history_preserved']=all(v is not None and v.startswith(setup[0]) and setup[1].startswith(v) for v in snapshots)
    r['idle_branch_passed']=r['boundary_analysis']['idle_branch_passed'] and r['checkpoint_history_preserved'] and all(v['probe_passed'] and v['copy_checks_passed'] and v['loop_coverage'] for v in r['samples']) and all(v['passed'] for v in r['dib_samples']) and r['normal_shutdown_count']==1 and r['dashboard_return']
    r['workload_passed']=r['idle_branch_passed'];r['pending_branch_passed']=False
scan(disk,art);a=read(out/'allocation.json');r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and all(v['matched'] for v in r['files']) and all(v['parsed'] for v in r['hives']) and r['startup_unchanged'] and r['event_history_preserved'] and r['setupapi_history_preserved']
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
r['diagnostic_usable']=r['workload_passed'] and r['integrity_passed']
r['ordinary_qualified']=False and r['diagnostic_usable'] and r['strict_events_passed']
r['physical_qualified']=False;r['performance_qualified']=False
r['limits']='Unobserved pending refusal coverage, not completed boot/restart or ordinary whole-boot qualification. Independent helper branches, not a matched performance pair. Pending host closure never normal shutdown. Idle retains settled emulator-only unused policy/115 display; no physical install or waiver. Polling is observational and cannot exclude unseen installer activity.'
save(dest,r);save(out/'closure.json',dict(closed=True,never_relaunch_or_recollect=True,audit_sha256=sha(dest),cleanup_sha256=sha(run/'cleanup.json'),diagnostic_usable=r['diagnostic_usable'],ordinary_qualified=r['ordinary_qualified'],physical_access=False))
print(json.dumps({v:r[v] for v in ['case','workload_passed','integrity_passed','diagnostic_usable','ordinary_qualified','normal_shutdown_count','warnings_errors']},indent=2))
