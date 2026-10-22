"""Audit659 retained before/after bytes once; no connection, collection or launch."""
import datetime,hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('/mnt/c/xwn659/physical001')
sys.path.insert(0,str(K.parent/'video-text-oracle206'));from common import hive
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((K/'collection001.json').read_text());assert c['completed'] and not c['test_hook']
s=json.loads((K/'preparation001.json').read_text());out=K/'audit001.json';assert not out.exists()
r=dict(completed=False,physical_collection=True,scope='Selected-file/hive/event audit; no full physical FATX allocation audit',source_sha256=sha(Path(__file__)),test_hook=False,hives=[],new_events={},history_preserved=True,expected_windows_run=False,expected_normal_windows_restart=False)
def save():out.write_text(json.dumps(r,indent=2)+'\n')
save()
try:
 for phase,rows in [('before',s['before']),('after',c['after'])]:
  for n,v in rows.items():assert sha(P/phase/n.lstrip('/'))==v['sha256'],n
 r['selected_files']=len(s['before']);r['all_selected_unchanged']=all(v['sha256']==c['after'][n]['sha256'] for n,v in s['before'].items())
 for name in ['system','software','sam','security','default']:
  r['hives'].append(dict(name=name,**hive(P/'after/E/winnt/system32/config'/name)));save()
 for name,label in [('sysevent.evt','system'),('appevent.evt','application')]:
  records=[]
  for phase in ['before','after']:
   src=P/phase/'E/winnt/system32/config'/name;dest=P/(phase+'-'+label+'.json');assert not dest.exists()
   subprocess.run([sys.executable,str(W/'outputs/native-windows-physical-f/decode-legacy-events.py'),str(src),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL,timeout=30)
   records.append(json.loads(dest.read_text())['records'])
  before,after=records;by={v['record']:v for v in after};r['history_preserved'] &= all(by.get(v['record'])==v for v in before)
  boundary=max((v['record'] for v in before),default=0);r['new_events'][label]=[v for v in after if v['record']>boundary];save()
 r['normal_shutdown_count']=sum(v['source']=='EventLog' and v['event_id']==6006 for v in r['new_events']['system'])
 r['saved_file_matches']=(P/'after/E/xwn480p642/input.txt').read_bytes() in [b'XBOX480',b'XBOX480\r\n']
 r['selected_integrity_passed']=r['all_selected_unchanged'] and c['protected_unchanged'] and r['saved_file_matches'] and all(v['parsed'] for v in r['hives']) and r['history_preserved']
 r.update(completed=True,windows_boot_proven=False,normal_windows_restart_proven=False,historical_Ftdisk49_and_Popup26_resolved=False)
except BaseException as e:r['failure']=repr(e);raise
finally:r['ended_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({k:r[k] for k in ['completed','selected_integrity_passed','all_selected_unchanged','normal_shutdown_count']}))
