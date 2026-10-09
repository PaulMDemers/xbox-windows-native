"""Close the host-only refusal without pretending Windows launched."""
import ast,subprocess
from common import *
out=k/'candidate001';dest=out/'host-closure.json';assert not dest.exists()
run=ws/'work/runs/nt5-settled180-candidate001';assert (run/'cleanup.json').exists() and not (out/'launch.json').exists()
f=read(k/'fixture-candidate001.json');disk=run/'hdd.qcow2';files=[]
with ColdIO(disk) as io:
 rr=readers(io,disk)
 for n,d in f['files'].items():v,p=n.split('/',1);files.append(dict(path=n,sha256=m.sha(rr[v].read(p)),matched=m.sha(rr[v].read(p))==d))
 for n in HIVES:assert rr['F'].read('winnt/system32/config/'+n)==(k.parent/'device-unused-package179/candidate001/artifacts'/('after-'+n)).read_bytes()
 if (out/'host-allocation.json').exists():raise AssertionError('Never repeat host audit')
scan(disk,out/'host-audit/artifacts');a=read(out/'host-audit/allocation.json')
pins=read(k/'frozen-inputs.json')
for n,d in pins.items():assert sha(ws/n)==d,n
for p in (out/'source').iterdir():assert p.read_bytes()==(k/p.name).read_bytes(),p
r=dict(closed=True,physical_access=False,windows_launch_requested=False,workload_passed=False,strict_qualification_passed=False,ordinary_qualified=False,
 host_bootstrap_failed=True,reason='Copied closed parent retained a Linux absolute backing path; Windows xemu refused opening /mnt/c backing. Original failed source/fixtures preserved. No supervisor or SITE EXEC Windows request.',
 files=files,all_prepared_payloads_unchanged=all(v['matched'] for v in files),five_hives_unchanged=True,allocation_passed=a['allocation_consistent'] and not a['errors'] and not a['orphan_cluster_count'],
 frozen_pins_checked=len(pins),source_snapshots_exact=True,cleanup_sha256=sha(run/'cleanup.json'),never_relaunch_or_recollect=True,
 next='Fresh181 copy must rebase only to a same-directory relative basename, compare virtual equality and validate every Windows backing path before bootstrap; never modify/rerun180.')
save(dest,r);print(json.dumps({v:r[v] for v in ['closed','windows_launch_requested','all_prepared_payloads_unchanged','allocation_passed','frozen_pins_checked']}))
