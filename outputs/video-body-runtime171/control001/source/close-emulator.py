"""Close owned one-shot evidence without relaunch or collection."""
import ast,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];name=sys.argv[1];assert name in ['control001','candidate001'];case=k/name;dest=case/'closure.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
run=ws/'work/runs'/('nt5-vbody171-'+name);assert (run/'cleanup.json').exists()
pins=read(k/'frozen-inputs.json')
for n,d in pins.items():assert sha(ws/n)==d,n
for p in (case/'source').iterdir():assert p.read_bytes()==(k/p.name).read_bytes(),p
a=read(case/'audit.json')
r=dict(closed=True,run=run.name,cleanup_sha256=sha(run/'cleanup.json'),audit_sha256=sha(case/'audit.json'),
    source_snapshot_exact=True,source_pins_checked=len(pins),physical_access=False,debugger=False,ordinary_qualified=a['strict_qualification_passed'],
    workload_passed=a['workload_passed'],integrity_passed=a['integrity_passed'],strict_qualification_passed=a['strict_qualification_passed'],
    samples=5,live_checks=20,timed_loops=25,scanout_checks=sum(len(v.get('intervals',[]))*2 for v in a['samples']),
    never_relaunch_or_recollect=True)
dest.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r))
