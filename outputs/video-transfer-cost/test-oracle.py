"""Equal-area, disjointness, row-copy and exact RGB oracle checks."""
import hashlib,json,struct
from pathlib import Path
from protocol import *
k=Path(__file__).resolve().parent;dest=k/'oracle-tests.json';assert not dest.exists();checks=0
for n in range(45):
 size,kind=identity(n);w,h=SIZES[size];rects=rectangles(n);points=set()
 for l,t,r,b in rects:
  assert 0<=l<r<=W and 0<=t<b<=H
  cells={(x,y) for y in range(t,b) for x in range(l,r)};assert not points&cells;points|=cells;checks+=1
 assert len(points)==w*h;checks+=1
 assert sum(b-t for l,t,r,b in rects)==h*(len(rects) if kind in [2,4] else 1);checks+=1
 data=expected_bytes(n);assert len(data)==W*H*4;values=struct.unpack('<%dI'%(W*H),data)
 for x,y in [(0,0),(W-1,H-1),(w-1,h-1),(w,h),(w//2,h//2),(2*w-w//16-1,h//2)]:
  assert values[y*W+x]==(0x2bc757 if (x,y) in points else base(x,y));checks+=1
 for x,y in points:assert values[y*W+x]==0x2bc757
 checks+=1
 if n>=15:
  match=next(j for j in range(15) if identity(j)==identity(n));assert data==expected_bytes(match);checks+=1
for data in [None,b'',b'garbage',b'ATTEMPT_ONCE 139 45 294912\n']:
 assert not validate_log(data)['passed'];checks+=1
r=dict(passed=True,checks=checks,cases=45,areas=[w*h for w,h in SIZES],pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['probe.c','protocol.py','test-oracle.py']})
dest.write_text(json.dumps(r,indent=2)+'\n');print(checks,'geometry/oracle checks passed')
