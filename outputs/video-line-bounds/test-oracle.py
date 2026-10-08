"""Host-only endpoint, clipping and protocol mutation checks."""
import hashlib,json,struct
from pathlib import Path
from protocol import LINES,CASES,points,expected_bytes,fnv,validate_log
k=Path(__file__).resolve().parent;checks=0
counts=[32,32,32,32,32,32,32,32,52,53,52,53,16,15,32,31,4,0]
for i,want in enumerate(counts):
 pts=points(i);assert len(pts)==want and len(set(pts))==want
 x,y,endx,endy,clip=LINES[i];assert (endx,endy) not in pts
 data=expected_bytes(i);assert len(data)==393216
 for px,py in pts:assert struct.unpack_from('<I',data,(py*384+px)*4)[0]==0xdd2597
 checks+=3
assert (20,20) in points(0) and (52,20) in points(1) and (20,20) not in points(1);checks+=1
assert points(16)==[(380,20),(381,20),(382,20),(383,20)];checks+=1
lines=[]
def add(s,*v):lines.append(s+' '+' '.join(map(str,v)))
add('ATTEMPT_ONCE',129,18,98304);add('INSTALL_IDLE_START',0,0,0);add('DRIVER_REVISION_GEOMETRY',109,1024,576)
for n in range(18):
 add('CLIP_TYPE_LEFT_TOP',2,0,0);add('CLIP_RIGHT_BOTTOM',1024,576,n);add('CASE_API',n,1,1);add('PIXELS_BAD_CHANGED',98304,0,counts[n]);digest=fnv(expected_bytes(n));add('REFERENCE_HASH_BYTES',digest,393216,digest);add('SOURCE_HASH_PAIR',1,1,0)
 for j in range(2,19):
  add('QUIET_COUNTER',j,0,0);add('REFERENCE_COUNTER',j,0,0);add('DRAW_COUNTER',j,0,1 if j in [8,16] and n!=17 else counts[n]*4 if j==17 else 0)
 add('COHERENCE_ACTIVE',0,1,0)
add('RELEASED',1,0,0);add('COMPLETE',0,18,18*98304);add('INSTALL_IDLE_END',0,0,0);add('NORMAL_RESTART_REQUEST',0,0,0)
raw=('\n'.join(lines)+'\n').encode();valid=validate_log(raw);assert valid['passed'] and valid['profile_attribution_passed'];checks+=1
mutations={
 'pixel':raw.replace(b'PIXELS_BAD_CHANGED 98304 0',b'PIXELS_BAD_CHANGED 98304 1',1),
 'endpoint_count':raw.replace(b'PIXELS_BAD_CHANGED 98304 0 32',b'PIXELS_BAD_CHANGED 98304 0 33',1),
 'quiet':raw.replace(b'QUIET_COUNTER 3 0 0',b'QUIET_COUNTER 3 1 0',1),
 'clip':raw.replace(b'CLIP_RIGHT_BOTTOM 1024 576',b'CLIP_RIGHT_BOTTOM 10 576',1),
 'api':raw.replace(b'CASE_API 0 1 1',b'CASE_API 0 1 0',1),
 'coherence':raw.replace(b'COHERENCE_ACTIVE 0 1 0',b'COHERENCE_ACTIVE 1 1 0',1),
 'missing_end':raw.rsplit(b'NORMAL_RESTART_REQUEST',1)[0]}
for name,bad in mutations.items():
 assert bad!=raw
 r=validate_log(bad);assert not(r['passed'] and r['profile_attribution_passed']),name;checks+=1
dest=k/'oracle-tests.json';assert not dest.exists()
dest.write_text(json.dumps(dict(passed=True,host_only=True,checks=checks,mutations=list(mutations),pins={n:hashlib.sha256((k/n).read_bytes()).hexdigest() for n in ['protocol.py','test-oracle.py']}),indent=2)+'\n',encoding='utf-8')
print(checks,'host checks passed')
