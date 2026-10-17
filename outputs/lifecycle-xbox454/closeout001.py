"""Close physical presentation evidence; system and sample gates stay separate."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def path(s):return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
out=K/'final-review.json';assert not out.exists()
r=json.loads((K/'runtime-review001.json').read_text());c=json.loads((K/'physical001-collection.json').read_text());stage=json.loads((K/'physical001-stage.json').read_text())
assert c['completed'] and c['hook_removed'] and c['protected_code_exact'] and r['normal_restart_supported']
private={}
for row in list(c['files'].values())+list(stage['before'].values()):
 p=path(row['path']);assert sha(p)==row['sha256'];private[str(p)]=row['sha256']
for p,h in r['frozen_dependencies'].items():assert sha(path(p))==h
build=json.loads((K/'build001.json').read_text());assert build['exit_code']==0
for p,h in build['headers'].items():assert sha(Path(p))==h
for row in build['rows']:assert sha(Path(row['path']))==row['sha256']
popups=[];ids={e['record'] for e in r['events']['system']['new_records']}
events=json.loads(path(c['files']['/E/winnt/system32/config/sysevent.evt']['path']).with_name('system-events.json').read_text())['records']
for e in events:
 if e['record'] in ids and e['source']=='Application Popup':popups.append({k:e[k] for k in ('record','event_id','strings')})
modes=[[row['fields'].get('mode.'+k) for k in ('width','height','bpp')] for row in r['rows']]
assert modes==[['1280','720','32']]*2,modes
controls=json.loads((K/'actual-controls001.json').read_text()) if (K/'actual-controls001.json').exists() else None
record=dict(scoped_lifecycle_passed=r['all_allowed_cases_passed'],strict_system_qualified=False,mode=modes,normal_restart_supported=True,hook_removed=True,protected_code_and_startup_exact=True,
 private_files=private,frozen_dependencies_verified=len(r['frozen_dependencies']),popups=popups,
 actual_mutations_rejected=sum(v['scalar_rejections']+v['pixel_length_rejections'] for v in controls['rows']) if controls else None,
 exact_bytes=sum(row.get('review',{}).get('exact_bytes',0) for row in r['rows']),
 limitations=['Historical Ftdisk49 remains','Shutdown event/typed-registry limitations remain separate','No full FATX allocation audit','Raw system-memory readback, not human visual/scanout qualification','No GPU/D3D/performance claim'],console_C_accessed=False)
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ('scoped_lifecycle_passed','exact_bytes','popups','normal_restart_supported')}))
