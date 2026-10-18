# SPDX-License-Identifier: MIT
"""Run actual candidate byte routines before build; no CPU/API simulation."""
import datetime,hashlib,json,shutil,traceback
from pathlib import Path
import candidate
from candidate import extent
K=Path(__file__).resolve().parent;O=K/'host001.json';assert not O.exists()
assert shutil.disk_usage('C:/').free-32*1024**2>=20*1024**3
sha=lambda b:hashlib.sha256(b).hexdigest();pins={}
def load(p):
    p=Path(p);b=p.read_bytes();pins[str(p.resolve())]=sha(b);return b
r=dict(passed=False,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),physical_access=False,cpu_execution=False,modeled_kernel_or_GL=False)
try:
    for p in [K/'host001.py',K/'candidate.py',K/'DESIGN.md',K/'.gitattributes',K.parent/'image-extent519/extent.py']:load(p)
    review=json.loads(load(K.parent/'image-extent519/final-review.json'));assert review['passed']
    parent=load('C:/xwn516/build001/default.xbe');b=candidate.prepare(parent);assert candidate.validate(b,parent)
    assert len(b)==544096 and b.count(candidate.NEW)==5 and candidate.OLD not in b
    off=candidate.offsets(parent);positions=set(range(4096))|set(range(0x84877,extent.SIZE))|set(range(4096,extent.SIZE,4096))
    for at in off:positions.update(range(at,at+len(candidate.NEW)))
    rejected=0
    for at in sorted(positions):
        q=bytearray(b);q[at]^=1
        if not 0x36c<=at<0x380:q[extent.DIGEST]=extent.digest(q)
        try:candidate.validate(bytes(q),parent)
        except ValueError:rejected+=1
        else:raise AssertionError(('byte mutation accepted',at))
    sizes=[0,4096,extent.SIZE-1,extent.SIZE+1,len(parent),0x85000]
    for size in sizes:
        q=b[:size]+bytes(max(0,size-len(b)))
        try:candidate.validate(q,parent)
        except ValueError:pass
        else:raise AssertionError(('size accepted',size))
    for at in off:
        q=bytearray(b);q[at:at+len(candidate.OLD)]=candidate.OLD;q[extent.DIGEST]=extent.digest(q)
        try:candidate.validate(bytes(q),parent)
        except ValueError:pass
        else:raise AssertionError('stale namespace accepted')
    for p,h in pins.items():assert sha(Path(p).read_bytes())==h
    r.update(passed=True,closed=True,expected_sha256=sha(b),expected_bytes=len(b),namespace_offsets=off,byte_mutations_rejected=rejected,invalid_lengths_rejected=sizes,stale_namespaces_rejected=len(off),actual_Python_transform_and_validator=True,new_XBE_saved=False)
except Exception:r['failure']=traceback.format_exc()
finally:
    r.update(finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs=pins)
    O.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({n:r[n] for n in ['passed','failure','expected_sha256','byte_mutations_rejected'] if n in r}))
if not r['passed']:raise SystemExit(1)
