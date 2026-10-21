"""Analyze retained collection only; never reconnect or launch."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn642/physical001')
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import hive
sys.path.insert(0,str(K.parent/'windows480p642'));from result_parser import analyze
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
c=json.loads((K/'collection001.json').read_text());assert c['completed'] and c['hook_removed']
s=json.loads((K/'stage001.json').read_text());out=K/'audit001.json';assert not out.exists()
r=dict(physical=True,closed=True,probe_present=c['probe_present'],protected_unchanged=c['protected_unchanged'],hook_removed=True,hives=[],new_events={},history_preserved=True,full_physical_FATX_allocation_audit=False)
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
log=(P/'after/E/xwn480p642/result.txt').read_bytes() if c['probe_present'] else None
r['probe_analysis']=analyze(log)
if log is not None:assert hashlib.sha256(log).hexdigest()==c['probe']['sha256'];(K/'probe-result001.txt').write_bytes(log)
saved=(P/'after/E/xwn480p642/input.txt').read_bytes() if c.get('input_present') else None
if saved is not None:assert hashlib.sha256(saved).hexdigest()==c['input']['sha256']
r['input_file_matches']=saved in [b'XBOX480',b'XBOX480\r\n']
r['selected_integrity_passed']=r['protected_unchanged'] and all(v['parsed'] for v in r['hives']) and r['history_preserved']
r['scoped_passed']=r['input_file_matches'] and r['probe_analysis']['passed'] and r['selected_integrity_passed'] and r['normal_shutdown_count']==1
r['strict_passed']=r['scoped_passed'] and not r['warnings_errors']
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['probe_present','normal_shutdown_count','selected_integrity_passed','scoped_passed','strict_passed']}))
