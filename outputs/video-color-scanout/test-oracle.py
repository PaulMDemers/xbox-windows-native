"""Negative checks on actual captured color, hidden and replacement frames."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001';read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
trace=read(out/'trace.json');stages=trace['cursor_events'][:3];assert len(stages)==3
paths=[out/'artifacts'/e['raw'] for e in stages];refs=[out/'artifacts'/e['reference_raw'] for e in stages]
for e,p,r in zip(stages,paths,refs):assert sha(p)==e['sha256'] and sha(r)==e['reference_sha256']
assert len({sha(p) for p in refs})==1
reference=refs[0].read_bytes();frames=[p.read_bytes() for p in paths]
def expected(shape,shown=True,hotspot_delta=0):
 result=bytearray(reference);hx,hy=([7,11] if shape==0 else [15,3]);hx+=hotspot_delta
 if shown:
  for y in range(32):
   for x in range(32):
    sx=80-hx+x;sy=70-hy+y
    if (x//8+shape)%3==0 or not (0<=sx<384 and 0<=sy<256):continue
    color=bytes([(x*3+y*5+shape*101)&255,(y*9+shape*43)&255,(x*7+shape*71)&255])
    at=(sy*384+sx)*4;result[at:at+3]=color
 return result
def mismatches(screen,want):
 return sum(screen[y*4096+x*4:y*4096+x*4+3]!=want[(y*384+x)*4:(y*384+x)*4+3] for y in range(256) for x in range(384))
assert [mismatches(frames[i],expected(i==2,i!=1)) for i in range(3)]==[0,0,0]
checks=[]
for name,data,oracle in [('old shape after replacement',frames[2],expected(0)),('wrong hotspot',frames[0],expected(0,hotspot_delta=1)),('cursor remains hidden',frames[2],reference),('cursor ghost while hidden',frames[0],reference)]:
 n=mismatches(data,oracle);assert n>0;checks.append(dict(name=name,rejected=True,mismatches=n))
damaged=bytearray(frames[1]);damaged[100*4096+250*4]^=1
n=mismatches(damaged,reference);assert n==1;checks.append(dict(name='single background RGB bit',rejected=True,mismatches=n))
dest=k/'oracle-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,baseline_three_phases_match=True,checks=checks,
 pins={str(p.relative_to(k)):sha(p) for p in paths+refs+[Path(__file__),out/'trace.json']}),indent=2)+'\n')
print('Five color lifecycle framebuffer oracle mutations rejected')
