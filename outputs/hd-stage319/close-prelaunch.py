"""Cold closure of prelaunch transport failure; no invented Windows launch."""
import sys,json,hashlib
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001';run=Path('/mnt/d/xwn319/runs/nt5-hd319-candidate001');assert (run/'cleanup.json').exists() and not (out/'launch.json').exists()
sys.path.insert(0,str(k.parent/'video-text-oracle206'));from common import ColdIO,readers,sha,hive,scan,HIVES,m
f=json.loads((out/'fixture.json').read_text());base=Path(f['fixture_path_linux']);disk=run/'hdd.qcow2';assert sha(base)==f['fixture_sha256']
r=dict(closed=True,physical_access=False,windows_launch_requested=False,trace_passed=False,files={},hives=[],no_workload=True)
with ColdIO(base) as a,ColdIO(disk) as b:
 before=readers(a,base);after=readers(b,disk)
 for n in f['files']:
  v,p=n.split('/',1);old=before[v].read(p);now=after[v].read(p);r['files'][n]=dict(sha256=m.sha(now),unchanged=old==now);assert old==now,n
 for n in HIVES:
  p=out/'artifacts'/('cold-'+n);p.write_bytes(after['F'].read('winnt/system32/config/'+n));r['hives'].append(dict(name=n,**hive(p)))
 try:after['F'].read(f['namespace']+'/attempt.log')
 except KeyError:pass
 else:raise AssertionError('Unexpected Windows workload')
scan(disk,out/'artifacts');allocation=json.loads((out/'allocation.json').read_text());assert allocation['allocation_consistent'] and not allocation['errors'] and not allocation['orphan_cluster_count']
r['allocation']=allocation;r['host_exit']=json.loads((run/'host-exit.json').read_text(encoding='utf-8-sig'));assert r['host_exit']['passed']
r['transport_cleanup']=json.loads((out/'transport-cleanup.json').read_text());assert r['transport_cleanup']['physical_mode']=='0' and 'VM status: running' in r['transport_cleanup']['after']
r['integrity_passed']=True;(k/'final-review.json').write_text(json.dumps(r,indent=2)+'\n');print('319 prelaunch failure closed; original files/hives/allocation clean; orderly exit')
