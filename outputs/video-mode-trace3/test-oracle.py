"""Reject wrong cursors/hotspots/ghosts and one RGB-bit error before and after reset."""
import hashlib,json
from pathlib import Path
from protocol import fnv
k=Path(__file__).resolve().parent;out=k/'candidate001';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
trace=read(out/'trace.json');audit=read(out/'audit.json');checks=[];pins={}
for case in [0,13]:
 stages=trace['cursor_events'][case*3:case*3+3];assert len(stages)==3
 ref=out/'artifacts'/('ref%02d.rgb'%case);reference=ref.read_bytes();assert sha(ref)==audit['files'][case]['sha256'] and audit['files'][case]['matched'];pins[str(ref.relative_to(k))]=sha(ref)
 frames=[]
 for phase,e in enumerate(stages):
  assert e['args'][:2]==[case,phase] and fnv(reference)==e['args'][6]
  p=out/'artifacts'/e['raw'];assert sha(p)==e['sha256'];frames.append(p.read_bytes());pins[str(p.relative_to(k))]=sha(p)
 cx,cy=stages[0]['args'][3:5]
 def expected(shape,shown=True,hotspot_delta=0):
  result=bytearray(reference);hx,hy=([7,11] if shape==0 else [15,3]);hx+=hotspot_delta
  if shown:
   for y in range(32):
    for x in range(32):
     sx=cx-hx+x;sy=cy-hy+y
     if (x//8+shape)%3==0 or not (0<=sx<384 and 0<=sy<256):continue
     at=(sy*384+sx)*4;result[at:at+3]=bytes([(x*3+y*5+shape*101)&255,(y*9+shape*43)&255,(x*7+shape*71)&255])
  return result
 def differences(screen,want):
  return sum(screen[y*4096+x*4:y*4096+x*4+3]!=want[(y*384+x)*4:(y*384+x)*4+3] for y in range(256) for x in range(384))
 old=case%2;new=1-old
 assert [differences(frames[i],expected(new if i==2 else old,i!=1)) for i in range(3)]==[0,0,0]
 for name,data,want in [('old shape after replacement',frames[2],expected(old)),('wrong hotspot',frames[0],expected(old,hotspot_delta=1)),('cursor remains hidden',frames[2],reference),('cursor ghost while hidden',frames[0],reference)]:
  n=differences(data,want);assert n>0;checks.append(dict(case=case,name=name,rejected=True,mismatches=n))
 damaged=bytearray(frames[1]);damaged[100*4096+250*4]^=1;n=differences(damaged,reference);assert n==1
 checks.append(dict(case=case,name='single background RGB bit',rejected=True,mismatches=n))
dest=k/'oracle-tests.json';assert not dest.exists();pins['verifier']=sha(Path(__file__));pins['trace']=sha(out/'trace.json')
dest.write_text(json.dumps(dict(passed=True,actual_before_after_cases=[0,13],checks=checks,pins=pins),indent=2)+'\n');print('Ten before/after-reset RGB oracle mutations rejected')
