"""Finish only missing cold reads after collection001 FTP502; never relaunch."""
import copy,hashlib,importlib.util,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K))
spec=importlib.util.spec_from_file_location('owned487',K/'physical.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=K/'physical001-collection.json';out=K/'collection-completed002.json';assert not out.exists()
initial=sha(src);r=copy.deepcopy(m.read(src));s=m.read(K/'physical001-stage.json')
assert r['hook_removed'] and r['protected_code_exact'] and not r['completed']
for n,row in r['files'].items():
 if row:assert sha(Path(row['path']))==row['sha256']
r.update(resumed_from_sha256=initial,original_collection_unchanged=True,missing_reads_only=True,remote_writes_after_original_collection=[],previous_failure='FTP PASV502 during next candidate file read; original partial record preserved',fresh_reads=[])
def save():m.write_json(out,r)
save()
with m.connect(timeout=20) as f:
 assert m.get(f,m.HOOK,True) is None
 m.baseline(f,'720p');m.startup(f)
 r['result_namespace_absent']='xwn487' not in {n.lower() for n in m.names(f,'/E')}
 r['candidate_listing']=m.names(f,m.REMOTE);save()
expected=[m.KITROOT+'/startup-used.cmd',m.NORMAL,m.TARGET]+m.MUTABLE+list(s['staged'])+[m.REMOTE+'/'+n for n in ['report.bin','refusal.bin','handoff.bin']]
for n in expected:
 if n in r['files']:continue
 with m.connect(timeout=20) as f:data=m.get(f,n,True)
 with m.connect(timeout=20) as f:second=m.get(f,n,True)
 assert data==second,n
 r['fresh_reads'].append(n)
 if data is None:r['files'][n]=None
 else:
  row=m.keep(m.P/'after-missing002',n,data);prior=s['before'].get(n) or s['staged'].get(n)
  if prior:row['unchanged']=row['sha256']==prior['sha256'];assert row['unchanged']
  r['files'][n]=row
 save()
assert sha(src)==initial
r.update(completed=True,ended_utc=m.utc(),normal_windows_shutdown_proved=False,original_collection_unchanged=True)
save();print(json.dumps(dict(completed=True,missing_reads=len(r['fresh_reads']),result_namespace_absent=r['result_namespace_absent'])))
