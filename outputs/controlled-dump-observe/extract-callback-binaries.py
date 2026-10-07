"""Read exact callback components from immutable before/closed-after disks."""
from common import *
out=k/'crash002';assert not (out/'callback-binaries.json').exists();f=read(k/'fixture-crash002.json')
base=ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'];disk=ws/'work/runs/nt5-controlled-dump-observe-crash002/hdd.qcow2'
assert sha(base)==f['fixture_sha256'] and (disk.parent/'cleanup.json').exists()
rows=[]
for phase,p in [('before',base),('after',disk)]:
    with ColdIO(p) as io:
        rr=readers(io,p)
        for n in ['ndis.sys','nvnetnt5.sys']:
            b=rr['F'].read('winnt/system32/drivers/'+n);dest=out/'artifacts'/(phase+'-'+n);assert not dest.exists();dest.write_bytes(b);rows.append(dict(phase=phase,name=n,sha256=m.sha(b),size=len(b)))
assert all(rows[i]['sha256']==rows[i+2]['sha256'] for i in range(2))
save(out/'callback-binaries.json',dict(scope=__doc__,unchanged=True,files=rows,physical_access=False));print(rows)
