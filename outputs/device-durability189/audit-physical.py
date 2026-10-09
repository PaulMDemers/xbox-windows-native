"""One read-only preserved physical observer/event/hive audit in WSL. No network."""
import subprocess
from common import *
from analyze import analyze
dest=k/'physical-audit.json';assert not dest.exists()
p=read(k/'physical.json');assert p.get('collected_utc') and not p['startup_enabled']
def data(row):
    path=ws/row['path'];assert sha(path)==row['sha256'];return path.read_bytes()
for group in [p['before'],p['after']]:
    for row in group.values():
        if row:data(row)
r=dict(physical_observation=True,physical_qualified=False,ordinary_qualified=False,hives=[],new_events={},manual_restart_method_verified=False)
log=p['after']['observer.log'];assert log is not None
observed=analyze(data(log));save(k/'physical-observation.json',observed);r['observer_completed']=observed['completed']
for phase in ['before','after']:
    for name in HIVES:
        path=ws/p[phase][name]['path'];r['hives'].append(dict(phase=phase,name=name,**hive(path)))
r['event_history_preserved']=True
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
    decoded=[]
    for phase in ['before','after']:
        path=ws/p[phase][name]['path'];d=k/(phase+'-physical-'+label+'-events.json')
        subprocess.run([sys.executable,str(k.parent/'native-windows-physical-f/decode-legacy-events.py'),str(path),'--output',str(d)],check=True,stdout=subprocess.DEVNULL);decoded.append(read(d)['records'])
    a,b=decoded;by={v['record']:v for v in b};r['event_history_preserved'] &= all(by.get(v['record'])==v for v in a)
    boundary=max((v['record'] for v in a),default=0);r['new_events'][label]=[v for v in b if v['record']>boundary]
a=data(p['before']['setupapi.log']);b=data(p['after']['setupapi.log']);r['setupapi_history_preserved']=b.startswith(a)
if b.startswith(a):(k/'artifacts/physical/setupapi-delta.txt').write_text(b[len(a):].decode('cp1252',errors='backslashreplace'),encoding='utf-8')
r['protected_exact']=all(row['sha256']==p['before'][row['path']]['sha256'] for row in p['after_checks'])
r['startup_restored']=data(p['after']['startup.cmd'])==data(p['before']['startup.cmd']) and p['startup_backup_exact']
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
r['strict_events_passed']=r['event_history_preserved'] and not r['warnings_errors'] and not r['new_events']['application']
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['diagnostic_usable']=r['observer_completed'] and r['protected_exact'] and r['startup_restored'] and p['helper_exact'] and all(v['parsed'] for v in r['hives']) and r['event_history_preserved'] and r['setupapi_history_preserved']
r['strict_qualification_passed']=False
r['limits']='Live physical diagnostic only; no full raw allocation audit, no performance pair, no driver/policy action or release promotion. All warnings/popups remain evidence. Manual restart method requires user observation.'
save(dest,r);save(k/'physical-closure.json',dict(closed=True,audit_sha256=sha(dest),never_relaunch_or_recollect=True,diagnostic_usable=r['diagnostic_usable'],physical_qualified=False))
print('Preserved physical188 observation audit',r['diagnostic_usable'],'strict events',r['strict_events_passed'])
