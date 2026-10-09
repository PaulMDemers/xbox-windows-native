"""One cold diagnostic audit after owned closure; never count host stop as normal shutdown."""
import contextlib,subprocess
from common import *
from analyze201 import analyze
out=k/'observe002';dest=out/'audit.json';assert not dest.exists()
run=ws/'work/runs/nt5-wizard201-observe002';assert (run/'cleanup.json').exists()
f=read(k/'fixture-observe002.json');base=Path(f['fixture_path_linux']);disk=run/'hdd.qcow2'
assert sha(base)==f['fixture_sha256']
for row in f['parents']:assert sha(Path(row['path']))==row['sha256']
for name,digest in read(k/'frozen-observe002.json').items():assert sha(ws/name)==digest,name
art=out/'artifacts';art.mkdir(exist_ok=True);r=dict(physical_access=False,debugger=False,files=[],hives=[],new_events={})
with contextlib.ExitStack() as stack:
    before,after=[readers(stack.enter_context(ColdIO(p)),p) for p in [base,disk]]
    try:data=after['F'].read('xwnwiz201/wizard201.log')
    except KeyError:data=None
    if data is not None:
        (art/'observer.log').write_bytes(data);r['observer_sha256']=m.sha(data)
        try:observed=analyze(data);save(out/'observation.json',observed);r['observer_completed']=observed['passive_observation_passed']
        except Exception as exc:r.update(observer_completed=False,parser_error=repr(exc))
    else:r.update(observer_completed=False,observer_absent=True)
    try:startup_result=after['F'].read('xwnwiz201/startup-result.txt')
    except KeyError:startup_result=None
    if startup_result is not None:(art/'startup-result.txt').write_bytes(startup_result)
    r['actual_helper_exit15']=startup_result is not None and startup_result.strip()==b'WIZARD_EXIT 15'
    r['startup_unchanged']=m.sha(after['F'].read(STARTUP))==f['files']['F/'+STARTUP]
    for name,digest in f['protected'].items():
        v,path=name.split('/',1)
        if path.startswith('winnt/system32/config/') or path in ['winnt/setupapi.log','winnt/system32/xwn-video-trace.bin']:continue
        actual=m.sha(after[v].read(path));r['files'].append(dict(path=name,before_sha256=digest,after_sha256=actual,matched=actual==digest))
    for name,row in read(k/'build-review.json')['providers'].items():
        path='winnt/system32/'+name;actual=m.sha(after['F'].read(path));r['files'].append(dict(path='F/'+path,before_sha256=row['sha256'],after_sha256=actual,matched=actual==row['sha256']))
    for name in HIVES:
        p=art/('after-'+name);p.write_bytes(after['F'].read('winnt/system32/config/'+name))
        try:result=hive(p)
        except Exception as exc:result=dict(parsed=False,error=repr(exc))
        r['hives'].append(dict(name=name,**result))
    for phase,rr in [('before',before),('after',after)]:
        (art/(phase+'-setupapi.log')).write_bytes(rr['F'].read('winnt/setupapi.log'))
    a=(art/'before-setupapi.log').read_bytes();b=(art/'after-setupapi.log').read_bytes()
    r['setupapi_history_preserved']=b.startswith(a)
    if b.startswith(a):(art/'setupapi-delta.txt').write_text(b[len(a):].decode('cp1252',errors='backslashreplace'),encoding='utf-8')
    r['event_history_preserved']=True
    for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
        decoded=[]
        for phase,rr in [('before',before),('after',after)]:
            p=art/(phase+'-'+name);p.write_bytes(rr['F'].read('winnt/system32/config/'+name));d=out/(phase+'-'+label+'-events.json')
            subprocess.run([sys.executable,str(k.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(d)],check=True,stdout=subprocess.DEVNULL);decoded.append(read(d)['records'])
        a,b=decoded;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
        boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
scan(disk,art);a=read(out/'allocation.json')
r['allocation_passed']=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count']
r['integrity_passed']=r['allocation_passed'] and all(v['parsed'] for v in r['hives']) and all(v['matched'] for v in r['files']) and r['setupapi_history_preserved'] and r['event_history_preserved']
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=not r['warnings_errors'] and not r['new_events']['application']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r.update(diagnostic_usable=r['observer_completed'] and r['actual_helper_exit15'] and r['startup_unchanged'] and r['integrity_passed'],ordinary_qualified=False,physical_qualified=False,strict_qualification_passed=False,
    closure='Bounded owned host termination expected; observer never requests guest shutdown. This is tool validation, not ordinary/persistence/performance qualification.')
save(dest,r)
save(out/'closure.json',dict(closed=True,never_relaunch_or_recollect=True,cleanup_sha256=sha(run/'cleanup.json'),audit_sha256=sha(dest),frozen_inputs_checked=len(read(k/'frozen-observe002.json')),diagnostic_usable=r['diagnostic_usable'],ordinary_qualified=False,physical_access=False))
print(json.dumps({v:r[v] for v in ['observer_completed','integrity_passed','diagnostic_usable','normal_shutdown_count','warnings_errors']},indent=2))
