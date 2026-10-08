"""Record completed owned emulator cases, verify frozen sources; no recollection."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=read(k/'frozen-inputs.json')
for name,digest in pins.items():assert sha(ws/name)==digest,name
cases=[]
for case in ['control001','candidate001']:
    out=k/case;dest=out/'closure.json';assert not dest.exists()
    run=ws/'work/runs'/('nt5-vperf166-'+case);assert (run/'cleanup.json').exists()
    a=read(out/'audit.json');assert a['workload_passed'] and a['integrity_passed']
    for p in (out/'source').iterdir():assert sha(p)==sha(k/p.name),p.name
    result=dict(closed=True,run=run.name,cleanup_sha256=sha(run/'cleanup.json'),audit_sha256=sha(out/'audit.json'),
        source_snapshot_exact=True,source_pins_checked=len(pins),physical_access=False,
        strict_qualification_passed=a['strict_qualification_passed'],samples=5,live_checks=20,timed_loops=25,
        never_relaunch_or_recollect=True)
    dest.write_bytes((json.dumps(result,indent=2)+'\n').encode('utf-8'));cases.append(result)
(k/'emulator-closure.json').write_bytes((json.dumps(dict(passed=True,cases=cases,owned_emulators_closed=True),indent=2)+'\n').encode('utf-8'))
print('Both emulator cases closed, source snapshots/pins exact')
