"""Audit the bounded physical diagnostic; never waive popup or warning failures."""
import json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];art=k/'artifacts/physical'
t=json.loads((k/'physical.json').read_text());assert t.get('collected_utc') and not t['startup_enabled']
observed=json.loads((k/'physical-observations.json').read_text());events={};known=[]
for label in ['system','application']:
    decoded=[]
    for phase in ['before','after']:
        dest=k/(phase+'-'+label+'-events.json')
        subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(art/(phase+'-'+label+'.evt')),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
        decoded.append(json.loads(dest.read_text())['records'])
    a,b=decoded;by={v['record']:v for v in b};assert all(by.get(v['record'])==v for v in a)
    known.extend(a);boundary=max((v['record'] for v in a),default=0);events[label]=[v for v in b if v['record']>boundary]
def recurring(v):return (v['source'],v['event_id']) in {('Service Control Manager',7000),('Ftdisk',49)} and any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)
errors=[v for group in events.values() for v in group if v['type'] in [1,2] and not recurring(v)]
popups=[v for v in events['system'] if v['source']=='Application Popup']
normal=sum(v['source']=='EventLog' and v['event_id']==6006 for v in events['system'])==1
before=(art/'before-setupapi.log').read_bytes();after=(art/'after-setupapi.log').read_bytes()
prefix=after.startswith(before)
r=dict(scope=__doc__,diagnostic_completed=observed['diagnostic_completed'],physical_result=True,normal_shutdown=normal,new_events=events,unexpected_errors=errors,popups=popups,baseline_checks=t['baseline_checks'],probe_exact=t['probe_exact'],startup_disabled=not t['startup_enabled'],setupapi_preserves_prefix=prefix,new_setupapi=after[len(before):].decode('cp1252',errors='backslashreplace') if prefix else None)
r['strict_run_passed']=observed['diagnostic_completed'] and normal and not errors and not popups and not events['application'] and t['probe_exact'] and all(v['sha256']==v['expected'] for v in t['baseline_checks'].values())
r['limits']='Observation helper, not a driver fix or full storage qualification. No independent post-run allocation/hive audit for this bounded diagnostic. Historical soak gates unchanged.'
(k/'physical-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['diagnostic_completed','normal_shutdown','unexpected_errors','popups','strict_run_passed','new_setupapi']},indent=2))
