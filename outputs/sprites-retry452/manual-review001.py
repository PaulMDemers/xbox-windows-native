"""Audit separate manual-boot capture; no per-boot attribution or sample claim."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
def path(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'manual-review001.json';assert not out.exists()
m=json.loads((K/'manual-observation002.json').read_text(encoding='utf-8'));assert m['completed']
old=json.loads((K.parent/'sprites-xbox451/physical001-collection.json').read_text())
r=dict(scope='Aggregate logs after user manual boots; no individual boot attribution',hives={},events={},sample_qualified=False)
for n,row in m['files'].items():assert sha(path(row['path']))==row['sha256']
for name in ['system','software','sam','security','default']:
 p=path(m['files']['/E/winnt/system32/config/'+name]['path']);v=audit(p)
 assert v['clean'] and v['header_valid'] and v['independent_raw_values_agree'];r['hives'][name]=v
for name in ['sysevent.evt','appevent.evt']:
 remote='/E/winnt/system32/config/'+name;rows={}
 for phase,record in [('before',old['files'][remote]),('after',m['files'][remote])]:
  p=path(record['path']);assert sha(p)==record['sha256']
  dest=path(m['files'][remote]['path']).with_name(name+'-'+phase+'-manual.json');assert not dest.exists()
  subprocess.run([sys.executable,'-B',str(K.parent/'native-windows-physical-f/decode-legacy-events.py'),str(p),'--output',str(dest)],check=True,stdout=subprocess.DEVNULL)
  rows[phase]=json.loads(dest.read_text())['records']
 boundary=max((e['record'] for e in rows['before']),default=0)
 r['events'][name]=dict(new_records=[{k:e[k] for k in ['record','source','event_id','type','generated_unix']} for e in rows['after'] if e['record']>boundary],normal_shutdown_delta=sum(e['source']=='EventLog' and e['event_id']==6006 for e in rows['after'])-sum(e['source']=='EventLog' and e['event_id']==6006 for e in rows['before']))
r.update(private_files_verified=len(m['files']),active_ring_completeness=False,per_boot_attribution=False)
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(clean_hives=len(r['hives']),shutdown_delta=r['events']['sysevent.evt']['normal_shutdown_delta'])))
