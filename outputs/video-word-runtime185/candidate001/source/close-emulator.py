"""Close single ordinary case and verify frozen sources; never relaunch."""
from common import *
case=sys.argv[1];assert case in ['control001','candidate001'];out=k/case;dest=out/'closure.json';assert not dest.exists()
run=ws/('work/runs/nt5-word185-'+case);assert (run/'cleanup.json').exists()
pins=read(k/'frozen-inputs.json')
for n,h in pins.items():assert sha(ws/n)==h,n
for p in (out/'source').iterdir():assert p.read_bytes()==(k/p.name).read_bytes(),p
a=read(out/'audit.json');package=read(out/'package-verification.json')
save(dest,dict(closed=True,run=run.name,cleanup_sha256=sha(run/'cleanup.json'),audit_sha256=sha(out/'audit.json'),source_snapshot_exact=True,source_pins_checked=len(pins),physical_access=False,debugger=False,workload_passed=a['workload_passed'],integrity_passed=a['integrity_passed'],strict_qualification_passed=a['strict_qualification_passed'],ordinary_qualified=a['strict_qualification_passed'],package_bound=package['package_bound'],samples=5,copy_checks=20,additional_dib_checks=sum(6 for v in a['dib_samples'] if v['passed']),timed_loops=sum(len(v['timed_loops']) for v in a['samples']),never_relaunch_or_recollect=True))
print('Closed185',case)
