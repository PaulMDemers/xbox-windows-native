"""Independent geometry/translation and exact image checks, not guest evidence."""
import hashlib,json,struct
from pathlib import Path
from protocol import *
k=Path(__file__).resolve().parent;dest=k/'oracle-tests.json';assert not dest.exists();checks=0
for sample in range(45):
 cell,kind=identity(sample);w,h,kind,x,y=GEOMETRIES[cell];rects=rectangles(sample);points=set()
 for l,t,r,b in rects:
  assert 0<=l<r<=W and 0<=t<b<=H
  cells={(px,py) for py in range(t,b) for px in range(l,r)}
  assert not cells&points;points |= cells;checks+=1
 assert len(points)==w*h;checks+=1
 assert sum(b-t for l,t,r,b in rects)==h*(len(rects) if kind==4 else 1);checks+=1
 if cell<9:
  basecell=cell-cell%3
  original=set((px,py) for l,t,r,b in rectangles(basecell) for py in range(t,b) for px in range(l,r))
  assert points=={(px+x,py+y) for px,py in original};checks+=1
 else:
  assert len(rects)==1 and h==96 and (x,y)==(320,64);checks+=1
 data=expected_bytes(sample);assert len(data)==W*H*4;values=struct.unpack('<%dI'%(W*H),data)
 for px,py in [(0,0),(W-1,H-1),(x,y),(x+w-1,y+h-1),(x+w,y+h)]:
  assert values[py*W+px]==(0x2bc757 if (px,py) in points else base(px,py));checks+=1
 assert all(values[py*W+px]==0x2bc757 for px,py in points);checks+=1
 if sample>=15:
  assert data==expected_bytes(cell);checks+=1
for bad in [None,b'',b'garbage',b'ATTEMPT_ONCE 141 45 294912\n']:
 assert not validate_log(bad)['passed'];checks+=1
r=dict(passed=True,checks=checks,cases=45,geometries=GEOMETRIES,pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['probe.c','protocol.py','test-oracle.py']})
dest.write_text(json.dumps(r,indent=2)+'\n');print(checks,'geometry/oracle checks passed')
