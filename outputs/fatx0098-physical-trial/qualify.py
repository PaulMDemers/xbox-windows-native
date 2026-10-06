"""Qualify the bounded physical0098 trial using independent collected evidence."""
import json,subprocess,sys
from physical import k,ws,art,sha,passed,save
trial=json.loads((k/'physical.json').read_text());assert trial.get('collected_utc') and not trial['startup_enabled']
sizes=[1,2,511,512,513,4095,4096,4097,8191,8192,8193,65535,65536,65537,131071,131072,131073]
files=[]
for kind,round in [('input',0),('output',8)]:
    for i,size in enumerate(sizes):
        name=f'{kind}{i:02}.bin';path=art/('after-'+name);data=path.read_bytes() if path.exists() else b''
        files.append(dict(name=name,bytes=len(data),sha256=sha(data),matched=data==bytes((offset*13+i*17+round*29)&255 for offset in range(size))))
path=art/'after-result.log';log=path.read_bytes().decode('ascii') if path.exists() else ''
checks=[line.split() for line in log.splitlines() if line.startswith(('INPUT ','OUTPUT '))]
sequence=[('INPUT',str(i)) for i in range(17)]+[('OUTPUT',str(i)) for _ in range(8) for i in range(17)]
probe_passed=len(checks)==153 and [(v[0],v[1]) for v in checks]==sequence and all(v[2:]==['0','0'] for v in checks) and log.startswith('ATTEMPT_ONCE 17 8 997\r\n') and log.endswith('COMPLETE 0 17 8\r\nNORMAL_RESTART_REQUEST 0 0 0\r\n') and 'FAIL_' not in log
events={};known=[]
for label in ['system','application']:
    decoded=[]
    for phase in ['before','after']:
        source=art/(phase+'-'+label+'.evt');assert sha(source.read_bytes())==(trial['preserved']['before-'+label+'.evt'] if phase=='before' else trial['collected'][label+'.evt'])['sha256']
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
r=dict(scope=__doc__,physical_result=True,probe_passed=probe_passed,mapping_checks=len(checks),files=files,log=log,new_events=events,unexpected_errors=errors,popups=popups,normal_shutdown=normal,baseline_payload_checks=trial['candidate_checks'],rollback_exact=trial['rollback_exact'],probe_unchanged=trial['probe_unchanged'],startup_disabled=not trial['startup_enabled'])
r['workload_and_events_passed']=all([probe_passed,all(v['matched'] for v in files),normal,not errors,not popups,not events['application'],passed(trial['candidate_checks']),r['rollback_exact'],r['probe_unchanged'],r['startup_disabled']])
r['allocation_audit_pending']=not (k/'allocation.json').exists();r['binary_audit_pending']=not (k/'binary-audit.json').exists()
if not r['allocation_audit_pending']:r['allocation']=json.loads((k/'allocation.json').read_text())
if not r['binary_audit_pending']:r['binary_audit']=json.loads((k/'binary-audit.json').read_text())
r['passed']=r['workload_and_events_passed'] and not r['allocation_audit_pending'] and r['allocation']['allocation_consistent'] and not r['binary_audit_pending'] and r['binary_audit'].get('complete',False) and r['binary_audit'].get('passed',False) and r['binary_audit']['checked']==r['binary_audit']['expected_count']==3439 and len(r['binary_audit']['hives'])==9
r['limits']='One bounded physical trial; no long-soak, generic PnP, higher video mode or acceleration qualification. Input slack was not deliberately poisoned on hardware.'
save(r,k/'qualification.json');print(json.dumps({n:r[n] for n in ['probe_passed','mapping_checks','normal_shutdown','unexpected_errors','popups','workload_and_events_passed','allocation_audit_pending','binary_audit_pending','passed']},indent=2))
