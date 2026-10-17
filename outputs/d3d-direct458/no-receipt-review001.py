"""Review collected no-receipt attempt without inventing sample execution."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent; W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
sys.path.insert(0,str(K.parent/'clean-media404'))
from hive_audit004 import audit
def path(s):
    return Path('/mnt/'+s[0].lower()+s[2:].replace('\\','/')) if len(s)>2 and s[1]==':' else Path(s)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'no-receipt-review001.json'; assert not out.exists()
stage=json.loads((K/'physical001-stage.json').read_text(encoding='utf-8'))
c=json.loads((K/'physical001-collection.json').read_text(encoding='utf-8'))
assert stage['completed'] and c['completed'] and c['hook_removed'] and c['protected_code_exact']
assert 'result_directory' not in c
private={}
for row in list(stage['before'].values())+list(c['files'].values()):
    p=path(row['path']); assert sha(p)==row['sha256']; private[str(p)]=row['sha256']
unchanged={}; hives={}
for name in ['system','software','sam','security','default','sysevent.evt','appevent.evt']:
    n='/E/winnt/system32/config/'+name
    a=path(stage['before'][n]['path']); b=path(c['files'][n]['path'])
    unchanged[name]=a.read_bytes()==b.read_bytes()
    if name.endswith('.evt'): continue
    hives[name]={'before':audit(a),'after':audit(b)}
    assert all(v['clean'] and v['header_valid'] and v['independent_raw_values_agree'] for v in hives[name].values())
package=json.loads((K/'package001.json').read_text(encoding='utf-8'))
for p,h in package['dependencies'].items(): assert sha(path(p))==h,p
for row in package['files'].values(): assert sha(path(row['path']))==row['sha256']
r=dict(scope='One accepted launch, no result directory or sample receipt at collection',
    sample_executed=None,scoped_inventory_passed=False,normal_windows_restart_proved=False,
    strict_system_qualified=False,hook_removed=True,mode='720p',protected_code_and_startup_exact=True,
    unchanged_hives_and_events=unchanged,hives=hives,private_files=private,
    frozen_dependencies_verified=len(package['dependencies']),payloads_verified=len(package['files']),
    console_C_accessed=False,full_allocation_audit=False,
    limitations=['Missing receipt does not identify the failing boot stage','No Direct3D inventory hardware qualification','No automatic relaunch of this consumed attempt'])
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:r[k] for k in ['scoped_inventory_passed','unchanged_hives_and_events','hook_removed']}))
