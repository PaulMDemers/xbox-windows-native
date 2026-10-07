"""Strict physical0101 concurrency qualification; no warning or popup waiver."""
import json,subprocess,sys
from physical import k,ws,art,sha,passed,save
from workload import verify_log
trial=json.loads((k/'physical.json').read_text());assert trial.get('collected_utc') and not trial['startup_enabled']
for name,entry in trial['collected'].items():
    if entry is not None:assert sha((art/('after-'+name)).read_bytes())==entry['sha256']
log=(art/'after-probe.log').read_text() if trial['collected']['probe.log'] else ''
workload,elapsed_ms=verify_log(log)
files=[]
for name,factor,offset in [('worker0.bin',13,499*29),('worker1.bin',13,17+499*29),('meta.bin',19,499*31)]:
    data=(art/('after-'+name)).read_bytes() if trial['collected'][name] else None
    files.append(dict(name=name,exact=data==bytes((i*factor+offset)&255 for i in range(4097)),sha256=sha(data) if data is not None else None))
events={};known=[]
for label in ['system','application']:
    decoded=[]
    for phase in ['before','after']:
        source=art/(phase+'-'+label+'.evt');entry=(trial['preserved']['before-'+label+'.evt'] if phase=='before' else trial['collected'][label+'.evt']);assert sha(source.read_bytes())==entry['sha256']
        dest=k/(phase+'-'+label+'-events.json')
        subprocess.run([sys.executable,str(ws/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(source),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
        decoded.append(json.loads(dest.read_text())['records'])
    before,after=decoded;by={v['record']:v for v in after};assert all(by.get(v['record'])==v for v in before)
    known.extend(before);boundary=max((v['record'] for v in before),default=0);events[label]=[v for v in after if v['record']>boundary]
def recurring(v):return (v['source'],v['event_id']) in {('Service Control Manager',7000),('Ftdisk',49)} and any(all(v[n]==old[n] for n in ['source','event_id','type','strings','data_hex']) for old in known)
errors=[v for group in events.values() for v in group if v['type'] in [1,2] and not recurring(v)]
popups=[v for v in events['system'] if v['source']=='Application Popup']
start=[v for v in events['system'] if v['source']=='EventLog' and v['event_id']==6005];stop=[v for v in events['system'] if v['source']=='EventLog' and v['event_id']==6006]
normal=len(start)==len(stop)==1 and start[0]['record']<stop[0]['record']
allocation=json.loads((k/'allocation.json').read_text()) if (k/'allocation.json').exists() else {}
binary=json.loads((k/'binary-audit.json').read_text()) if (k/'binary-audit.json').exists() else {}
ret=json.loads((k/'windows-return.json').read_text()) if (k/'windows-return.json').exists() else {}
gates=dict(workload=workload,exact_files=all(v['exact'] for v in files),intermediate_absent=trial['collected']['meta.tmp'] is None,normal_shutdown=normal,dashboard_return=ret.get('dashboard_return',False),strict_events=not errors and not popups and not events['application'],payload=passed(trial['candidate_checks']),rollback=trial['rollback_exact'],probe=trial['probe_unchanged'],startup_disabled=not trial['startup_enabled'],allocation=bool(allocation.get('capture_complete') and allocation.get('allocation_consistent') and not allocation.get('errors') and not allocation.get('orphan_cluster_count')),binary_audit=bool(binary.get('complete') and binary.get('passed') and binary.get('checked')==binary.get('expected_count')==3439 and len(binary.get('hives',[]))==9 and all(h['tree']['passed'] and h['matching_sequences'] and h['checksum_valid'] for h in binary.get('hives',[]))))
r=dict(scope=__doc__,physical_result=True,passed=all(gates.values()),gates=gates,log=log,files=files,new_events=events,unexpected_errors=errors,popups=popups,elapsed_ms=elapsed_ms,allocation_pending=not allocation,binary_audit_pending=not binary.get('complete',False),limits='One five-worker500-round physical test, not the15-minute mapping soak, Paint UI, generic PnP, arbitrary mapped truncation or video qualification. Earlier strict physical failures remain preserved.')
save(r,k/'qualification.json');print(json.dumps({n:r[n] for n in ['passed','gates','elapsed_ms','unexpected_errors','popups']},indent=2))
