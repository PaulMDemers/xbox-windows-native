"""Analyze retained collection only; never reconnect or launch."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn654/physical001')
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import hive
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
c=json.loads((K/'collection001.json').read_text());assert c['completed'] and not c['test_hook']
s=json.loads((K/'preparation001.json').read_text());out=K/'audit001.json';assert not out.exists()
r=dict(physical=True,closed=True,protected_unchanged=c['protected_unchanged'],test_hook=False,hives=[],new_events={},history_preserved=True,full_physical_FATX_allocation_audit=False)
for phase,rows in [('before',s['before']),('after',c['after'])]:
 for n,v in rows.items():assert sha(P/phase/n.lstrip('/'))==v['sha256'],n
for name in ['system','software','sam','security','default']:
 r['hives'].append(dict(name=name,**hive(P/'after/E/winnt/system32/config'/name)))
for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
 records=[]
 for phase in ['before','after']:
  src=P/phase/'E/winnt/system32/config'/name;dest=P/(phase+'-'+label+'.json');assert not dest.exists()
  subprocess.run([sys.executable,str(W/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(src),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
  records.append(json.loads(dest.read_text())['records'])
 before,after=records;by={v['record']:v for v in after};r['history_preserved'] &= all(by.get(v['record'])==v for v in before)
 boundary=max((v['record'] for v in before),default=0);r['new_events'][label]=[v for v in after if v['record']>boundary]
r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
r['warnings_errors']=[v for group in r['new_events'].values() for v in group if v['type'] in [1,2]]
saved=(P/'after/E/xwn480p642/input.txt').read_bytes()
r['saved_file_matches']=saved in [b'XBOX480',b'XBOX480\r\n']
r['selected_integrity_passed']=r['saved_file_matches'] and r['protected_unchanged'] and all(v['parsed'] for v in r['hives']) and r['history_preserved']
r['normal_restart_and_integrity_passed']=r['selected_integrity_passed'] and r['normal_shutdown_count']==1
r['desktop_observation_required_separately']=True
r['strict_passed']=r['normal_restart_and_integrity_passed'] and not r['warnings_errors']
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['normal_shutdown_count','selected_integrity_passed','normal_restart_and_integrity_passed','strict_passed']}))
