"""Qualify the bounded physical0098 trial using independent collected evidence."""
import json,subprocess,sys
from physical import k,ws,art,sha,passed,save
trial=json.loads((k/'physical.json').read_text());assert trial.get('collected_utc') and not trial['startup_enabled']
from workload import verify
workload=verify(lambda name:(art/('after-'+name)).read_bytes() if (art/('after-'+name)).exists() else None,(k/'artifacts/scribble.bmp').read_bytes(),60000)
files=workload['files'];log=workload['log'];probe_passed=workload['passed'];checks=range(workload['mapping_checks'])
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
r=dict(scope=__doc__,workload=workload,physical_result=True,probe_passed=probe_passed,mapping_checks=len(checks),files=files,log=log,new_events=events,unexpected_errors=errors,popups=popups,normal_shutdown=normal,baseline_payload_checks=trial['candidate_checks'],rollback_exact=trial['rollback_exact'],probe_unchanged=trial['probe_unchanged'],startup_disabled=not trial['startup_enabled'])
r['workload_and_events_passed']=all([probe_passed,all(v['matched'] for v in files),normal,not errors,not popups,not events['application'],passed(trial['candidate_checks']),r['rollback_exact'],r['probe_unchanged'],r['startup_disabled']])
r['allocation_audit_pending']=not (k/'allocation.json').exists();r['binary_audit_pending']=not (k/'binary-audit.json').exists()
if not r['allocation_audit_pending']:r['allocation']=json.loads((k/'allocation.json').read_text())
if not r['binary_audit_pending']:r['binary_audit']=json.loads((k/'binary-audit.json').read_text())
r['passed']=r['workload_and_events_passed'] and not r['allocation_audit_pending'] and r['allocation']['allocation_consistent'] and not r['binary_audit_pending'] and r['binary_audit'].get('complete',False) and r['binary_audit'].get('passed',False) and r['binary_audit']['checked']==r['binary_audit']['expected_count']==3439 and len(r['binary_audit']['hives'])==9
r['limits']='One serial 15-minute physical soak and Paint API replay; actual Paint UI observations separate. No concurrent mapped truncation, generic PnP, higher video mode or acceleration qualification.'
r['helper_checks']=trial['helper_checks']
r['passed']=r['passed'] and all(r['helper_checks'].values()) and all(h['tree']['passed'] and h['matching_sequences'] and h['checksum_valid'] for h in r.get('binary_audit',{}).get('hives',[]))
save(r,k/'qualification.json');print(json.dumps({n:r[n] for n in ['probe_passed','mapping_checks','normal_shutdown','unexpected_errors','popups','workload_and_events_passed','allocation_audit_pending','binary_audit_pending','passed']},indent=2))
